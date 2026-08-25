# -*- coding: utf-8 -*-
import sys, os

# 4 levels up to scripts/ from book/programming/languages/constructors-destructors
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. object-lifecycle-timeline: Життєвий цикл об'єкта ───────────────────────
def fig_object_lifecycle():
    W, H = 820, 360
    p = []
    
    p.append(text(W / 2, 26, "Життєвий цикл об'єкта: розділення виділення пам'яті та ініціалізації", size=15, bold=True))
    
    # 5 етапів вздовж часової осі
    steps = [
        ("1. Сира пам'ять", "malloc / стек / static\nВиділено n байтів\n(значення невизначені)", "#f4f6f8", LINE),
        ("2. Конструктор", "1. Базові класи\n2. Поля (за порядком)\n3. Тіло конструктора", "#eaf2fd", NEG),
        ("3. Живий об'єкт", "Інваріант встановлено\nОб'єкт валідний\nВиклики методів", "#eafaf1", FIELD),
        ("4. Деструктор", "1. Тіло деструктора\n2. Поля (LIFO порядок)\n3. Базові класи", "#fef9e7", "#d4ac0d"),
        ("5. Звільнення", "free / зсув rsp\nПам'ять повернуто\nсистемі", "#fdecea", POS)
    ]
    
    bw = 140
    bh = 110
    gap = 20
    x_start = 20
    y_box = 70
    
    for i, (title, desc, fill, stroke) in enumerate(steps):
        bx = x_start + i * (bw + gap)
        p.append(rect(bx, y_box, bw, bh, fill=fill, stroke=stroke, sw=1.5, rx=6))
        p.append(text(bx + bw / 2, y_box + 22, title, size=12, bold=True, color=stroke if stroke != LINE else INK))
        p.append(line(bx + 10, y_box + 30, bx + bw - 10, y_box + 30, color=stroke, sw=1, dash="2,2"))
        
        lines = desc.split("\n")
        for li, ln in enumerate(lines):
            p.append(text(bx + bw / 2, y_box + 48 + li * 17, ln, size=10, color=INK))
            
        if i < len(steps) - 1:
            arr_x1 = bx + bw + 2
            arr_x2 = bx + bw + gap - 2
            arr_y = y_box + bh / 2
            p.append(arrow(arr_x1, arr_y, arr_x2, arr_y, color=LINE, sw=1.6))
            
    # Нижня частина: порівняння фаз (народження vs життя vs смерть)
    y_bot = 220
    h_bot = 95
    
    # Фаза створення
    w_birth = (bw * 2) + gap
    p.append(rect(x_start, y_bot, w_birth, h_bot, fill="#f8fafc", stroke=NEG, sw=1.2, rx=6))
    p.append(text(x_start + w_birth / 2, y_bot + 22, "ФАЗА СТВОРЕННЯ (Народження)", size=12, bold=True, color=NEG))
    p.append(text(x_start + w_birth / 2, y_bot + 45, "1. Отримання сирої адреси (void*)", size=11, color=INK))
    p.append(text(x_start + w_birth / 2, y_bot + 65, "2. Ініціалізація полів і vptr (placement new)", size=11, color=INK))
    p.append(text(x_start + w_birth / 2, y_bot + 83, "Виняток тут → деструктор не викликається", size=10, italic=True, color=POS))
    
    # Фаза використання
    w_live = bw
    x_live = x_start + w_birth + gap
    p.append(rect(x_live, y_bot, w_live, h_bot, fill="#f4faf6", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(x_live + w_live / 2, y_bot + 22, "ЧАС ЖИТТЯ", size=12, bold=True, color=FIELD))
    p.append(text(x_live + w_live / 2, y_bot + 52, "Гарантія інваріанта:", size=11, color=INK))
    p.append(text(x_live + w_live / 2, y_bot + 72, "усі поля ініціалізовані", size=10, color=INK))
    
    # Фаза знищення
    w_death = (bw * 2) + gap
    x_death = x_live + w_live + gap
    p.append(rect(x_death, y_bot, w_death, h_bot, fill="#fff5f5", stroke=POS, sw=1.2, rx=6))
    p.append(text(x_death + w_death / 2, y_bot + 22, "ФАЗА ЗНИЩЕННЯ (Смерть)", size=12, bold=True, color=POS))
    p.append(text(x_death + w_death / 2, y_bot + 45, "1. Звільнення ресурсів (виклик ~T())", size=11, color=INK))
    p.append(text(x_death + w_death / 2, y_bot + 65, "2. Повернення адреси алокатору / ядру", size=11, color=INK))
    p.append(text(x_death + w_death / 2, y_bot + 83, "Деструктор ніколи не кидає винятків", size=10, italic=True, color=POS))
    
    # Стрілки від верхніх блоків до фаз
    p.append(line(x_start + bw, y_box + bh, x_start + w_birth / 2, y_bot, color=NEG, sw=1, dash="3,3"))
    p.append(line(x_death + bw, y_box + bh, x_death + w_death / 2, y_bot, color=POS, sw=1, dash="3,3"))
    
    render(os.path.join(OUT, "object-lifecycle-timeline.svg"), W, H, *p)


# ── 2. virtual-destructor-call: Віртуальний деструктор ───────────────────────
def fig_virtual_destructor():
    W, H = 820, 390
    p = []
    
    p.append(text(W / 2, 26, "Видалення через покажчик на базовий клас: Base* p = new Derived();", size=15, bold=True))
    
    colw = 370
    x_left = 25
    x_right = x_left + colw + 30
    ytop = 55
    boxh = 310
    
    # Ліва колонка: БЕЗ virtual деструктора (Помилка / UB)
    p.append(rect(x_left, ytop, colw, boxh, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    p.append(text(x_left + colw / 2, ytop + 24, "ДЕСТРУКТОР НЕ ВІРТУАЛЬНИЙ (~Base())", size=13, bold=True, color=POS))
    
    b1, _, _ = textbox(x_left + colw / 2, ytop + 65, "Виклик delete p; (статичне зв'язування)", size=11, pad=6, fill=BG, stroke=MUTED)
    p.append(b1)
    
    p.append(arrow(x_left + colw / 2, ytop + 83, x_left + colw / 2, ytop + 115, color=POS))
    
    b2, _, _ = textbox(x_left + colw / 2, ytop + 135, "1. Викликається ЛИШЕ ~Base()\nКомпілятор дивиться лише на тип Base*", size=11, pad=6, fill="#fee2e2", stroke=POS)
    p.append(b2)
    
    p.append(arrow(x_left + colw / 2, ytop + 160, x_left + colw / 2, ytop + 195, color=POS))
    
    b3, _, _ = textbox(x_left + colw / 2, ytop + 215, "2. ~Derived() ПРОПУЩЕНО!\nБуфери, сокети й поля Derived НЕ очищено", size=11, pad=6, fill="#fee2e2", stroke=POS, bold=True, color=POS)
    p.append(b3)
    
    p.append(arrow(x_left + colw / 2, ytop + 240, x_left + colw / 2, ytop + 270, color=POS))
    
    b4, _, _ = textbox(x_left + colw / 2, ytop + 288, "Результат: Невизначена поведінка (UB) + витік", size=11, pad=6, fill="#fdecea", stroke=POS, bold=True, color=POS)
    p.append(b4)
    
    # Права колонка: З virtual деструктором (Правильно)
    p.append(rect(x_right, ytop, colw, boxh, fill="#f4faf6", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(x_right + colw / 2, ytop + 24, "ВІРТУАЛЬНИЙ ДЕСТРУКТОР (virtual ~Base())", size=13, bold=True, color=FIELD))
    
    b_r1, _, _ = textbox(x_right + colw / 2, ytop + 65, "Виклик delete p; (динамічне зв'язування)", size=11, pad=6, fill=BG, stroke=MUTED)
    p.append(b_r1)
    
    p.append(arrow(x_right + colw / 2, ytop + 83, x_right + colw / 2, ytop + 115, color=FIELD))
    
    b_r2, _, _ = textbox(x_right + colw / 2, ytop + 135, "1. Пошук адреси через vtable\nВиклик реального деструктора ~Derived()", size=11, pad=6, fill="#e8f8f0", stroke=FIELD)
    p.append(b_r2)
    
    p.append(arrow(x_right + colw / 2, ytop + 160, x_right + colw / 2, ytop + 195, color=FIELD))
    
    b_r3, _, _ = textbox(x_right + colw / 2, ytop + 215, "2. ~Derived() звільняє свої ресурси,\nа потім автоматично викликає ~Base()", size=11, pad=6, fill="#e8f8f0", stroke=FIELD)
    p.append(b_r3)
    
    p.append(arrow(x_right + colw / 2, ytop + 240, x_right + colw / 2, ytop + 270, color=FIELD))
    
    b_r4, _, _ = textbox(x_right + colw / 2, ytop + 288, "Результат: 100% коректне повне очищення", size=11, pad=6, fill="#d1fae5", stroke=FIELD, bold=True, color=FIELD)
    p.append(b_r4)
    
    render(os.path.join(OUT, "virtual-destructor-call.svg"), W, H, *p)


# ── 3. construction-unwinding-failure: Виняток у конструкторі ─────────────────
def fig_construction_unwinding():
    W, H = 820, 390
    p = []
    
    p.append(text(W / 2, 26, "Виняток у конструкторі: часткова ініціалізація та розгортання", size=15, bold=True))
    
    # Послідовність ініціалізації полів
    # Поле 1: успіх -> Поле 2: успіх -> Поле 3: аварія (throw)
    fw = 230
    fh = 160
    gap = 25
    x0 = 35
    y0 = 60
    
    # Поле 1
    p.append(rect(x0, y0, fw, fh, fill="#f4faf6", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(x0 + fw / 2, y0 + 24, "1. Поле: std::string name", size=12, bold=True, color=FIELD))
    p.append(text(x0 + fw / 2, y0 + 50, "Конструктор успішний", size=11, color=INK))
    p.append(text(x0 + fw / 2, y0 + 72, "Виділено буфер у купі", size=11, color=MUTED))
    p.append(rect(x0 + 15, y0 + 95, fw - 30, 45, fill="#d1fae5", stroke=FIELD, sw=1, rx=4))
    p.append(text(x0 + fw / 2, y0 + 115, "СТАН: Ініціалізовано", size=11, bold=True, color=FIELD))
    p.append(text(x0 + fw / 2, y0 + 132, "Підлягає деструкції", size=10, color=FIELD))
    
    # Стрілка 1->2
    p.append(arrow(x0 + fw + 2, y0 + fh / 2, x0 + fw + gap - 2, y0 + fh / 2, color=LINE, sw=1.6))
    
    # Поле 2
    x1 = x0 + fw + gap
    p.append(rect(x1, y0, fw, fh, fill="#f4faf6", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(x1 + fw / 2, y0 + 24, "2. Поле: std::vector buf", size=12, bold=True, color=FIELD))
    p.append(text(x1 + fw / 2, y0 + 50, "Конструктор успішний", size=11, color=INK))
    p.append(text(x1 + fw / 2, y0 + 72, "Виділено масив у купі", size=11, color=MUTED))
    p.append(rect(x1 + 15, y0 + 95, fw - 30, 45, fill="#d1fae5", stroke=FIELD, sw=1, rx=4))
    p.append(text(x1 + fw / 2, y0 + 115, "СТАН: Ініціалізовано", size=11, bold=True, color=FIELD))
    p.append(text(x1 + fw / 2, y0 + 132, "Підлягає деструкції", size=10, color=FIELD))
    
    # Стрілка 2->3
    p.append(arrow(x1 + fw + 2, y0 + fh / 2, x1 + fw + gap - 2, y0 + fh / 2, color=LINE, sw=1.6))
    
    # Поле 3
    x2 = x1 + fw + gap
    p.append(rect(x2, y0, fw, fh, fill="#fff5f5", stroke=POS, sw=1.5, rx=6))
    p.append(text(x2 + fw / 2, y0 + 24, "3. Поле: Socket connection", size=12, bold=True, color=POS))
    p.append(text(x2 + fw / 2, y0 + 50, "throw std::runtime_error;", size=11, bold=True, color=POS))
    p.append(text(x2 + fw / 2, y0 + 72, "Мережевий збій підключення", size=11, color=MUTED))
    p.append(rect(x2 + 15, y0 + 95, fw - 30, 45, fill="#fee2e2", stroke=POS, sw=1, rx=4))
    p.append(text(x2 + fw / 2, y0 + 115, "СТАН: НЕ створено", size=11, bold=True, color=POS))
    p.append(text(x2 + fw / 2, y0 + 132, "Об'єкт класу не народився!", size=10, color=POS))
    
    # Нижній блок: Автоматичне розгортання та виклики деструкторів
    y_bot = 245
    h_bot = 120
    p.append(rect(x0, y_bot, W - 70, h_bot, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    
    p.append(text(W / 2, y_bot + 24, "РЕАКЦІЯ РАНТАЙМУ: РОЗГОРТАННЯ СТЕКА (Stack Unwinding)", size=13, bold=True, color=INK))
    
    p.append(text(x0 + 25, y_bot + 52, "• Деструктор САМОГО КЛАСУ ~MyClass() НЕ викликається (об'єкт офіційно не народився).", size=11, color=POS, anchor="start", bold=True))
    p.append(text(x0 + 25, y_bot + 74, "• Компілятор автоматично викликає деструктори вже ініціалізованих полів у зворотному порядку:", size=11, color=INK, anchor="start"))
    p.append(text(x0 + 45, y_bot + 94, "1. ~vector() знищує буфер  →  2. ~string() звільняє пам'ять  →  пам'ять сирого об'єкта повертається.", size=11, color=FIELD, anchor="start", bold=True))
    
    render(os.path.join(OUT, "construction-unwinding-failure.svg"), W, H, *p)


if __name__ == "__main__":
    fig_object_lifecycle()
    fig_virtual_destructor()
    fig_construction_unwinding()
    print("Figures generated successfully.")
