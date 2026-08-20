# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GOLD = "#b8860b"
MONO = "Consolas, 'DejaVu Sans Mono', monospace"


def code_line(x, y, s, size=13.0, color="#e8e8e8", anchor="start", bold=True):
    w = ' font-weight="700"' if bold else ''
    a = ' text-anchor="%s"' % anchor
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%.1f" fill="%s"%s%s>%s</text>'
            % (x, y, MONO, size, color, a, w, esc(s)))


# ── 1. shadow-mapping: пряма трансляція адрес у тіньову пам'ять ───────────────
def fig_shadow_mapping():
    W, H = 840, 420
    p = []

    # Заголовок блоку
    p.append(text(W / 2, 28, "Пряме відображення адреси в тіньову пам'ять (Scale = 3, Offset = 0x7fff8000)",
                  size=14, color=INK, bold=True))

    # Схема простору пам'яті (горизонтальна шкала)
    p.append(rect(40, 55, 760, 90, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    
    # Секції простору 64-біт: High Mem, High Shadow, Bad Zone, Low Shadow, Low Mem
    sections = [
        (50, 140, "Low Memory", "0x000000000000 — 0x10007fff7fff", "#e2e8f0", INK),
        (200, 110, "Low Shadow", "0x7fff8000 — ...", "#fed7aa", "#c2410c"),
        (320, 100, "Bad Zone", "Захищений бар'єр", "#fca5a5", POS),
        (430, 110, "High Shadow", "Тінь високої пам'яті", "#fed7aa", "#c2410c"),
        (550, 240, "High Memory", "0x7fffffffffff", "#e2e8f0", INK),
    ]
    for x, w, title, desc, bg, fg in sections:
        p.append(rect(x, 65, w, 70, fill=bg, stroke=LINE, sw=1, rx=4))
        p.append(text(x + w / 2, 92, title, size=11, color=fg, bold=True))
        p.append(text(x + w / 2, 115, desc, size=10, color=MUTED))

    # Формула трансляції
    p.append(rect(180, 165, 480, 50, fill="#0f172a", stroke=FIELD, sw=2, rx=8))
    p.append(code_line(W / 2, 196, "ShadowAddr = (AppAddr >> 3) + Offset", size=15, color="#38bdf8", anchor="middle"))

    # Зв'язок 8 байтів додатку -> 1 байт тіні
    # Лівий блок: 8 байтів пам'яті додатку
    p.append(rect(40, 245, 410, 145, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(text(245, 270, "8 байтів пам'яті програми (AppAddr)", size=12, color=INK, bold=True))
    
    # 8 комірок
    for i in range(8):
        bx = 60 + i * 45
        p.append(rect(bx, 285, 42, 45, fill="#dbeafe", stroke=NEG, sw=1.2, rx=3))
        p.append(text(bx + 21, 305, "Байт %d" % i, size=10, color=NEG, bold=True))
        p.append(text(bx + 21, 322, "+%d B" % i, size=10, color=MUTED))

    p.append(text(245, 360, "Кожні 8 байтів адреси діляться на 8 (зсув >> 3)", size=10.5, color=MUTED, italic=True))

    # Стрілка трансляції
    p.append(arrow(460, 310, 510, 310, color=FIELD, sw=3))
    p.append(text(485, 295, ">> 3", size=12, color=FIELD, bold=True))

    # Правий блок: 1 байт тіні
    p.append(rect(520, 245, 280, 145, fill="#fffbeb", stroke=GOLD, sw=1.5, rx=6))
    p.append(text(660, 270, "1 байт тіні (ShadowAddr)", size=12, color=GOLD, bold=True))
    p.append(rect(610, 285, 100, 45, fill="#fef3c7", stroke=GOLD, sw=2, rx=4))
    p.append(text(660, 306, "0x00 .. 0x07", size=12, color=GOLD, bold=True))
    p.append(text(660, 322, "або < 0 (код пастки)", size=10, color=POS))
    p.append(text(660, 360, "0x00: усі 8 B валідні; k: перші k B валідні", size=10, color=INK))

    render(os.path.join(OUT, "shadow-mapping.svg"), W, H, *p,
           title="Пряме відображення пам'яті в тінь Scale and Offset")


# ── 2. asan-redzones: червоні зони та отруєння тіні в ASan ────────────────────
def fig_asan_redzones():
    W, H = 840, 410
    p = []

    p.append(text(W / 2, 28, "Червоні зони (Redzones) та карантин у купі (Heap)",
                  size=14, color=INK, bold=True))

    # Фізичний розподіл у пам'яті
    p.append(text(120, 65, "Фізична пам'ять (Купа / Стек):", size=12, color=INK, bold=True, anchor="start"))
    
    # Блоки пам'яті: Left Redzone (32B), Payload (24B), Right Redzone (40B)
    p.append(rect(40, 80, 200, 60, fill="#fee2e2", stroke=POS, sw=1.8, rx=4))
    p.append(text(140, 106, "Ліва червона зона (32 B)", size=11, color=POS, bold=True))
    p.append(text(140, 126, "Отруєна пам'ять", size=10, color=POS))

    p.append(rect(245, 80, 260, 60, fill="#dcfce7", stroke=FIELD, sw=2, rx=4))
    p.append(text(375, 106, "Корисні дані (Payload 24 B)", size=12, color=FIELD, bold=True))
    p.append(text(375, 126, "Доступ дозволено (malloc)", size=10, color=FIELD))

    p.append(rect(510, 80, 290, 60, fill="#fee2e2", stroke=POS, sw=1.8, rx=4))
    p.append(text(655, 106, "Права червона зона (40 B)", size=11, color=POS, bold=True))
    p.append(text(655, 126, "Отруєна пам'ять", size=10, color=POS))

    # Стрілки відображення в тінь
    p.append(arrow(140, 145, 140, 185, color=MUTED, sw=1.5))
    p.append(arrow(375, 145, 375, 185, color=MUTED, sw=1.5))
    p.append(arrow(655, 145, 655, 185, color=MUTED, sw=1.5))

    # Тіньова пам'ять (байти тіні)
    p.append(text(120, 180, "Тіньова пам'ять (Shadow Bytes):", size=12, color=INK, bold=True, anchor="start"))
    
    # Тінь лівої зони: 4 байти по 0xFA
    p.append(rect(40, 195, 200, 50, fill="#fca5a5", stroke=POS, sw=1.5, rx=4))
    p.append(text(140, 220, "0xFA 0xFA 0xFA 0xFA", size=11, color="#7f1d1d", bold=True))
    p.append(text(140, 236, "heap-left-redzone", size=10, color="#7f1d1d"))

    # Тінь корисних даних: 3 байти по 0x00 (24 B / 8 = 3 байти тіні)
    p.append(rect(245, 195, 260, 50, fill="#86efac", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(375, 220, "0x00 0x00 0x00", size=12, color="#14532d", bold=True))
    p.append(text(375, 236, "усі байти валідні", size=10, color="#14532d"))

    # Тінь правої зони: 5 байтів по 0xFB
    p.append(rect(510, 195, 290, 50, fill="#fca5a5", stroke=POS, sw=1.5, rx=4))
    p.append(text(655, 220, "0xFB 0xFB 0xFB 0xFB 0xFB", size=11, color="#7f1d1d", bold=True))
    p.append(text(655, 236, "heap-right-redzone", size=10, color="#7f1d1d"))

    # Нижній блок: Звільнення пам'яті та карантин (Use-After-Free)
    p.append(rect(40, 275, 760, 115, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(60, 298, "Після free(ptr) — Карантинна черга (FIFO Quarantine Queue):", size=11.5, color=INK, bold=True, anchor="start"))

    p.append(rect(60, 312, 380, 62, fill="#fef2f2", stroke=POS, sw=1.5, rx=4))
    p.append(text(250, 335, "Весь блок отруюється значенням 0xFD", size=11, color=POS, bold=True))
    p.append(text(250, 355, "Shadow: 0xFD 0xFD 0xFD 0xFD ... (heap-freed)", size=10, color=MUTED))

    p.append(rect(460, 312, 320, 62, fill="#f1f5f9", stroke=LINE, sw=1.2, rx=4))
    p.append(text(620, 335, "Пам'ять затримується в карантині", size=10.5, color=INK, bold=True))
    p.append(text(620, 355, "Будь-який доступ негайно генерує Use-After-Free", size=10, color=POS))

    render(os.path.join(OUT, "asan-redzones.svg"), W, H, *p,
           title="Червоні зони ASan, отруєння тіні та карантин купи")


# ── 3. tsan-vector-clock: векторні годинники та гонки даних у TSan ─────────────
def fig_tsan_vector_clock():
    W, H = 840, 430
    p = []

    p.append(text(W / 2, 28, "Виявлення гонок даних (Data Race) через векторні годинники TSan",
                  size=14, color=INK, bold=True))

    # Стовпчик Потоку 1
    p.append(rect(40, 60, 340, 340, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(210, 88, "Потік 1 (Thread 1)", size=13, color=FIELD, bold=True))
    p.append(text(210, 108, "Годинник T1: [T1: 12, T2: 4]", size=10.5, color=MUTED))

    p.append(rect(60, 130, 300, 65, fill="#ffffff", stroke=LINE, sw=1.2, rx=5))
    p.append(code_line(75, 155, "x = 42;  // Write(X)", size=13, color="#1e293b"))
    p.append(text(75, 180, "Тінь: Записано (T1, Epoch 12, Write)", size=10, color=FIELD, anchor="start", bold=True))

    p.append(rect(60, 220, 300, 70, fill="#f8fafc", stroke=LINE, sw=1.2, rx=5))
    p.append(code_line(75, 245, "pthread_mutex_unlock(&m);", size=12, color="#0f766e"))
    p.append(text(75, 272, "Публікація годинника T1 в м'ютекс: [12, 4]", size=10, color=MUTED, anchor="start"))

    p.append(text(210, 340, "T1 закінчив запис змінної X", size=10.5, color=INK))
    p.append(text(210, 365, "і звільнив замок", size=10, color=MUTED))

    # Стовпчик Потоку 2 (без синхронізації)
    p.append(rect(460, 60, 340, 340, fill="#fef2f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(630, 88, "Потік 2 (Thread 2)", size=13, color=POS, bold=True))
    p.append(text(630, 108, "Годинник T2: [T1: 2, T2: 5]", size=10.5, color=MUTED))

    p.append(rect(480, 130, 300, 65, fill="#ffffff", stroke=POS, sw=1.5, rx=5))
    p.append(code_line(495, 155, "int v = x;  // Read(X)", size=13, color="#b91c1c"))
    p.append(text(495, 180, "Читання БЕЗ взяття м'ютекса!", size=10, color=POS, anchor="start", bold=True))

    p.append(rect(480, 220, 300, 100, fill="#fff1f2", stroke=POS, sw=1.2, rx=5))
    p.append(text(630, 242, "Перевірка стану TSan:", size=11, color=POS, bold=True))
    p.append(text(630, 264, "Попередній запис був в T1 (епоха 12)", size=10, color=INK))
    p.append(text(630, 284, "Поточний T2 знає про T1 лише епоху 2 (< 12)", size=10, color=POS, bold=True))
    p.append(text(630, 304, "→ Немає відношення happens-before!", size=10, color=POS, bold=True))

    p.append(text(630, 355, "ФАТАЛЬНА ПОМИЛКА:", size=11, color=POS, bold=True))
    p.append(text(630, 375, "WARNING: ThreadSanitizer: data race on x", size=10.5, color=POS, bold=True))

    # Стрілка конфлікту між потоками
    p.append(arrow(365, 160, 475, 160, color=POS, sw=2.5))
    p.append(text(420, 150, "ГОНКА", size=10, color=POS, bold=True))

    render(os.path.join(OUT, "tsan-vector-clock.svg"), W, H, *p,
           title="Виявлення гонок даних через векторні годинники TSan")


# ── 4. msan-bit-shadow: бітова тінь та поширення неініціалізованих значень ────
def fig_msan_bit_shadow():
    W, H = 840, 420
    p = []

    p.append(text(W / 2, 28, "MemorySanitizer: Побайтове/побітове відстеження неініціалізованої пам'яті",
                  size=14, color=INK, bold=True))

    # Лівий блок: Справжні дані та тінь
    p.append(rect(40, 60, 360, 160, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(220, 85, "Значення змінної x (32-bit int)", size=12, color=INK, bold=True))
    
    # Дані: 4 байти
    p.append(rect(60, 100, 320, 40, fill="#dbeafe", stroke=NEG, sw=1.2, rx=4))
    p.append(text(220, 125, "Реальні дані: 0x?? 0x?? 0x?? 0x?? (сміття зі стеку)", size=10, color=NEG, bold=True))

    # Тінь: 4 байти тіні (1 біт = 1 біт, 0 = валідно, 1 = uninitialized)
    p.append(rect(60, 150, 320, 40, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(220, 175, "Тінь (Shadow): 0xFF 0xFF 0xFF 0xFF (неініціалізовано)", size=10, color=POS, bold=True))

    # Центральний блок: Поширення тіні (Propagation)
    p.append(rect(440, 60, 360, 160, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(620, 85, "Поширення тіні в операціях (ALU)", size=12, color=FIELD, bold=True))
    p.append(code_line(460, 115, "int y = x + 10;  // Обчислення", size=12, color="#1e293b"))
    p.append(text(460, 140, "Дані: y обчислюється як сміття + 10", size=10, color=MUTED, anchor="start"))
    p.append(text(460, 160, "Тінь: Shadow_y = Shadow_x (0xFFFFFFFF)", size=10, color=POS, anchor="start", bold=True))
    p.append(text(620, 195, "ОБЧИСЛЕННЯ НЕ ВИКЛИКАЄ ПОМИЛКИ!", size=10, color=FIELD, bold=True))

    # Нижній блок: Момент спрацювання (Trigger check)
    p.append(rect(40, 240, 760, 155, fill="#fff1f2", stroke=POS, sw=2, rx=8))
    p.append(text(W / 2, 268, "Момент перевірки: Розгалуження або Системний виклик (Check on Use)",
                  size=13, color=POS, bold=True))

    # Код з if (y > 0)
    p.append(rect(60, 285, 340, 90, fill="#ffffff", stroke=POS, sw=1.5, rx=6))
    p.append(code_line(80, 315, "if (y > 0) {", size=14, color="#b91c1c"))
    p.append(code_line(80, 340, "    do_something();", size=14, color="#1e293b"))
    p.append(code_line(80, 365, "}", size=14, color="#b91c1c"))

    # Пояснення вердикту MSan
    p.append(rect(420, 285, 360, 90, fill="#fee2e2", stroke=POS, sw=1.2, rx=6))
    p.append(text(600, 310, "Компілятор вставив інструментацію:", size=10.5, color=POS, bold=True))
    p.append(code_line(440, 335, "if (__msan_test_shadow(&y))", size=11.5, color="#7f1d1d"))
    p.append(code_line(440, 358, "    __msan_warning();", size=11.5, color="#7f1d1d"))

    render(os.path.join(OUT, "msan-bit-shadow.svg"), W, H, *p,
           title="MemorySanitizer: побітова тінь та момент виявлення неініціалізованого читання")


if __name__ == "__main__":
    fig_shadow_mapping()
    fig_asan_redzones()
    fig_tsan_vector_clock()
    fig_msan_bit_shadow()
    print("All figures generated successfully.")
