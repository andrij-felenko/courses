# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. allocator-role: міст між запитами програми та сторінками ОС ──────────
def fig_allocator_role():
    W, H = 820, 360
    p = []
    
    p.append(text(W / 2, 26, "Роль алокатора: міст між гранулярними запитами програми та сторінками ОС", size=15, bold=True))
    
    colw = 230
    h_box = 270
    ytop = 50
    
    # Колонка 1: Програма
    x1 = 25
    p.append(rect(x1, ytop, colw, h_box, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(x1 + colw / 2, ytop + 26, "Програма користувача", size=14, bold=True, color=INK))
    p.append(text(x1 + colw / 2, ytop + 46, "(Дрібні довільні виділення)", size=11, color=MUTED))
    
    b_req1, _, _ = textbox(x1 + colw / 2, ytop + 90, "malloc(24) // вузол списку", size=11, pad=6, fill=BG, stroke=NEG)
    b_req2, _, _ = textbox(x1 + colw / 2, ytop + 140, "malloc(128) // рядок тексту", size=11, pad=6, fill=BG, stroke=NEG)
    b_req3, _, _ = textbox(x1 + colw / 2, ytop + 190, "free(ptr) // звільнення", size=11, pad=6, fill=BG, stroke=POS)
    b_req4, _, _ = textbox(x1 + colw / 2, ytop + 240, "Частота: 10⁶–10⁷ викликів/с", size=11, pad=5, fill="#edf2f7", stroke=MUTED, bold=True)
    p.extend([b_req1, b_req2, b_req3, b_req4])
    
    # Стрілка 1->2
    p.append(arrow(x1 + colw + 5, ytop + 115, x1 + colw + 55, ytop + 115, color=NEG, sw=2))
    p.append(text(x1 + colw + 30, ytop + 105, "запит", size=11, bold=True, color=NEG))
    
    p.append(arrow(x1 + colw + 55, ytop + 165, x1 + colw + 5, ytop + 165, color=FIELD, sw=2))
    p.append(text(x1 + colw + 30, ytop + 155, "покажчик", size=11, bold=True, color=FIELD))
    
    p.append(text(x1 + colw + 30, ytop + 205, "≈ 5–15 тактів", size=10, bold=True, color=FIELD))
    p.append(text(x1 + colw + 30, ytop + 218, "(без syscall)", size=10, color=MUTED))
    
    # Колонка 2: Алокатор
    x2 = x1 + colw + 65
    p.append(rect(x2, ytop, colw, h_box, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(x2 + colw / 2, ytop + 26, "Алокатор (User Space)", size=14, bold=True, color=FIELD))
    p.append(text(x2 + colw / 2, ytop + 46, "(ptmalloc / jemalloc / mimalloc)", size=11, color=MUTED))
    
    b_al1, _, _ = textbox(x2 + colw / 2, ytop + 90, "Локальні кеші потоків (tcache)", size=11, pad=6, fill=BG, stroke=FIELD)
    b_al2, _, _ = textbox(x2 + colw / 2, ytop + 138, "Розмірні класи та списки (Bins)", size=11, pad=6, fill=BG, stroke=FIELD)
    b_al3, _, _ = textbox(x2 + colw / 2, ytop + 186, "Розбиття й злиття (Coalescing)", size=11, pad=6, fill=BG, stroke=FIELD)
    b_al4, _, _ = textbox(x2 + colw / 2, ytop + 236, "Керування аренами пам'яті", size=11, pad=5, fill="#dcfce7", stroke=FIELD, bold=True)
    p.extend([b_al1, b_al2, b_al3, b_al4])
    
    # Стрілка 2->3
    p.append(arrow(x2 + colw + 5, ytop + 115, x2 + colw + 55, ytop + 115, color=POS, sw=2))
    p.append(text(x2 + colw + 30, ytop + 105, "brk / mmap", size=11, bold=True, color=POS))
    
    p.append(arrow(x2 + colw + 55, ytop + 165, x2 + colw + 5, ytop + 165, color=INK, sw=2))
    p.append(text(x2 + colw + 30, ytop + 155, "сторінки", size=11, bold=True, color=INK))
    
    p.append(text(x2 + colw + 30, ytop + 205, "≈ 500–2000 тактів", size=10, bold=True, color=POS))
    p.append(text(x2 + colw + 30, ytop + 218, "(перехід у ядро)", size=10, color=MUTED))
    
    # Колонка 3: Ядро ОС
    x3 = x2 + colw + 65
    p.append(rect(x3, ytop, colw, h_box, fill="#fef2f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(x3 + colw / 2, ytop + 26, "Ядро ОС (Kernel / VMM)", size=14, bold=True, color=POS))
    p.append(text(x3 + colw / 2, ytop + 46, "(Сторінкова організація)", size=11, color=MUTED))
    
    b_os1, _, _ = textbox(x3 + colw / 2, ytop + 90, "Апаратні сторінки (4 КіБ / 2 МіБ)", size=11, pad=6, fill=BG, stroke=POS)
    b_os2, _, _ = textbox(x3 + colw / 2, ytop + 138, "Таблиці сторінок і блок MMU", size=11, pad=6, fill=BG, stroke=POS)
    b_os3, _, _ = textbox(x3 + colw / 2, ytop + 186, "Віртуальні області (VMA)", size=11, pad=6, fill=BG, stroke=POS)
    b_os4, _, _ = textbox(x3 + colw / 2, ytop + 236, "Фізичні кадри RAM (DRAM)", size=11, pad=5, fill="#fee2e2", stroke=POS, bold=True)
    p.extend([b_os1, b_os2, b_os3, b_os4])
    
    render(os.path.join(OUT, "allocator-role.svg"), W, H, *p)


# ── 2. chunk-layout: анатомія зайнятого та вільного чанка ────────────────────
def fig_chunk_layout():
    W, H = 820, 390
    p = []
    
    p.append(text(W / 2, 26, "Анатомія чанка пам'яті: зайнятий блок проти вільного", size=15, bold=True))
    
    cw = 360
    ch = 300
    y0 = 55
    
    # 1. Зайнятий чанк
    x1 = 35
    p.append(rect(x1, y0, cw, ch, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(x1 + cw / 2, y0 + 24, "Зайнятий чанк (Allocated Chunk)", size=13, bold=True, color=INK))
    
    # Заголовок
    hy = y0 + 45
    p.append(rect(x1 + 15, hy, cw - 30, 48, fill="#fee2e2", stroke=POS, sw=1.5, rx=4))
    p.append(text(x1 + cw / 2, hy + 20, "Chunk Size (61 біт) | A | M | P (3 біти)", size=11, bold=True, color=POS))
    p.append(text(x1 + cw / 2, hy + 38, "Заголовок: розмір блоку + прапорці (8 байтів)", size=10, color=MUTED))
    
    # Покажчик ptr
    p.append(arrow(x1 - 18, hy + 58, x1 + 10, hy + 58, color=FIELD, sw=2))
    p.append(text(x1 - 22, hy + 62, "ptr", size=12, bold=True, color=FIELD, anchor="end"))
    
    # Payload
    py = hy + 56
    p.append(rect(x1 + 15, py, cw - 30, 110, fill="#ecfdf5", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(x1 + cw / 2, py + 45, "Корисне навантаження користувача (Payload)", size=12, bold=True, color=FIELD))
    p.append(text(x1 + cw / 2, py + 68, "Дані програми: `malloc(N)` повертає адресу `ptr`", size=11, color=INK))
    p.append(text(x1 + cw / 2, py + 88, "Користувач бачить лише цю область пам'яті", size=10, color=MUTED))
    
    # Padding
    pdy = py + 118
    p.append(rect(x1 + 15, pdy, cw - 30, 36, fill="#f1f5f9", stroke=MUTED, sw=1.2, rx=4))
    p.append(text(x1 + cw / 2, pdy + 22, "Вирівнювання (Padding до 16 байтів)", size=10, color=MUTED))
    
    p.append(text(x1 + cw / 2, y0 + ch - 12, "Заголовок передує покажчику; футер відсутній (економія пам'яті)", size=10, italic=True, color=MUTED))
    
    # 2. Вільний чанк
    x2 = x1 + cw + 30
    p.append(rect(x2, y0, cw, ch, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(x2 + cw / 2, y0 + 24, "Вільний чанк (Free Chunk у списку)", size=13, bold=True, color=INK))
    
    # Заголовок
    p.append(rect(x2 + 15, hy, cw - 30, 48, fill="#fee2e2", stroke=POS, sw=1.5, rx=4))
    p.append(text(x2 + cw / 2, hy + 20, "Chunk Size (61 біт) | A | M | P (3 біти)", size=11, bold=True, color=POS))
    p.append(text(x2 + cw / 2, hy + 38, "Заголовок: розмір вільного блоку (8 байтів)", size=10, color=MUTED))
    
    # Вбудовані покажчики
    p.append(rect(x2 + 15, py, cw - 30, 75, fill="#eff6ff", stroke=NEG, sw=1.5, rx=4))
    p.append(text(x2 + cw / 2, py + 22, "Вбудовані покажчики списку (Embedded Pointers)", size=11, bold=True, color=NEG))
    p.append(text(x2 + cw / 2, py + 44, "fd: покажчик на наступний вільний чанк (8 B)", size=10, color=INK))
    p.append(text(x2 + cw / 2, py + 62, "bk: покажчик на попередній вільний чанк (8 B)", size=10, color=INK))
    
    # Вільне місце
    fuy = py + 82
    p.append(rect(x2 + 15, fuy, cw - 30, 36, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=4))
    p.append(text(x2 + cw / 2, fuy + 22, "Невикористаний простір чанка", size=10, color=MUTED))
    
    # Граничний тег / Footer
    fty = fuy + 44
    p.append(rect(x2 + 15, fty, cw - 30, 36, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
    p.append(text(x2 + cw / 2, fty + 22, "prev_size: розмір цього чанка для сусіда (8 B)", size=10, bold=True, color="#b45309"))
    
    p.append(text(x2 + cw / 2, y0 + ch - 12, "Покажчики `fd`/`bk` лежать у тілі чанка без додаткових витрат", size=10, italic=True, color=MUTED))
    
    render(os.path.join(OUT, "chunk-layout.svg"), W, H, *p)


# ── 3. coalescing-boundary-tags: злиття за тегами Кнута ───────────────────────
def fig_coalescing():
    W, H = 820, 360
    p = []
    
    p.append(text(W / 2, 26, "Коалесценція за граничними тегами: злиття вільних блоків за O(1)", size=15, bold=True))
    
    # ── Верхній рівень: До звільнення ──
    y1 = 52
    p.append(text(40, y1 + 15, "1. До free(B): три суміжні блоки в пам'яті", size=13, bold=True, color=INK, anchor="start"))
    
    # Блок A (Free)
    xa = 40
    wa = 200
    h_blk = 75
    p.append(rect(xa, y1 + 30, wa, h_blk, fill="#eff6ff", stroke=NEG, sw=1.5, rx=4))
    p.append(text(xa + wa / 2, y1 + 55, "Чанк A: ВІЛЬНИЙ", size=12, bold=True, color=NEG))
    p.append(text(xa + wa / 2, y1 + 75, "Розмір = 64 байти", size=11, color=INK))
    p.append(rect(xa + wa - 60, y1 + 80, 56, 20, fill="#fef3c7", stroke="#d97706", sw=1, rx=2))
    p.append(text(xa + wa - 32, y1 + 94, "size=64", size=9, bold=True, color="#b45309"))
    
    # Блок B (Звільняється)
    xb = xa + wa + 10
    wb = 240
    p.append(rect(xb, y1 + 30, wb, h_blk, fill="#fee2e2", stroke=POS, sw=2, rx=4))
    p.append(text(xb + wb / 2, y1 + 55, "Чанк B: ЗВІЛЬНЯЄТЬСЯ (free)", size=12, bold=True, color=POS))
    p.append(text(xb + wb / 2, y1 + 75, "Розмір = 48 байтів | PREV_INUSE = 0", size=11, color=INK))
    p.append(rect(xb + 5, y1 + 35, 75, 18, fill="#fee2e2", stroke=POS, sw=1, rx=2))
    p.append(text(xb + 42, y1 + 47, "Hdr: sz=48", size=9, bold=True, color=POS))
    
    # Блок C (Free)
    xc = xb + wb + 10
    wc = 240
    p.append(rect(xc, y1 + 30, wc, h_blk, fill="#eff6ff", stroke=NEG, sw=1.5, rx=4))
    p.append(text(xc + wc / 2, y1 + 55, "Чанк C: ВІЛЬНИЙ", size=12, bold=True, color=NEG))
    p.append(text(xc + wc / 2, y1 + 75, "Розмір = 80 байтів", size=11, color=INK))
    p.append(rect(xc + 5, y1 + 35, 75, 18, fill="#eff6ff", stroke=NEG, sw=1, rx=2))
    p.append(text(xc + 42, y1 + 47, "Hdr: sz=80", size=9, bold=True, color=NEG))
    
    # Стрілки перевірки
    p.append(arrow(xb + 40, y1 + 115, xa + wa - 30, y1 + 115, color=NEG, sw=1.8))
    p.append(text(xa + wa + 5, y1 + 130, "1. Погляд назад (prev_size) → A вільний", size=10, bold=True, color=NEG))
    
    p.append(arrow(xb + wb - 40, y1 + 115, xc + 30, y1 + 115, color=NEG, sw=1.8))
    p.append(text(xb + wb + 5, y1 + 130, "2. Погляд вперед (B + 48) → C вільний", size=10, bold=True, color=NEG))
    
    # ── Нижній рівень: Після злиття ──
    y2 = 205
    p.append(text(40, y2 + 15, "2. Після коалесценції: єдиний неперервний блок у списку вільних", size=13, bold=True, color=INK, anchor="start"))
    
    w_total = wa + wb + wc + 20
    p.append(rect(xa, y2 + 30, w_total, 75, fill="#f0fdf4", stroke=FIELD, sw=2, rx=6))
    p.append(text(xa + w_total / 2, y2 + 58, "Об'єднаний вільний чанк A + B + C", size=14, bold=True, color=FIELD))
    p.append(text(xa + w_total / 2, y2 + 80, "Сумарний розмір = 64 + 48 + 80 = 192 байти (готові для великого malloc)", size=12, color=INK))
    
    p.append(rect(xa + 10, y2 + 36, 120, 20, fill="#dcfce7", stroke=FIELD, sw=1, rx=2))
    p.append(text(xa + 70, y2 + 50, "Header: size = 192", size=10, bold=True, color=FIELD))
    
    p.append(rect(xa + w_total - 130, y2 + 80, 120, 20, fill="#fef3c7", stroke="#d97706", sw=1, rx=2))
    p.append(text(xa + w_total - 70, y2 + 94, "prev_size = 192", size=10, bold=True, color="#b45309"))
    
    p.append(text(W / 2, y2 + 135, "Злиття усуває зовнішню фрагментацію миттєво без перебору всієї купи", size=11, italic=True, color=MUTED))
    
    render(os.path.join(OUT, "coalescing-boundary-tags.svg"), W, H, *p)


# ── 4. multi-tier-hierarchy: багаторівнева ієрархія алокатора ─────────────────
def fig_multi_tier():
    W, H = 820, 370
    p = []
    
    p.append(text(W / 2, 26, "Багаторівнева ієрархія алокатора: оптимізація швидкодії та блокувань", size=15, bold=True))
    
    h_lvl = 75
    w_lvl = 740
    x_lvl = 40
    
    # Рівень 1: tcache
    y1 = 50
    p.append(rect(x_lvl, y1, w_lvl, h_lvl, fill="#f0fdf4", stroke=FIELD, sw=2, rx=8))
    p.append(text(x_lvl + 20, y1 + 28, "Рівень 1: Локальний кеш потоку (Thread-Local Cache / tcache)", size=13, bold=True, color=FIELD, anchor="start"))
    p.append(text(x_lvl + 20, y1 + 52, "• Зберігається у TLS (__thread) окремо для кожного потоку процесу", size=11, color=INK, anchor="start"))
    p.append(text(x_lvl + 430, y1 + 28, "Швидкість: ≈ 5–12 тактів", size=11, bold=True, color=FIELD, anchor="start"))
    p.append(text(x_lvl + 430, y1 + 52, "Синхронізація: БЕЗ М'ЮТЕКСІВ (Lock-free)", size=11, bold=True, color=FIELD, anchor="start"))
    
    # Стрілка 1->2
    p.append(arrow(W / 2 - 60, y1 + h_lvl, W / 2 - 60, y1 + h_lvl + 25, color=MUTED, sw=2))
    p.append(text(W / 2 - 70, y1 + h_lvl + 16, "промах кешу", size=10, bold=True, color=MUTED, anchor="end"))
    
    p.append(arrow(W / 2 + 60, y1 + h_lvl + 25, W / 2 + 60, y1 + h_lvl, color=MUTED, sw=2))
    p.append(text(W / 2 + 70, y1 + h_lvl + 16, "поповнення", size=10, bold=True, color=MUTED, anchor="start"))
    
    # Рівень 2: Arenas
    y2 = y1 + h_lvl + 28
    p.append(rect(x_lvl, y2, w_lvl, h_lvl, fill="#eff6ff", stroke=NEG, sw=2, rx=8))
    p.append(text(x_lvl + 20, y2 + 28, "Рівень 2: Арени пам'яті (Thread Arenas & Segregated Bins)", size=13, bold=True, color=NEG, anchor="start"))
    p.append(text(x_lvl + 20, y2 + 52, "• Масиви списків вільних блоків за розмірними класами (Fast, Small, Large Bins)", size=11, color=INK, anchor="start"))
    p.append(text(x_lvl + 430, y2 + 28, "Швидкість: ≈ 50–150 тактів", size=11, bold=True, color=NEG, anchor="start"))
    p.append(text(x_lvl + 430, y2 + 52, "Синхронізація: М'ютекс арени (Per-arena lock)", size=11, bold=True, color=NEG, anchor="start"))
    
    # Стрілка 2->3
    p.append(arrow(W / 2 - 60, y2 + h_lvl, W / 2 - 60, y2 + h_lvl + 25, color=MUTED, sw=2))
    p.append(text(W / 2 - 70, y2 + h_lvl + 16, "нестача пулу", size=10, bold=True, color=MUTED, anchor="end"))
    
    p.append(arrow(W / 2 + 60, y2 + h_lvl + 25, W / 2 + 60, y2 + h_lvl, color=MUTED, sw=2))
    p.append(text(W / 2 + 70, y2 + h_lvl + 16, "madvise / trim", size=10, bold=True, color=MUTED, anchor="start"))
    
    # Рівень 3: OS Kernel
    y3 = y2 + h_lvl + 28
    p.append(rect(x_lvl, y3, w_lvl, h_lvl, fill="#fee2e2", stroke=POS, sw=2, rx=8))
    p.append(text(x_lvl + 20, y3 + 28, "Рівень 3: Ядро операційної системи (OS Virtual Memory Manager)", size=13, bold=True, color=POS, anchor="start"))
    p.append(text(x_lvl + 20, y3 + 52, "• Виділення великих арен через mmap(MAP_ANONYMOUS) або розширення brk", size=11, color=INK, anchor="start"))
    p.append(text(x_lvl + 430, y3 + 28, "Швидкість: ≈ 1000–3000 тактів", size=11, bold=True, color=POS, anchor="start"))
    p.append(text(x_lvl + 430, y3 + 52, "Синхронізація: Системні виклики ядра (Syscalls)", size=11, bold=True, color=POS, anchor="start"))
    
    p.append(text(W / 2, y3 + h_lvl + 20, "99% запитів malloc/free завершуються на Рівні 1 без звернення до м'ютексів та ядра", size=11, italic=True, color=MUTED))
    
    render(os.path.join(OUT, "multi-tier-hierarchy.svg"), W, H, *p)


# ── 5. buddy-split-merge: робота Buddy-алокатора ──────────────────────────────
def fig_buddy():
    W, H = 820, 360
    p = []
    
    p.append(text(W / 2, 26, "Двійковий Buddy-алокатор: рекурсивне розбиття та злиття степенів двійки", size=15, bold=True))
    
    # Рівень 0: 64 КіБ
    y0 = 55
    p.append(rect(60, y0, 700, 42, fill="#f1f5f9", stroke=LINE, sw=1.5, rx=4))
    p.append(text(60 + 350, y0 + 26, "Початковий суцільний блок: 64 КіБ [Адреса: 0x00000]", size=12, bold=True, color=INK))
    
    # Рівень 1: 32 КіБ + 32 КіБ
    y1 = y0 + 55
    p.append(arrow(410, y0 + 44, 410, y1 - 2, color=MUTED, sw=1.5))
    p.append(text(410, y1 - 8, "розбиття", size=10, color=MUTED))
    
    p.append(rect(60, y1, 345, 42, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=4))
    p.append(text(60 + 172, y1 + 26, "Блок A: 32 КіБ [0x00000]", size=11, bold=True, color=INK))
    
    p.append(rect(415, y1, 345, 42, fill="#eff6ff", stroke=NEG, sw=1.5, rx=4))
    p.append(text(415 + 172, y1 + 26, "Близнюк (Buddy): 32 КіБ [0x08000] (Вільний)", size=11, bold=True, color=NEG))
    
    # Рівень 2: 16 КіБ + 16 КіБ
    y2 = y1 + 55
    p.append(arrow(232, y1 + 44, 232, y2 - 2, color=MUTED, sw=1.5))
    p.append(text(232, y2 - 8, "розбиття", size=10, color=MUTED))
    
    p.append(rect(60, y2, 170, 42, fill="#cbd5e1", stroke=LINE, sw=1.5, rx=4))
    p.append(text(60 + 85, y2 + 26, "Блок: 16 КіБ", size=11, bold=True, color=INK))
    
    p.append(rect(235, y2, 170, 42, fill="#eff6ff", stroke=NEG, sw=1.5, rx=4))
    p.append(text(235 + 85, y2 + 26, "Buddy: 16 КіБ (Вільний)", size=10, bold=True, color=NEG))
    
    # Рівень 3: 8 КіБ (Зайнятий) + 8 КіБ (Вільний)
    y3 = y2 + 55
    p.append(arrow(145, y2 + 44, 145, y3 - 2, color=MUTED, sw=1.5))
    p.append(text(145, y3 - 8, "розбиття", size=10, color=MUTED))
    
    p.append(rect(60, y3, 82, 42, fill="#fee2e2", stroke=POS, sw=1.8, rx=4))
    p.append(text(60 + 41, y3 + 20, "8 КіБ", size=11, bold=True, color=POS))
    p.append(text(60 + 41, y3 + 34, "ЗАЙНЯТО", size=9, bold=True, color=POS))
    
    p.append(rect(148, y3, 82, 42, fill="#eff6ff", stroke=NEG, sw=1.5, rx=4))
    p.append(text(148 + 41, y3 + 20, "8 КіБ", size=11, bold=True, color=NEG))
    p.append(text(148 + 41, y3 + 34, "ВІЛЬНИЙ", size=9, bold=True, color=NEG))
    
    # Пояснення формули справа
    x_formula = 450
    y_formula = y2 - 5
    p.append(rect(x_formula, y_formula, 310, 115, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(x_formula + 155, y_formula + 24, "Формула адреси близнюка (Buddy):", size=11, bold=True, color=INK))
    p.append(text(x_formula + 155, y_formula + 50, "buddy_addr = block_addr ^ block_size", size=12, bold=True, color=FIELD))
    p.append(text(x_formula + 155, y_formula + 76, "• Бінарний XOR знаходить пару за 1 такт", size=10, color=INK))
    p.append(text(x_formula + 155, y_formula + 96, "• Якщо сусід вільний — миттєве злиття назад", size=10, color=INK))
    
    p.append(text(W / 2, y3 + 60, "Buddy-алокація гарантує миттєве злиття за O(1), але створює внутрішню фрагментацію", size=11, italic=True, color=MUTED))
    
    render(os.path.join(OUT, "buddy-split-merge.svg"), W, H, *p)


if __name__ == "__main__":
    fig_allocator_role()
    fig_chunk_layout()
    fig_coalescing()
    fig_multi_tier()
    fig_buddy()
    print("All figures generated successfully.")
