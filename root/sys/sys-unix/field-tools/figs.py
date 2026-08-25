import os
import sys

# Add scripts/ to sys.path (4 levels up from topic folder)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import render as svg_render, rect, text, mtext, line, arrow, circle, textbox, fitbox, FILL, INK, LINE, MUTED, POS, NEG, FIELD

def render_cut_paste_ops(img_dir):
    w, h = 760, 480
    frags = []

    # Title & Subtitle
    frags.append(text(w / 2, 25, "Механіка cut (розрізання) та paste (злиття стовпців)", size=15, bold=True))

    # --- TOP PANEL: cut ---
    frags.append(rect(20, 45, 720, 195, fill="#f8fafc", stroke="#64748b", sw=1.5))
    frags.append(text(35, 68, "cut: вибірка вертикальних фрагментів із потоку рядків", size=13, bold=True, color="#0f172a", anchor="start"))

    # Delimiter mode
    frags.append(rect(35, 85, 335, 140, fill="#ffffff", stroke="#94a3b8", sw=1))
    frags.append(text(45, 105, "Поля за роздільником (-d ':' -f 1,3)", size=11, bold=True, color="#1e293b", anchor="start"))
    
    # Input stream row
    frags.append(rect(45, 118, 90, 24, fill="#e2e8f0", stroke="#94a3b8", sw=1))
    frags.append(text(90, 134, "root (f1)", size=10, bold=True, color="#0f172a"))
    frags.append(text(140, 134, ":", size=12, bold=True, color=POS))
    frags.append(rect(148, 118, 40, 24, fill="#f1f5f9", stroke="#cbd5e1", sw=1))
    frags.append(text(168, 134, "x (f2)", size=10, color=MUTED))
    frags.append(text(193, 134, ":", size=12, bold=True, color=POS))
    frags.append(rect(200, 118, 40, 24, fill="#e2e8f0", stroke="#94a3b8", sw=1))
    frags.append(text(220, 134, "0 (f3)", size=10, bold=True, color="#0f172a"))
    frags.append(text(245, 134, ":", size=12, bold=True, color=POS))
    frags.append(rect(252, 118, 105, 24, fill="#f1f5f9", stroke="#cbd5e1", sw=1))
    frags.append(text(304, 134, "/root:/bin/bash", size=9, color=MUTED))

    # Arrow down
    frags.append(arrow(200, 148, 200, 175, color=FIELD, sw=2))
    frags.append(text(215, 166, "-f 1,3", size=10, bold=True, color=FIELD, anchor="start"))

    # Output stream row
    frags.append(rect(45, 182, 120, 26, fill="#dcfce7", stroke="#16a34a", sw=1.5))
    frags.append(text(105, 199, "root:0", size=11, bold=True, color="#15803d"))
    frags.append(text(175, 199, "Збережено роздільник між полями", size=10, color=MUTED, anchor="start"))

    # Byte/Char slice mode
    frags.append(rect(390, 85, 335, 140, fill="#ffffff", stroke="#94a3b8", sw=1))
    frags.append(text(400, 105, "Фіксовані зміщення байтів (-b 1-4,9-12)", size=11, bold=True, color="#1e293b", anchor="start"))

    # Byte index grid
    frags.append(rect(400, 118, 65, 24, fill="#e0f2fe", stroke="#0284c7", sw=1))
    frags.append(text(432, 134, "2026", size=10, bold=True, color="#0369a1"))
    frags.append(rect(468, 118, 45, 24, fill="#f1f5f9", stroke="#cbd5e1", sw=1))
    frags.append(text(490, 134, "-08-", size=10, color=MUTED))
    frags.append(rect(516, 118, 55, 24, fill="#e0f2fe", stroke="#0284c7", sw=1))
    frags.append(text(543, 134, "25 15", size=10, bold=True, color="#0369a1"))
    frags.append(rect(574, 118, 80, 24, fill="#f1f5f9", stroke="#cbd5e1", sw=1))
    frags.append(text(614, 134, ":30:00 UTC", size=9, color=MUTED))

    # Arrow down
    frags.append(arrow(550, 148, 550, 175, color=NEG, sw=2))
    frags.append(text(565, 166, "Вибірка байтів", size=10, bold=True, color=NEG, anchor="start"))

    # Output stream row
    frags.append(rect(400, 182, 120, 26, fill="#dbeafe", stroke="#2563eb", sw=1.5))
    frags.append(text(460, 199, "202625 15", size=11, bold=True, color="#1d4ed8"))
    frags.append(text(530, 199, "Без вставки роздільника", size=10, color=MUTED, anchor="start"))

    # --- BOTTOM PANEL: paste ---
    frags.append(rect(20, 255, 720, 205, fill="#f8fafc", stroke="#64748b", sw=1.5))
    frags.append(text(35, 278, "paste: паралельне горизонтальне злиття та серіалізація", size=13, bold=True, color="#0f172a", anchor="start"))

    # Side-by-side merging
    frags.append(rect(35, 295, 335, 150, fill="#ffffff", stroke="#94a3b8", sw=1))
    frags.append(text(45, 315, "Злиття файлів бік-о-бік: paste -d ',' A B", size=11, bold=True, color="#1e293b", anchor="start"))

    # File A and File B
    frags.append(rect(45, 330, 60, 48, fill="#fef3c7", stroke="#d97706", sw=1))
    frags.append(mtext(75, 348, ["web01", "web02"], size=10, bold=True, color="#92400e", lh=1.4))

    frags.append(text(120, 355, "+", size=14, bold=True, color=MUTED))

    frags.append(rect(140, 330, 85, 48, fill="#ede9fe", stroke="#7c3aed", sw=1))
    frags.append(mtext(182, 348, ["10.0.0.1", "10.0.0.2"], size=10, bold=True, color="#5b21b6", lh=1.4))

    frags.append(arrow(235, 355, 265, 355, color="#16a34a", sw=2))

    frags.append(rect(275, 330, 85, 48, fill="#dcfce7", stroke="#16a34a", sw=1.5))
    frags.append(mtext(317, 348, ["web01,10.0.0.1", "web02,10.0.0.2"], size=9, bold=True, color="#15803d", lh=1.4))
    frags.append(text(45, 400, "Одночасне читання рядків із двох дескрипторів", size=9, color=MUTED, anchor="start"))
    frags.append(text(45, 415, "та склеювання через обраний символ роздільника", size=9, color=MUTED, anchor="start"))

    # N-tuple grouping trick (paste - - -)
    frags.append(rect(390, 295, 335, 150, fill="#ffffff", stroke="#94a3b8", sw=1))
    frags.append(text(400, 315, "Групування потоку stdin: paste - - -", size=11, bold=True, color="#1e293b", anchor="start"))

    frags.append(rect(400, 330, 70, 70, fill="#fef3c7", stroke="#d97706", sw=1))
    frags.append(mtext(435, 345, ["1", "2", "3", "4", "5", "6"], size=9, bold=True, color="#92400e", lh=1.2))

    frags.append(arrow(480, 365, 520, 365, color="#2563eb", sw=2))
    frags.append(text(500, 355, "3 stdin", size=9, bold=True, color="#2563eb"))

    frags.append(rect(530, 330, 180, 50, fill="#dbeafe", stroke="#2563eb", sw=1.5))
    frags.append(mtext(620, 350, ["1 \\t 2 \\t 3  (рядок 1)", "4 \\t 5 \\t 6  (рядок 2)"], size=9, bold=True, color="#1d4ed8", lh=1.4))

    frags.append(text(400, 418, "Три аргументи '-' почергово вичитують спільний fd 0", size=9, color=MUTED, anchor="start"))
    frags.append(text(400, 432, "формуючи таблицю з трьох колонок за один прохід.", size=9, color=MUTED, anchor="start"))

    path = os.path.join(img_dir, "cut-paste-mechanics.svg")
    svg_render(path, w, h, *frags)

def render_join_relational(img_dir):
    w, h = 760, 460
    frags = []

    frags.append(text(w / 2, 25, "Реляційне з'єднання потоків утилітою join", size=15, bold=True))

    # Two sorted streams
    frags.append(rect(30, 50, 200, 190, fill="#fef3c7", stroke="#d97706", sw=1.5))
    frags.append(text(130, 72, "Файл 1 (відсортований)", size=12, bold=True, color="#92400e"))
    
    frags.append(rect(45, 88, 170, 26, fill="#ffffff", stroke="#d97706", sw=1))
    frags.append(text(130, 105, "101  Альфа  Відділ_А", size=10, bold=True, color="#78350f"))
    frags.append(rect(45, 120, 170, 26, fill="#ffffff", stroke="#d97706", sw=1))
    frags.append(text(130, 137, "102  Бета   Відділ_Б", size=10, bold=True, color="#78350f"))
    frags.append(rect(45, 152, 170, 26, fill="#ffffff", stroke="#d97706", sw=1))
    frags.append(text(130, 169, "104  Гамма  Відділ_В", size=10, bold=True, color="#78350f"))
    frags.append(text(130, 205, "Ключ: колонка 1 (ID)", size=10, color=MUTED))
    frags.append(text(130, 222, "LC_ALL=C порядок", size=10, bold=True, color=POS))

    frags.append(rect(530, 50, 200, 190, fill="#ede9fe", stroke="#7c3aed", sw=1.5))
    frags.append(text(630, 72, "Файл 2 (відсортований)", size=12, bold=True, color="#5b21b6"))
    
    frags.append(rect(545, 88, 170, 26, fill="#ffffff", stroke="#7c3aed", sw=1))
    frags.append(text(630, 105, "101  25000  Київ", size=10, bold=True, color="#4c1d95"))
    frags.append(rect(545, 120, 170, 26, fill="#ffffff", stroke="#7c3aed", sw=1))
    frags.append(text(630, 137, "103  31000  Львів", size=10, bold=True, color="#4c1d95"))
    frags.append(rect(545, 152, 170, 26, fill="#ffffff", stroke="#7c3aed", sw=1))
    frags.append(text(630, 169, "104  28000  Одеса", size=10, bold=True, color="#4c1d95"))
    frags.append(text(630, 205, "Ключ: колонка 1 (ID)", size=10, color=MUTED))
    frags.append(text(630, 222, "LC_ALL=C порядок", size=10, bold=True, color=POS))

    # Center processing: Two-Pointer Merge
    frags.append(rect(260, 65, 240, 160, fill="#f1f5f9", stroke="#475569", sw=1.5))
    frags.append(text(380, 88, "Двовказівниковий марш", size=12, bold=True, color="#0f172a"))
    frags.append(text(380, 108, "O(N + M) час · O(1) пам'ять", size=10, bold=True, color="#0369a1"))
    frags.append(line(275, 118, 485, 118, color="#cbd5e1", sw=1))
    
    frags.append(text(380, 136, "key1 == key2 ──► Емісія з'єднання", size=9, bold=True, color="#15803d"))
    frags.append(text(380, 154, "key1 < key2  ──► Просунути ptr1", size=9, color="#0f172a"))
    frags.append(text(380, 172, "key1 > key2  ──► Просунути ptr2", size=9, color="#0f172a"))
    frags.append(text(380, 198, "Не потребує завантаження в RAM", size=9, color=MUTED))

    # Arrows into engine
    frags.append(arrow(230, 115, 258, 115, color="#d97706", sw=2))
    frags.append(arrow(530, 115, 502, 115, color="#7c3aed", sw=2))

    # Output sections: Inner, Left Outer, Full Outer
    frags.append(arrow(380, 225, 380, 260, color="#475569", sw=2))

    frags.append(rect(30, 265, 700, 175, fill="#ffffff", stroke="#94a3b8", sw=1.5))
    frags.append(text(45, 288, "Результати різних режимів реляційного з'єднання:", size=12, bold=True, color="#0f172a", anchor="start"))

    # Inner join box
    frags.append(rect(45, 305, 210, 120, fill="#f0fdf4", stroke="#16a34a", sw=1.2))
    frags.append(text(150, 324, "Внутрішнє з'єднання (Inner Join)", size=10, bold=True, color="#15803d"))
    frags.append(text(150, 338, "join file1 file2", size=9, color=MUTED))
    frags.append(line(55, 345, 245, 345, color="#bbf7d0", sw=1))
    frags.append(mtext(55, 362, ["101 Альфа Відділ_А 25000 Київ", "104 Гамма Відділ_В 28000 Одеса"], size=9, bold=True, color="#14532d", anchor="start", lh=1.4))
    frags.append(text(150, 410, "Лише спільні ключі (101, 104)", size=9, color="#15803d"))

    # Left outer join box
    frags.append(rect(275, 305, 210, 120, fill="#eff6ff", stroke="#2563eb", sw=1.2))
    frags.append(text(380, 324, "Ліве зовнішнє (Left Outer)", size=10, bold=True, color="#1d4ed8"))
    frags.append(text(380, 338, "join -a 1 -e 'NULL' -o auto file1 file2", size=9, color=MUTED))
    frags.append(line(285, 345, 475, 345, color="#bfdbfe", sw=1))
    frags.append(mtext(285, 362, ["101 Альфа Відділ_А 25000 Київ", "102 Бета Відділ_Б NULL NULL", "104 Гамма Відділ_В 28000 Одеса"], size=9, bold=True, color="#1e40af", anchor="start", lh=1.4))
    frags.append(text(380, 410, "Збережено ключ 102 з файлу 1", size=9, color="#1d4ed8"))

    # Anti-join box
    frags.append(rect(505, 305, 210, 120, fill="#fff1f2", stroke="#e11d48", sw=1.2))
    frags.append(text(610, 324, "Анти-з'єднання (Unpaired Only)", size=10, bold=True, color="#be123c"))
    frags.append(text(610, 338, "join -v 1 file1 file2", size=9, color=MUTED))
    frags.append(line(515, 345, 705, 345, color="#fecdd3", sw=1))
    frags.append(mtext(515, 372, ["102 Бета Відділ_Б"], size=9, bold=True, color="#9f1239", anchor="start"))
    frags.append(text(610, 410, "Рядки 1-го файлу без пари в 2-му", size=9, color="#be123c"))

    path = os.path.join(img_dir, "join-relational-logic.svg")
    svg_render(path, w, h, *frags)

def render_comm_sets(img_dir):
    w, h = 760, 420
    frags = []

    frags.append(text(w / 2, 25, "Операції над множинами за допомогою утиліти comm", size=15, bold=True))

    # Visual Venn circles
    # Set A circle
    frags.append(circle(220, 125, 80, fill="#fef3c7", stroke="#d97706", sw=2))
    # Set B circle
    frags.append(circle(320, 125, 80, fill="#dbeafe", stroke="#2563eb", sw=2))

    # Overlap visual fix (green overlay)
    frags.append(text(180, 128, "Лише A (Кол 1)", size=11, bold=True, color="#92400e"))
    frags.append(text(270, 128, "Спільні A∩B\n(Кол 3)", size=10, bold=True, color="#15803d"))
    frags.append(text(360, 128, "Лише B (Кол 2)", size=11, bold=True, color="#1d4ed8"))

    # Three standard columns explanation box
    frags.append(rect(450, 48, 280, 155, fill="#f8fafc", stroke="#64748b", sw=1.5))
    frags.append(text(590, 68, "Формат виводу comm fileA fileB", size=11, bold=True, color="#0f172a"))
    frags.append(line(460, 78, 720, 78, color="#cbd5e1", sw=1))
    
    frags.append(text(465, 96, "Колонка 1 (без відступу):", size=10, bold=True, color="#92400e", anchor="start"))
    frags.append(text(475, 110, "Елементи виключно з fileA", size=9, color=MUTED, anchor="start"))
    
    frags.append(text(465, 128, "Колонка 2 (відступ \\t):", size=10, bold=True, color="#1d4ed8", anchor="start"))
    frags.append(text(475, 142, "Елементи виключно з fileB", size=9, color=MUTED, anchor="start"))

    frags.append(text(465, 160, "Колонка 3 (відступ \\t\\t):", size=10, bold=True, color="#15803d", anchor="start"))
    frags.append(text(475, 174, "Спільні елементи для fileA та fileB", size=9, color=MUTED, anchor="start"))

    # Bottom flags mapping matrix
    frags.append(rect(30, 220, 700, 180, fill="#ffffff", stroke="#94a3b8", sw=1.5))
    frags.append(text(45, 242, "Матриця селекції стовпців прапорцями придушення (-1, -2, -3):", size=12, bold=True, color="#0f172a", anchor="start"))

    # Row 1: Intersection
    frags.append(rect(45, 258, 210, 60, fill="#dcfce7", stroke="#16a34a", sw=1.2))
    frags.append(text(150, 276, "Перетин: A ∩ B", size=11, bold=True, color="#15803d"))
    frags.append(text(150, 294, "comm -12 fileA fileB", size=10, bold=True, color="#0f172a"))
    frags.append(text(150, 308, "Придушено кол. 1 та 2", size=9, color=MUTED))

    # Row 2: Relative difference A \ B
    frags.append(rect(275, 258, 210, 60, fill="#fef3c7", stroke="#d97706", sw=1.2))
    frags.append(text(380, 276, "Різниця: A \\ B (тільки в A)", size=11, bold=True, color="#92400e"))
    frags.append(text(380, 294, "comm -23 fileA fileB", size=10, bold=True, color="#0f172a"))
    frags.append(text(380, 308, "Придушено кол. 2 та 3", size=9, color=MUTED))

    # Row 3: Relative difference B \ A
    frags.append(rect(505, 258, 210, 60, fill="#dbeafe", stroke="#2563eb", sw=1.2))
    frags.append(text(610, 276, "Різниця: B \\ A (тільки в B)", size=11, bold=True, color="#1d4ed8"))
    frags.append(text(610, 294, "comm -13 fileA fileB", size=10, bold=True, color="#0f172a"))
    frags.append(text(610, 308, "Придушено кол. 1 та 3", size=9, color=MUTED))

    # Row 4: Symmetric difference A △ B
    frags.append(rect(45, 328, 670, 58, fill="#f5f3ff", stroke="#7c3aed", sw=1.2))
    frags.append(text(180, 350, "Симетрична різниця: A △ B", size=11, bold=True, color="#5b21b6", anchor="start"))
    frags.append(text(180, 368, "comm -3 fileA fileB", size=10, bold=True, color="#0f172a", anchor="start"))
    frags.append(text(460, 350, "Вимикає лише спільні елементи (-3).", size=9, color=MUTED, anchor="start"))
    frags.append(text(460, 368, "Виводить 2 колонки: що зникло та що додалося.", size=9, color=MUTED, anchor="start"))

    path = os.path.join(img_dir, "comm-set-operations.svg")
    svg_render(path, w, h, *frags)

def render_tr_architecture(img_dir):
    w, h = 760, 440
    frags = []

    frags.append(text(w / 2, 25, "Внутрішня архітектура табличної обробки утиліти tr", size=15, bold=True))

    # Stream Input
    frags.append(rect(30, 60, 150, 340, fill="#f8fafc", stroke="#64748b", sw=1.5))
    frags.append(text(105, 85, "Потік stdin", size=12, bold=True, color="#0f172a"))
    frags.append(text(105, 102, "Дескриптор fd 0", size=10, color=MUTED))
    frags.append(line(45, 115, 165, 115, color="#cbd5e1", sw=1))

    frags.append(rect(45, 130, 120, 30, fill="#ffffff", stroke="#94a3b8", sw=1))
    frags.append(text(105, 150, "Байт 0x61 ('a')", size=10, bold=True, color="#0f172a"))
    frags.append(rect(45, 170, 120, 30, fill="#ffffff", stroke="#94a3b8", sw=1))
    frags.append(text(105, 190, "Байт 0x0D ('\\r')", size=10, bold=True, color=POS))
    frags.append(rect(45, 210, 120, 30, fill="#ffffff", stroke="#94a3b8", sw=1))
    frags.append(text(105, 230, "Байт 0x20 (' ')", size=10, bold=True, color="#0f172a"))
    frags.append(rect(45, 250, 120, 30, fill="#ffffff", stroke="#94a3b8", sw=1))
    frags.append(text(105, 270, "Байт 0x20 (' ')", size=10, bold=True, color="#0f172a"))
    frags.append(rect(45, 290, 120, 30, fill="#ffffff", stroke="#94a3b8", sw=1))
    frags.append(text(105, 310, "Байт 0x62 ('b')", size=10, bold=True, color="#0f172a"))
    frags.append(text(105, 360, "Буферизований I/O\n(read / fread)", size=10, color=MUTED))

    # Center Engine: 256-byte Lookup Table
    frags.append(rect(220, 60, 320, 340, fill="#ffffff", stroke="#2563eb", sw=2))
    frags.append(text(380, 85, "Пряма таблиця трансляції [256]", size=13, bold=True, color="#1d4ed8"))
    frags.append(text(380, 102, "unsigned char map[256] · O(1) складність", size=10, bold=True, color="#0369a1"))
    frags.append(line(235, 115, 525, 115, color="#bfdbfe", sw=1))

    # Array cells visualization
    frags.append(rect(240, 130, 280, 32, fill="#f0fdf4", stroke="#16a34a", sw=1))
    frags.append(text(250, 150, "map['a']", size=10, bold=True, color="#15803d", anchor="start"))
    frags.append(text(380, 150, "──► 'A' (0x41)", size=10, bold=True, color="#15803d", anchor="start"))
    frags.append(text(510, 150, "Заміна", size=9, color=MUTED, anchor="end"))

    frags.append(rect(240, 170, 280, 32, fill="#fff1f2", stroke="#e11d48", sw=1))
    frags.append(text(250, 190, "map['\\r']", size=10, bold=True, color="#be123c", anchor="start"))
    frags.append(text(380, 190, "──► SKIP (флаг -d)", size=10, bold=True, color="#be123c", anchor="start"))
    frags.append(text(510, 190, "Видалення", size=9, color=MUTED, anchor="end"))

    frags.append(rect(240, 210, 280, 52, fill="#fef3c7", stroke="#d97706", sw=1))
    frags.append(text(250, 230, "map[' ']", size=10, bold=True, color="#92400e", anchor="start"))
    frags.append(text(380, 230, "──► SQUEEZE (-s)", size=10, bold=True, color="#92400e", anchor="start"))
    frags.append(text(250, 250, "prev_byte == ' ' ? SKIP : EMIT", size=9, color="#78350f", anchor="start"))

    frags.append(rect(240, 270, 280, 32, fill="#f8fafc", stroke="#cbd5e1", sw=1))
    frags.append(text(250, 290, "map['b']", size=10, color=MUTED, anchor="start"))
    frags.append(text(380, 290, "──► 'B' (0x42)", size=10, bold=True, color="#15803d", anchor="start"))

    frags.append(rect(240, 310, 280, 75, fill="#eff6ff", stroke="#93c5fd", sw=1))
    frags.append(text(380, 330, "Гарячий цикл обробки:", size=10, bold=True, color="#1e40af"))
    frags.append(text(380, 348, "out_buf[j++] = map[in_buf[i]];", size=10, bold=True, color="#0f172a"))
    frags.append(text(380, 368, "Без перевірок if/switch на кожен байт", size=9, color=MUTED))

    # Stream Output
    frags.append(rect(580, 60, 150, 340, fill="#f8fafc", stroke="#64748b", sw=1.5))
    frags.append(text(655, 85, "Потік stdout", size=12, bold=True, color="#0f172a"))
    frags.append(text(655, 102, "Дескриптор fd 1", size=10, color=MUTED))
    frags.append(line(595, 115, 715, 115, color="#cbd5e1", sw=1))

    frags.append(rect(595, 130, 120, 30, fill="#dcfce7", stroke="#16a34a", sw=1.5))
    frags.append(text(655, 150, "'A' (0x41)", size=10, bold=True, color="#15803d"))
    
    frags.append(rect(595, 170, 120, 30, fill="#fef3c7", stroke="#d97706", sw=1.5))
    frags.append(text(655, 190, "' ' (1 пробіл)", size=10, bold=True, color="#92400e"))

    frags.append(rect(595, 210, 120, 30, fill="#dcfce7", stroke="#16a34a", sw=1.5))
    frags.append(text(655, 230, "'B' (0x42)", size=10, bold=True, color="#15803d"))

    frags.append(text(655, 320, "Результат: \"A B\"", size=11, bold=True, color="#0f172a"))
    frags.append(text(655, 345, "\\r видалено,", size=9, color=MUTED))
    frags.append(text(655, 360, "пробіли стиснуто,", size=9, color=MUTED))
    frags.append(text(655, 375, "регістр піднято.", size=9, color=MUTED))

    # Arrows
    frags.append(arrow(180, 200, 218, 200, color="#2563eb", sw=2))
    frags.append(arrow(540, 200, 578, 200, color="#16a34a", sw=2))

    path = os.path.join(img_dir, "tr-byte-lookup-table.svg")
    svg_render(path, w, h, *frags)

def render():
    base_dir = os.path.dirname(__file__)
    img_dir = os.path.join(base_dir, 'img')
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
        
    render_cut_paste_ops(img_dir)
    render_join_relational(img_dir)
    render_comm_sets(img_dir)
    render_tr_architecture(img_dir)

if __name__ == '__main__':
    render()
