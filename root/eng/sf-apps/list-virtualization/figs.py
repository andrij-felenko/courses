# -*- coding: utf-8 -*-
"""Фігури до теми «Віртуалізація довгих списків»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Анатомія віртуалізованого контейнера: Viewport та Overscan ───────────
def fig_viewport_overscan():
    W, H = 1000, 620
    f = []

    # Заголовок / підписи зон ліворуч
    f.append(text(280, 40, "Повна віртуальна висота списку (H_total = 100 000 px)", size=15, bold=True))

    # Стовпчик 1: Повний фантомний простір (зовнішній скролер)
    f.append(rect(60, 70, 440, 500, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    
    # Невидима зона зверху
    f.append(rect(75, 85, 410, 110, fill="#edf2f7", stroke="#cbd5e0", sw=1, rx=4))
    f.append(text(280, 145, "Невіртуалізовані елементи зверху (не існують у DOM)", size=13, color=MUTED))

    # Верхній буфер (Overscan Top)
    f.append(rect(75, 205, 410, 65, fill="#e6f0fa", stroke=NEG, sw=1.5, rx=4))
    f.append(text(280, 242, "Верхній буфер (overscan): рендериться про запас", size=13, color=NEG, bold=True))

    # Видиме вікно (Viewport)
    f.append(rect(70, 275, 420, 150, fill="#ffffff", stroke=FIELD, sw=2.5, rx=6))
    f.append(text(280, 310, "ВИДИМЕ ВІКНО (VIEWPORT)", size=14, color=FIELD, bold=True))
    f.append(text(280, 335, "Рендериться у DOM (10–20 вузлів)", size=12, color=INK))
    f.append(text(280, 360, "Користувач бачить лише цю область", size=12, color=MUTED))
    f.append(text(280, 385, "Зсув: transform: translateY(scrollTop)", size=12, color=INK, italic=True))

    # Нижній буфер (Overscan Bottom)
    f.append(rect(75, 430, 410, 65, fill="#e6f0fa", stroke=NEG, sw=1.5, rx=4))
    f.append(text(280, 467, "Нижній буфер (overscan): готові до появи вузли", size=13, color=NEG, bold=True))

    # Невидима зона знизу
    f.append(rect(75, 505, 410, 50, fill="#edf2f7", stroke="#cbd5e0", sw=1, rx=4))
    f.append(text(280, 535, "Невіртуалізовані елементи знизу (не існують у DOM)", size=12, color=MUTED))

    # Смуга прокрутки праворуч від контейнера
    f.append(rect(508, 70, 16, 500, fill="#f1f5f9", stroke="#cbd5e0", sw=1, rx=4))
    f.append(rect(510, 220, 12, 120, fill="#94a3b8", stroke="#64748b", sw=1, rx=3))

    # Права частина: деталізація DOM-структури та розрахунку
    f.append(fitbox(560, 85, 390, 110, 
                    "Фантомний розпірник (Phantom Spacer):\n"
                    "• Висота: H_total = ∑ h_i\n"
                    "• Створює природний повзунок скролбару\n"
                    "• Не містить дочірніх DOM-вузлів", size=13))

    f.append(fitbox(560, 215, 390, 165,
                    "Змонтоване вікно (Mounted Window):\n"
                    "• Кількість вузлів = N_vis + 2 · N_overscan\n"
                    "• Фіксована кількість (~20–40 замість 100 000)\n"
                    "• Позиція через transform: translateY(offset_start)\n"
                    "• Поточна позиція скролу: scrollTop", size=13, stroke=FIELD, fill="#f0fdf4"))

    f.append(fitbox(560, 400, 390, 155,
                    "Чому потрібен буфер (Overscan):\n"
                    "• Швидке гортання пальцем (інерційний скрол)\n"
                    "• Рендеринг за межами екрана випереджає око\n"
                    "• Запобігає білим спалахам порожнечі\n"
                    "• Оптимальний розмір: 3–5 елементів", size=13, stroke=NEG, fill="#eff6ff"))

    # Стрілки-покажчики
    f.append(arrow(550, 140, 526, 140))
    f.append(arrow(550, 300, 492, 300))
    f.append(arrow(550, 460, 490, 460))

    render(os.path.join(OUT, 'viewport-overscan.svg'), W, H, *f)


# ── 2. Префіксні суми та бінарний пошук для динамічних висот ─────────────────
def fig_prefix_sums_binary_search():
    W, H = 1000, 580
    f = []

    f.append(text(500, 35, "Відображення зміщення скролу на індекс елемента через префіксні суми", size=15, bold=True))

    # Ряд 1: Елементи різної висоти
    f.append(text(120, 75, "Масив висот h[i]:", size=13, bold=True, anchor="start"))
    heights = [40, 60, 30, 90, 50, 70, 40]
    offsets = [0, 40, 100, 130, 220, 270, 340, 380]
    
    x_start = 120
    for i, h in enumerate(heights):
        w = 100
        f.append(rect(x_start + i * 110, 90, w, 50, fill="#f1f5f9", stroke=MUTED, sw=1.5, rx=4))
        f.append(text(x_start + i * 110 + w/2, 110, f"Item {i}", size=12, bold=True))
        f.append(text(x_start + i * 110 + w/2, 130, f"h = {h} px", size=12, color=MUTED))

    # Ряд 2: Масив префіксних сум зміщень
    f.append(text(120, 185, "Префіксні суми offset[i] = ∑ h[k] (монотонно зростає):", size=13, bold=True, anchor="start"))
    for i, off in enumerate(offsets[:-1]):
        w = 100
        f.append(rect(x_start + i * 110, 200, w, 50, fill="#e6f0fa", stroke=NEG, sw=1.5, rx=4))
        f.append(text(x_start + i * 110 + w/2, 220, f"offset[{i}]", size=12, color=NEG, bold=True))
        f.append(text(x_start + i * 110 + w/2, 240, f"{off} px", size=12, color=INK))

    # Стрілка двійкового пошуку
    f.append(rect(120, 285, 760, 90, fill="#fefce8", stroke="#ca8a04", sw=1.5, rx=6))
    f.append(text(500, 312, "ДВІЙКОВИЙ ПОШУК (Binary Search): O(log N)", size=14, color="#854d0e", bold=True))
    f.append(text(500, 335, "Запит: знайти перший елемент, у якого offset[i + 1] > scrollTop", size=13, color=INK))
    f.append(text(500, 357, "Приклад: scrollTop = 150 px  →  знайдено Item 3 (діапазон [130, 220) px)", size=13, color=FIELD, bold=True))

    # Результат пошуку: активний елемент
    f.append(arrow(500, 375, 495, 420))
    f.append(rect(340, 425, 320, 110, fill="#ecfdf5", stroke=FIELD, sw=2, rx=6))
    f.append(text(500, 455, "Результат пошуку діапазону:", size=13, color=FIELD, bold=True))
    f.append(text(500, 480, "start_index = 3 (offset = 130 px)", size=13, color=INK))
    f.append(text(500, 505, "end_index = binary_search(scrollTop + H_view)", size=13, color=INK))
    f.append(text(500, 525, "Зсув для CSS translateY = offset[start_index]", size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, 'prefix-sums-binary-search.svg'), W, H, *f)


# ── 3. Перевикористання DOM-вузлів (ViewHolder Recycling) ───────────────────
def fig_viewholder_recycling():
    W, H = 1020, 600
    f = []

    f.append(text(510, 35, "Життєвий цикл перевикористання DOM-вузлів (Recycling / ViewHolder)", size=15, bold=True))

    # Ліва колонка: Список що скролиться вниз
    f.append(rect(50, 70, 360, 490, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    f.append(text(230, 100, "Віртуальне вікно списку", size=14, bold=True))

    # Елемент 0 виходить вгору
    f.append(rect(70, 120, 320, 60, fill="#fdecea", stroke=POS, sw=2, rx=4))
    f.append(text(230, 145, "Вузол A: Item 0 (Виходить за буфер)", size=13, color=POS, bold=True))
    f.append(text(230, 168, "Старий контент: «Запис #0»", size=12, color=MUTED))

    # Видимі елементи 1, 2, 3
    f.append(rect(70, 195, 320, 60, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(230, 220, "Вузол B: Item 1 (Видимий)", size=13, color=FIELD, bold=True))
    f.append(text(230, 242, "Контент: «Запис #1»", size=12, color=INK))

    f.append(rect(70, 265, 320, 60, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(230, 290, "Вузол C: Item 2 (Видимий)", size=13, color=FIELD, bold=True))
    f.append(text(230, 312, "Контент: «Запис #2»", size=12, color=INK))

    f.append(rect(70, 335, 320, 60, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(230, 360, "Вузол D: Item 3 (Видимий)", size=13, color=FIELD, bold=True))
    f.append(text(230, 382, "Контент: «Запис #3»", size=12, color=INK))

    # Нове місце знизу для появи Item 4
    f.append(rect(70, 410, 320, 60, fill="#e6f0fa", stroke=NEG, sw=2, rx=4))
    f.append(text(230, 435, "Нова позиція для Item 4", size=13, color=NEG, bold=True))
    f.append(text(230, 458, "Потрібен DOM-вузол знизу!", size=12, color=MUTED))

    # Стрілка скролу вниз
    f.append(arrow(30, 250, 30, 380, color=LINE, sw=2.5))
    f.append(text(25, 235, "Скрол", size=12, bold=True, anchor="start"))
    f.append(text(25, 400, "вниз", size=12, bold=True, anchor="start"))

    # Центральна частина: Пул переробки (Recycler Pool)
    f.append(rect(460, 160, 180, 260, fill="#fffbeb", stroke="#d97706", sw=2, rx=8))
    f.append(text(550, 195, "ПУЛ ВУЗЛІВ", size=14, color="#b45309", bold=True))
    f.append(text(550, 215, "(Recycler Pool)", size=12, color="#b45309"))

    f.append(rect(480, 240, 140, 60, fill="#ffffff", stroke="#d97706", sw=1.5, rx=4))
    f.append(text(550, 265, "Вільний вузол A", size=12, bold=True))
    f.append(text(550, 285, "(не знищується)", size=11, color=MUTED))

    f.append(rect(480, 320, 140, 60, fill="#ffffff", stroke="#d97706", sw=1.5, rx=4))
    f.append(text(550, 345, "Вільний вузол E", size=12, bold=True))
    f.append(text(550, 365, "в очікуванні", size=11, color=MUTED))

    # Стрілки руху вузла
    f.append(arrow(390, 150, 460, 240, color=POS, sw=2))
    f.append(text(435, 175, "1. Відкріплення", size=11, color=POS, bold=True))

    f.append(arrow(550, 420, 550, 470, color=NEG, sw=2))
    f.append(arrow(550, 470, 390, 450, color=NEG, sw=2))
    f.append(text(490, 500, "2. Переміщення вниз + підстановка даних", size=11, color=NEG, bold=True))

    # Права колонка: Переваги відмови від GC та Reflow
    f.append(fitbox(680, 90, 300, 130,
                    "Чому не create/destroy:\n"
                    "• Створення DOM-вузла коштує ~10–50 мкс\n"
                    "• Знищення породжує сміття в пам'яті\n"
                    "• Збирач сміття (GC) викликає мікрофризи\n"
                    "• Перевикористання тримає пул сталим", size=13))

    f.append(fitbox(680, 240, 300, 150,
                    "Фаза прив'язки (onBind / Patch):\n"
                    "1. Зміна тексту та атрибутів вузла\n"
                    "2. Оновлення CSS transform (зміщення)\n"
                    "3. Повна відсутність видалення з DOM\n"
                    "4. Вузол миттєво готовий до показу", size=13, stroke=FIELD, fill="#f0fdf4"))

    f.append(fitbox(680, 410, 300, 150,
                    "Пастка втрати стану:\n"
                    "• Внутрішній стан форми (input focus)\n"
                    "• Незавершені CSS-анімації\n"
                    "• Фокус клавіатури злітає при ресайклінгу\n"
                    "• Потрібне скидання або явне збереження", size=13, stroke=POS, fill="#fdecea"))

    render(os.path.join(OUT, 'viewholder-recycling.svg'), W, H, *f)


# ── 4. Стрибки скролу та механізм якірної фіксації (Scroll Anchoring) ───────
def fig_scroll_anchoring_correction():
    W, H = 1020, 600
    f = []

    f.append(text(510, 35, "Запобігання стрибкам прокрутки при зміні розміру елементів над вікном", size=15, bold=True))

    # Ліва колонка: Проблема (без Scroll Anchoring)
    f.append(rect(50, 70, 430, 490, fill="#fef2f2", stroke=POS, sw=1.5, rx=8))
    f.append(text(265, 100, "БЕЗ ЯКІРНОЇ ФІКСАЦІЇ (Стрибок)", size=14, color=POS, bold=True))

    f.append(rect(80, 125, 370, 50, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    f.append(text(265, 155, "Item 0 (над екраном): було h = 50 px", size=12, color=MUTED))

    # Зміна висоти над екраном
    f.append(rect(80, 185, 370, 90, fill="#fee2e2", stroke=POS, sw=2, rx=4))
    f.append(text(265, 215, "Item 0 заміряно: h = 150 px (+100 px)", size=13, color=POS, bold=True))
    f.append(text(265, 240, "Завантажилась картинка / розкрився текст", size=12, color=MUTED))
    f.append(text(265, 260, "Зсув усіх наступних елементів зріс на +100 px!", size=12, color=POS))

    # Видиме вікно до і після
    f.append(rect(80, 290, 370, 120, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=4))
    f.append(text(265, 320, "scrollTop залишається старим (наприклад 300 px)", size=12, color=MUTED))
    f.append(text(265, 350, "Вміст вікна різко зсунувся вниз на 100 px", size=13, color=POS, bold=True))
    f.append(text(265, 380, "Користувач втратив місце читання! (Стрибок)", size=12, color=POS, italic=True))

    f.append(fitbox(80, 430, 370, 110,
                    "Наслідок:\n"
                    "• Текст тікає з-під очей читача\n"
                    "• Клік потрапляє по іншій кнопці\n"
                    "• Неможливо читати при підвантаженні контенту", size=12, stroke=POS, fill="#ffffff"))

    # Права колонка: Рішення (Scroll Anchoring)
    f.append(rect(540, 70, 430, 490, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(755, 100, "ЗІ SCROLL ANCHORING (Стабільність)", size=14, color=FIELD, bold=True))

    f.append(rect(570, 125, 370, 60, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(755, 150, "1. Фіксація якоря перед рендером:", size=13, color=FIELD, bold=True))
    f.append(text(755, 170, "Якір = перший видимий елемент (Item 2)", size=12, color=INK))

    f.append(rect(570, 195, 370, 80, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    f.append(text(755, 220, "2. Замір нових висот (ResizeObserver):", size=13, color=INK, bold=True))
    f.append(text(755, 245, "Item 0 виріс: Δh = +100 px", size=12, color=POS))
    f.append(text(755, 265, "Нове зміщення якоря = old_offset + 100 px", size=12, color=INK))

    f.append(rect(570, 285, 370, 125, fill="#ecfdf5", stroke=FIELD, sw=2, rx=4))
    f.append(text(755, 315, "3. Миттєва компенсація прокрутки:", size=13, color=FIELD, bold=True))
    f.append(text(755, 340, "scrollTop_new = scrollTop_old + Δh", size=13, color=FIELD, bold=True))
    f.append(text(755, 365, "300 px + 100 px = 400 px", size=13, color=INK))
    f.append(text(755, 390, "Виконується синхронно до показу кадру", size=12, color=MUTED, italic=True))

    f.append(fitbox(570, 430, 370, 110,
                    "Результат компенсації:\n"
                    "• Відносне положення якоря у вікні не змінилося\n"
                    "• Око користувача не помічає перебудови зверху\n"
                    "• Ідеально стабільний скрол у чатах і стрічках", size=12, stroke=FIELD, fill="#ffffff"))

    render(os.path.join(OUT, 'scroll-anchoring-correction.svg'), W, H, *f)


# ── 5. Структури даних: Масив префіксів vs Дерево Фенвіка ───────────────────
def fig_fenwick_vs_prefix():
    W, H = 1000, 560
    f = []

    f.append(text(500, 35, "Порівняння структур для підтримки динамічних висот елементів", size=15, bold=True))

    # Ліва половина: Звичайний масив префіксних сум
    f.append(rect(50, 70, 430, 460, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    f.append(text(265, 100, "ПЛОСКИЙ МАСИВ ПРЕФІКСІВ", size=14, bold=True))

    f.append(fitbox(75, 120, 380, 80,
                    "Запит зміщення (Offset Query):\n"
                    "• offset[i] читається за O(1)\n"
                    "• Двійковий пошук діапазону: O(log N)", size=13, stroke=FIELD, fill="#ecfdf5"))

    f.append(fitbox(75, 215, 380, 140,
                    "Оновлення висоти (Height Update):\n"
                    "• Зміна h[k] на Δh вимагає зсуву ВСІХ наступних сум:\n"
                    "  for i = k+1 to N-1: offset[i] += Δh\n"
                    "• Складність оновлення: O(N)\n"
                    "• Для N = 100 000 це 100 000 операцій запису!", size=13, stroke=POS, fill="#fdecea"))

    f.append(rect(75, 375, 380, 130, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    f.append(text(265, 405, "Каскадне оновлення (Ripple Effect):", size=12, bold=True))
    f.append(rect(95, 430, 60, 40, fill="#fecaca", stroke=POS, sw=1, rx=3))
    f.append(text(125, 455, "h[k]", size=12, color=POS, bold=True))
    f.append(arrow(160, 450, 185, 450, color=POS, sw=1.5))
    f.append(rect(190, 430, 70, 40, fill="#fee2e2", stroke=POS, sw=1, rx=3))
    f.append(text(225, 455, "+Δ", size=12, color=POS))
    f.append(arrow(265, 450, 290, 450, color=POS, sw=1.5))
    f.append(rect(295, 430, 70, 40, fill="#fee2e2", stroke=POS, sw=1, rx=3))
    f.append(text(330, 455, "+Δ", size=12, color=POS))
    f.append(arrow(370, 450, 395, 450, color=POS, sw=1.5))
    f.append(text(420, 455, "… O(N)", size=12, color=POS, bold=True))

    # Права половина: Дерево Фенвіка (Binary Indexed Tree)
    f.append(rect(520, 70, 430, 460, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    f.append(text(735, 100, "ДЕРЕВО ФЕНВІКА (FENWICK TREE)", size=14, color=NEG, bold=True))

    f.append(fitbox(545, 120, 380, 80,
                    "Запит префіксної суми (Prefix Query):\n"
                    "• Спуск по бітовому розкладу (i -= i & -i)\n"
                    "• Складність запиту: O(log N)", size=13, stroke=NEG, fill="#eff6ff"))

    f.append(fitbox(545, 215, 380, 140,
                    "Оновлення висоти (Height Update):\n"
                    "• Оновлюються лише предки у дереві (i += i & -i)\n"
                    "• Складність оновлення: O(log N)\n"
                    "• Для N = 100 000 це щонайбільше ~17 операцій!\n"
                    "• Пам'ять: рівно N чисел (O(N) без вказівників)", size=13, stroke=FIELD, fill="#ecfdf5"))

    f.append(rect(545, 375, 380, 130, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    f.append(text(735, 405, "Двійкове розповсюдження оновлення:", size=12, bold=True))
    f.append(rect(565, 430, 60, 40, fill="#dbeafe", stroke=NEG, sw=1, rx=3))
    f.append(text(595, 455, "Node", size=12, color=NEG, bold=True))
    f.append(arrow(630, 450, 665, 450, color=NEG, sw=1.5))
    f.append(rect(670, 430, 70, 40, fill="#eff6ff", stroke=NEG, sw=1, rx=3))
    f.append(text(705, 455, "+LSB", size=12, color=NEG))
    f.append(arrow(745, 450, 780, 450, color=NEG, sw=1.5))
    f.append(rect(785, 430, 70, 40, fill="#eff6ff", stroke=NEG, sw=1, rx=3))
    f.append(text(820, 455, "+LSB", size=12, color=NEG))
    f.append(text(885, 455, "≤ 17 кроків", size=12, color=FIELD, bold=True))

    render(os.path.join(OUT, 'fenwick-vs-prefix.svg'), W, H, *f)


def main():
    fig_viewport_overscan()
    fig_prefix_sums_binary_search()
    fig_viewholder_recycling()
    fig_scroll_anchoring_correction()
    fig_fenwick_vs_prefix()
    print("Figures generated successfully in", OUT)


if __name__ == '__main__':
    main()
