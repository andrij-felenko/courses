# -*- coding: utf-8 -*-
"""Фігури до теми «Віддалений сеанс: SSH — модель, автентифікація, канал»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_ssh_layer_stack():
    """Трирівнева архітектура SSH-2 (RFC 4251-4254) та мультиплексування каналів."""
    W, H = 1000, 680
    g = []

    # Рівень 1: Connection Layer (вгорі)
    g.append(rect(40, 50, 920, 185, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    g.append(text(500, 75, "Connection Layer (RFC 4254) — Мультиплексування логічних каналів", size=15, color=INK, bold=True))

    ch_boxes = [
        (60, 95, 205, 120, "Канал #0: session\n(інтерактивна оболонка,\nкоманда exec, sftp)", "#eaf0fd", NEG),
        (290, 95, 205, 120, "Канал #1: direct-tcpip\n(локальне прокидання\n-L 8080:db:5432)", "#e8f8f0", FIELD),
        (520, 95, 205, 120, "Канал #2: forwarded-tcpip\n(віддалене прокидання\n-R 9000:localhost:3000)", "#fef7e7", "#d97706"),
        (750, 95, 190, 120, "Канал #3: x11 / agent\n(графічні програми X11,\nагент ssh-agent)", "#fdecea", POS)
    ]
    for x, y, w, h, lbl, fill, st in ch_boxes:
        g.append(fitbox(x, y, w, h, lbl, size=12, fill=fill, stroke=st, bold=False))

    # Стрілки переходу між рівнями 1 і 2
    g.append(arrow(350, 235, 350, 270, color=LINE, sw=1.8))
    g.append(arrow(650, 270, 650, 235, color=LINE, sw=1.8))
    g.append(fitbox(390, 243, 220, 24, "службовий запит ssh-connection", size=11, fill="#ffffff", stroke=MUTED))

    # Рівень 2: User Authentication Layer (посередині)
    g.append(rect(40, 275, 920, 140, fill="#fdfbf7", stroke=LINE, sw=1.5, rx=8))
    g.append(text(500, 300, "User Authentication Layer (RFC 4252) — Автентифікація користувача", size=15, color=INK, bold=True))

    auth_boxes = [
        (60, 320, 270, 80, "publickey (Ed25519, RSA)\nпідпис хешу сеансу клієнтом,\nзвірка з ~/.ssh/authorized_keys", "#ffffff", LINE),
        (360, 320, 270, 80, "password / keyboard-interactive\nпароль або багатофакторний\nвиклик-відповідь через PAM", "#ffffff", LINE),
        (660, 320, 280, 80, "hostbased / gssapi\nдовіра до хоста або\nквитки Kerberos / SSO", "#ffffff", LINE),
    ]
    for x, y, w, h, lbl, fill, st in auth_boxes:
        g.append(fitbox(x, y, w, h, lbl, size=12, fill=fill, stroke=st))

    # Стрілки переходу між рівнями 2 і 3
    g.append(arrow(350, 415, 350, 450, color=LINE, sw=1.8))
    g.append(arrow(650, 450, 650, 415, color=LINE, sw=1.8))
    g.append(fitbox(390, 423, 220, 24, "службовий запит ssh-userauth", size=11, fill="#ffffff", stroke=MUTED))

    # Рівень 3: Transport Layer (внизу)
    g.append(rect(40, 455, 920, 140, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=8))
    g.append(text(500, 480, "Transport Layer (RFC 4253) — Шифрування, цілісність, автентичність хоста", size=15, color=INK, bold=True))

    trans_boxes = [
        (60, 500, 270, 80, "Узгодження ключів (KEX)\nECDH Curve25519 / DH group14\nавтентифікація хоста (known_hosts)", "#ffffff", LINE),
        (360, 500, 270, 80, "Симетричний шифр та AEAD\nChaCha20-Poly1305, AES-256-GCM\nабо AES-CTR + HMAC (EtM)", "#ffffff", LINE),
        (660, 500, 280, 80, "Двійковий пакетний протокол (BPP)\nдоповнення, лічильник пакетів,\nзахист від підміни та replay", "#ffffff", LINE)
    ]
    for x, y, w, h, lbl, fill, st in trans_boxes:
        g.append(fitbox(x, y, w, h, lbl, size=12, fill=fill, stroke=st))

    # Фундамент: TCP socket
    g.append(arrow(500, 595, 500, 625, color=LINE, sw=1.8))
    g.append(fitbox(330, 630, 340, 28, "Єдине TCP-з'єднання (за замовчуванням порт 22/tcp)", size=12, fill="#ffffff", stroke=LINE, bold=True))

    render(os.path.join(IMG, 'ssh-layer-stack.svg'), W, H, *g,
           title="Трирівнева архітектура протоколу SSH-2")


def fig_ssh_session_pty_flow():
    """Потік даних інтерактивного сеансу: від термінала клієнта через SSH до PTY сервера."""
    W, H = 1040, 560
    g = []

    # Лівий блок — локальний хост
    g.append(rect(30, 40, 420, 420, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    g.append(text(240, 65, "Локальний хост (клієнт ssh)", size=15, color=INK, bold=True))

    g.append(fitbox(45, 80, 390, 80,
                    "Емулятор термінала користувача\n"
                    "Термінал переведено в RAW-режим (cfmakeraw):\n"
                    "ICANON=0, ECHO=0, ISIG=0. Ctrl+C та Ctrl+Z\n"
                    "не генерують локальних сигналів",
                    size=12, fill="#ffffff", stroke=NEG))

    g.append(arrow(240, 160, 240, 185, color=NEG, sw=1.6))
    g.append(fitbox(150, 165, 180, 20, "сирі байти введення (stdin)", size=10, fill="#ffffff", stroke=MUTED))

    g.append(fitbox(45, 185, 390, 115,
                    "Процес OpenSSH клієнта (ssh)\n"
                    "• Зчитує байти з дескриптора stdin\n"
                    "• Перевіряє ескейп-автомат на префікс ~\n"
                    "• Пакує в SSH_MSG_CHANNEL_DATA\n"
                    "• Ловить SIGWINCH і шле window-change",
                    size=12, fill="#eaf0fd", stroke=LINE))

    g.append(arrow(240, 300, 240, 330, color=LINE, sw=1.6))

    g.append(fitbox(45, 330, 390, 95,
                    "Шар шифрування та транспорту клієнта\n"
                    "• Шифрування AEAD (ChaCha20-Poly1305)\n"
                    "• Додавання MAC / тегу автентифікації\n"
                    "• Відправлення у TCP-сокет",
                    size=12, fill="#ffffff", stroke=MUTED))

    # Правий блок — віддалений сервер
    g.append(rect(590, 40, 420, 420, fill="#fdfbf7", stroke=LINE, sw=1.5, rx=8))
    g.append(text(800, 65, "Віддалений хост (сервер sshd)", size=15, color=INK, bold=True))

    g.append(fitbox(605, 80, 390, 95,
                    "Демон OpenSSH сервера (sshd)\n"
                    "• Розшифровує SSH_MSG_CHANNEL_DATA\n"
                    "• Записує байти в майстер PTY (/dev/ptmx)\n"
                    "• За запитом window-change викликає\n"
                    "  ioctl(master_fd, TIOCSWINSZ, &ws)",
                    size=12, fill="#e8f8f0", stroke=LINE))

    g.append(arrow(800, 175, 800, 205, color=LINE, sw=1.6))
    g.append(fitbox(700, 180, 200, 20, "write() у майстер-дескриптор", size=10, fill="#ffffff", stroke=MUTED))

    g.append(fitbox(605, 205, 390, 105,
                    "Ядро Linux: Дисципліна ліній PTY (n_tty)\n"
                    "• Реалізує віддалений режим обробки termios\n"
                    "• Генерує ехо-символи назад у /dev/ptmx\n"
                    "• Перетворює 0x03 (Ctrl+C) на сигнал SIGINT\n"
                    "• Передає дані підлеглому /dev/pts/N",
                    size=12, fill="#ffffff", stroke=LINE))

    g.append(arrow(800, 310, 800, 340, color=FIELD, sw=1.6))
    g.append(fitbox(720, 315, 160, 20, "читання з /dev/pts/N", size=10, fill="#ffffff", stroke=MUTED))

    g.append(fitbox(605, 340, 390, 90,
                    "Дочірній процес (Shell / vim / htop)\n"
                    "• fd 0, 1, 2 підключені до /dev/pts/N\n"
                    "• Керівний термінал сесії (TIOCSCTTY)\n"
                    "• Отримує SIGWINCH при зміні розміру",
                    size=12, fill="#e8f8f0", stroke=FIELD))

    # Зв'язок по мережі посередині
    g.append(fitbox(465, 210, 110, 60, "Зашифрований\nканал SSH\n(TCP 22)", size=11, fill="#ffffff", stroke=LINE, bold=True))
    g.append(arrow(435, 375, 465, 240, color=NEG, sw=1.8))
    g.append(arrow(575, 240, 605, 125, color=NEG, sw=1.8))

    # Нижній блок підсумку
    g.append(fitbox(80, 485, 880, 35,
                    "Зворотний потік: вивід програми з /dev/pts/N -> n_tty -> sshd -> SSH-пакет -> клієнт ssh -> локальний stdout",
                    size=11, fill="#ffffff", stroke=MUTED))

    render(os.path.join(IMG, 'ssh-session-pty-flow.svg'), W, H, *g,
           title="Архітектура та потік даних інтерактивного SSH-сеансу з PTY")


def fig_ssh_escape_state_machine():
    """Скінченний автомат ескейп-послідовностей клієнта OpenSSH."""
    W, H = 1000, 560
    g = []

    # Стан 0: Звичайний ввід
    g.append(rect(40, 80, 260, 120, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=8))
    g.append(text(170, 105, "Стан: NORMAL", size=14, color=INK, bold=True))
    g.append(fitbox(55, 120, 230, 68,
                    "Символи одразу шлються\n"
                    "в канал SSH_MSG_CHANNEL_DATA.\n"
                    "Символ ~ тут не діє",
                    size=12, fill="#ffffff", stroke=MUTED))

    # Стан 1: Початок нового рядка
    g.append(rect(370, 80, 260, 120, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=8))
    g.append(text(500, 105, "Стан: START_OF_LINE", size=14, color=NEG, bold=True))
    g.append(fitbox(385, 120, 230, 68,
                    "Щойно натиснуто Enter (\\r або \\n).\n"
                    "Клієнт очікує перший символ\n"
                    "нового рядка",
                    size=12, fill="#ffffff", stroke=NEG))

    # Стан 2: Очікування команди ескейпу
    g.append(rect(700, 80, 260, 120, fill="#fdecea", stroke=POS, sw=1.8, rx=8))
    g.append(text(830, 105, "Стан: ESCAPE_PENDING", size=14, color=POS, bold=True))
    g.append(fitbox(715, 120, 230, 68,
                    "Натиснуто ~ на початку рядка.\n"
                    "Символ буферизується локально\n"
                    "й у мережу не шлеться",
                    size=12, fill="#ffffff", stroke=POS))

    # Переходи між основними станами
    g.append(arrow(300, 120, 370, 120, color=NEG, sw=1.8))
    g.append(fitbox(315, 95, 42, 20, "Enter", size=11, fill="#ffffff", stroke=NEG, bold=True))

    g.append(arrow(630, 120, 700, 120, color=POS, sw=1.8))
    g.append(fitbox(645, 95, 40, 20, "~", size=12, fill="#ffffff", stroke=POS, bold=True))

    # Повернення зі START_OF_LINE до NORMAL
    g.append(arrow(370, 160, 300, 160, color=LINE, sw=1.6))
    g.append(fitbox(305, 165, 60, 18, "інший знак", size=10, fill="#ffffff", stroke=MUTED))

    # Обхідна лінія зверху для повернення з ESCAPE_PENDING до NORMAL
    g.append(line(830, 80, 830, 42, color=LINE, sw=1.5))
    g.append(line(830, 42, 170, 42, color=LINE, sw=1.5))
    g.append(arrow(170, 42, 170, 80, color=LINE, sw=1.5))
    g.append(fitbox(380, 32, 240, 22, "~~ або інший символ -> шле ~ у NORMAL", size=11, fill="#ffffff", stroke=MUTED))

    # Дії зі стану ESCAPE_PENDING (команди)
    actions = [
        (60, 310, 190, 180, "~. (крапка)\nМиттєвий розрив\n\nЗакриває TCP-сокет,\nскидає термінал із raw,\nповертає локальний shell", "#fdecea", POS),
        (290, 310, 190, 180, "~^Z (Ctrl+Z)\nФонування клієнта\n\nШле SIGTSTP процесу ssh,\nповертає керування shell.\nВідновлення: $ fg", "#eaf0fd", NEG),
        (520, 310, 190, 180, "~# (решітка)\nСписок прокидань\n\nДрукує в термінал\nперелік активних\nканалів і forwarded портів", "#e8f8f0", FIELD),
        (750, 310, 190, 180, "~C (велика C)\nКомандний рядок ssh>\n\nДозволяє на льоту додати\n-L, -R або -D прокидання\nбез перезапуску сеансу", "#fef7e7", "#d97706")
    ]
    for x, y, w, h, lbl, fill, st in actions:
        g.append(fitbox(x, y, w, h, lbl, size=12, fill=fill, stroke=st))

    g.append(arrow(750, 200, 160, 310, color=POS, sw=1.6))
    g.append(arrow(780, 200, 380, 310, color=NEG, sw=1.6))
    g.append(arrow(830, 200, 610, 310, color=FIELD, sw=1.6))
    g.append(arrow(880, 200, 840, 310, color="#d97706", sw=1.6))

    render(os.path.join(IMG, 'ssh-escape-state-machine.svg'), W, H, *g,
           title="Скінченний автомат ескейп-послідовностей клієнта OpenSSH")


if __name__ == '__main__':
    # Видаляємо старі невикористовувані SVG якщо є
    old_file = os.path.join(IMG, 'ssh-channel-multiplexing.svg')
    if os.path.exists(old_file):
        os.remove(old_file)
    fig_ssh_layer_stack()
    fig_ssh_session_pty_flow()
    fig_ssh_escape_state_machine()
    print('All 3 figures generated successfully.')