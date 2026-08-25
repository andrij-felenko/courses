# -*- coding: utf-8 -*-
"""Фігури до теми «Шар TTY та віртуальні консолі: лінійна дисципліна й режими клавіатури»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_tty_subsystem_architecture():
    """Повна архітектура підсистеми TTY у ядрі Linux: від файлового дескриптора до драйверів."""
    W, H = 1040, 640
    g = []

    # 1. Верхній шар: Простір користувача
    g.append(rect(40, 30, 960, 70, fill="#eef2f7", stroke=NEG, sw=1.8))
    g.append(text(520, 58, "Простір користувача: процеси, термінальні емулятори, системні виклики",
                  size=15, bold=True, color=NEG))
    g.append(text(520, 82, "read(fd, buf, n)  ·  write(fd, buf, n)  ·  ioctl(fd, TCSETS / TIOCSWINSZ / TIOCSETD, …)",
                  size=13, color=MUTED))

    # Стрілка вниз від користувача до VFS
    g.append(arrow(520, 100, 520, 136, color=INK, sw=1.8))

    # 2. Шар TTY Core (VFS & tty_io.c)
    g.append(rect(40, 140, 960, 90, fill="#fdfaf3", stroke=MUTED, sw=1.6))
    g.append(text(520, 168, "Шар ядра TTY (drivers/tty/tty_io.c · struct tty_struct)",
                  size=14.5, bold=True, color=INK))
    g.append(fitbox(60, 185, 430, 36, "Маршрутизація за major/minor · Таблиця відкритих tty",
                    size=12, fill="#ffffff", stroke=MUTED))
    g.append(fitbox(510, 185, 470, 36, "Сесії та групи процесів: pgrp, session, керування завданнями",
                    size=12, fill="#ffffff", stroke=MUTED))

    # Стрілка між TTY Core та Line Discipline
    g.append(arrow(520, 230, 520, 266, color=INK, sw=1.8))

    # 3. Шар лінійної дисципліни
    g.append(rect(40, 270, 960, 120, fill="#f4fbf7", stroke=FIELD, sw=1.8))
    g.append(text(520, 296, "Шар лінійної дисципліни (struct tty_ldisc · tty_ldisc_ops)",
                  size=14.5, bold=True, color=FIELD))

    # Блоки дисциплін
    g.append(rect(60, 312, 440, 66, fill="#ffffff", stroke=FIELD, sw=1.5))
    g.append(text(280, 334, "N_TTY (ldisc 0 — типова дисципліна термінала)", size=13, bold=True, color=FIELD))
    g.append(text(280, 358, "ICANON (буфер рядка) · ISIG (Ctrl+C, Ctrl+Z) · ECHO · OPOST", size=11.5, color=INK))

    g.append(rect(520, 312, 460, 66, fill="#ffffff", stroke=MUTED, sw=1.5))
    g.append(text(750, 334, "Спеціалізовані дисципліни (перемикання через TIOCSETD)", size=13, bold=True, color=INK))
    g.append(text(750, 358, "N_PPP (мережеві пакети) · N_GSM0710 (модем) · N_SLCAN (CAN-шина)", size=11.5, color=MUTED))

    # Стрілка між Line Discipline та Flip Buffers
    g.append(arrow(520, 390, 520, 426, color=INK, sw=1.8))

    # 4. Шар буферизації (Flip Buffers & Workqueue)
    g.append(rect(40, 430, 960, 58, fill="#fdf3f2", stroke=POS, sw=1.6))
    g.append(text(520, 454, "Кільцевий буфер tty_buffer (Flip Buffers) і робоча черга flush_to_ldisc",
                  size=13.5, bold=True, color=POS))
    g.append(text(520, 474, "Асинхронний міст: драйвер/переривання кладе байти в atomic-контексті → воркер передає їх у ldisc",
                  size=11.5, color=INK))

    # Стрілки вниз до трьох родин драйверів
    g.append(arrow(200, 488, 200, 524, color=INK, sw=1.8))
    g.append(arrow(520, 488, 520, 524, color=INK, sw=1.8))
    g.append(arrow(840, 488, 840, 524, color=INK, sw=1.8))

    # 5. Шар драйверів (3 родини)
    # Послідовні порти
    g.append(rect(40, 528, 300, 84, fill="#ffffff", stroke=MUTED, sw=1.5))
    g.append(text(190, 552, "Послідовні порти (UART)", size=13, bold=True, color=INK))
    g.append(text(190, 574, "/dev/ttyS*, /dev/ttyUSB*", size=12, color=MUTED))
    g.append(text(190, 596, "8250, serial_core, USB CDC-ACM", size=11, color=INK))

    # Псевдотермінали
    g.append(rect(360, 528, 320, 84, fill="#ffffff", stroke=MUTED, sw=1.5))
    g.append(text(520, 552, "Псевдотермінали (PTY)", size=13, bold=True, color=INK))
    g.append(text(520, 574, "/dev/ptmx ⇄ /dev/pts/N", size=12, color=MUTED))
    g.append(text(520, 596, "SSH-сервери, tmux, емулятори (pty.c)", size=11, color=INK))

    # Віртуальні консолі
    g.append(rect(700, 528, 300, 84, fill="#ffffff", stroke=MUTED, sw=1.5))
    g.append(text(850, 552, "Віртуальні консолі (VT)", size=13, bold=True, color=INK))
    g.append(text(850, 574, "/dev/tty1..63, /dev/tty0", size=12, color=MUTED))
    g.append(text(850, 596, "vt.c, keyboard.c, fbcon / vgacon", size=11, color=INK))

    render(os.path.join(IMG, 'tty-subsystem-architecture.svg'), W, H, *g,
           title="Архітектура підсистеми TTY у ядрі Linux")


def fig_n_tty_buffer_ring():
    """Механіка кільцевого буфера read_buf лінійної дисципліни N_TTY."""
    W, H = 1040, 580
    g = []

    g.append(fitbox(40, 24, 960, 48,
                    "Кільцевий буфер read_buf (4096 байтів) у struct n_tty_data",
                    size=15, bold=True, fill="#eef2f7", stroke=NEG))

    # Основний прямокутник кільцевого буфера
    BX, BY, BW, BH = 80, 110, 880, 90
    g.append(rect(BX, BY, BW, BH, fill="#ffffff", stroke=INK, sw=2))

    # Секції буфера
    # 1. Прочитані дані (вільні)
    g.append(rect(BX, BY, 180, BH, fill="#f4f6f8", stroke=MUTED, sw=1))
    g.append(text(BX + 90, BY + 42, "Вільна пам'ять", size=12, color=MUTED))
    g.append(text(BX + 90, BY + 62, "(вже віддано в read)", size=11, color=MUTED))

    # 2. Зафіксовані рядки (готові до видачі в read)
    g.append(rect(BX + 180, BY, 320, BH, fill="#eafaf1", stroke=FIELD, sw=1.5))
    g.append(text(BX + 340, BY + 38, "Зафіксовані рядки: «ls -la\\n», «cat file\\n»", size=13, bold=True, color=FIELD))
    g.append(text(BX + 340, BY + 62, "Готові до видачі в системний виклик read()", size=11.5, color=INK))

    # 3. Поточний незавершений рядок (редагування наживо)
    g.append(rect(BX + 500, BY, 240, BH, fill="#fdf3f2", stroke=POS, sw=1.5))
    g.append(text(BX + 620, BY + 38, "Поточний рядок: «grepp»", size=13, bold=True, color=POS))
    g.append(text(BX + 620, BY + 62, "Забій (0x7F) зітре останнє «p»", size=11.5, color=POS))

    # 4. Вільне місце до кінця
    g.append(rect(BX + 740, BY, 140, BH, fill="#f4f6f8", stroke=MUTED, sw=1))
    g.append(text(BX + 810, BY + 50, "Вільний буфер", size=12, color=MUTED))

    # Покажчики
    # read_tail
    g.append(arrow(BX + 180, BY + BH + 50, BX + 180, BY + BH + 6, color=INK, sw=1.8))
    g.append(text(BX + 180, BY + BH + 70, "read_tail", size=13, bold=True, color=INK))
    g.append(text(BX + 180, BY + BH + 90, "звідси читає read()", size=11.5, color=MUTED))

    # canon_head / commit_head
    g.append(arrow(BX + 500, BY + BH + 50, BX + 500, BY + BH + 6, color=FIELD, sw=1.8))
    g.append(text(BX + 500, BY + BH + 70, "canon_head (commit_head)", size=13, bold=True, color=FIELD))
    g.append(text(BX + 500, BY + BH + 90, "межа зафіксованого '\\n'", size=11.5, color=FIELD))

    # read_head
    g.append(arrow(BX + 740, BY + BH + 50, BX + 740, BY + BH + 6, color=POS, sw=1.8))
    g.append(text(BX + 740, BY + BH + 70, "read_head", size=13, bold=True, color=POS))
    g.append(text(BX + 740, BY + BH + 90, "сюди пише воркер ldisc", size=11.5, color=POS))

    # Пояснювальний блок знизу
    g.append(rect(40, 340, 960, 210, fill="#ffffff", stroke=MUTED, sw=1.5))
    g.append(text(520, 368, "Обробка вхідного байта в n_tty_receive_buf()", size=14, bold=True, color=INK))

    g.append(fitbox(60, 390, 430, 60,
                    "1. Перевірка сигналів (ISIG):\nЯкщо байт == VINTR (0x03) → kill_pgrp(SIGINT);\nбайт відкидається і в read_buf НЕ потрапляє",
                    size=12, fill="#fdf3f2", stroke=POS))

    g.append(fitbox(510, 390, 470, 60,
                    "2. Редагування рядка (ICANON):\nЯкщо байт == ERASE (0x7F) → read_head зменшується;\nЯкщо байт == KILL (0x15) → read_head = canon_head",
                    size=12, fill="#fdfaf3", stroke=MUTED))

    g.append(fitbox(60, 465, 430, 64,
                    "3. Фіксація рядка (EOL / EOF):\nСимвол '\\n' зсуває canon_head до read_head;\nпробуджує процеси в tty->read_wait",
                    size=12, fill="#eafaf1", stroke=FIELD))

    g.append(fitbox(510, 465, 470, 64,
                    "4. Дроселювання потоку (Flow Control):\nЯкщо вільне місце < 256 байтів → tty_throttle();\nдрайвер опускає RTS або шле XOFF (0x13)",
                    size=12, fill="#eef2f7", stroke=NEG))

    render(os.path.join(IMG, 'n-tty-buffer-ring.svg'), W, H, *g,
           title="Кільцевий буфер read_buf у лінійній дисципліні N_TTY")


def fig_vt_keyboard_modes_pipeline():
    """Конвеєр обробки подій клавіатури у віртуальній консолі та 5 режимів KDSKBMODE."""
    W, H = 1040, 620
    g = []

    # Залізо клавіатури
    g.append(fitbox(40, 24, 960, 50,
                    "Фізична клавіатура (USB HID / PS/2) → Підсистема evdev (/dev/input/event*)",
                    size=14.5, bold=True, fill="#eef2f7", stroke=NEG))

    g.append(arrow(520, 76, 520, 114, color=INK, sw=1.8))

    # Драйвер keyboard.c
    g.append(rect(40, 116, 960, 70, fill="#fdfaf3", stroke=INK, sw=1.6))
    g.append(text(520, 142, "Обробник драйвера віртуальної консолі (drivers/tty/vt/keyboard.c · kbd_event)",
                  size=14, bold=True, color=INK))
    g.append(text(520, 166, "Отримує EV_KEY (код клавіші, натиск/відпускання) · Перевіряє поточний режим клавіатури KDSKBMODE",
                  size=12, color=MUTED))

    # 5 розгалужень режимів
    Y0 = 230
    BOX_W = 180
    BOX_H = 180
    GAP = 15
    START_X = 40

    modes = [
        ("K_RAW (0x00)", "Сирі сканкоди XT (Set 1)",
         "байт на натиск (1..127);\nбайт | 0x80 на відпускання;\nпрефікс 0xE0 для розширених;\n(X11 без evdev)",
         "#fdf3f2", POS),
        ("K_XLATE (0x01)", "Таблиця розкладки ядра",
         "Обробка Shift/Ctrl/Alt;\nгенерація 8-біт символів\n(ISO-8859-1 / Latin-1)\nабо ESC-послідовностей",
         "#ffffff", INK),
        ("K_MEDIUMRAW (0x02)", "Медіум-сканкоди",
         "1 байт для кодів 0..127;\n2-3 байти для кодів >= 128;\n(уніфікований сканкод\nбез прив'язки до порту)",
         "#fdfaf3", MUTED),
        ("K_UNICODE (0x03)", "Повний UTF-8 ввід",
         "Таблиця розкладки видає\n16-біт Unicode (UCS-2);\nkeyboard.c кодує їх\nу 1..4 байти UTF-8",
         "#eafaf1", FIELD),
        ("K_OFF (0x04)", "Вимкнено у VT",
         "keyboard.c повністю ігнорує\nусі натиски клавіш;\nWayland/Xorg читають\n/dev/input/event* напряму",
         "#eef2f7", NEG),
    ]

    for i, (m_title, m_sub, m_desc, fill_c, stroke_c) in enumerate(modes):
        x = START_X + i * (BOX_W + GAP)
        g.append(arrow(520, 188, x + BOX_W / 2.0, Y0 - 6, color=stroke_c, sw=1.6))
        g.append(rect(x, Y0, BOX_W, BOX_H, fill=fill_c, stroke=stroke_c, sw=1.6))
        g.append(text(x + BOX_W / 2.0, Y0 + 26, m_title, size=12.5, bold=True, color=stroke_c))
        g.append(text(x + BOX_W / 2.0, Y0 + 46, m_sub, size=10.5, bold=True, color=INK))
        g.append(mtext(x + BOX_W / 2.0, Y0 + 72, m_desc, size=10.5, color=MUTED, lh=1.35))

    # Стрілки вниз до TTY Flip Buffer або прямого обходу
    for i in range(4):
        x = START_X + i * (BOX_W + GAP) + BOX_W / 2.0
        g.append(arrow(x, Y0 + BOX_H + 4, x, Y0 + BOX_H + 54, color=INK, sw=1.6))

    # Окремий вихід для K_OFF
    x_off = START_X + 4 * (BOX_W + GAP) + BOX_W / 2.0
    g.append(arrow(x_off, Y0 + BOX_H + 4, x_off, Y0 + BOX_H + 54, color=NEG, sw=1.8))

    # Нижній шар: Куди потрапляють дані
    g.append(rect(40, 480, 765, 100, fill="#ffffff", stroke=FIELD, sw=1.6))
    g.append(text(422, 510, "Потік байтів у кільцевий буфер tty_buffer активної консолі (/dev/ttyN)",
                  size=13.5, bold=True, color=FIELD))
    g.append(text(422, 534, "Далі проходить крізь лінійну дисципліну N_TTY до командної оболонки (bash / zsh)",
                  size=12, color=INK))
    g.append(text(422, 558, "Гарячі клавіші Alt+Fn перехоплюються keyboard.c до запису в буфер tty",
                  size=11.5, color=MUTED))

    g.append(rect(820, 480, 180, 100, fill="#eef2f7", stroke=NEG, sw=1.8))
    g.append(text(910, 510, "Прямий ввід", size=13, bold=True, color=NEG))
    g.append(text(910, 532, "libinput", size=12, bold=True, color=INK))
    g.append(text(910, 554, "у композиторі", size=11.5, color=MUTED))
    g.append(text(910, 570, "Wayland / Xorg", size=11, color=MUTED))

    render(os.path.join(IMG, 'vt-keyboard-modes-pipeline.svg'), W, H, *g,
           title="Конвеєр обробки подій клавіатури у віртуальній консолі та режими KDSKBMODE")


def fig_vt_switching_handover():
    """Діаграма кооперативного перемикання VT (VT_PROCESS) між графічним сервером і консоллю."""
    W, H = 1040, 660
    g = []

    # Колони (учасники взаємодії)
    cols = [
        (130, "Користувач / Ввід\n(Ctrl+Alt+F3)", NEG),
        (390, "Ядро Linux\n(підсистема vt.c)", INK),
        (650, "Графічний сервер\n(Wayland / Xorg на VT2)", POS),
        (910, "Відеоадаптер / DRM\n(KMS / Direct Rendering)", FIELD),
    ]

    for cx, label, color in cols:
        g.append(rect(cx - 100, 24, 200, 50, fill="#f4f6f8", stroke=color, sw=1.8))
        g.append(mtext(cx, 44, label, size=12.5, bold=True, color=color, lh=1.25))
        g.append(line(cx, 76, cx, 620, color="#d0d7de", sw=1.5, dash="5,5"))

    # Послідовність подій
    # 1. Сигнал перемикання
    g.append(arrow(130, 110, 390, 110, color=NEG, sw=1.8))
    g.append(text(260, 102, "1. Натиск Ctrl+Alt+F3", size=12, bold=True, color=NEG))

    # 2. Ядро надсилає relsig графічному серверу
    g.append(rect(290, 130, 200, 36, fill="#fdfaf3", stroke=MUTED))
    g.append(text(390, 152, "VT2 у режимі VT_PROCESS", size=11.5, color=MUTED))

    g.append(arrow(390, 185, 650, 185, color=POS, sw=1.8))
    g.append(text(520, 177, "2. Сигнал relsig (SIGUSR1)", size=12, bold=True, color=POS))

    # 3. Сервер звільняє DRM master
    g.append(rect(550, 205, 200, 42, fill="#fdf3f2", stroke=POS))
    g.append(text(650, 222, "Зупиняє рендеринг,", size=11, color=POS))
    g.append(text(650, 238, "блокує пристрої вводу", size=11, color=POS))

    g.append(arrow(650, 265, 910, 265, color=FIELD, sw=1.8))
    g.append(text(780, 257, "3. drmDropMaster()", size=12, bold=True, color=FIELD))

    # 4. Сервер підтверджує звільнення ядру
    g.append(arrow(650, 310, 390, 310, color=POS, sw=1.8))
    g.append(text(520, 302, "4. ioctl(VT_RELDISP, 1)", size=12, bold=True, color=POS))

    # 5. Ядро перемикає активну VT
    g.append(rect(290, 335, 200, 48, fill="#eafaf1", stroke=FIELD))
    g.append(text(390, 355, "5. Перемикання на VT3,", size=11.5, bold=True, color=FIELD))
    g.append(text(390, 372, "відновлення fbcon / тексту", size=11, color=INK))

    g.append(arrow(390, 400, 910, 400, color=FIELD, sw=1.8))
    g.append(text(650, 392, "Відновлення текстового кадрового буфера", size=11.5, color=FIELD))

    # 6. Зворотне перемикання на VT2
    g.append(arrow(130, 440, 390, 440, color=NEG, sw=1.8))
    g.append(text(260, 432, "6. Натиск Alt+F2 (повернення)", size=12, bold=True, color=NEG))

    g.append(rect(290, 460, 200, 36, fill="#fdfaf3", stroke=MUTED))
    g.append(text(390, 482, "Ядро активує VT2", size=11.5, color=MUTED))

    # 7. Ядро надсилає acqsig графічному серверу
    g.append(arrow(390, 515, 650, 515, color=POS, sw=1.8))
    g.append(text(520, 507, "7. Сигнал acqsig (SIGUSR2)", size=12, bold=True, color=POS))

    # 8. Сервер захоплює DRM master і підтверджує
    g.append(arrow(650, 545, 910, 545, color=FIELD, sw=1.8))
    g.append(text(780, 537, "8. drmSetMaster()", size=12, bold=True, color=FIELD))

    g.append(arrow(650, 580, 390, 580, color=POS, sw=1.8))
    g.append(text(520, 572, "9. ioctl(VT_RELDISP, VT_ACKACQ)", size=12, bold=True, color=POS))

    g.append(rect(550, 595, 200, 30, fill="#eafaf1", stroke=FIELD))
    g.append(text(650, 615, "Відновлення графічного екрана", size=11, bold=True, color=FIELD))

    render(os.path.join(IMG, 'vt-switching-handover.svg'), W, H, *g,
           title="Кооперативний протокол перемикання VT між ядром і графічним сервером")


if __name__ == '__main__':
    fig_tty_subsystem_architecture()
    fig_n_tty_buffer_ring()
    fig_vt_keyboard_modes_pipeline()
    fig_vt_switching_handover()
    print("All figures generated successfully.")
