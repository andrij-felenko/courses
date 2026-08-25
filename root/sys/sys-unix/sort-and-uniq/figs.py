import os
import sys

# Add scripts/ to sys.path (4 levels up from topic folder)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import render as svg_render, rect, text, mtext, line, arrow, FILL, INK, LINE, MUTED, POS, NEG, FIELD

def render_external_merge_sort(img_dir):
    w, h = 860, 480
    frags = []

    frags.append(text(w / 2, 28, "Архітектура зовнішнього сортування злиттям (External Merge Sort)", size=16, bold=True))

    # Phase 1 Box
    frags.append(rect(30, 55, 380, 400, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(220, 80, "Фаза 1: Генерація серій (Run Generation)", size=14, color="#0f172a", bold=True))

    # Input Stream
    frags.append(rect(50, 105, 340, 50, fill="#e2e8f0", stroke="#64748b", sw=1.2, rx=4))
    frags.append(text(220, 126, "Вхідний потік / Великий файл (наприклад, 50 GB)", size=12, bold=True, color="#334155"))
    frags.append(text(220, 144, "stdin або несортований файл на диску", size=10, color="#64748b"))

    frags.append(line(220, 155, 220, 180, color=LINE, sw=1.5))
    frags.append(arrow(220, 180, 220, 185, color=LINE, sw=1.5))

    # RAM Buffer
    frags.append(rect(50, 185, 340, 85, fill="#dbeafe", stroke="#2563eb", sw=1.5, rx=4))
    frags.append(text(220, 208, "Буфер оперативної пам'яті (RAM Buffer, sort -S)", size=12, bold=True, color="#1e40af"))
    frags.append(text(220, 228, "1. Зчитування порції до ліміту RAM (наприклад, 2 GB)", size=10, color="#1e3a8a"))
    frags.append(text(220, 246, "2. Внутрішнє сортування в пам'яті (Quicksort / Mergesort)", size=10, color="#1e3a8a"))
    frags.append(text(220, 262, "3. Скидання відсортованого блоку на диск", size=10, color="#1e3a8a"))

    frags.append(line(220, 270, 220, 295, color=LINE, sw=1.5))
    frags.append(arrow(220, 295, 220, 300, color=LINE, sw=1.5))

    # Temp Runs Disk
    frags.append(rect(50, 300, 340, 135, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
    frags.append(text(220, 322, "Тимчасові файли серій на диску ($TMPDIR / sort -T)", size=12, bold=True, color="#92400e"))

    # Runs items
    runs = [
        (65, 340, "Run 1 (сортований)", "#fde68a"),
        (170, 340, "Run 2 (сортований)", "#fde68a"),
        (275, 340, "Run K (сортований)", "#fde68a"),
    ]
    for rx, ry, rtxt, rbg in runs:
        frags.append(rect(rx, ry, 100, 32, fill=rbg, stroke="#b45309", sw=1, rx=3))
        frags.append(text(rx + 50, ry + 20, rtxt, size=9, bold=True, color="#78350f"))

    frags.append(text(220, 395, "N блоків записуються послідовно у файл підкачки", size=10, color="#92400e"))
    frags.append(text(220, 415, "Кожен Run містить локально відсортовані рядки", size=10, color="#92400e"))

    # Bridge between Phase 1 and Phase 2
    frags.append(line(410, 365, 445, 365, color="#d97706", sw=2))
    frags.append(line(445, 365, 445, 175, color="#d97706", sw=2))
    frags.append(line(445, 175, 475, 175, color="#d97706", sw=2))
    frags.append(arrow(475, 175, 480, 175, color="#d97706", sw=2))

    # Phase 2 Box
    frags.append(rect(480, 55, 350, 400, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(655, 80, "Фаза 2: K-входове злиття (K-Way Merge)", size=14, color="#0f172a", bold=True))

    # Streams to Min-Heap
    frags.append(rect(500, 110, 310, 95, fill="#ede9fe", stroke="#7c3aed", sw=1.5, rx=4))
    frags.append(text(655, 132, "Потоки зчитування з K файлів серій", size=12, bold=True, color="#5b21b6"))
    frags.append(text(655, 152, "Буфер читання для кожного відкритого Run-файлу", size=10, color="#6d28d9"))
    frags.append(text(655, 172, "Поточний мінімальний елемент кожного потоку", size=10, color="#6d28d9"))
    frags.append(text(655, 192, "завантажується у пріоритетну чергу", size=10, color="#6d28d9"))

    frags.append(line(655, 205, 655, 225, color=LINE, sw=1.5))
    frags.append(arrow(655, 225, 655, 230, color=LINE, sw=1.5))

    # Min-Heap Box
    frags.append(rect(500, 230, 310, 85, fill="#dcfce7", stroke="#16a34a", sw=1.5, rx=4))
    frags.append(text(655, 252, "Мін-купа / Турнірне дерево (Min-Heap розміру K)", size=12, bold=True, color="#15803d"))
    frags.append(text(655, 272, "1. Витяг абсолютного мінімуму: O(log K)", size=10, color="#166534"))
    frags.append(text(655, 290, "2. Запис найменшого рядка у вихідний потік", size=10, color="#166534"))
    frags.append(text(655, 306, "3. Дочитування наступного рядка з вичерпаного Run", size=10, color="#166534"))

    frags.append(line(655, 315, 655, 340, color=LINE, sw=1.5))
    frags.append(arrow(655, 340, 655, 345, color=LINE, sw=1.5))

    # Output Box
    frags.append(rect(500, 345, 310, 85, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=4))
    frags.append(text(655, 370, "Вихідний потік (Повністю впорядковані дані)", size=12, bold=True, color="#075985"))
    frags.append(text(655, 392, "Глобально відсортований потік stdout / файл", size=10, color="#0c4a6e"))
    frags.append(text(655, 412, "Тимчасові файли серій автоматично видаляються", size=10, color="#0c4a6e"))

    path = os.path.join(img_dir, "external-merge-sort.svg")
    svg_render(path, w, h, *frags)

def render_sort_key_parsing(img_dir):
    w, h = 840, 440
    frags = []

    frags.append(text(w / 2, 28, "Синтаксис ключів sort -k: поля, зміщення та межі вибірки", size=16, bold=True))

    # Key Syntax Box
    frags.append(rect(40, 50, 760, 75, fill="#f1f5f9", stroke="#475569", sw=1.5, rx=6))
    frags.append(text(420, 73, "Синтаксис специфікатора ключа:  -k POS1[,POS2]", size=14, bold=True, color="#0f172a"))
    frags.append(text(420, 95, "POS = F[.C][OPTS]  де  F = номер поля (1-based),  C = символ у полі (1-based),  OPTS = n, r, b, V, h", size=11, color="#334155"))
    frags.append(text(420, 113, "POS1 визначає початок ключа сортування; POS2 визначає кінець включно (якщо опущено — до кінця рядка)", size=10, color="#64748b"))

    # Sample Log Line Box
    frags.append(rect(40, 140, 760, 85, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(120, 160, "Приклад рядка (роздільник -t ' '):", size=11, bold=True, color="#475569", anchor="start"))

    # Fields visual
    fields = [
        (45, 175, 130, "Поле 1", "2026-08-25", "#fee2e2", "#dc2626", "#991b1b"),
        (185, 175, 100, "Поле 2", "14:30:15", "#fef3c7", "#d97706", "#92400e"),
        (295, 175, 65, "Поле 3", "GET", "#dcfce7", "#16a34a", "#15803d"),
        (370, 175, 185, "Поле 4", "/api/v2/items", "#e0f2fe", "#0284c7", "#075985"),
        (565, 175, 65, "Поле 5", "200", "#ede9fe", "#7c3aed", "#5b21b6"),
        (640, 175, 150, "Поле 6", "1420", "#f3e8ff", "#9333ea", "#6b21a8"),
    ]

    for fx, fy, fw, flabel, fval, fbg, fstrk, ftxt in fields:
        frags.append(rect(fx, fy, fw, 42, fill=fbg, stroke=fstrk, sw=1.2, rx=4))
        frags.append(text(fx + fw/2, fy + 16, flabel, size=10, bold=True, color=ftxt))
        frags.append(text(fx + fw/2, fy + 33, fval, size=11, bold=True, color="#0f172a"))

    # Comparison Section
    y_base = 240
    frags.append(rect(40, y_base, 760, 185, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(420, y_base + 22, "Порівняння поведінки специфікаторів на практиці", size=13, bold=True, color="#0f172a"))

    examples = [
        ("sort -k2,2", "Обмежує ключ суворо Полем 2 ('14:30:15'). Інші поля не впливають на сортування цього ключа.", "#15803d", "#dcfce7"),
        ("sort -k2", "ПАСТКА: починає з Поля 2 і бере ВЕСЬ залишок рядка до кінця ('14:30:15 GET /api/v2/items 200 1420').", "#b91c1c", "#fee2e2"),
        ("sort -k1.6,1.7n", "Внутрішньопольовий діапазон: вибирає символи 6–7 поля 1 (місяць '08') і сортує як число.", "#0369a1", "#e0f2fe"),
        ("sort -k5,5n -k6,6nr", "Багатоключове сортування: спочатку за HTTP-кодом (поле 5, зростання), потім за розміром (поле 6, спадання).", "#7e22ce", "#f3e8ff"),
    ]

    ey = y_base + 40
    for cmd, desc, col, bg in examples:
        frags.append(rect(55, ey, 165, 26, fill=bg, stroke=col, sw=1, rx=3))
        frags.append(text(137, ey + 17, cmd, size=11, bold=True, color=col))
        frags.append(text(230, ey + 17, desc, size=10.5, color="#1e293b", anchor="start"))
        ey += 34

    path = os.path.join(img_dir, "sort-key-parsing.svg")
    svg_render(path, w, h, *frags)

def render_sort_uniq_pipeline(img_dir):
    w, h = 820, 450
    frags = []

    frags.append(text(w / 2, 28, "Взаємодія sort і uniq: потокова дедуплікація та фактор LC_ALL=C", size=16, bold=True))

    # Top: Stream Model of uniq
    frags.append(rect(30, 50, 760, 165, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(410, 72, "Потокова модель утиліти uniq: вікно порівняння в 1 попередній рядок", size=13, bold=True, color="#0f172a"))

    # Flow demo
    # Unsorted input
    frags.append(rect(50, 95, 190, 70, fill="#fee2e2", stroke="#dc2626", sw=1.2, rx=4))
    frags.append(text(145, 115, "Несортований вхід:", size=11, bold=True, color="#991b1b"))
    frags.append(text(145, 132, "apple, banana, apple", size=10, color="#7f1d1d"))
    frags.append(text(145, 150, "uniq бачить сусіда != apple", size=9, color="#991b1b"))

    frags.append(line(240, 130, 275, 130, color=LINE, sw=1.5))
    frags.append(arrow(275, 130, 280, 130, color=LINE, sw=1.5))

    # Uniq alone
    frags.append(rect(280, 95, 200, 70, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=4))
    frags.append(text(380, 115, "uniq без попереднього sort:", size=11, bold=True, color="#92400e"))
    frags.append(text(380, 135, "Вихід: apple, banana, apple", size=10, bold=True, color="#b91c1c"))
    frags.append(text(380, 152, "Помилка: дублікати не злито!", size=9, color="#b91c1c"))

    frags.append(line(480, 130, 515, 130, color=LINE, sw=1.5))
    frags.append(arrow(515, 130, 520, 130, color=LINE, sw=1.5))

    # Sorted + uniq
    frags.append(rect(520, 95, 250, 70, fill="#dcfce7", stroke="#16a34a", sw=1.2, rx=4))
    frags.append(text(645, 115, "Конвеєр sort | uniq -c:", size=11, bold=True, color="#15803d"))
    frags.append(text(645, 135, "sort збирає однакові рядки поруч", size=10, color="#166534"))
    frags.append(text(645, 152, "Вихід: 2 apple, 1 banana", size=10, bold=True, color="#15803d"))

    frags.append(text(410, 195, "uniq споживає O(1) RAM, порівнюючи лише поточний рядок з рядком у буфері попереднього кроку", size=10, color="#475569"))

    # Bottom: UTF-8 vs LC_ALL=C
    frags.append(rect(30, 230, 760, 200, fill="#ffffff", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(410, 252, "Вплив локалі на порівняння: UTF-8 Collation проти LC_ALL=C", size=13, bold=True, color="#0f172a"))

    # Left box: UTF-8
    frags.append(rect(45, 270, 350, 145, fill="#fee2e2", stroke="#dc2626", sw=1.2, rx=4))
    frags.append(text(220, 290, "LC_COLLATE=en_US.UTF-8 (Важка коллація)", size=11.5, bold=True, color="#991b1b"))
    frags.append(text(220, 310, "1. Виклики strcoll() з багатопрохідними таблицями", size=10, color="#7f1d1d"))
    frags.append(text(220, 328, "2. Ігнорування пунктуації на первинних рівнях", size=10, color="#7f1d1d"))
    frags.append(text(220, 346, "3. Недетермінованість для бінарних даних", size=10, color="#7f1d1d"))
    frags.append(text(220, 364, "4. Сповільнення сортування в 5–10 разів", size=10, bold=True, color="#b91c1c"))
    frags.append(text(220, 382, "5. Ризик розбіжності між sort і strcmp в uniq", size=10, color="#7f1d1d"))

    # Right box: LC_ALL=C
    frags.append(rect(425, 270, 350, 145, fill="#dcfce7", stroke="#16a34a", sw=1.2, rx=4))
    frags.append(text(600, 290, "LC_ALL=C / LC_COLLATE=C (Золотий стандарт)", size=11.5, bold=True, color="#15803d"))
    frags.append(text(600, 310, "1. Пряме побайтове порівняння memcmp() / strcmp()", size=10, color="#166534"))
    frags.append(text(600, 328, "2. Суворий детермінований числовий порядок байтів", size=10, color="#166534"))
    frags.append(text(600, 346, "3. Апаратна векторизація (SIMD AVX-2 / SSE)", size=10, color="#166534"))
    frags.append(text(600, 364, "4. Максимальна пропускна здатність процесора", size=10, bold=True, color="#15803d"))
    frags.append(text(600, 382, "5. 100% сумісність порядку sort із логікою uniq", size=10, color="#166534"))

    path = os.path.join(img_dir, "sort-uniq-pipeline.svg")
    svg_render(path, w, h, *frags)

def main():
    topic_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(topic_dir, "img")
    os.makedirs(img_dir, exist_ok=True)

    render_external_merge_sort(img_dir)
    render_sort_key_parsing(img_dir)
    render_sort_uniq_pipeline(img_dir)
    print("All figures successfully rendered to", img_dir)

if __name__ == "__main__":
    main()
