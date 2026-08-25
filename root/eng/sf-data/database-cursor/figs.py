# -*- coding: utf-8 -*-
"""Фігури для теми «Курсор бази даних» (root/eng/sf-data/database-cursor)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
TEAL_F, TEAL_S = "#e6fffa", "#0d9488"
BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
RED_F, RED_S = "#fef2f2", "#dc2626"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"

def fig1_cursor_streaming_vs_buffering():
    """fig1-cursor-streaming-vs-buffering.svg: Буферизування vs Потоковий курсор."""
    W, H = 840, 460
    frags = []

    frags.append(rect(10, 10, 820, 440, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 36, "Порівняння архітектур вибірки: Клієнтське буферизування проти Серверного курсора", size=15, bold=True, color="#1e293b"))

    # Ліва колонка: Повне клієнтське буферизування
    frags.append(rect(30, 60, 375, 370, fill=RED_F, stroke=RED_S, sw=1.2, rx=8))
    frags.append(text(217, 85, "Клієнтське буферизування (Всі рядки одразу)", size=13, bold=True, color="#991b1b"))

    b_srv1, _, _ = textbox(217, 130, "Сервер СУБД\nВиконує повний запит (50 млн рядків)\nВивантажує всі дані у TCP-сокет", size=10.5, pad=6, fill="#ffffff", stroke=RED_S, min_w=335)
    frags.append(b_srv1)

    frags.append(arrow(217, 165, 217, 205, color=RED_S, sw=2))
    frags.append(text(275, 185, "TCP Stream (60 ГБ)", size=10, italic=True, color="#991b1b"))

    b_net1, _, _ = textbox(217, 240, "Мережевий буфер і Драйвер\nКлієнт накопичує всі 60 ГБ у RAM\nВеличезна затримка до 1-го рядка", size=10.5, pad=6, fill="#ffffff", stroke=RED_S, min_w=335)
    frags.append(b_net1)

    frags.append(arrow(217, 275, 217, 315, color=RED_S, sw=2))

    b_oom, _, _ = textbox(217, 365, "Аварія пам'яті (OOM Crash)\nRAM клієнта вичерпано (виділено 4 ГБ < 60 ГБ)\nПроцес аварійно зупинено", size=10.5, pad=6, fill="#fee2e2", stroke="#b91c1c", bold=True, min_w=335)
    frags.append(b_oom)

    # Права колонка: Серверний потоковий курсор
    frags.append(rect(435, 60, 375, 370, fill=GREEN_F, stroke=GREEN_S, sw=1.2, rx=8))
    frags.append(text(622, 85, "Серверний потоковий курсор (Ітеративна вибірка)", size=13, bold=True, color="#166534"))

    b_srv2, _, _ = textbox(622, 130, "Сервер СУБД (Ітератор плану)\nЗберігає активний стан виконання (Portal)\nГенерує кортежі за запитом", size=10.5, pad=6, fill="#ffffff", stroke=GREEN_S, min_w=335)
    frags.append(b_srv2)

    frags.append(arrow(622, 165, 622, 205, color=GREEN_S, sw=2))
    frags.append(text(710, 185, "FETCH 1000 (1.5 МБ)", size=10, italic=True, color="#166534"))

    b_net2, _, _ = textbox(622, 240, "Клієнтський ітератор\nОтримує пакет із 1000 рядків\nОбробляє рядки у конвеєрі", size=10.5, pad=6, fill="#ffffff", stroke=GREEN_S, min_w=335)
    frags.append(b_net2)

    frags.append(arrow(622, 275, 622, 315, color=GREEN_S, sw=2))

    b_ok, _, _ = textbox(622, 365, "Стабільне виконання O(1) RAM\nПам'ять клієнта обмежена розміром пакета\nМінімальний час до початку обробки", size=10.5, pad=6, fill="#dcfce7", stroke="#15803d", bold=True, min_w=335)
    frags.append(b_ok)

    render(os.path.join(IMG, "fig1-cursor-streaming-vs-buffering.svg"), W, H, *frags)

def fig2_volcano_iterator_engine():
    """fig2-volcano-iterator-engine.svg: Дерево ітераторів моделі Volcano та курсор."""
    W, H = 840, 480
    frags = []

    frags.append(rect(10, 10, 820, 460, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 36, "Модель ітераторів Volcano: Інтеграція курсора з деревом плану виконання", size=15, bold=True, color="#1e293b"))

    # Клієнтська межа
    b_client, _, _ = textbox(160, 100, "Клієнтська програма\nFETCH 1 FROM cur\n(Очікує 1 кортеж)", size=11, pad=8, fill=BLUE_F, stroke=BLUE_S, bold=True, min_w=220)
    frags.append(b_client)

    frags.append(arrow(275, 100, 360, 100, color=BLUE_S, sw=2))
    frags.append(text(318, 90, "SQL FETCH", size=10, italic=True, color=BLUE_S))

    # Курсорний портал на сервері
    b_portal, _, _ = textbox(520, 100, "Серверний портал (Cursor Portal)\nТримає вказівник на корінь дерева плану\nВикликає root_plan->next()", size=11, pad=8, fill=PURPLE_F, stroke=PURPLE_S, bold=True, min_w=300)
    frags.append(b_portal)

    # Дерево фізичних операторів Volcano
    frags.append(arrow(520, 135, 520, 175, color=PURPLE_S, sw=2))
    frags.append(text(560, 155, "next()", size=10, bold=True, color=PURPLE_S))

    b_limit, _, _ = textbox(520, 205, "Вузол Limit / Projection\nВибирає необхідні стовпці та передає вгору", size=10.5, pad=6, fill=TEAL_F, stroke=TEAL_S, min_w=280)
    frags.append(b_limit)

    frags.append(arrow(520, 235, 520, 275, color=TEAL_S, sw=2))
    frags.append(text(560, 255, "next()", size=10, bold=True, color=TEAL_S))

    b_filter, _, _ = textbox(520, 305, "Вузол Filter (Selection: amount > 1000)\nВикликає дочірній вузол, доки умова не стане TRUE", size=10.5, pad=6, fill=AMBER_F, stroke=AMBER_S, min_w=280)
    frags.append(b_filter)

    frags.append(arrow(520, 335, 520, 375, color=AMBER_S, sw=2))
    frags.append(text(560, 355, "next()", size=10, bold=True, color=AMBER_S))

    b_scan, _, _ = textbox(520, 405, "Вузол IndexScan (B-Tree Scan)\nЧитає сторінки індексу та видобуває кортеж із таблиці", size=10.5, pad=6, fill=GREEN_F, stroke=GREEN_S, min_w=280)
    frags.append(b_scan)

    # Пояснення зліва
    b_desc, _, _ = textbox(160, 290, "Властивості конвеєра:\n1. open(): ініціалізація стану\n2. next(): повертає рівно 1 рядок\n3. close(): звільнення ресурсів\n\nНемає матеріалізації,\nдані течуть «знизу-вгору».", size=10, pad=8, fill=GRAY_F, stroke=GRAY_S, min_w=220)
    frags.append(b_desc)

    render(os.path.join(IMG, "fig2-volcano-iterator-engine.svg"), W, H, *frags)

def fig3_cursor_lifecycle_and_types():
    """fig3-cursor-lifecycle-and-types.svg: Життєвий цикл курсора та типи матеріалізації."""
    W, H = 840, 460
    frags = []

    frags.append(rect(10, 10, 820, 440, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 34, "Життєвий цикл курсора, команди керування та режими зберігання", size=15, bold=True, color="#1e293b"))

    # Фази життєвого циклу
    states = [
        ("DECLARE", "Оголошення запиту\nСтворення структури плану", 100, 110, BLUE_F, BLUE_S),
        ("OPEN", "Створення знімка\nІніціалізація Portal", 280, 110, TEAL_F, TEAL_S),
        ("FETCH / MOVE", "Ітеративне читання\nЗсув позиції рядка", 470, 110, GREEN_F, GREEN_S),
        ("CLOSE / COMMIT", "Звільнення дескриптора\nОчищення пам'яті", 680, 110, AMBER_F, AMBER_S),
    ]

    for title, desc, cx, cy, f_clr, s_clr in states:
        box, _, _ = textbox(cx, cy, title + "\n" + desc, size=10, pad=6, fill=f_clr, stroke=s_clr, bold=True, min_w=150)
        frags.append(box)

    frags.append(arrow(180, 110, 200, 110, color=LINE, sw=1.8))
    frags.append(arrow(360, 110, 390, 110, color=LINE, sw=1.8))
    frags.append(arrow(550, 110, 595, 110, color=LINE, sw=1.8))

    # Нижній блок 1: Режими переміщення (SCROLL vs NO SCROLL)
    frags.append(rect(30, 190, 375, 235, fill=GRAY_F, stroke=GRAY_S, sw=1.2, rx=8))
    frags.append(text(217, 215, "Режими переміщення (Scrollability)", size=12, bold=True, color="#1e293b"))

    b_noscroll, _, _ = textbox(217, 270, "NO SCROLL (Тільки вперед):\n• Дозволяє чистий потоковий конвеєр\n• Нульові накладні витрати на тимчасовий диск\n• Підтримує лише FETCH NEXT", size=10, pad=6, fill="#ffffff", stroke=GREEN_S, min_w=345)
    frags.append(b_noscroll)

    b_scroll, _, _ = textbox(217, 365, "SCROLL (Двонапрямлений рух):\n• Дозволяє FETCH PRIOR / FIRST / ABSOLUTE\n• Примусово матеріалізує результат у Tuplestore\n• Додаткове навантаження на I/O та пам'ять", size=10, pad=6, fill="#ffffff", stroke=AMBER_S, min_w=345)
    frags.append(b_scroll)

    # Нижній блок 2: Межі транзакцій (WITH HOLD vs WITHOUT HOLD)
    frags.append(rect(435, 190, 375, 235, fill=GRAY_F, stroke=GRAY_S, sw=1.2, rx=8))
    frags.append(text(622, 215, "Межі транзакцій (Holdability)", size=12, bold=True, color="#1e293b"))

    b_withouthold, _, _ = textbox(622, 270, "WITHOUT HOLD (За замовчуванням):\n• Курсор прив'язаний до транзакції\n• Автоматично закривається при COMMIT/ROLLBACK\n• Блокування рядків утримуються протягом транзакції", size=10, pad=6, fill="#ffffff", stroke=BLUE_S, min_w=345)
    frags.append(b_withouthold)

    b_withhold, _, _ = textbox(622, 365, "WITH HOLD (Збереження після фіксації):\n• Залишається відкритим після COMMIT\n• Сервер повністю матеріалізує залишок у файл\n• Блокування таблиць знімаються, читання зі знімка", size=10, pad=6, fill="#ffffff", stroke=PURPLE_S, min_w=345)
    frags.append(b_withhold)

    render(os.path.join(IMG, "fig3-cursor-lifecycle-and-types.svg"), W, H, *frags)

def fig4_cursor_mvcc_vacuum_impact():
    """fig4-cursor-mvcc-vacuum-impact.svg: Вплив відкритого курсора на MVCC та очищення (Vacuum)."""
    W, H = 840, 450
    frags = []

    frags.append(rect(10, 10, 820, 430, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(420, 34, "Вплив довготривалого курсора на MVCC: Утримання горизонту xmin та розростання таблиць", size=14, bold=True, color="#1e293b"))

    # Часова шкала транзакцій
    frags.append(line(50, 80, 780, 80, color=LINE, sw=2))
    frags.append(text(780, 70, "Час / Номери транзакцій (XID)", size=10, italic=True, color=MUTED, anchor="end"))

    tx_marks = [(120, "TX 1000\n(Старт)"), (260, "TX 1020\n(Курсор OPEN)"), (430, "TX 1050\n(UPDATE рядок A)"), (600, "TX 1080\n(DELETE рядок B)"), (740, "TX 1100\n(Поточний час)")]
    for x, lbl in tx_marks:
        frags.append(circle(x, 80, 5, fill=BLUE_S, stroke=BLUE_S))
        frags.append(mtext(x, 100, lbl, size=9.5, color="#1e293b", bold=True))

    # Горизонт xmin
    frags.append(line(260, 135, 260, 310, color=RED_S, sw=1.8, dash="4,4"))
    b_xmin, _, _ = textbox(260, 340, "Горизонт активних транзакцій (xmin = 1020)\nКурсор тримає знімок відкритим!\nВерсії після 1020 не очищаються", size=9.5, pad=6, fill=RED_F, stroke=RED_S, bold=True, min_w=280)
    frags.append(b_xmin)

    # Таблиця з мертвими версіями рядків (панель без суцільної заливки, щоб не конфліктувати з внутрішніми блоками)
    frags.append(rect(430, 135, 380, 220, fill="none", stroke=GRAY_S, sw=1.2, rx=6))
    frags.append(text(620, 155, "Фізичні сторінки таблиці (Heap Pages)", size=11, bold=True, color="#1e293b"))

    b_row1, _, _ = textbox(620, 185, "Рядок A v1 (xmin=1000, xmax=1050) -> Потрібен курсору", size=9.5, pad=5, fill="#fee2e2", stroke=RED_S, min_w=350)
    b_row2, _, _ = textbox(620, 225, "Рядок A v2 (xmin=1050, xmax=0) -> Живий (нова версія)", size=9.5, pad=5, fill=GREEN_F, stroke=GREEN_S, min_w=350)
    b_row3, _, _ = textbox(620, 265, "Рядок B v1 (xmin=1000, xmax=1080) -> Видалений, заблокований", size=9.5, pad=5, fill="#fee2e2", stroke=RED_S, min_w=350)
    b_vac, _, _ = textbox(620, 305, "VACUUM / Purge: ПРОПУСКАЄ очищення через xmin", size=9.5, pad=5, fill=AMBER_F, stroke=AMBER_S, bold=True, min_w=350)
    frags.extend([b_row1, b_row2, b_row3, b_vac])

    b_warn, _, _ = textbox(420, 400, "Наслідок: Накопичення мертвих кортежів (Table Bloat), деградація B-Tree індексів, вичерпання диска.", size=10, pad=5, fill="#fff1f2", stroke="#e11d48", bold=True, min_w=760)
    frags.append(b_warn)

    render(os.path.join(IMG, "fig4-cursor-mvcc-vacuum-impact.svg"), W, H, *frags)

if __name__ == "__main__":
    fig1_cursor_streaming_vs_buffering()
    fig2_volcano_iterator_engine()
    fig3_cursor_lifecycle_and_types()
    fig4_cursor_mvcc_vacuum_impact()
    print("Усі 4 фігури успішно згенеровано.")
