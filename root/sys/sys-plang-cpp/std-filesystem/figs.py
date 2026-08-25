# -*- coding: utf-8 -*-
"""Фігури до теми «std::filesystem: кросплатформова файлова система, шляхи та системні виклики»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Архітектурний макет модуля std::filesystem ──────────────────────────────
def fig_fs_architecture_and_types():
    W, H = 940, 520
    f = []

    f.append(text(470, 35, "Архітектура та компоненти std::filesystem (C++17)", size=16, color=INK, anchor="middle", bold=True))

    # Рівень 1: Абстракції C++
    f.append(text(50, 70, "Рівень абстракцій C++ (High-Level C++ Abstractions)", size=13, color=FIELD, anchor="start", bold=True))
    
    f.append(fitbox(50, 90, 200, 110, "std::filesystem::path\n• Кросплатформовий шлях\n• Синтаксичний розбір\n• Кодування char/wchar_t\n• preferred_separator", size=11, fill="#e8f6ee", stroke=FIELD))
    f.append(fitbox(270, 90, 200, 110, "std::filesystem::directory_entry\n• Кешований елемент каталогу\n• status() / symlink_status()\n• file_size() / last_write_time()\n• Мінімізація syscalls", size=11, fill="#e8f6ee", stroke=FIELD))
    f.append(fitbox(490, 90, 200, 110, "Спеціальні типи даних\n• file_status (file_type, perms)\n• space_info (capacity, free, avail)\n• file_time_type (std::chrono)\n• copy_options / perm_options", size=11, fill="#e8f6ee", stroke=FIELD))
    f.append(fitbox(710, 90, 180, 110, "Ітератори дерева\n• directory_iterator\n• recursive_directory_iterator\n• directory_options", size=11, fill="#e8f6ee", stroke=FIELD))

    # Рівень 2: Операції та обробка помилок
    f.append(text(50, 230, "Рівень операцій та двокамерна обробка помилок", size=13, color=INK, anchor="start", bold=True))
    
    f.append(fitbox(50, 250, 420, 100, "Вільні операційні функції (fs::copy, fs::remove_all, fs::create_directories, ...)\n\n[ Шлях із винятками ]                 [ Шлях із кодами помилок ]\nfs::exists(p) ──> throws std::filesystem_error   fs::exists(p, ec) ──> ec.clear() / ec.assign()", size=11, fill="#eef2f7", stroke=LINE))
    
    f.append(fitbox(490, 250, 400, 100, "Правила обробки TOCTOU та симпосилань\n• symlink_status() проти status()\n• canonical() проти weakly_canonical()\n• skip_permission_denied прапорці", size=11, fill="#fff7e6", stroke=POS))

    # Розділювальна лінія
    f.append(line(40, 375, 900, 375, color=MUTED, sw=1, dash="6 5"))

    # Рівень 3: ОС абстракція та Системні виклики
    f.append(text(50, 400, "Низькорівневий шар операційної системи (VFS / Native OS APIs)", size=13, color=NEG, anchor="start", bold=True))

    f.append(fitbox(50, 420, 410, 75, "POSIX Systems (Linux / macOS / BSD)\n• syscalls: stat(), lstat(), openat(), readdir_r()\n• UTF-8 шляхи (std::string / char*)\n• / ідентифікатор розділювача", size=11, fill="#f4f6f8", stroke=LINE))

    f.append(fitbox(480, 420, 410, 75, "Windows Systems (Win32 / NTFS)\n• APIs: GetFileAttributesExW, FindFirstFileW\n• UTF-16 шляхи (std::wstring / wchar_t*)\n• \\ та / розділювачі, букви дисків (C:)", size=11, fill="#f4f6f8", stroke=LINE))

    render(os.path.join(OUT, 'fs-architecture-and-types.svg'), W, H, *f,
           title="Архітектурний макет модуля std::filesystem")


# ── 2. Декомпозиція шляху в std::filesystem::path ──────────────────────────────
def fig_path_decomposition_model():
    W, H = 940, 460
    f = []

    f.append(text(470, 35, "Компоненти синтаксичного розбору std::filesystem::path", size=16, color=INK, anchor="middle", bold=True))

    # Приклад 1: POSIX Absolute Path
    f.append(text(50, 70, "Приклад 1: Абсолютний шлях POSIX: /usr/local/bin/app.tar.gz", size=13, color=FIELD, anchor="start", bold=True))
    
    # Контейнери елементів шляху
    f.append(fitbox(50, 95, 60, 45, "/", size=12, fill="#e8f6ee", stroke=FIELD))
    f.append(fitbox(115, 95, 80, 45, "usr", size=12, fill="#eef2f7", stroke=LINE))
    f.append(fitbox(200, 95, 90, 45, "local", size=12, fill="#eef2f7", stroke=LINE))
    f.append(fitbox(295, 95, 75, 45, "bin", size=12, fill="#eef2f7", stroke=LINE))
    f.append(fitbox(375, 95, 175, 45, "app.tar.gz", size=12, fill="#fff7e6", stroke=POS))

    # Описи методів декомпозиції
    f.append(text(50, 160, "• root_name(): \"\"", size=11, color=MUTED, anchor="start"))
    f.append(text(200, 160, "• root_directory(): \"/\"", size=11, color=MUTED, anchor="start"))
    f.append(text(380, 160, "• root_path(): \"/\"", size=11, color=MUTED, anchor="start"))
    
    f.append(text(50, 185, "• parent_path(): \"/usr/local/bin\"", size=11, color=MUTED, anchor="start"))
    f.append(text(380, 185, "• filename(): \"app.tar.gz\"", size=11, color=FIELD, anchor="start", bold=True))

    f.append(text(50, 210, "• stem(): \"app.tar\"", size=11, color=MUTED, anchor="start"))
    f.append(text(380, 210, "• extension(): \".gz\"", size=11, color=POS, anchor="start", bold=True))

    # Розділювач
    f.append(line(40, 235, 900, 235, color=MUTED, sw=1, dash="6 5"))

    # Приклад 2: Windows Absolute Path
    f.append(text(50, 260, "Приклад 2: Абсолютний шлях Windows: C:\\Program Files\\App\\data.db", size=13, color=NEG, anchor="start", bold=True))

    f.append(fitbox(50, 285, 75, 45, "C:", size=12, fill="#e8f6ee", stroke=FIELD))
    f.append(fitbox(130, 285, 45, 45, "\\", size=12, fill="#e8f6ee", stroke=FIELD))
    f.append(fitbox(180, 285, 150, 45, "Program Files", size=12, fill="#eef2f7", stroke=LINE))
    f.append(fitbox(335, 285, 80, 45, "App", size=12, fill="#eef2f7", stroke=LINE))
    f.append(fitbox(420, 285, 130, 45, "data.db", size=12, fill="#fff7e6", stroke=POS))

    f.append(text(50, 350, "• root_name(): \"C:\"", size=11, color=FIELD, anchor="start", bold=True))
    f.append(text(220, 350, "• root_directory(): \"\\\"", size=11, color=MUTED, anchor="start"))
    f.append(text(410, 350, "• root_path(): \"C:\\\"", size=11, color=MUTED, anchor="start"))

    f.append(text(50, 375, "• parent_path(): \"C:\\Program Files\\App\"", size=11, color=MUTED, anchor="start"))
    f.append(text(410, 375, "• filename(): \"data.db\"", size=11, color=FIELD, anchor="start", bold=True))

    f.append(text(50, 400, "• stem(): \"data\"", size=11, color=MUTED, anchor="start"))
    f.append(text(410, 400, "• extension(): \".db\"", size=11, color=POS, anchor="start", bold=True))

    f.append(text(470, 435, "std::filesystem::path розбирає рядки синтаксично без викликів до діючої файлової системи", size=11, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, 'path-decomposition-model.svg'), W, H, *f,
           title="Декомпозиція шляху в std::filesystem::path")


# ── 3. Порівняння directory_iterator та recursive_directory_iterator ──────────
def fig_traversal_iterators_comparison():
    W, H = 940, 480
    f = []

    f.append(text(470, 35, "Моделі обходу дерев каталогів: Однорівнева vs Рекурсивна", size=16, color=INK, anchor="middle", bold=True))

    # Ліва колонка: directory_iterator
    f.append(text(50, 70, "std::filesystem::directory_iterator", size=14, color=FIELD, anchor="start", bold=True))
    f.append(fitbox(50, 95, 400, 330,
                    "Сканування тільки поточного рівня (Shallow Traversal)\n\n"
                    "root_dir/\n"
                    "  ├── file1.txt       [ Прочитано ]\n"
                    "  ├── sub_dir/        [ Прочитано лише запис про підкаталог ]\n"
                    "  │     ├── sub1.cpp  [ Ігнорується / Не заходимо ]\n"
                    "  │     └── sub2.h    [ Ігнорується / Не заходимо ]\n"
                    "  └── file2.bin       [ Прочитано ]\n\n"
                    "Особливості:\n"
                    "• Одиничний виклик opendir / readdir у системному дескрипторі\n"
                    "• Мінімальний стек пам'яті O(1)\n"
                    "• Ітератор звертається до directory_entry", size=11, fill="#e8f6ee", stroke=FIELD))

    # Права колонка: recursive_directory_iterator
    f.append(text(490, 70, "std::filesystem::recursive_directory_iterator", size=14, color=POS, anchor="start", bold=True))
    f.append(fitbox(490, 95, 400, 330,
                    "Рекурсивний обхід вглиб (DFS Depth-First Traversal)\n\n"
                    "root_dir/\n"
                    "  ├── file1.txt       [ 1. Зайти ]\n"
                    "  ├── sub_dir/        [ 2. Зайти рекурсивно ]\n"
                    "  │     ├── sub1.cpp  [ 3. Обробити ]\n"
                    "  │     └── sub2.h    [ 4. Обробити ]\n"
                    "  └── file2.bin       [ 5. Повернутися та обробити ]\n\n"
                    "Управління стеком рекурсії:\n"
                    "• depth(): поточна глибина занурення\n"
                    "• disable_recursion_pending(): пропустити поточний підкаталог\n"
                    "• pop(): примусовий вихід на рівень вгору\n"
                    "• follow_directory_symlinks: захист від зациклень!", size=11, fill="#fff7e6", stroke=POS))

    f.append(text(470, 455, "Кожен крок ітератора повертає const directory_entry& з кешованим статусом файлу", size=11, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, 'traversal-iterators-comparison.svg'), W, H, *f,
           title="Порівняння моделей обходу каталогів")


# ── 4. Двокамерна обробка помилок та системні виклики ────────────────────────
def fig_syscall_cost_and_error_handling():
    W, H = 940, 440
    f = []

    f.append(text(470, 35, "Двокамерний механізм обробки помилок та кешування lstat/stat", size=16, color=INK, anchor="middle", bold=True))

    # Лівий блок: Винятки vs Коди помилок
    f.append(text(50, 70, "1. Двокамерний API операцій (No-throw vs Throwing)", size=13, color=FIELD, anchor="start", bold=True))
    
    f.append(fitbox(50, 95, 410, 140,
                    "Гілка A: Виклики з винятками\n"
                    "auto sz = fs::file_size(path);\n"
                    "──> При помильні (ENOENT/EACCES):\n"
                    "    throw std::filesystem_error(\n"
                    "        \"file_size: no such file\", path, ec);\n"
                    "• Накладні витрати: алокація винятку, unwind стеку", size=11, fill="#eef2f7", stroke=LINE))

    f.append(fitbox(480, 95, 410, 140,
                    "Гілка B: Виклики з std::error_code (No-throw)\n"
                    "std::error_code ec;\n"
                    "auto sz = fs::file_size(path, ec);\n"
                    "if (ec) { /* Обробка без винятків */ }\n"
                    "• Накладні витрати: 0 (запис значення еквивалента errno в ec)", size=11, fill="#e8f6ee", stroke=FIELD))

    # Нижній блок: Кешування у directory_entry
    f.append(text(50, 260, "2. Продуктивність: Кешування атрибутів у directory_entry проти прямого lstat()", size=13, color=NEG, anchor="start", bold=True))

    f.append(fitbox(50, 285, 410, 110,
                    "Прямий системний виклик (Висока ціна)\n"
                    "if (fs::exists(p) && fs::is_regular_file(p))\n"
                    "  auto sz = fs::file_size(p);\n"
                    "──> 3 окремі системні виклики stat() / TOCTOU гонка!", size=11, fill="#fff7e6", stroke=POS))

    f.append(fitbox(480, 285, 410, 110,
                    "Оптимальний обхід через directory_entry\n"
                    "for (const auto& entry : fs::directory_iterator(dir))\n"
                    "  if (entry.is_regular_file())\n"
                    "    auto sz = entry.file_size(); // Взяття з кешу d_type/stat\n"
                    "──> 0 додаткових системних викликів!", size=11, fill="#e8f6ee", stroke=FIELD))

    f.append(text(470, 420, "Використання методів directory_entry зменшує кількість системних викликів stat() у 3-5 разів", size=11, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, 'syscall-cost-and-error-handling.svg'), W, H, *f,
           title="Двокамерна обробка помилок та продуктивність")


if __name__ == '__main__':
    fig_fs_architecture_and_types()
    fig_path_decomposition_model()
    fig_traversal_iterators_comparison()
    fig_syscall_cost_and_error_handling()
    print("Всі 4 фігури успішно згенеровано у теку img/")
