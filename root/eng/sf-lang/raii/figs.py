# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. raii-lifecycle: ручне керування проти RAII ────────────────────────────
def fig_raii_lifecycle():
    W, H = 760, 420
    p = []
    
    p.append(text(W / 2, 28, "Керування ресурсами: ручне очищення проти RAII", size=16, bold=True))
    
    colw = 340
    gap = 30
    x_left = 25
    x_right = x_left + colw + gap
    ytop = 55
    boxh = 345
    
    # Ліва колонка: Ручне керування
    p.append(rect(x_left, ytop, colw, boxh, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    p.append(text(x_left + colw / 2, ytop + 24, "Ручне керування (C / явне звільнення)", size=13, bold=True, color=POS))
    
    b1, _, _ = textbox(x_left + colw / 2, ytop + 65, "1. Захоплення: fd = open(...)", size=12, pad=6, fill=BG, stroke=MUTED)
    p.append(b1)
    
    p.append(arrow(x_left + colw / 2, ytop + 82, x_left + colw / 2, ytop + 110, color=MUTED))
    
    b2, _, _ = textbox(x_left + colw / 2, ytop + 130, "Виконання логіки / розгалуження", size=12, pad=6, fill=BG, stroke=MUTED)
    p.append(b2)
    
    # 3 гілки виходу
    # Гілка 1: Нормальний вихід
    p.append(arrow(x_left + 80, ytop + 150, x_left + 60, ytop + 195, color=MUTED))
    b_ok, _, _ = textbox(x_left + 60, ytop + 215, "Нормальний return\nclose(fd);", size=11, pad=5, fill="#eafaf1", stroke=FIELD)
    p.append(b_ok)
    p.append(text(x_left + 60, ytop + 252, "✓ Звільнено", size=11, bold=True, color=FIELD))
    
    # Гілка 2: Помилка / ранній return
    p.append(arrow(x_left + colw / 2, ytop + 150, x_left + colw / 2, ytop + 195, color=POS))
    b_err, _, _ = textbox(x_left + colw / 2, ytop + 215, "if (err) return -1;\n(забули close)", size=11, pad=5, fill="#fde8e8", stroke=POS)
    p.append(b_err)
    p.append(text(x_left + colw / 2, ytop + 252, "✗ ВИТІК РЕСУРСУ", size=11, bold=True, color=POS))
    
    # Гілка 3: Виняток
    p.append(arrow(x_left + colw - 80, ytop + 150, x_left + colw - 60, ytop + 195, color=POS))
    b_exc, _, _ = textbox(x_left + colw - 60, ytop + 215, "Виняток / abort\n(пропуск коду)", size=11, pad=5, fill="#fde8e8", stroke=POS)
    p.append(b_exc)
    p.append(text(x_left + colw - 60, ytop + 252, "✗ ВИТІК РЕСУРСУ", size=11, bold=True, color=POS))
    
    b_bad_tag, _, _ = textbox(x_left + colw / 2, ytop + 310, "Потрібен ручний догляд за кожним виходом", size=11, pad=6, fill="#fee2e2", stroke=POS, bold=True, color=POS)
    p.append(b_bad_tag)
    
    # Права колонка: RAII
    p.append(rect(x_right, ytop, colw, boxh, fill="#f4faf6", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(x_right + colw / 2, ytop + 24, "RAII (прив'язка до області видимості)", size=13, bold=True, color=FIELD))
    
    b_r1, _, _ = textbox(x_right + colw / 2, ytop + 65, "Конструктор: File f(\"data.txt\")", size=12, pad=6, fill=BG, stroke=FIELD)
    p.append(b_r1)
    
    p.append(arrow(x_right + colw / 2, ytop + 82, x_right + colw / 2, ytop + 110, color=FIELD))
    
    b_r2, _, _ = textbox(x_right + colw / 2, ytop + 130, "Область видимості { ... }\nІнваріант: ресурс завжди валідний", size=12, pad=6, fill=BG, stroke=MUTED)
    p.append(b_r2)
    
    p.append(arrow(x_right + colw / 2, ytop + 158, x_right + colw / 2, ytop + 195, color=FIELD))
    
    b_r3, _, _ = textbox(x_right + colw / 2, ytop + 215, "Будь-який вихід зі scope:\n• return  • break  • exception", size=11, pad=6, fill=BG, stroke=FIELD)
    p.append(b_r3)
    
    p.append(arrow(x_right + colw / 2, ytop + 242, x_right + colw / 2, ytop + 268, color=FIELD))
    
    b_r4, _, _ = textbox(x_right + colw / 2, ytop + 288, "Деструктор ~File(): close(fd)\nвикликається АВТОМАТИЧНО", size=11, pad=6, fill="#d1fae5", stroke=FIELD, bold=True, color=FIELD)
    p.append(b_r4)
    
    b_good_tag, _, _ = textbox(x_right + colw / 2, ytop + 325, "100% гарантія звільнення без сміттяра", size=11, pad=5, fill=BG, stroke=FIELD, bold=True, color=FIELD)
    p.append(b_good_tag)
    
    render(os.path.join(OUT, "raii-lifecycle.svg"), W, H, *p)


# ── 2. unwinding-flow: розгортання стека при винятках ────────────────────────
def fig_unwinding_flow():
    W, H = 760, 430
    p = []
    
    p.append(text(W / 2, 28, "Розгортання стека (Stack Unwinding) та деструктори", size=16, bold=True))
    
    # Фрейми стека знизу вгору
    fy_main = 330
    fy_proc = 215
    fy_read = 100
    
    fw = 420
    fx = 40
    
    # Frame 1: main
    p.append(rect(fx, fy_main, fw, 75, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=6))
    p.append(text(fx + 15, fy_main + 22, "Фрейм 1: main()", size=13, bold=True, anchor="start", color=INK))
    p.append(text(fx + 15, fy_main + 44, "try { process_request(); } catch (...) { ... }", size=11, anchor="start", color=MUTED))
    p.append(text(fx + fw - 15, fy_main + 60, "Перехоплювач (catch)", size=11, bold=True, anchor="end", color=FIELD))
    
    # Frame 2: process_request
    p.append(rect(fx, fy_proc, fw, 95, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=6))
    p.append(text(fx + 15, fy_proc + 20, "Фрейм 2: process_request()", size=13, bold=True, anchor="start", color=INK))
    
    b_lock, _, _ = textbox(fx + 110, fy_proc + 55, "std::lock_guard lk(mtx)", size=11, pad=5, fill="#e0f2fe", stroke=NEG)
    p.append(b_lock)
    
    b_file, _, _ = textbox(fx + 310, fy_proc + 55, "FileDescriptor fd(\"log\")", size=11, pad=5, fill="#e0f2fe", stroke=NEG)
    p.append(b_file)
    
    p.append(text(fx + 15, fy_proc + 85, "виклик: parse_payload()", size=11, italic=True, anchor="start", color=MUTED))
    
    # Frame 3: parse_payload
    p.append(rect(fx, fy_read, fw, 95, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(fx + 15, fy_read + 20, "Фрейм 3: parse_payload()", size=13, bold=True, anchor="start", color=POS))
    
    b_buf, _, _ = textbox(fx + 130, fy_read + 55, "std::vector<char> buf", size=11, pad=5, fill="#fee2e2", stroke=POS)
    p.append(b_buf)
    
    p.append(text(fx + fw - 15, fy_read + 55, "throw std::runtime_error(\"bad packet\");", size=11, bold=True, anchor="end", color=POS))
    p.append(text(fx + 15, fy_read + 85, "Аварійний стан! Стек починає розмотуватися", size=11, italic=True, anchor="start", color=POS))
    
    # Стрілки викликів вгору
    p.append(arrow(fx + fw + 20, fy_main + 30, fx + fw + 20, fy_proc + 60, color=MUTED))
    p.append(text(fx + fw + 25, (fy_main + fy_proc) / 2 + 35, "виклик", size=10, anchor="start", color=MUTED))
    
    p.append(arrow(fx + fw + 20, fy_proc + 20, fx + fw + 20, fy_read + 60, color=MUTED))
    p.append(text(fx + fw + 25, (fy_proc + fy_read) / 2 + 35, "виклик", size=10, anchor="start", color=MUTED))
    
    # Права панель: Хвиля розгортання (Unwinding wave)
    rx = 520
    rw = 215
    p.append(rect(rx, 80, rw, 325, fill="#f0fdf4", stroke=FIELD, sw=2, rx=8))
    p.append(text(rx + rw / 2, 105, "Порядок LIFO виклику", size=12, bold=True, color=FIELD))
    p.append(text(rx + rw / 2, 122, "деструкторів при винятку", size=12, bold=True, color=FIELD))
    
    # Крок 1
    p.append(rect(rx + 15, 140, rw - 30, 48, fill=BG, stroke=FIELD, sw=1.2, rx=4))
    p.append(text(rx + rw / 2, 158, "1. ~vector()", size=12, bold=True, color=INK))
    p.append(text(rx + rw / 2, 175, "пам'ять буфера звільнено", size=10, color=MUTED))
    
    p.append(arrow(rx + rw / 2, 190, rx + rw / 2, 206, color=FIELD))
    
    # Крок 2
    p.append(rect(rx + 15, 208, rw - 30, 48, fill=BG, stroke=FIELD, sw=1.2, rx=4))
    p.append(text(rx + rw / 2, 226, "2. ~FileDescriptor()", size=12, bold=True, color=INK))
    p.append(text(rx + rw / 2, 243, "дескриптор log закрито", size=10, color=MUTED))
    
    p.append(arrow(rx + rw / 2, 258, rx + rw / 2, 274, color=FIELD))
    
    # Крок 3
    p.append(rect(rx + 15, 276, rw - 30, 48, fill=BG, stroke=FIELD, sw=1.2, rx=4))
    p.append(text(rx + rw / 2, 294, "3. ~lock_guard()", size=12, bold=True, color=INK))
    p.append(text(rx + rw / 2, 311, "м'ютекс розблоковано", size=10, color=MUTED))
    
    p.append(arrow(rx + rw / 2, 326, rx + rw / 2, 345, color=FIELD))
    
    p.append(text(rx + rw / 2, 365, "Вхід у catch блок main()", size=11, bold=True, color=FIELD))
    p.append(text(rx + rw / 2, 385, "Жодних витоків і дедлоків!", size=10, italic=True, color=INK))
    
    render(os.path.join(OUT, "unwinding-flow.svg"), W, H, *p)


# ── 3. ownership-move: переміщення та інваріант єдиного володіння ─────────────
def fig_ownership_move():
    W, H = 760, 360
    p = []
    
    p.append(text(W / 2, 28, "Ексклюзивне володіння: переміщення (Move) ресурсу", size=16, bold=True))
    
    # Стан 1: До переміщення
    y1 = 60
    p.append(rect(30, y1, 700, 125, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(45, y1 + 22, "1. Стан до переміщення: std::unique_ptr<Buffer> a = std::make_unique<Buffer>()", size=11, bold=True, anchor="start", color=INK))
    
    # Змінна a
    p.append(rect(60, y1 + 42, 160, 65, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(140, y1 + 62, "Змінна a (на стеку)", size=12, bold=True, color=NEG))
    p.append(text(140, y1 + 86, "ptr = 0x7FFF10", size=12, bold=True, color=INK))
    
    # Стрілка на купу
    p.append(arrow(220, y1 + 75, 420, y1 + 75, color=NEG, sw=2))
    p.append(text(320, y1 + 65, "володіє", size=11, color=NEG))
    
    # Блок на купі
    p.append(rect(430, y1 + 42, 270, 65, fill="#ecfdf5", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(565, y1 + 62, "Ресурс у купі (Адреса: 0x7FFF10)", size=12, bold=True, color=FIELD))
    p.append(text(565, y1 + 86, "Буфер даних [ 4096 байтів ]", size=11, color=INK))
    
    # Дія
    p.append(text(W / 2, 205, "Операція: b = std::move(a);   (передача права власності)", size=13, bold=True, color=POS))
    
    # Стан 2: Після переміщення
    y2 = 220
    p.append(rect(30, y2, 700, 125, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(45, y2 + 22, "2. Стан після переміщення: a стає порожнім (nullptr), b стає єдиним власником", size=11, bold=True, anchor="start", color=INK))
    
    # Змінна a (порожня)
    p.append(rect(60, y2 + 42, 140, 65, fill="#f1f5f9", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(130, y2 + 62, "Змінна a", size=12, color=MUTED))
    p.append(text(130, y2 + 86, "ptr = nullptr", size=12, bold=True, color=MUTED))
    
    # Змінна b
    p.append(rect(230, y2 + 42, 160, 65, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(310, y2 + 62, "Змінна b (новий власник)", size=12, bold=True, color=NEG))
    p.append(text(310, y2 + 86, "ptr = 0x7FFF10", size=12, bold=True, color=INK))
    
    # Стрілка від b на купу
    p.append(arrow(390, y2 + 75, 470, y2 + 75, color=FIELD, sw=2))
    p.append(text(430, y2 + 65, "володіє", size=11, color=FIELD))
    
    # Блок на купі
    p.append(rect(480, y2 + 42, 220, 65, fill="#ecfdf5", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(590, y2 + 62, "Ресурс у купі (0x7FFF10)", size=12, bold=True, color=FIELD))
    p.append(text(590, y2 + 86, "~b() звільнить його рівно 1 раз", size=10, italic=True, color=INK))
    
    render(os.path.join(OUT, "ownership-move.svg"), W, H, *p)


# ── 4. paradigms-comparison: порівняння парадигм очищення ─────────────────────
def fig_paradigms_comparison():
    W, H = 760, 370
    p = []
    
    p.append(text(W / 2, 28, "Порівняння підходів до очищення ресурсів", size=16, bold=True))
    
    colw = 165
    gap = 16
    x0 = 22
    ytop = 55
    boxh = 295
    
    cols = [
        ("Ручний goto", "C",
         ["goto cleanup;", "", "Повний контроль", "АЛЕ комбінаторний", "вибух помилок і", "витоки на винятках"],
         POS, "#fef2f2", "помилки"),
        ("try-finally", "Java / Python / JS",
         ["try { ... }", "finally { r.close(); }", "", "Зв'язано з блоком", "АЛЕ громіздко при", "кількох ресурсах"],
         "#d97706", "#fffbeb", "лексично"),
        ("defer", "Go / Zig",
         ["defer file.Close()", "", "Поруч із відкриттям", "АЛЕ прив'язано до", "функції, а не", "до типу/scope"],
         NEG, "#eff6ff", "відкладено"),
        ("RAII / Drop", "C++ / Rust",
         ["~Destructor()", "Drop::drop()", "", "Автоматично на виході", "Безпечно при винятках", "Нульова ціна (Zero-cost)"],
         FIELD, "#f0fdf4", "ідеально"),
    ]
    
    for i, (title, lang, lines, col, fill, tag) in enumerate(cols):
        x = x0 + i * (colw + gap)
        p.append(rect(x, ytop, colw, boxh, fill=fill, stroke=col, sw=1.8, rx=8))
        p.append(text(x + colw / 2, ytop + 26, title, size=13, bold=True, color=col))
        p.append(text(x + colw / 2, ytop + 45, lang, size=11, italic=True, color=MUTED))
        
        yy = ytop + 75
        for ln in lines:
            if ln:
                p.append(text(x + colw / 2, yy, ln, size=11, color=INK))
            yy += 20
            
        b, _, _ = textbox(x + colw / 2, ytop + boxh - 26, tag, size=11, pad=6,
                          fill=BG, stroke=col, bold=True, color=col)
        p.append(b)
        
    render(os.path.join(OUT, "paradigms-comparison.svg"), W, H, *p)


if __name__ == "__main__":
    fig_raii_lifecycle()
    fig_unwinding_flow()
    fig_ownership_move()
    fig_paradigms_comparison()
    print("All figures generated successfully.")
