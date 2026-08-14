# -*- coding: utf-8 -*-
import sys
import os

# Додаємо шлях до scripts/ для імпорту svgkit (4 рівні вгору від теми)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../scripts')))

import svgkit

def generate_startup_flow():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, 'shell-startup-flow.svg')

    w, h = 860, 520
    frags = []

    # Заголовок
    frags.append(svgkit.text(w / 2, 28, "Граф ініціалізації конфігураційних файлів оболонки", size=18, bold=True))

    # Вхідна точка
    frags.append(svgkit.fitbox(330, 55, 200, 42, "Вхідний виклик оболонки\n(SSH, Terminal, Script)", size=13, bold=True, fill="#e8f4f8", stroke="#2457d6"))
    frags.append(svgkit.arrow(430, 97, 430, 125))

    # Перевірка Login shell
    frags.append(svgkit.fitbox(300, 125, 260, 45, "Сеанс є Login shell?\n(argv[0] == '-bash' або --login)", size=13, bold=True, fill="#fdfefe", stroke="#1a1a1a"))

    # Гілка ТАК (Login Shell) -> ліворуч
    frags.append(svgkit.arrow(300, 147, 180, 147))
    frags.append(svgkit.text(240, 138, "ТАК", size=12, bold=True, color="#27ae60"))
    frags.append(svgkit.arrow(180, 147, 180, 190))

    # Блок Login Shell
    frags.append(svgkit.fitbox(40, 190, 280, 44, "1. Глобальний профіль:\n/etc/profile та /etc/profile.d/*.sh", size=12, fill="#f4f6f8"))
    frags.append(svgkit.arrow(180, 234, 180, 265))
    frags.append(svgkit.fitbox(40, 265, 280, 50, "2. Користувацький профіль (перший наявний):\n~/.bash_profile, ~/.bash_login чи ~/.profile", size=12, fill="#f4f6f8"))
    frags.append(svgkit.arrow(180, 315, 180, 345))
    frags.append(svgkit.fitbox(40, 345, 280, 44, "3. Явний виклик (sourcing):\n. ~/.bashrc (якщо існує)", size=12, fill="#eaf0fd", stroke="#2457d6"))

    # Гілка НІ (Non-Login Shell) -> праворуч
    frags.append(svgkit.arrow(560, 147, 680, 147))
    frags.append(svgkit.text(615, 138, "НІ", size=12, bold=True, color="#c0392b"))
    frags.append(svgkit.arrow(680, 147, 680, 190))

    # Перевірка Interactive shell
    frags.append(svgkit.fitbox(560, 190, 240, 45, "Інтерактивний сеанс?\n(isatty(0) == 1 та прапорець -i)", size=13, bold=True, fill="#fdfefe", stroke="#1a1a1a"))

    # Гілка Interactive Non-Login -> вниз
    frags.append(svgkit.arrow(680, 235, 680, 275))
    frags.append(svgkit.text(700, 255, "ТАК", size=12, bold=True, color="#27ae60", anchor="start"))
    frags.append(svgkit.fitbox(540, 275, 280, 44, "1. Глобальний RC-файл:\n/etc/bash.bashrc", size=12, fill="#f4f6f8"))
    frags.append(svgkit.arrow(680, 319, 680, 350))
    frags.append(svgkit.fitbox(540, 350, 280, 44, "2. Користувацький RC-файл:\n~/.bashrc", size=12, fill="#eaf0fd", stroke="#2457d6"))

    # Гілка Non-Interactive -> вправо
    frags.append(svgkit.arrow(800, 212, 830, 212))
    frags.append(svgkit.arrow(830, 212, 830, 420))
    frags.append(svgkit.arrow(830, 420, 710, 420))
    frags.append(svgkit.text(815, 202, "НІ", size=11, bold=True, color="#c0392b"))
    frags.append(svgkit.fitbox(470, 410, 240, 45, "Неінтерактивний сценарій:\nВиконання $BASH_ENV (якщо задано)", size=12, fill="#fef9e7", stroke="#f39c12"))

    # Підсумок і фінішна лінія
    frags.append(svgkit.arrow(180, 389, 180, 475))
    frags.append(svgkit.arrow(680, 394, 680, 475))
    frags.append(svgkit.arrow(180, 475, 350, 475))
    frags.append(svgkit.arrow(680, 475, 510, 475))
    frags.append(svgkit.fitbox(350, 455, 160, 40, "Готова оболонка\nГотовність до команд", size=13, bold=True, fill="#e8f8f5", stroke="#27ae60"))

    svgkit.render(out_path, w, h, *frags)
    print(f"Generated {out_path}")

def generate_path_lookup():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, 'path-lookup-mechanics.svg')

    w, h = 880, 500
    frags = []

    # Заголовок
    frags.append(svgkit.text(w / 2, 28, "Механіка вирішення імені команди та пошуку в PATH", size=18, bold=True))

    # Вхідне слово
    frags.append(svgkit.fitbox(40, 60, 180, 44, "Команда для виконання\n(наприклад: 'grep')", size=13, bold=True, fill="#e8f4f8", stroke="#2457d6"))

    # Крок 1: Чи є сліш '/'?
    frags.append(svgkit.arrow(220, 82, 260, 82))
    frags.append(svgkit.fitbox(260, 60, 180, 44, "Команда містить '/'?\n(напр. ./bin/grep)", size=12, fill="#fdfefe"))
    frags.append(svgkit.arrow(350, 104, 350, 140))
    frags.append(svgkit.text(365, 122, "ТАК", size=11, bold=True, color="#27ae60"))
    frags.append(svgkit.fitbox(260, 140, 180, 40, "Прямий execve()\nбез пошуку в PATH", size=12, fill="#f4f6f8"))

    # Гілка НІ для сліша -> Крок 2: Аліаси та функції
    frags.append(svgkit.arrow(440, 82, 480, 82))
    frags.append(svgkit.text(455, 74, "НІ", size=11, bold=True, color="#c0392b"))
    frags.append(svgkit.fitbox(480, 60, 170, 44, "Перевірка Aliases,\nFunctions та Builtins", size=12, fill="#fdfefe"))

    # Знайдено builtins?
    frags.append(svgkit.arrow(565, 104, 565, 140))
    frags.append(svgkit.text(580, 122, "Знайдено", size=11, bold=True, color="#27ae60"))
    frags.append(svgkit.fitbox(480, 140, 170, 40, "Виконати внутрішньо\nу процесі оболонки", size=12, fill="#e8f8f5", stroke="#27ae60"))

    # Не вбудована -> Крок 3: Перевірка Hash Table
    frags.append(svgkit.arrow(650, 82, 690, 82))
    frags.append(svgkit.text(665, 74, "Зовнішня", size=11, bold=True, color="#2457d6"))
    frags.append(svgkit.fitbox(690, 60, 160, 44, "Пошук у кеші\nHash Table оболонки", size=12, bold=True, fill="#eaf0fd", stroke="#2457d6"))

    # Hash HIT -> execve
    frags.append(svgkit.arrow(770, 104, 770, 140))
    frags.append(svgkit.text(785, 122, "HIT", size=11, bold=True, color="#27ae60"))
    frags.append(svgkit.fitbox(690, 140, 160, 40, "Виконати execve()\nза кешованим шляхом", size=12, fill="#e8f8f5", stroke="#27ae60"))

    # Hash MISS -> Крок 4: Обхід каталогів PATH
    frags.append(svgkit.arrow(770, 180, 770, 220))
    frags.append(svgkit.arrow(770, 220, 130, 220))
    frags.append(svgkit.arrow(130, 220, 130, 260))
    frags.append(svgkit.text(450, 210, "MISS: Послідовне сканування елементів PATH (ліворуч вправо)", size=12, bold=True, color="#c0392b"))

    # Блоки каталогів PATH
    frags.append(svgkit.fitbox(50, 260, 160, 50, "PATH елемент N:\n/usr/local/bin", size=12, fill="#f4f6f8"))
    frags.append(svgkit.arrow(210, 285, 250, 285))
    frags.append(svgkit.fitbox(250, 260, 160, 50, "PATH елемент N+1:\n/usr/bin", size=12, fill="#f4f6f8"))
    frags.append(svgkit.arrow(410, 285, 450, 285))
    frags.append(svgkit.fitbox(450, 260, 160, 50, "PATH елемент N+2:\n/bin", size=12, fill="#f4f6f8"))

    # Системний виклик faccessat/stat
    frags.append(svgkit.arrow(330, 310, 330, 350))
    frags.append(svgkit.fitbox(220, 350, 220, 45, "Системна перевірка:\nfaccessat(dir, cmd, X_OK)", size=12, bold=True, fill="#fdfefe", stroke="#1a1a1a"))

    # Успіх -> Збереження у hash table + execve
    frags.append(svgkit.arrow(440, 372, 530, 372))
    frags.append(svgkit.text(450, 362, "Знайдено (X_OK)", size=11, bold=True, color="#27ae60", anchor="start"))
    frags.append(svgkit.fitbox(530, 350, 260, 45, "1. Додати запис у Hash Table\n2. Запустити execve(full_path)", size=12, fill="#e8f8f5", stroke="#27ae60"))

    # Невдача для всіх -> Command Not Found
    frags.append(svgkit.arrow(330, 395, 330, 435))
    frags.append(svgkit.text(345, 415, "Вичерпано всі елементи PATH", size=11, bold=True, color="#c0392b", anchor="start"))
    frags.append(svgkit.fitbox(220, 435, 220, 42, "Помилка виконання:\n'command not found' (exit 127)", size=12, bold=True, fill="#fdecea", stroke="#c0392b"))

    svgkit.render(out_path, w, h, *frags)
    print(f"Generated {out_path}")

if __name__ == "__main__":
    generate_startup_flow()
    generate_path_lookup()
