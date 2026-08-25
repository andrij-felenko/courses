# -*- coding: utf-8 -*-
"""Фігури до теми «Керувати програмою, що вимагає термінала»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_dev_tty_bypass():
    """Як /dev/tty обходить стандартні дескриптори 0, 1, 2."""
    W, H = 1060, 490
    g = []

    # Заголовок та контекст
    g.append(text(W / 2, 40, "Спроба конвеєрного введення: echo 'пароль' | sudo / passwd",
                  size=14, color=MUTED))

    # Ліва колонка: стандартні потоки введення/виведення
    g.append(rect(40, 70, 310, 360, fill="#fdf6f5", stroke=POS, sw=1.4))
    g.append(text(195, 96, "Стандартні потоки (перенаправлені)", size=13, color=POS, bold=True))

    g.append(fitbox(60, 120, 270, 60, "fd 0 (stdin)\nтруба від echo 'пароль'", size=12, fill="#ffffff", stroke=POS))
    g.append(fitbox(60, 200, 270, 60, "fd 1 (stdout)\nперенаправлено у файл або пайп", size=12, fill="#ffffff", stroke=MUTED))
    g.append(fitbox(60, 280, 270, 60, "fd 2 (stderr)\nперенаправлено або термінал", size=12, fill="#ffffff", stroke=MUTED))

    g.append(fitbox(60, 360, 270, 52, "isatty(0) повертає 0 (хибно)\ntcgetattr(0) дає помилку ENOTTY",
                    size=11, fill="#fdecea", stroke=POS))

    # Середня колонка: процес sudo / passwd
    g.append(rect(400, 70, 260, 360, fill="#eef2f7", stroke=LINE, sw=1.4))
    g.append(text(530, 96, "Інтерактивний процес", size=13, color=INK, bold=True))
    g.append(text(530, 116, "sudo / passwd / ssh", size=12, color=MUTED))

    g.append(fitbox(420, 140, 220, 90, "Функція getpass(3):\n1. open('/dev/tty', O_RDWR)\n2. tcgetattr(&termios)\n3. вимикає прапорець ECHO",
                    size=12, fill="#ffffff", stroke=LINE))

    g.append(fitbox(420, 250, 220, 70, "Програма ігнорує fd 0\nі запитує пароль прямо\nчерез новий дескриптор tty",
                    size=12, fill="#fef9e7", stroke="#d4ac0d"))

    g.append(fitbox(420, 340, 220, 70, "Результат конвеєра:\nпароль із труби не прочитано,\nкоманда вимагає TTY або падає",
                    size=11, fill="#fdecea", stroke=POS))

    # Права колонка: керівний термінал сеансу
    g.append(rect(710, 70, 310, 360, fill="#eaf7ee", stroke=FIELD, sw=1.4))
    g.append(text(865, 96, "Керівний термінал сеансу", size=13, color=FIELD, bold=True))
    g.append(text(865, 116, "/dev/tty вказує на поточний TTY сеансу", size=12, color=MUTED))

    g.append(fitbox(730, 140, 270, 70, "Фізична клавіатура та екран\nабо зовнішній /dev/pts/N\n(де сидить користувач)",
                    size=12, fill="#ffffff", stroke=FIELD))

    g.append(fitbox(730, 230, 270, 80, "Ядро надсилає запит:\n[sudo] password for user:\nпрямо на екран оператора",
                    size=12, fill="#ffffff", stroke=FIELD))

    g.append(fitbox(730, 330, 270, 80, "Читання символів без відлуння:\nкористувач має ввести пароль вручну,\nабо open('/dev/tty') поверне ENXIO",
                    size=11, fill="#eaf7ee", stroke=FIELD))

    # Стрілки взаємодії
    g.append(arrow(332, 150, 398, 150, color=POS, sw=1.6))
    g.append(text(365, 140, "ігнор", size=10, color=POS))

    g.append(arrow(642, 175, 728, 175, color=FIELD, sw=1.8))
    g.append(text(685, 163, "open()", size=11, color=FIELD))

    g.append(arrow(728, 270, 642, 270, color=FIELD, sw=1.8))
    g.append(text(685, 258, "read()", size=11, color=FIELD))

    return render(os.path.join(IMG, 'dev-tty-bypass.svg'), W, H, *g,
                  title="Обхід стандартних потоків через /dev/tty")


def fig_pty_automation_architecture():
    """Архітектура керування програмою через пару псевдотермінала."""
    W, H = 1060, 520
    g = []

    # Ліва колонка: процес-керівник (Expect / Python / супервізор)
    g.append(rect(30, 60, 310, 420, fill="#eaf7ee", stroke=FIELD, sw=1.4))
    g.append(text(185, 88, "Процес-керівник (Driver)", size=14, color=FIELD, bold=True))
    g.append(text(185, 108, "Expect / Python pexpect / C++ демон", size=12, color=MUTED))

    g.append(fitbox(50, 130, 270, 70, "Ведучий кінець (Master FD)\nposix_openpt() / open('/dev/ptmx')\nчитання виводу та запис команд",
                    size=12, fill="#ffffff", stroke=FIELD))

    g.append(fitbox(50, 220, 270, 100, "Скінченний автомат:\n1. Очікує підказку ('Password:')\n2. Перевіряє регулярні вирази\n3. Надсилає відповідь ('секрет\\r')\n4. Контролює таймаути",
                    size=12, fill="#ffffff", stroke=FIELD))

    g.append(fitbox(50, 340, 270, 70, "Обробка завершення:\nread() повертає EIO на Linux\nwaitpid(child_pid, &status, 0)",
                    size=12, fill="#ffffff", stroke=MUTED))

    g.append(fitbox(50, 424, 270, 42, "Повна ізоляція облікових даних", size=11, fill="#eaf7ee", stroke=FIELD))

    # Центральна частина: ядро Linux та PTY лінія
    g.append(rect(370, 60, 320, 420, fill="#f8fafc", stroke=MUTED, sw=1.4))
    g.append(text(530, 88, "Ядро Linux: підсистема PTY", size=14, color=INK, bold=True))

    g.append(fitbox(390, 120, 280, 80, "Лінійна дисципліна підлеглого кінця:\n- Буферизація рядків (ICANON)\n- Обробка відлуння (ECHO)\n- Перетворення \\r в \\n (ICRNL)",
                    size=11, fill="#eef2f7", stroke=LINE))

    g.append(fitbox(390, 220, 280, 70, "Клон-пристрій /dev/ptmx\nта вузол /dev/pts/N у devpts",
                    size=12, fill="#ffffff", stroke=LINE))

    g.append(fitbox(390, 310, 280, 80, "Прив'язка сеансу (TIOCSCTTY):\n/dev/pts/N стає керівним терміналом\nдля нового сеансу",
                    size=11, fill="#eaf7ee", stroke=FIELD))

    g.append(fitbox(390, 410, 280, 56, "Сигнали та розрив:\nЗакриття master_fd → SIGHUP дитині",
                    size=11, fill="#fdecea", stroke=POS))

    # Права колонка: цільова програма (sudo, passwd, ssh)
    g.append(rect(720, 60, 310, 420, fill="#eef3fb", stroke=NEG, sw=1.4))
    g.append(text(875, 88, "Цільова програма (Child)", size=14, color=NEG, bold=True))
    g.append(text(875, 108, "sudo / ssh / passwd / fdisk", size=12, color=MUTED))

    g.append(fitbox(740, 130, 270, 70, "Власний сеанс (setsid()):\n/dev/pts/N як дескриптори 0, 1, 2\nisatty(0) == 1 (справжній TTY)",
                    size=12, fill="#ffffff", stroke=NEG))

    g.append(fitbox(740, 220, 270, 80, "Прямий доступ до /dev/tty:\nopen('/dev/tty') відкриває /dev/pts/N\nЗапит пароля йде в псевдотермінал",
                    size=12, fill="#ffffff", stroke=NEG))

    g.append(fitbox(740, 320, 270, 80, "Режим termios без помилок:\ntcgetattr / tcsetattr успішні,\nпрограма вважає, що працює людина",
                    size=12, fill="#ffffff", stroke=NEG))

    g.append(fitbox(740, 420, 270, 46, "Звичайна взаємодія без падінь", size=11, fill="#eaf7ee", stroke=FIELD))

    # Стрілки між колонками
    g.append(arrow(322, 160, 388, 160, color=FIELD, sw=1.6))
    g.append(text(355, 148, "write", size=11, color=FIELD))

    g.append(arrow(388, 250, 322, 250, color=FIELD, sw=1.6))
    g.append(text(355, 238, "read", size=11, color=FIELD))

    g.append(arrow(672, 160, 738, 160, color=NEG, sw=1.6))
    g.append(text(705, 148, "read", size=11, color=NEG))

    g.append(arrow(738, 250, 672, 250, color=NEG, sw=1.6))
    g.append(text(705, 238, "write", size=11, color=NEG))

    return render(os.path.join(IMG, 'pty-automation-architecture.svg'), W, H, *g,
                  title="Архітектура автоматизації програми через PTY")


def fig_expect_state_machine():
    """Скінченний автомат діалогової автоматизації Expect."""
    W, H = 1060, 460
    g = []

    # Стан 1: Створення процесу
    g.append(fitbox(40, 70, 200, 70, "1. SPAWN\nСтворення PTY і запуск\nдочірньої програми",
                    size=12, fill="#eaf7ee", stroke=FIELD, bold=True))

    g.append(arrow(242, 105, 308, 105, color=LINE, sw=1.6))

    # Стан 2: Накопичення у ковзний буфер
    g.append(fitbox(310, 60, 240, 90, "2. READ_BUFFER\nЗчитування байтів із PTY\nу ковзний віконний буфер\n(перевірка таймауту)",
                    size=12, fill="#eef2f7", stroke=LINE, bold=True))

    g.append(arrow(552, 105, 618, 105, color=LINE, sw=1.6))

    # Стан 3: Зіставлення шаблонів (Pattern Matching)
    g.append(fitbox(620, 50, 250, 110, "3. PATTERN_MATCH\nЗіставлення вмісту буфера\nіз переліком очікуваних\nрегулярних виразів",
                    size=12, fill="#fef9e7", stroke="#d4ac0d", bold=True))

    # Гілки дій від Pattern Match
    # Гілка А: Співпав запит пароля
    g.append(arrow(745, 162, 745, 238, color=FIELD, sw=1.6))
    g.append(text(755, 195, "пароль / підказка", size=11, color=FIELD, anchor="start"))

    g.append(fitbox(620, 240, 250, 80, "4a. SEND RESPONSE\nНадсилання рядка з '\\r'\n(send 'пароль\\r')\nОчищення знайденого префікса",
                    size=12, fill="#eaf7ee", stroke=FIELD))

    # Петля повернення до читання
    g.append(line(620, 280, 430, 280, color=FIELD, sw=1.4, dash="5 4"))
    g.append(arrow(430, 280, 430, 152, color=FIELD, sw=1.4))
    g.append(text(520, 268, "наступний крок діалогу", size=11, color=FIELD))

    # Гілка Б: Таймаут
    g.append(arrow(872, 85, 948, 85, color=POS, sw=1.6))
    g.append(text(910, 72, "timeout", size=11, color=POS))

    g.append(fitbox(950, 55, 90, 60, "TIMEOUT\nПомилка / abort", size=11, fill="#fdecea", stroke=POS))

    # Гілка В: Кінець виводу (EOF / EIO)
    g.append(arrow(872, 130, 948, 170, color=NEG, sw=1.6))
    g.append(text(910, 140, "EOF / EIO", size=11, color=NEG))

    g.append(fitbox(900, 180, 140, 70, "EOF\nУспішне завершення\nwaitpid() статусу", size=11, fill="#eaf0fd", stroke=NEG))

    # Гілка Г: Передача оператору (Interact)
    g.append(fitbox(620, 360, 250, 60, "4b. INTERACT\nПеремикання нашого термінала\nв сирий режим: оператор керує сам",
                    size=12, fill="#ffffff", stroke=MUTED))
    g.append(arrow(745, 322, 745, 358, color=MUTED, sw=1.4))

    # Пояснювальний блок знизу
    g.append(fitbox(40, 360, 510, 60, "Інваріант безпеки:\nСкінченний автомат надсилає введення лише ПІСЛЯ появи підказки,\nщо гарантує завершення відключення ECHO програмою.",
                    size=12, fill="#eaf7ee", stroke=FIELD))

    return render(os.path.join(IMG, 'expect-state-machine.svg'), W, H, *g,
                  title="Скінченний автомат взаємодії Expect")


if __name__ == '__main__':
    fig_dev_tty_bypass()
    fig_pty_automation_architecture()
    fig_expect_state_machine()
    print("Готово. Згенеровано файли у:", IMG)
