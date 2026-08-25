# -*- coding: utf-8 -*-
"""Фігури для теми «Від рядка в історії до сценарію» (root/course/unix/from-history-line-to-script)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# Палітра кольорів
AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
TEAL_F, TEAL_S = "#e6fffa", "#0d9488"
BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
RED_F, RED_S = "#fef2f2", "#dc2626"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"

def fig_interactive_vs_cron():
    """interactive-vs-cron-environment.svg: Відмінності середовища інтерактивної сесії та cron/фонового демона."""
    W, H = 1000, 520
    frags = []

    # Заголовок
    frags.append(text(500, 32, "Анатомія середовища: інтерактивна сесія користувача проти cron / демона", size=16, bold=True, color="#1e293b"))

    # Ліва колонка: Інтерактивний термінал (людина за клавіатурою)
    frags.append(rect(40, 65, 435, 425, fill="#f8fafc", stroke=BLUE_S, sw=1.5, rx=8))
    b_inter, _, _ = textbox(257, 95, "Інтерактивна сесія (Користувач у TTY)", size=13, bold=True, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_inter)

    # Пункти інтерактивного оточення
    items_left = [
        ("1. Керівний термінал (TTY):", "stdin, stdout, stderr підключені до /dev/pts/X; доступне ручне введення.", GREEN_S),
        ("2. Змінні середовища сеансу:", "Зчитано ~/.bashrc, ~/.profile; PATH містить /usr/local/bin, ~/bin.", "#334155"),
        ("3. Інтерактивні аліаси й функції:", "Активні безпечні аліаси: alias cp='cp -i', alias rm='rm -i'.", "#334155"),
        ("4. Робочий каталог ($PWD):", "Поточна тека проєкту або репозиторію; відносні шляхи валідні.", "#334155"),
        ("5. Реакція на збої та запити:", "Людина бачить помилку в реальному часі й може підтвердити дію.", "#334155"),
        ("6. Буферизація виводу:", "Порядкова буферизація (Line buffering) — повідомлення видно негайно.", "#334155"),
    ]

    y_pos = 135
    for title_txt, desc_txt, col in items_left:
        frags.append(text(60, y_pos, title_txt, size=11, bold=True, color=col, anchor="start"))
        frags.append(text(60, y_pos + 18, desc_txt, size=10, color="#475569", anchor="start"))
        y_pos += 56

    # Права колонка: Неінтерактивне середовище cron / systemd
    frags.append(rect(525, 65, 435, 425, fill="#fdfbf7", stroke=RED_S, sw=1.5, rx=8))
    b_cron, _, _ = textbox(742, 95, "Автоматизований запуск (cron / systemd)", size=13, bold=True, fill=RED_F, stroke=RED_S)
    frags.append(b_cron)

    # Пункти неінтерактивного оточення
    items_right = [
        ("1. Відсутність TTY (No controlling terminal):", "stdin закритий або з /dev/null; інтерактивний запит зависає або падає.", RED_S),
        ("2. Мінімальний системний PATH:", "Лише /usr/bin:/bin; сторонні бінарники (aws, docker) не знайдено.", RED_S),
        ("3. Неінтерактивна оболонка:", "~/.bashrc НЕ завантажується; аліаси та кастомні функції відсутні.", RED_S),
        ("4. Непередбачуваний $PWD:", "За замовчуванням $HOME або /; відносні шляхи вказують у нікуди.", RED_S),
        ("5. Мовчазне виконання збоїв:", "Ніхто не читає stdout; помилка посеред ланцюжка ігнорується.", RED_S),
        ("6. Повна буферизація блоками:", "Буферизація по 4 КіБ — логи не з'являються у файлі до змиву.", "#78350f"),
    ]

    y_pos = 135
    for title_txt, desc_txt, col in items_right:
        frags.append(text(545, y_pos, title_txt, size=11, bold=True, color=col, anchor="start"))
        frags.append(text(545, y_pos + 18, desc_txt, size=10, color="#78350f", anchor="start"))
        y_pos += 56

    # Центральна стрілка / розділювач
    frags.append(arrow(478, 275, 520, 275, color=AMBER_S, sw=2.5))
    frags.append(text(498, 255, "Прірва", size=10.5, bold=True, color="#b45309"))

    render(os.path.join(IMG, "interactive-vs-cron-environment.svg"), W, H, *frags)


def fig_strict_mode():
    """strict-mode-execution-flow.svg: Порівняння поведінки звичайного режиму та set -euo pipefail."""
    W, H = 1000, 500
    frags = []

    # Заголовок
    frags.append(text(500, 32, "Поведінка сценарію при збоях: звичайний режим проти set -euo pipefail", size=16, bold=True, color="#1e293b"))

    # Лівий блок: Звичайний небезпечний режим (дефолт Bash)
    frags.append(rect(40, 65, 435, 405, fill="#fef2f2", stroke=RED_S, sw=1.5, rx=8))
    b_def, _, _ = textbox(257, 95, "Звичайний режим (Замовчування)", size=12.5, bold=True, fill="#fee2e2", stroke=RED_S)
    frags.append(b_def)

    # Кроки ліворуч
    frags.append(rect(60, 130, 395, 45, fill="#ffffff", stroke="#fca5a5", sw=1, rx=6))
    frags.append(text(75, 150, "1. cd /var/backups/db (помилка: каталогу немає)", size=10.5, bold=True, color=RED_S, anchor="start"))
    frags.append(text(75, 166, "Код виходу 1. Оболонка ігнорує збій і йде далі!", size=9.5, color="#7f1d1d", anchor="start"))

    frags.append(rect(60, 190, 395, 45, fill="#ffffff", stroke="#fca5a5", sw=1, rx=6))
    frags.append(text(75, 210, "2. rm -rf \"$TARGET_DIR/*\" (змінна не оголошена)", size=10.5, bold=True, color=RED_S, anchor="start"))
    frags.append(text(75, 226, "Розкривається в 'rm -rf /*'! Спроба очистити корінь ОС.", size=9.5, color="#7f1d1d", anchor="start"))

    frags.append(rect(60, 250, 395, 45, fill="#ffffff", stroke="#fca5a5", sw=1, rx=6))
    frags.append(text(75, 270, "3. mysqldump db | gzip > backup.sql.gz", size=10.5, bold=True, color=RED_S, anchor="start"))
    frags.append(text(75, 286, "mysqldump впав з помилкою, але gzip повернув 0. $? = 0!", size=9.5, color="#7f1d1d", anchor="start"))

    frags.append(rect(60, 310, 395, 45, fill="#ffffff", stroke="#fca5a5", sw=1, rx=6))
    frags.append(text(75, 330, "4. echo \"Резервна копія успішна!\"", size=10.5, bold=True, color=RED_S, anchor="start"))
    frags.append(text(75, 346, "Скрипт звітує про успіх, зберігши порожній стиснений файл.", size=9.5, color="#7f1d1d", anchor="start"))

    b_res_bad, _, _ = textbox(257, 415, "Результат: Знищення даних або фальшивий успіх", size=11, bold=True, fill="#fecaca", stroke=RED_S, color="#991b1b")
    frags.append(b_res_bad)

    # Правий блок: Суворий режим (Strict Mode)
    frags.append(rect(525, 65, 435, 405, fill="#f0fdf4", stroke=GREEN_S, sw=1.5, rx=8))
    b_str, _, _ = textbox(742, 95, "Суворий режим (set -euo pipefail)", size=12.5, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_str)

    # Кроки праворуч
    frags.append(rect(545, 130, 395, 45, fill="#ffffff", stroke="#86efac", sw=1, rx=6))
    frags.append(text(560, 150, "1. cd /var/backups/db (помилка: каталогу немає)", size=10.5, bold=True, color="#166534", anchor="start"))
    frags.append(text(560, 166, "set -e (errexit): миттєва зупинка сценарію. Код 1.", size=9.5, color="#14532d", anchor="start", bold=True))

    frags.append(rect(545, 190, 395, 45, fill="#ffffff", stroke="#86efac", sw=1, rx=6))
    frags.append(text(560, 210, "2. rm -rf \"$TARGET_DIR/*\" (змінна не оголошена)", size=10.5, bold=True, color="#166534", anchor="start"))
    frags.append(text(560, 226, "set -u (nounset): аварійне завершення: 'unbound variable'.", size=9.5, color="#14532d", anchor="start", bold=True))

    frags.append(rect(545, 250, 395, 45, fill="#ffffff", stroke="#86efac", sw=1, rx=6))
    frags.append(text(560, 270, "3. mysqldump db | gzip > backup.sql.gz", size=10.5, bold=True, color="#166534", anchor="start"))
    frags.append(text(560, 286, "pipefail: конвеєр повертає код виходу mysqldump (!= 0).", size=9.5, color="#14532d", anchor="start", bold=True))

    frags.append(rect(545, 310, 395, 45, fill="#ffffff", stroke="#86efac", sw=1, rx=6))
    frags.append(text(560, 330, "4. IFS=$'\\n\\t' — безпечне розбиття слів", size=10.5, bold=True, color="#166534", anchor="start"))
    frags.append(text(560, 346, "Шляхи з пробілами не розпадаються на окремі аргументи.", size=9.5, color="#14532d", anchor="start"))

    b_res_good, _, _ = textbox(742, 415, "Результат: Детермінована зупинка та безпека системи", size=11, bold=True, fill="#bbf7d0", stroke=GREEN_S, color="#14532d")
    frags.append(b_res_good)

    render(os.path.join(IMG, "strict-mode-execution-flow.svg"), W, H, *frags)


def fig_tempdir_and_trap():
    """atomic-tempdir-and-trap-lifecycle.svg: Життєвий цикл mktemp, пастки trap та атомарної підміни файлів."""
    W, H = 1000, 480
    frags = []

    # Заголовок
    frags.append(text(500, 30, "Керування тимчасовими ресурсами: mktemp, пастка trap та атомарна заміна", size=16, bold=True, color="#1e293b"))

    # 4 послідовні фази (горизонтальний потік)
    # Фаза 1: Створення
    frags.append(rect(30, 65, 215, 360, fill="#f8fafc", stroke=BLUE_S, sw=1.3, rx=8))
    b1, _, _ = textbox(137, 92, "1. Створення каталогу", size=11.5, bold=True, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b1)
    frags.append(text(45, 125, "mktemp -d", size=11, bold=True, color=BLUE_S, anchor="start"))
    frags.append(text(45, 148, "• Генерує унікальне ім'я", size=10, color="#334155", anchor="start"))
    frags.append(text(45, 168, "  /tmp/job.XXXXXX", size=10, color="#64748b", anchor="start"))
    frags.append(text(45, 195, "• Маска прав 0700", size=10, color=GREEN_S, anchor="start", bold=True))
    frags.append(text(45, 215, "  (лише для власника)", size=9.5, color="#64748b", anchor="start"))
    frags.append(text(45, 245, "• Захист від Symlink Race", size=10, color="#334155", anchor="start", bold=True))
    frags.append(text(45, 265, "  і підміни TOCTOU.", size=9.5, color="#64748b", anchor="start"))

    # Фаза 2: Реєстрація пастки
    frags.append(rect(275, 65, 215, 360, fill="#f3e8ff", stroke=PURPLE_S, sw=1.3, rx=8))
    b2, _, _ = textbox(382, 92, "2. Пастка (trap)", size=11.5, bold=True, fill="#ede9fe", stroke=PURPLE_S)
    frags.append(b2)
    frags.append(text(290, 125, "trap cleanup EXIT INT TERM", size=10, bold=True, color=PURPLE_S, anchor="start"))
    frags.append(text(290, 150, "cleanup() {", size=10.5, color="#581c87", anchor="start", bold=True))
    frags.append(text(305, 172, "rm -rf \"$tmp_dir\"", size=10, color="#581c87", anchor="start"))
    frags.append(text(290, 194, "}", size=10.5, color="#581c87", anchor="start", bold=True))
    frags.append(text(290, 225, "• EXIT: будь-який вихід", size=10, color="#3b0764", anchor="start"))
    frags.append(text(290, 248, "• INT: переривання Ctrl+C", size=10, color="#3b0764", anchor="start"))
    frags.append(text(290, 271, "• TERM: сигнал kill/systemd", size=10, color="#3b0764", anchor="start"))
    frags.append(text(290, 300, "Гарантія: немає сміття!", size=10, color=GREEN_S, anchor="start", bold=True))

    # Фаза 3: Робота в пісочниці
    frags.append(rect(520, 65, 215, 360, fill="#fdfbf7", stroke=AMBER_S, sw=1.3, rx=8))
    b3, _, _ = textbox(627, 92, "3. Ізольована робота", size=11.5, bold=True, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b3)
    frags.append(text(535, 125, "Робота всередині $tmp_dir", size=10.5, bold=True, color="#92400e", anchor="start"))
    frags.append(text(535, 155, "• Генерація чернеток", size=10, color="#78350f", anchor="start"))
    frags.append(text(535, 178, "• Стиснення архіву", size=10, color="#78350f", anchor="start"))
    frags.append(text(535, 201, "• Обчислення sha256sum", size=10, color="#78350f", anchor="start"))
    frags.append(text(535, 235, "Якщо стається збій:", size=10, color=RED_S, anchor="start", bold=True))
    frags.append(text(535, 258, "Цільовий файл не чіпали.", size=9.5, color="#78350f", anchor="start"))
    frags.append(text(535, 281, "Чернетку видалить trap.", size=9.5, color="#78350f", anchor="start"))

    # Фаза 4: Атомарна фіксація
    frags.append(rect(765, 65, 205, 360, fill="#f0fdf4", stroke=GREEN_S, sw=1.3, rx=8))
    b4, _, _ = textbox(867, 92, "4. Атомарний коміт", size=11.5, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b4)
    frags.append(text(780, 125, "mv target.tmp target", size=11, bold=True, color=GREEN_S, anchor="start"))
    frags.append(text(780, 155, "• Системний виклик", size=10, color="#166534", anchor="start"))
    frags.append(text(795, 175, "rename() у VFS ядра", size=10, color="#166534", anchor="start", bold=True))
    frags.append(text(780, 205, "• Підміна вказівника іноди", size=10, color="#14532d", anchor="start"))
    frags.append(text(780, 235, "• Немає напівзаписаного", size=10, color="#14532d", anchor="start"))
    frags.append(text(795, 255, "пошкодженого стану!", size=10, color="#14532d", anchor="start", bold=True))
    frags.append(text(780, 290, "Паралельні процеси", size=10, color="#166534", anchor="start"))
    frags.append(text(780, 310, "бачать лише 100% файл.", size=9.5, color="#166534", anchor="start"))

    # Сполучні стрілки
    frags.append(arrow(245, 230, 275, 230, color="#94a3b8", sw=2))
    frags.append(arrow(490, 230, 520, 230, color="#94a3b8", sw=2))
    frags.append(arrow(735, 230, 765, 230, color="#94a3b8", sw=2))

    # Нижній підсумок
    b_bot, _, _ = textbox(500, 450, "Повний життєвий цикл: жодних витоків файлових дескрипторів і сміття на диску", size=11.5, bold=True, fill="#f1f5f9", stroke="#94a3b8", color="#334155")
    frags.append(b_bot)

    render(os.path.join(IMG, "atomic-tempdir-and-trap-lifecycle.svg"), W, H, *frags)

if __name__ == "__main__":
    fig_interactive_vs_cron()
    fig_strict_mode()
    fig_tempdir_and_trap()
    print("Фігури успішно скомпільовано в img/")
