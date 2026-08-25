# -*- coding: utf-8 -*-
"""Фігури до теми «Перенесення файлів: scp, sftp і rsync поверх SSH»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def fig_protocols_architecture():
    """Порівняння архітектури SCP, SFTP та Rsync поверх SSH."""
    W, H = 1180, 680
    f = []

    # Заголовок зверху
    f.append(text(W / 2, 40, "Архітектура транспорту та виконання процесів при передачі файлів через SSH", size=17, bold=True))

    # Стовпець 1: Класичний SCP
    col1_x = 210
    f.append(rect(col1_x - 170, 70, 340, 560, fill="#fffaf9", stroke=POS))
    f.append(text(col1_x, 100, "Класичний SCP (RCP)", size=15, bold=True, color=POS))
    f.append(text(col1_x, 125, "ssh remote \"scp -t /path\"", size=12, color=MUTED))

    b, _, _ = textbox(col1_x, 175, "Клієнт scp\n(парсить аргументи CLI)", size=13)
    f.append(b)
    f.append(arrow(col1_x, 205, col1_x, 245))

    b, _, _ = textbox(col1_x, 275, "SSH-канал сеансу\n(віддалений запуск оболонки)", size=13, fill="#fdf0ed", stroke=POS)
    f.append(b)
    f.append(arrow(col1_x, 305, col1_x, 345))

    b, _, _ = textbox(col1_x, 375, "Віддалена оболонка\n(/bin/sh -c \"scp -t /path\")", size=13)
    f.append(b)
    f.append(arrow(col1_x, 405, col1_x, 445))

    b, _, _ = textbox(col1_x, 485, "Потоковий протокол RCP\nC0644 <size> <name>\\n\n[сирі байти без фреймів]", size=12, fill="#fbebe8")
    f.append(b)

    f.append(fitbox(col1_x - 150, 550, 300, 60,
                    "Вразливості: розкриття масок оболонкою\nі підміна файлів клієнта (CVE-2019-6111)",
                    size=12, fill="#fdf2f0", stroke=POS))

    # Стовпець 2: SFTP
    col2_x = 590
    f.append(rect(col2_x - 170, 70, 340, 560, fill="#f8faff", stroke=NEG))
    f.append(text(col2_x, 100, "Підсистема SFTP (OpenSSH)", size=15, bold=True, color=NEG))
    f.append(text(col2_x, 125, "SSH Subsystem sftp / internal-sftp", size=12, color=MUTED))

    b, _, _ = textbox(col2_x, 175, "Клієнт sftp / scp (v9.0+)\n(структуровані запити)", size=13)
    f.append(b)
    f.append(arrow(col2_x, 205, col2_x, 245))

    b, _, _ = textbox(col2_x, 275, "SSH-канал підсистеми\n(SSH_MSG_CHANNEL_REQUEST)", size=13, fill="#edf3fd", stroke=NEG)
    f.append(b)
    f.append(arrow(col2_x, 305, col2_x, 345))

    b, _, _ = textbox(col2_x, 375, "internal-sftp у sshd\n(без запуску /bin/sh)", size=13)
    f.append(b)
    f.append(arrow(col2_x, 405, col2_x, 445))

    b, _, _ = textbox(col2_x, 485, "Бінарний протокол SFTP\n[len][type][id][payload]\nSSH_FXP_OPEN, READ, WRITE", size=12, fill="#eaf0fa")
    f.append(b)

    f.append(fitbox(col2_x - 150, 550, 300, 60,
                    "Безпека: довільний доступ за зміщенням,\nізоляція ChrootDirectory, без оболонки",
                    size=12, fill="#edf3fd", stroke=NEG))

    # Стовпець 3: Rsync over SSH
    col3_x = 970
    f.append(rect(col3_x - 170, 70, 340, 560, fill="#f7fbf8", stroke=FIELD))
    f.append(text(col3_x, 100, "Дельта-синхронізація Rsync", size=15, bold=True, color=FIELD))
    f.append(text(col3_x, 125, "ssh remote \"rsync --server ...\"", size=12, color=MUTED))

    b, _, _ = textbox(col3_x, 175, "Локальний rsync (Sender)\n(ковзне вікно + хеш-таблиця)", size=13)
    f.append(b)
    f.append(arrow(col3_x, 205, col3_x, 245))

    b, _, _ = textbox(col3_x, 275, "Двосторонній SSH-пайп\n(захищений транспорт потоку)", size=13, fill="#eef7f0", stroke=FIELD)
    f.append(b)
    f.append(arrow(col3_x, 305, col3_x, 345))

    b, _, _ = textbox(col3_x, 375, "Віддалений rsync (Generator)\n(сканування блоків цілі)", size=13)
    f.append(b)
    f.append(arrow(col3_x, 405, col3_x, 445))

    b, _, _ = textbox(col3_x, 485, "Дельта-протокол rsync\n[хеші блоків] <-> [токени дельти]\nпередача лише змінених байтів", size=12, fill="#e8f5ec")
    f.append(b)

    f.append(fitbox(col3_x - 150, 550, 300, 60,
                    "Ефективність: передача лише різниць,\nзбереження метаданих, докачування",
                    size=12, fill="#eef7f0", stroke=FIELD))

    render(os.path.join(OUT, 'protocols-architecture.svg'), W, H, *f,
           title="Порівняння архітектури передачі файлів через SSH: SCP, SFTP та Rsync")


def fig_sftp_chroot_jail():
    """Схема ізоляції користувача SFTP у ChrootDirectory з internal-sftp."""
    W, H = 1140, 600
    f = []

    f.append(text(W / 2, 40, "Ізоляція користувача SFTP за допомогою ChrootDirectory та internal-sftp", size=17, bold=True))

    # Ліва частина: Клієнт та з'єднання
    f.append(rect(50, 90, 280, 460, fill="#f8faff", stroke=NEG))
    f.append(text(190, 125, "Зовнішній клієнт SFTP", size=15, bold=True, color=NEG))
    f.append(fitbox(70, 155, 240, 70, "Автентифікація:\nSSH-ключ або пароль\nUser: sftpuser", size=13))
    f.append(fitbox(70, 245, 240, 70, "Канал сеансу:\nЗапит підсистеми 'sftp'\nбез запиту PTY/оболонки", size=13))

    f.append(arrow(330, 280, 420, 280, color=NEG, sw=2.5))
    f.append(text(375, 265, "SSH", size=12, color=NEG, bold=True))

    # Середня та права частина: Демон sshd та файлова система хоста
    f.append(rect(420, 90, 670, 460, fill="#fafbfc", stroke=LINE))
    f.append(text(755, 125, "Сервер sshd (хост)", size=15, bold=True))

    # Блок перевірки прав ChrootDirectory
    f.append(fitbox(450, 155, 610, 75,
                    "Правило безпеки sshd:\n"
                    "Каталог ChrootDirectory і всі його батьківські каталоги\n"
                    "повинні належати root:root і мати права не більше ніж 0755",
                    size=13, fill="#fdf0ed", stroke=POS))

    # Jail блок
    f.append(rect(450, 255, 610, 275, fill="#f4f6f8", stroke=MUTED, sw=1.5, rx=8))
    f.append(text(755, 280, "Ізольоване дерево ChrootDirectory: /var/sftp/sftpuser (для процесу це «/»)", size=13, bold=True, color=MUTED))

    # Каталоги всередині jail
    # Корінь jail
    f.append(rect(470, 310, 280, 200, fill="#ffffff", stroke=POS))
    f.append(text(610, 335, "Корінь jail: /", size=14, bold=True, color=POS))
    f.append(text(610, 360, "Власник: root:root", size=12))
    f.append(text(610, 385, "Права: drwxr-xr-x (0755)", size=12))
    f.append(fitbox(485, 415, 250, 75, "Запис заборонено!\nЗахист від підміни\nдинамічних бібліотек і конфігів", size=12, fill="#fdf2f0"))

    # Вкладений каталог uploads
    f.append(rect(770, 310, 270, 200, fill="#ffffff", stroke=FIELD))
    f.append(text(905, 335, "Підкаталог: /uploads", size=14, bold=True, color=FIELD))
    f.append(text(905, 360, "Власник: sftpuser:sftpusers", size=12))
    f.append(text(905, 385, "Права: drwxr-xr-x (0755/0775)", size=12))
    f.append(fitbox(785, 415, 240, 75, "Запис дозволено:\nКлієнт може завантажувати\nі читати файли тут", size=12, fill="#eef7f0"))

    render(os.path.join(OUT, 'sftp-chroot-jail.svg'), W, H, *f,
           title="Ізоляція користувача SFTP через ChrootDirectory та internal-sftp")


def fig_rsync_delta_cycle():
    """Схема роботи дельта-алгоритму rsync між генератором і відправником."""
    W, H = 1180, 640
    f = []

    f.append(text(W / 2, 38, "Трифазний дельта-алгоритм синхронізації rsync", size=17, bold=True))

    # Ліва колонка: Одержувач (Ціль)
    f.append(rect(60, 75, 480, 520, fill="#f8faff", stroke=NEG))
    f.append(text(300, 105, "Одержувач / Receiver (Цільовий хост)", size=15, bold=True, color=NEG))
    f.append(text(300, 130, "Має застарілу версію файлу B (розмір N байтів)", size=12, color=MUTED))

    # Фаза 1: Розбиття на блоки
    f.append(rect(80, 155, 440, 165, fill="#ffffff", stroke=NEG))
    f.append(text(300, 180, "Фаза 1: Розбиття файлу B на блоки розміру S", size=13, bold=True))
    f.append(text(300, 205, "Блок 0 [0..S-1]  ->  rollsum_0 (32-bit) + MD4_0 (128-bit)", size=12))
    f.append(text(300, 230, "Блок 1 [S..2S-1] ->  rollsum_1 (32-bit) + MD4_1 (128-bit)", size=12))
    f.append(text(300, 255, "Блок 2 [2S..3S-1]-> rollsum_2 (32-bit) + MD4_2 (128-bit)", size=12))
    f.append(fitbox(100, 275, 400, 35, "Генерація таблиці сигнатур блоків цілі", size=12, fill="#edf3fd"))

    # Стрілка передачі хешів
    f.append(arrow(520, 230, 660, 230, color=NEG, sw=2.5))
    f.append(text(590, 215, "Таблиця хешів", size=12, color=NEG, bold=True))

    # Права колонка: Відправник (Джерело)
    f.append(rect(640, 75, 480, 520, fill="#f7fbf8", stroke=FIELD))
    f.append(text(880, 105, "Відправник / Sender (Джерельний хост)", size=15, bold=True, color=FIELD))
    f.append(text(880, 130, "Має свіжу версію файлу A (нові правки)", size=12, color=MUTED))

    # Фаза 2: Пошук ковзним вікном
    f.append(rect(660, 155, 440, 165, fill="#ffffff", stroke=FIELD))
    f.append(text(880, 180, "Фаза 2: Пошук збігів ковзним вікном розміру S", size=13, bold=True))
    f.append(text(880, 205, "Побайтовий зсув вікна: перерахунок rollsum за O(1)", size=12))
    f.append(text(880, 230, "Якщо rollsum є в хеш-таблиці -> звірка сильного MD4", size=12))
    f.append(text(880, 255, "Збіг: токен MATCH(block_idx) | Немає: байт у буфер LITERAL", size=12))
    f.append(fitbox(680, 275, 400, 35, "Стиснений потік інструкцій відновлення", size=12, fill="#eef7f0"))

    # Стрілка передачі дельти назад
    f.append(arrow(660, 360, 520, 360, color=FIELD, sw=2.5))
    f.append(text(590, 345, "Токени дельти", size=12, color=FIELD, bold=True))

    # Фаза 3: Збирання файлу
    f.append(rect(80, 370, 440, 195, fill="#ffffff", stroke=NEG))
    f.append(text(300, 395, "Фаза 3: Реконструкція файлу в .file.XXXXXX", size=13, bold=True))
    f.append(text(300, 425, "1. Отримано MATCH(i) -> копіювати блок i з файлу B", size=12))
    f.append(text(300, 450, "2. Отримано LITERAL(bytes) -> записати нові байти з мережі", size=12))
    f.append(text(300, 475, "3. Звірка цілісного хеша відновленого файлу", size=12))
    f.append(text(300, 500, "4. Атомарна заміна: rename(.file.XXXXXX, file)", size=12))
    f.append(fitbox(100, 525, 400, 30, "Цільовий файл оновлено без повної передачі даних", size=12, fill="#eef7f0", stroke=FIELD))

    # Пояснювальний блок унизу
    f.append(rect(660, 370, 440, 195, fill="#ffffff", stroke=MUTED))
    f.append(text(880, 395, "Переваги дельта-алгоритму", size=13, bold=True))
    f.append(text(880, 430, "• Трафік = тільки змінені байти + метадані хешів", size=12))
    f.append(text(880, 460, "• Вставка байтів на початку файлу не ламає алгоритм:", size=12))
    f.append(text(880, 485, "  ковзне вікно знайде зсунуті блоки на будь-якій позиції", size=12))
    f.append(text(880, 515, "• Безпека при збоях: старий файл цілий до rename()", size=12))

    render(os.path.join(OUT, 'rsync-delta-cycle.svg'), W, H, *f,
           title="Трифазний дельта-алгоритм синхронізації rsync")


if __name__ == '__main__':
    fig_protocols_architecture()
    fig_sftp_chroot_jail()
    fig_rsync_delta_cycle()
    print("Фігури успішно згенеровано у %s" % OUT)
