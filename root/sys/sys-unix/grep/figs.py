import sys
import os

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def build_grep_pipeline_model(path):
    frags = []

    # Outer background
    frags.append(rect(10, 10, 840, 320, fill="#ffffff", stroke="#cfd8dc", sw=1.5, rx=8))
    frags.append(text(430, 35, "Архітектура потокового конвеєра grep: обробка блоків та фільтрація рядків", size=14, color="#263238", bold=True))

    # Stage 1: Input stream
    frags.append(rect(25, 60, 160, 245, fill="#f3e5f5", stroke="#8e24aa", sw=1.5, rx=6))
    frags.append(text(105, 85, "1. Вхідний потік", size=13, color="#4a148c", bold=True))
    frags.append(text(105, 105, "stdin / файл / канал", size=11, color=MUTED))

    frags.append(rect(35, 125, 140, 165, fill="#ffffff", stroke="#ce93d8", rx=4))
    frags.append(text(105, 150, "read(fd, buf, 64KB)", size=11, color="#6a1b9a", bold=True))
    frags.append(text(105, 175, "Блоковий ввід", size=11, color=INK))
    frags.append(text(105, 195, "Неперервний потік", size=11, color=INK))
    frags.append(text(105, 215, "Безструктурні байти", size=11, color=MUTED))
    frags.append(text(105, 245, "Символ \\n ділить", size=11, color=POS, bold=True))
    frags.append(text(105, 265, "потік на записи", size=11, color=POS))

    # Arrow 1 -> 2
    frags.append(arrow(190, 180, 225, 180, color="#8e24aa", sw=2))

    # Stage 2: Buffer & Line splitting
    frags.append(rect(230, 60, 200, 245, fill="#e8eaf6", stroke="#3949ab", sw=1.5, rx=6))
    frags.append(text(330, 85, "2. Зсувний буфер і SIMD", size=13, color="#1a237e", bold=True))
    frags.append(text(330, 105, "Пошук меж рядків", size=11, color=MUTED))

    frags.append(rect(242, 125, 176, 165, fill="#ffffff", stroke="#9fa8da", rx=4))
    frags.append(text(330, 145, "memchr(buf, '\\n', len)", size=11, color="#283593", bold=True))
    frags.append(text(330, 165, "AVX2 / SSE2 вектори", size=11, color="#00695c"))
    frags.append(rect(250, 180, 160, 45, fill="#e8f5e9", stroke="#81c784", rx=3))
    frags.append(text(330, 198, "Рядок k (завершений)", size=10, color="#1b5e20", bold=True))
    frags.append(text(330, 215, "Зсув залишку на початок", size=10, color=MUTED))
    frags.append(text(330, 245, "Zero-copy слайсинг", size=11, color="#d84315", bold=True))
    frags.append(text(330, 265, "Вказівник + довжина", size=11, color=INK))

    # Arrow 2 -> 3
    frags.append(arrow(435, 180, 470, 180, color="#3949ab", sw=2))

    # Stage 3: Matching Engine
    frags.append(rect(475, 60, 180, 245, fill="#fff3e0", stroke="#fb8c00", sw=1.5, rx=6))
    frags.append(text(565, 85, "3. Рушій зіставлення", size=13, color="#e65100", bold=True))
    frags.append(text(565, 105, "Перевірка критерію", size=11, color=MUTED))

    frags.append(rect(487, 125, 156, 165, fill="#ffffff", stroke="#ffcc80", rx=4))
    frags.append(text(565, 145, "Вибір алгоритму:", size=11, color="#bf360c", bold=True))
    frags.append(text(565, 168, "• Boyer-Moore (-F)", size=11, color=INK))
    frags.append(text(565, 188, "• DFA автомат (-E)", size=11, color=INK))
    frags.append(text(565, 208, "• PCRE VM (-P)", size=11, color=INK))
    frags.append(rect(495, 225, 140, 55, fill="#fbe9e7", stroke="#ffab91", rx=3))
    frags.append(text(565, 243, "Результат: Є ЗБІГ?", size=10, color="#c62828", bold=True))
    frags.append(text(565, 263, "Так (0) / Ні (1)", size=10, color=INK))

    # Arrow 3 -> 4
    frags.append(arrow(660, 180, 695, 180, color="#fb8c00", sw=2))

    # Stage 4: Output & Exit code
    frags.append(rect(700, 60, 140, 245, fill="#e8f5e9", stroke="#43a047", sw=1.5, rx=6))
    frags.append(text(770, 85, "4. Вивід", size=13, color="#1b5e20", bold=True))
    frags.append(text(770, 105, "stdout / статус", size=11, color=MUTED))

    frags.append(rect(710, 125, 120, 165, fill="#ffffff", stroke="#a5d6a7", rx=4))
    frags.append(text(770, 145, "Фільтрація:", size=11, color="#2e7d32", bold=True))
    frags.append(text(770, 168, "• Рядок цілком", size=10, color=INK))
    frags.append(text(770, 188, "• Тільки збіг (-o)", size=10, color=INK))
    frags.append(text(770, 208, "• Інверсія (-v)", size=10, color=INK))
    frags.append(text(770, 228, "• Контекст (-C)", size=10, color=INK))
    frags.append(text(770, 255, "exit(0) / exit(1)", size=11, color="#1b5e20", bold=True))
    frags.append(text(770, 273, "Код статусу", size=10, color=MUTED))

    render(path, 860, 340, *frags)

def build_grep_regex_dialects(path):
    frags = []

    frags.append(rect(10, 10, 840, 360, fill="#ffffff", stroke="#cfd8dc", sw=1.5, rx=8))
    frags.append(text(430, 35, "Ієрархія діалектів регулярних виразів та рушіїв у grep", size=14, color="#263238", bold=True))

    dialects = [
        {
            "x": 25, "w": 190, "title": "grep -F (Fixed)", "sub": "Без регулярних виразів",
            "bg": "#e0f2f1", "border": "#00897b", "title_col": "#004d40",
            "algo": "Boyer-Moore / Aho-Corasick", "comp": "O(N/M) сублінійний",
            "syntax": "Точні рядки (літерали)",
            "details": ["Немає метасимволів", "Спецсимволи як байти", "Швидкий пошук слів", "Низькі накладні витрати"]
        },
        {
            "x": 230, "w": 190, "title": "grep -G (BRE)", "sub": "Базові вирази (POSIX)",
            "bg": "#f9fbe7", "border": "#9e9d24", "title_col": "#827717",
            "algo": "DFA / NFA автомат", "comp": "O(N) лінійний час",
            "syntax": "\\( \\)  \\{m,n\\}  \\1  .",
            "details": ["Дужки экрануються", "Квантифікатори з \\", "+ та ? є літералами", "Історична сумісність"]
        },
        {
            "x": 435, "w": 190, "title": "grep -E (ERE)", "sub": "Розширені вирази (POSIX)",
            "bg": "#e3f2fd", "border": "#1e88e5", "title_col": "#0d47a1",
            "algo": "DFA автомат (детерм.)", "comp": "O(N) гарантований",
            "syntax": "( )  {m,n}  +  ?  |",
            "details": ["Оператори без слешів", "Альтернатива a|b", "Один або більше +", "Передбачуваний час"]
        },
        {
            "x": 640, "w": 190, "title": "grep -P (PCRE)", "sub": "Perl-сумісні вирази",
            "bg": "#fce4ec", "border": "#d81b60", "title_col": "#880e4f",
            "algo": "Backtracking VM", "comp": "O(2^N) найгірший час",
            "syntax": "(?=...)  (?<=...)  \\d  \\s",
            "details": ["Lookaround перевірки", "Нежадібні квантифікатори", "Зворотні посилання", "Ризик ReDoS зависань"]
        }
    ]

    for d in dialects:
        frags.append(rect(d["x"], 60, d["w"], 290, fill=d["bg"], stroke=d["border"], sw=1.5, rx=6))
        frags.append(text(d["x"] + d["w"]/2, 85, d["title"], size=13, color=d["title_col"], bold=True))
        frags.append(text(d["x"] + d["w"]/2, 105, d["sub"], size=10, color=MUTED))

        # Inner card 1: Algorithm & complexity
        frags.append(rect(d["x"] + 10, 120, d["w"] - 20, 55, fill="#ffffff", stroke=d["border"], rx=4))
        frags.append(text(d["x"] + d["w"]/2, 138, d["algo"], size=10, color=d["title_col"], bold=True))
        frags.append(text(d["x"] + d["w"]/2, 158, "Час: " + d["comp"], size=10, color=POS if "2^N" in d["comp"] else FIELD, bold=True))

        # Inner card 2: Syntax
        frags.append(rect(d["x"] + 10, 185, d["w"] - 20, 45, fill="#ffffff", stroke="#b0bec5", rx=4))
        frags.append(text(d["x"] + d["w"]/2, 202, "Ключовий синтаксис:", size=9, color=MUTED))
        frags.append(text(d["x"] + d["w"]/2, 220, d["syntax"], size=10, color=INK, bold=True))

        # Inner card 3: Bullet points
        frags.append(rect(d["x"] + 10, 240, d["w"] - 20, 95, fill="#ffffff", stroke="#cfd8dc", rx=4))
        for idx, item in enumerate(d["details"]):
            frags.append(text(d["x"] + 18, 258 + idx * 20, "• " + item, size=9, color=INK, anchor="start"))

    render(path, 860, 380, *frags)

def build_grep_boyer_moore_stream(path):
    frags = []

    frags.append(rect(10, 10, 840, 360, fill="#ffffff", stroke="#cfd8dc", sw=1.5, rx=8))
    frags.append(text(430, 35, "Оптимізація пошуку в grep -F: алгоритм Боєра-Мура-Горспула", size=14, color="#263238", bold=True))

    frags.append(text(120, 75, "Вхідний текст у буфері:", size=12, color=INK, bold=True, anchor="start"))

    text_chars = ["E", "R", "R", "O", "R", ":", " ", "D", "I", "S", "K", "_", "F", "A", "I", "L", "U", "R", "E", " ", "O", "C", "C", "U", "R", "R", "E", "D"]
    cell_w = 26
    start_x = 40
    start_y = 90

    for i, ch in enumerate(text_chars):
        x = start_x + i * cell_w
        is_match = (i >= 7 and i <= 14)
        bg_col = "#c8e6c9" if is_match else "#f5f5f5"
        border_col = "#43a047" if is_match else "#bdbdbd"
        frags.append(rect(x, start_y, cell_w - 2, 32, fill=bg_col, stroke=border_col, rx=3))
        frags.append(text(x + cell_w/2 - 1, start_y + 21, ch, size=11, color=INK, bold=True))
        frags.append(text(x + cell_w/2 - 1, start_y + 45, str(i), size=9, color=MUTED))

    # Step 1: Mismatch & Skip (Left Card)
    frags.append(rect(40, 155, 380, 190, fill="#fff3e0", stroke="#ff9800", sw=1.5, rx=6))
    frags.append(text(230, 178, "Крок 1: Порівняння з правого краю шаблону", size=12, color="#e65100", bold=True))

    pattern_1 = ["D", "I", "S", "K", "_", "F", "A", "I"]
    for i, ch in enumerate(pattern_1):
        px = 55 + i * 42
        is_last = (i == len(pattern_1) - 1)
        bg_p = "#ffcdd2" if is_last else "#ffffff"
        bd_p = "#e53935" if is_last else "#ffb74d"
        frags.append(rect(px, 195, 38, 28, fill=bg_p, stroke=bd_p, rx=3))
        frags.append(text(px + 19, 214, ch, size=11, color=INK, bold=True))

    frags.append(text(230, 248, "Текст[7] ('D') ≠ Шаблон[7] ('I')", size=10, color=POS, bold=True))
    frags.append(text(230, 268, "Символ 'D' знаходиться в шаблоні на поз. 0", size=10, color=INK))
    frags.append(text(230, 288, "Зсув (Bad Character) = 8 - 1 - 0 = 7 позицій", size=10, color="#b71c1c", bold=True))
    frags.append(text(230, 318, "Пропускаємо 7 байтів без їх читання!", size=11, color=FIELD, bold=True))

    # Step 2: Alignment after shift (Right Card)
    frags.append(rect(440, 155, 380, 190, fill="#e8f5e9", stroke="#4caf50", sw=1.5, rx=6))
    frags.append(text(630, 178, "Крок 2: Зсув на 7 і повний збіг рядка", size=12, color="#1b5e20", bold=True))

    for i, ch in enumerate(pattern_1):
        px = 455 + i * 42
        frags.append(rect(px, 195, 38, 28, fill="#c8e6c9", stroke="#2e7d32", rx=3))
        frags.append(text(px + 19, 214, ch, size=11, color="#1b5e20", bold=True))

    frags.append(text(630, 248, "Порівняння праворуч-наліво: 'I'=='I', 'A'=='A'...", size=10, color="#1b5e20", bold=True))
    frags.append(text(630, 268, "Усі 8 символів співпали з позиції 7 по 14", size=10, color=INK))
    frags.append(text(630, 288, "Рядок позначено як збіг -> вивід у stdout", size=10, color=FIELD, bold=True))
    frags.append(text(630, 318, "Ефективність: перевірено лише 9 байтів із 15", size=11, color="#0d47a1", bold=True))

    render(path, 860, 380, *frags)

def build_grep_symlinks_traversal(path):
    frags = []

    frags.append(rect(10, 10, 840, 360, fill="#ffffff", stroke="#cfd8dc", sw=1.5, rx=8))
    frags.append(text(430, 35, "Рекурсивний обхід дерева каталогів: фізичний (-r) проти логічного (-R)", size=14, color="#263238", bold=True))

    # Left: grep -r (Physical traversal)
    frags.append(rect(25, 60, 390, 285, fill="#f5f5f5", stroke="#78909c", sw=1.5, rx=6))
    frags.append(text(220, 85, "grep -r (Фізичний обхід, --no-dereference)", size=13, color="#37474f", bold=True))
    frags.append(text(220, 105, "Не переходить за символічними посиланнями", size=11, color=MUTED))

    frags.append(rect(45, 125, 150, 40, fill="#bbdefb", stroke="#1976d2", rx=4))
    frags.append(text(120, 150, "Каталог: /var/log", size=11, color="#0d47a1", bold=True))

    frags.append(line(120, 165, 85, 195, color="#78909c", sw=1.5))
    frags.append(line(120, 165, 155, 195, color="#78909c", sw=1.5))

    frags.append(rect(45, 195, 80, 35, fill="#c8e6c9", stroke="#388e3c", rx=3))
    frags.append(text(85, 217, "app.log", size=10, color="#1b5e20", bold=True))

    frags.append(rect(135, 195, 95, 35, fill="#ffecb3", stroke="#ffa000", rx=3))
    frags.append(text(182, 217, "link -> /opt", size=10, color="#e65100", bold=True))

    frags.append(rect(245, 125, 155, 105, fill="#ffffff", stroke="#b0bec5", rx=4))
    frags.append(text(322, 145, "Поведінка -r:", size=11, color=INK, bold=True))
    frags.append(text(322, 168, "• app.log: ЧИТАЄТЬСЯ", size=10, color=FIELD, bold=True))
    frags.append(text(322, 188, "• link: ІГНОРУЄТЬСЯ", size=10, color=POS, bold=True))
    frags.append(text(322, 208, "• /opt: НЕ ОБХОДИТЬСЯ", size=10, color=MUTED))

    frags.append(rect(45, 245, 355, 85, fill="#e8f5e9", stroke="#81c784", rx=4))
    frags.append(text(222, 265, "Безпека та гарантії:", size=11, color="#2e7d32", bold=True))
    frags.append(text(222, 285, "Неможливо потрапити в нескінченний цикл", size=10, color=INK))
    frags.append(text(222, 305, "Сканування суворо обмежене поточною файловою системою", size=10, color=INK))

    # Right: grep -R (Logical traversal)
    frags.append(rect(435, 60, 390, 285, fill="#fff8e1", stroke="#ffa000", sw=1.5, rx=6))
    frags.append(text(630, 85, "grep -R (Логічний обхід, --dereference)", size=13, color="#e65100", bold=True))
    frags.append(text(630, 105, "Розкриває та переходить за симлінками", size=11, color=MUTED))

    frags.append(rect(455, 125, 150, 40, fill="#bbdefb", stroke="#1976d2", rx=4))
    frags.append(text(530, 150, "Каталог: /var/log", size=11, color="#0d47a1", bold=True))

    frags.append(line(530, 165, 495, 195, color="#ffa000", sw=1.5))
    frags.append(line(530, 165, 565, 195, color="#ffa000", sw=1.5))

    frags.append(rect(455, 195, 80, 35, fill="#c8e6c9", stroke="#388e3c", rx=3))
    frags.append(text(495, 217, "app.log", size=10, color="#1b5e20", bold=True))

    frags.append(rect(545, 195, 95, 35, fill="#ffecb3", stroke="#ffa000", rx=3))
    frags.append(text(592, 217, "link -> /opt", size=10, color="#e65100", bold=True))

    # Arrow from link to /opt
    frags.append(arrow(645, 212, 675, 150, color="#e65100", sw=1.8))

    frags.append(rect(675, 125, 135, 75, fill="#fbe9e7", stroke="#ff7043", rx=4))
    frags.append(text(742, 145, "Каталог: /opt", size=11, color="#bf360c", bold=True))
    frags.append(text(742, 165, "link_back -> /var", size=10, color=POS, bold=True))
    frags.append(text(742, 185, "Ризик циклу!", size=10, color=POS, bold=True))

    frags.append(rect(455, 245, 355, 85, fill="#ffffff", stroke="#ffb74d", rx=4))
    frags.append(text(632, 265, "Механізм захисту від зациклення:", size=11, color="#bf360c", bold=True))
    frags.append(text(632, 285, "Відстеження хеш-таблиці пар (st_dev, st_ino)", size=10, color=INK))
    frags.append(text(632, 305, "Повторно зустрінутий inode каталогу пропускається", size=10, color=FIELD, bold=True))

    render(path, 860, 380, *frags)

if __name__ == "__main__":
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)

    build_grep_pipeline_model(os.path.join(img_dir, "grep-pipeline-model.svg"))
    build_grep_regex_dialects(os.path.join(img_dir, "grep-regex-dialects.svg"))
    build_grep_boyer_moore_stream(os.path.join(img_dir, "grep-boyer-moore-stream.svg"))
    build_grep_symlinks_traversal(os.path.join(img_dir, "grep-symlinks-traversal.svg"))
    print("All figures successfully generated in", img_dir)
