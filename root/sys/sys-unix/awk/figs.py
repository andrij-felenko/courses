import sys
import os

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def build_awk_execution_model(path):
    frags = []
    
    # Background Canvas / Container
    frags.append(rect(15, 15, 770, 370, fill="#ffffff", stroke="#cfd8dc", sw=1.5, rx=8))
    frags.append(text(400, 42, "Трифазний життєвий цикл програми AWK", size=15, color="#263238", bold=True))

    # Phase 1: BEGIN
    frags.append(rect(35, 65, 210, 290, fill="#e8f5e9", stroke="#2e7d32", sw=1.8, rx=6))
    frags.append(text(140, 95, "1. Фаза ініціалізації", size=13, color="#1b5e20", bold=True))
    frags.append(text(140, 115, "BEGIN { ... }", size=13, color="#2e7d32", bold=True))
    
    frags.append(rect(45, 135, 190, 205, fill="#ffffff", stroke="#a5d6a7", rx=4))
    frags.append(text(140, 160, "Виконується ОДИН раз", size=11, color="#2e7d32", bold=True))
    frags.append(text(140, 185, "• До відкриття вхідних файлів", size=10, color=INK))
    frags.append(text(140, 210, "• Встановлення FS, RS, OFS", size=10, color=INK))
    frags.append(text(140, 235, "• Друк заголовків звітів", size=10, color=INK))
    frags.append(text(140, 260, "• Ініціалізація лічильників", size=10, color=INK))
    frags.append(text(140, 285, "• Обробка параметрів -v", size=10, color=INK))
    frags.append(text(140, 315, "Вхідний потік ще не читається", size=10, color=MUTED, italic=True))

    # Arrow 1 -> 2
    frags.append(arrow(245, 210, 275, 210, color="#2e7d32", sw=2))

    # Phase 2: Main Loop (Pattern { Action })
    frags.append(rect(280, 65, 240, 290, fill="#e3f2fd", stroke="#1565c0", sw=1.8, rx=6))
    frags.append(text(400, 95, "2. Головний цикл обробки", size=13, color="#0d47a1", bold=True))
    frags.append(text(400, 115, "pattern { action }", size=13, color="#1565c0", bold=True))

    frags.append(rect(290, 135, 220, 205, fill="#ffffff", stroke="#90caf9", rx=4))
    frags.append(text(400, 155, "Автоматичний цикл по записах:", size=11, color="#1565c0", bold=True))
    frags.append(text(400, 178, "1. Читання запису за RS → $0", size=10, color=INK))
    frags.append(text(400, 200, "2. Оновлення NR++, FNR++", size=10, color=INK))
    frags.append(text(400, 222, "3. Розбиття $0 за FS → $1..$NF", size=10, color=INK))
    frags.append(text(400, 244, "4. Перевірка шаблонів (pattern)", size=10, color=INK))
    frags.append(text(400, 266, "5. Виконання блоків дій { action }", size=10, color=INK))
    frags.append(text(400, 288, "6. Перехід до наступного запису", size=10, color=INK))
    frags.append(text(400, 315, "Повторюється для кожного $0", size=10, color=MUTED, italic=True))

    # Arrow 2 -> 3
    frags.append(arrow(520, 210, 550, 210, color="#1565c0", sw=2))

    # Phase 3: END
    frags.append(rect(555, 65, 210, 290, fill="#fff3e0", stroke="#e65100", sw=1.8, rx=6))
    frags.append(text(660, 95, "3. Фаза завершення", size=13, color="#bf360c", bold=True))
    frags.append(text(660, 115, "END { ... }", size=13, color="#e65100", bold=True))

    frags.append(rect(565, 135, 190, 205, fill="#ffffff", stroke="#ffcc80", rx=4))
    frags.append(text(660, 160, "Виконується ОДИН раз", size=11, color="#e65100", bold=True))
    frags.append(text(660, 185, "• Після отримання EOF", size=10, color=INK))
    frags.append(text(660, 210, "• Обхід масивів for (k in a)", size=10, color=INK))
    frags.append(text(660, 235, "• Агрегація середніх / сум", size=10, color=INK))
    frags.append(text(660, 260, "• Друк підсумкових таблиць", size=10, color=INK))
    frags.append(text(660, 285, "• Форматований вивід printf", size=10, color=INK))
    frags.append(text(660, 315, "Всі файли вже оброблено", size=10, color=MUTED, italic=True))

    render(path, 800, 400, *frags)

def build_awk_record_field_model(path):
    frags = []
    
    # Outer box
    frags.append(rect(15, 15, 770, 370, fill="#ffffff", stroke="#cfd8dc", sw=1.5, rx=8))
    frags.append(text(400, 42, "Модель декомпозиції даних: потік байтів → записи → поля", size=15, color="#263238", bold=True))

    # Level 1: Raw Byte Stream
    frags.append(rect(35, 65, 730, 50, fill="#f5f5f5", stroke="#9e9e9e", rx=5))
    frags.append(text(120, 95, "Вхідний потік байтів:", size=12, color=INK, bold=True))
    frags.append(text(450, 95, "user1 10.0.0.1 200\\nuser2 10.0.0.2 404\\nuser3 10.0.0.1 500\\n", size=12, color="#37474f"))

    # Separator RS arrow
    frags.append(arrow(400, 115, 400, 145, color="#d32f2f", sw=2))
    frags.append(text(540, 133, "Роздільник записів RS (за замовчуванням '\\n')", size=11, color="#d32f2f", bold=True))

    # Level 2: Records ($0)
    frags.append(rect(35, 150, 730, 75, fill="#fff8e1", stroke="#ffa000", sw=1.5, rx=6))
    frags.append(text(150, 175, "Поточний запис $0 (Record):", size=12, color="#e65100", bold=True))
    frags.append(text(520, 175, "\"user2    10.0.0.2    404\"", size=13, color="#bf360c", bold=True))
    frags.append(text(150, 205, "Лічильники записів:", size=11, color=MUTED))
    frags.append(text(330, 205, "NR = 2 (глобальний)", size=11, color="#e65100", bold=True))
    frags.append(text(530, 205, "FNR = 2 (у поточному файлі)", size=11, color="#e65100", bold=True))

    # Separator FS arrow
    frags.append(arrow(400, 225, 400, 255, color="#1976d2", sw=2))
    frags.append(text(540, 243, "Роздільник полів FS (за замовчуванням [ \\t]+)", size=11, color="#1976d2", bold=True))

    # Level 3: Fields ($1..$NF)
    frags.append(rect(35, 260, 730, 105, fill="#e8eaf6", stroke="#3f51b5", sw=1.5, rx=6))
    frags.append(text(120, 285, "Поля (Fields):", size=12, color="#1a237e", bold=True))
    frags.append(text(350, 285, "NF = 3 (кількість полів у поточному записі)", size=11, color="#283593", bold=True))

    # Field boxes
    f1, _, _ = textbox(130, 325, "$1\n\"user2\"", size=12, fill="#ffffff", stroke="#3f51b5", bold=True)
    frags.append(f1)
    f2, _, _ = textbox(300, 325, "$2\n\"10.0.0.2\"", size=12, fill="#ffffff", stroke="#3f51b5", bold=True)
    frags.append(f2)
    f3, _, _ = textbox(470, 325, "$3\n\"404\"", size=12, fill="#ffffff", stroke="#3f51b5", bold=True)
    frags.append(f3)
    fnf, _, _ = textbox(650, 325, "$NF (тотожно $3)\n\"404\"", size=11, fill="#e1f5fe", stroke="#0288d1", bold=True)
    frags.append(fnf)

    render(path, 800, 400, *frags)

def build_awk_associative_arrays(path):
    frags = []
    
    # Outer box
    frags.append(rect(15, 15, 770, 380, fill="#ffffff", stroke="#cfd8dc", sw=1.5, rx=8))
    frags.append(text(400, 42, "Внутрішня організація асоціативних масивів у AWK", size=15, color="#263238", bold=True))

    # Left box: String Keys and Value storage
    frags.append(rect(35, 65, 345, 305, fill="#fafafa", stroke="#78909c", sw=1.5, rx=6))
    frags.append(text(207, 92, "Одновимірні ключі (рядкові хеш-таблиці)", size=12, color="#37474f", bold=True))

    # Key Value table
    keys = ["\"GET\"", "\"POST\"", "\"DELETE\"", "\"192.168.1.1\""]
    vals = ["4521 (число)", "819 (число)", "12 (число)", "\"blocked\" (рядок)"]
    for i in range(4):
        y = 120 + i * 42
        frags.append(rect(50, y, 140, 32, fill="#e0f2f1", stroke="#00897b", rx=3))
        frags.append(text(120, y + 20, keys[i], size=11, color="#004d40", bold=True))
        
        frags.append(arrow(190, y + 16, 215, y + 16, color="#00897b", sw=1.5))
        
        frags.append(rect(220, y, 145, 32, fill="#ffffff", stroke="#80cbc4", rx=3))
        frags.append(text(292, y + 20, vals[i], size=10, color=INK))

    frags.append(rect(50, 295, 315, 60, fill="#fff3e0", stroke="#ffb74d", rx=4))
    frags.append(text(207, 317, "Перевірка наявності ключа:", size=11, color="#e65100", bold=True))
    frags.append(text(207, 337, "if (\"GET\" in count)  — без створення нового елемента", size=10, color="#bf360c"))

    # Right box: Multidimensional indexing & SUBSEP
    frags.append(rect(400, 65, 365, 305, fill="#f3e5f5", stroke="#8e24aa", sw=1.5, rx=6))
    frags.append(text(582, 92, "Багатовимірні індекси та конкатенація SUBSEP", size=12, color="#4a148c", bold=True))

    frags.append(rect(415, 115, 335, 75, fill="#ffffff", stroke="#ce93d8", rx=4))
    frags.append(text(582, 137, "Синтаксис AWK: matrix[user, ip] += bytes", size=11, color="#6a1b9a", bold=True))
    frags.append(text(582, 160, "user = \"alice\", ip = \"10.0.0.5\"", size=10, color=MUTED))
    frags.append(text(582, 178, "SUBSEP = \"\\034\" (ASCII 28 Field Separator)", size=10, color="#c2185b", bold=True))

    frags.append(arrow(582, 190, 582, 215, color="#8e24aa", sw=1.8))

    frags.append(rect(415, 220, 335, 60, fill="#ede7f6", stroke="#7e57c2", rx=4))
    frags.append(text(582, 242, "Реальний ключ у пам'яті:", size=11, color="#4527a0", bold=True))
    frags.append(text(582, 263, "\"alice\\03410.0.0.5\"", size=12, color="#311b92", bold=True))

    frags.append(rect(415, 295, 335, 60, fill="#ffffff", stroke="#ab47bc", rx=4))
    frags.append(text(582, 317, "Ітерація: for (combined in matrix)", size=11, color="#6a1b9a", bold=True))
    frags.append(text(582, 337, "split(combined, parts, SUBSEP) → parts[1], parts[2]", size=10, color=INK))

    render(path, 800, 410, *frags)

def render_all():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)

    build_awk_execution_model(os.path.join(img_dir, 'awk-execution-model.svg'))
    build_awk_record_field_model(os.path.join(img_dir, 'awk-record-field-model.svg'))
    build_awk_associative_arrays(os.path.join(img_dir, 'awk-associative-arrays.svg'))

if __name__ == '__main__':
    render_all()
