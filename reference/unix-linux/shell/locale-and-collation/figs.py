import os
import sys

# Add scripts/ to sys.path (4 levels up from topic folder)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import render as svg_render, rect, text, mtext, line, arrow, FILL, INK, LINE, MUTED, POS, NEG, FIELD

def render_hierarchy(img_dir):
    w, h = 680, 420
    frags = []

    frags.append(text(w / 2, 25, "Ієрархія резолюції змінних локалі у POSIX", size=15, bold=True))

    # Level 1: LC_ALL
    frags.append(rect(140, 50, 400, 60, fill="#fee2e2", stroke="#dc2626", sw=1.5))
    frags.append(text(340, 75, "LC_ALL", size=14, color="#991b1b", bold=True))
    frags.append(text(340, 95, "Найвищий пріоритет: перевизначає всі категорії та LANG", size=11, color="#7f1d1d"))

    frags.append(line(340, 110, 340, 135, color=LINE, sw=1.5))
    frags.append(arrow(340, 135, 340, 140, color=LINE, sw=1.5))

    # Level 2: LC_* Specific Categories
    frags.append(rect(140, 140, 400, 75, fill="#e0f2fe", stroke="#0284c7", sw=1.5))
    frags.append(text(340, 162, "Специфічні категорії LC_*", size=14, color="#075985", bold=True))
    frags.append(mtext(340, 183, ["LC_CTYPE, LC_COLLATE, LC_MESSAGES, LC_NUMERIC", "LC_TIME, LC_MONETARY, LC_PAPER, LC_MEASUREMENT"], size=11, color="#0c4a6e"))

    frags.append(line(340, 215, 340, 240, color=LINE, sw=1.5))
    frags.append(arrow(340, 240, 340, 245, color=LINE, sw=1.5))

    # Level 3: LANG
    frags.append(rect(140, 245, 400, 60, fill="#fef3c7", stroke="#d97706", sw=1.5))
    frags.append(text(340, 270, "LANG", size=14, color="#92400e", bold=True))
    frags.append(text(340, 290, "Значення за замовчуванням для всіх невстановлених LC_*", size=11, color="#78350f"))

    frags.append(line(340, 305, 340, 330, color=LINE, sw=1.5))
    frags.append(arrow(340, 330, 340, 335, color=LINE, sw=1.5))

    # Level 4: Fallback C / POSIX
    frags.append(rect(140, 335, 400, 55, fill="#f3f4f6", stroke="#4b5563", sw=1.5))
    frags.append(text(340, 358, "Системний за замовчуванням: C / POSIX", size=14, color="#1f2937", bold=True))
    frags.append(text(340, 378, "7-бітний ASCII, байтове сортування, стандартні повідомлення", size=11, color="#374151"))

    path = os.path.join(img_dir, "locale-hierarchy.svg")
    svg_render(path, w, h, *frags)

def render_collation_levels(img_dir):
    w, h = 700, 430
    frags = []

    frags.append(text(w / 2, 25, "Багаторівневе зіставлення рядків (Collation Weighting)", size=15, bold=True))

    levels = [
        ("1. Первинний вага (Primary)", "#dcfce7", "#16a34a", "#15803d", "Базовий символ / літера (напр. 'a' == 'A' == 'á' ≠ 'b')", "Визначає основний алфавітний порядок слів"),
        ("2. Вторинний вага (Secondary)", "#e0f2fe", "#0284c7", "#0369a1", "Акценти та діакритичні знаки (напр. 'a' ≠ 'á')", "Застосовується при збігу первинних вагових значень"),
        ("3. Третинний вага (Tertiary)", "#fef3c7", "#d97706", "#b45309", "Регістр символів (напр. 'a' ≠ 'A')", "Розрізняє великі та малі літери"),
        ("4. Четвертинний вага (Quaternary)", "#f3e8ff", "#9333ea", "#6b21a8", "Пунктуація та спеціальні символи", "Враховує дефіси, пробіли та розділові знаки"),
        ("5. Байтовий tie-breaker", "#fee2e2", "#dc2626", "#b91c1c", "Двійкове кодування UTF-8 / ASCII (strcmp)", "Забезпечує детермінованість при повній еквівалентності")
    ]

    y_pos = 50
    for title, bg_col, border_col, text_col, desc1, desc2 in levels:
        frags.append(rect(40, y_pos, 620, 62, fill=bg_col, stroke=border_col, sw=1.5))
        frags.append(text(60, y_pos + 22, title, size=13, color=text_col, anchor="start", bold=True))
        frags.append(text(60, y_pos + 42, f"{desc1} — {desc2}", size=11, color=INK, anchor="start"))
        y_pos += 72

    path = os.path.join(img_dir, "collation-levels.svg")
    svg_render(path, w, h, *frags)

def render_data_flow(img_dir):
    w, h = 720, 400
    frags = []

    frags.append(text(w / 2, 25, "Потік обробки локалі у системних утилітах", size=15, bold=True))

    # Box 1: Environment
    frags.append(rect(30, 60, 200, 110, fill="#fef3c7", stroke="#d97706", sw=1.5))
    frags.append(text(130, 85, "Змінні оточення", size=13, color="#92400e", bold=True))
    frags.append(mtext(130, 108, ["LC_ALL=uk_UA.UTF-8", "LC_COLLATE=C", "LANG=en_US.UTF-8"], size=11, color="#78350f"))

    frags.append(line(230, 115, 270, 115, color=LINE, sw=1.5))
    frags.append(arrow(270, 115, 275, 115, color=LINE, sw=1.5))

    # Box 2: libc setlocale
    frags.append(rect(275, 60, 200, 110, fill="#e0f2fe", stroke="#0284c7", sw=1.5))
    frags.append(text(375, 85, "C-бібліотека (libc)", size=13, color="#075985", bold=True))
    frags.append(mtext(375, 108, ["setlocale(LC_ALL, \"\")", "Завантаження таблиць з", "/usr/lib/locale/archive"], size=11, color="#0c4a6e"))

    frags.append(line(475, 115, 515, 115, color=LINE, sw=1.5))
    frags.append(arrow(515, 115, 520, 115, color=LINE, sw=1.5))

    # Box 3: Utility / Runtime
    frags.append(rect(520, 60, 170, 110, fill="#dcfce7", stroke="#16a34a", sw=1.5))
    frags.append(text(605, 85, "Утиліта (sort/grep)", size=13, color="#166534", bold=True))
    frags.append(mtext(605, 108, ["Виклики strcoll()", "або strcmp()", "Розкриття [a-z]"], size=11, color="#14532d"))

    # Bottom comparison table
    frags.append(rect(30, 200, 660, 170, fill="#f9fafb", stroke="#6b7280", sw=1.5))
    frags.append(text(360, 225, "Порівняння режимів обробки під час розбору тексту", size=13, color="#111827", bold=True))

    frags.append(line(40, 238, 680, 238, color="#d1d5db", sw=1))

    frags.append(text(180, 258, "Режим LC_ALL=C", size=12, color="#991b1b", bold=True))
    frags.append(text(520, 258, "Режим UTF-8 (uk_UA.UTF-8 / en_US.UTF-8)", size=12, color="#065f46", bold=True))

    frags.append(line(360, 240, 360, 360, color="#d1d5db", sw=1))

    c_points = [
        "• Швидке порівняння байтів (O(1) / strcmp)",
        "• [a-z] — тільки ASCII від 0x61 до 0x7A",
        "• Висока швидкість sort та grep (SIMD/AVX)"
    ]
    utf_points = [
        "• Багаторівневе зіставлення (O(N) / strcoll)",
        "• [a-z] — мовний порядок зіставлення (collation)",
        "• Враховує абетку, але потребує більше CPU"
    ]

    frags.append(mtext(180, 280, c_points, size=11, color="#374151"))
    frags.append(mtext(520, 280, utf_points, size=11, color="#374151"))

    path = os.path.join(img_dir, "locale-data-flow.svg")
    svg_render(path, w, h, *frags)

def render():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    render_hierarchy(img_dir)
    render_collation_levels(img_dir)
    render_data_flow(img_dir)

if __name__ == "__main__":
    render()
