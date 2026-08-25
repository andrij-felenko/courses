# -*- coding: utf-8 -*-
"""Фігури до теми «Коли термінала немає»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_process_terminal_link():
    """Порівняння структури інтерактивного процесу та процесу без керуючого термінала в ядрі."""
    W, H = 1100, 520
    f = []

    f.append(text(W / 2, 40, "Анатомія процесу в ядрі: наявність проти відсутності керуючого термінала", size=16, bold=True))

    # Ліва колонка: Інтерактивний процес
    lx, lw = 40, 490
    f.append(rect(lx, 70, lw, 400, fill="#f8fafc", stroke=FIELD, sw=2, rx=8))
    f.append(text(lx + lw / 2, 98, "Інтерактивний процес (Bash / SSH / TTY)", size=15, bold=True, color=FIELD))

    f.append(fitbox(lx + 20, 120, lw - 40, 70,
                    "task_struct -> signal_struct\ntty = struct tty_struct* (наприклад, /dev/pts/4)\nЛідер або член сеансу термінала",
                    size=13, fill=BG))

    f.append(fitbox(lx + 20, 205, lw - 40, 75,
                    "Дескриптори входу/виходу:\n0 (stdin) -> /dev/pts/4 (читання з клавіатури)\n1, 2 (stdout, stderr) -> /dev/pts/4 (екран)",
                    size=13, fill=BG))

    f.append(fitbox(lx + 20, 295, lw - 40, 65,
                    "Буферизація libc (isatty(1) == 1):\nstdout: лінійна (_IOLBF) — скидання на кожному '\\n'\nІнтерактивні підказки з'являються миттєво",
                    size=12.5, fill="#eef7f0", stroke=FIELD))

    f.append(fitbox(lx + 20, 375, lw - 40, 80,
                    "Взаємодія з /dev/tty та сигналами:\nopen(\"/dev/tty\") -> успіх (дескриптор на /dev/pts/4)\nСигнали клавіатури: Ctrl+C -> SIGINT, Ctrl+Z -> SIGTSTP",
                    size=12.5, fill=BG))

    # Права колонка: Процес без термінала (Headless)
    rx, rw = 570, 490
    f.append(rect(rx, 70, rw, 400, fill="#f8fafc", stroke=POS, sw=2, rx=8))
    f.append(text(rx + rw / 2, 98, "Headless-процес (systemd / cron / Docker / CI)", size=15, bold=True, color=POS))

    f.append(fitbox(rx + 20, 120, rw - 40, 70,
                    "task_struct -> signal_struct\ntty = NULL (керівний термінал відсутній)\nСеанс від'єднаний від будь-якого TTY",
                    size=13, fill=BG))

    f.append(fitbox(rx + 20, 205, rw - 40, 75,
                    "Дескриптори входу/виходу:\n0 (stdin) -> /dev/null або закритий\n1, 2 (stdout, stderr) -> journald socket / pipe / /dev/null",
                    size=13, fill=BG))

    f.append(fitbox(rx + 20, 295, rw - 40, 65,
                    "Буферизація libc (isatty(1) == 0):\nstdout: блочна (_IOFBF) — накопичення до 4096 байтів\nВивід у журнал затримується або губиться при падінні",
                    size=12.5, fill="#fdecea", stroke=POS))

    f.append(fitbox(rx + 20, 375, rw - 40, 80,
                    "Взаємодія з /dev/tty та сигналами:\nopen(\"/dev/tty\") -> фатальна помилка ENXIO\nНемає клавіатурних сигналів; зупинка лише через SIGTERM/SIGKILL",
                    size=12.5, fill=BG))

    f.append(text(W / 2, 495, "Ядро зв'язує процес із терміналом через покажчик tty; коли покажчик NULL — середовище стає неінтерактивним", size=13, color=MUTED))

    render(os.path.join(IMG, 'process-terminal-link.svg'), W, H, *f)


def fig_double_fork_steps():
    """Чотири кроки класичної Unix-демонізації: подвійне розгалуження та ізоляція."""
    W, H = 1120, 480
    f = []

    f.append(text(W / 2, 38, "Класичний обряд подвійного fork: навіщо потрібен кожен крок", size=16, bold=True))

    bw, bh = 240, 175
    y0 = 75
    xs = [30, 305, 580, 855]

    steps = [
        ("1. Перший fork()",
         "Батько: exit(0)\nДитина: продовжує\n\nМета: гарантувати, що\nдитина не є лідером групи\n(PID != PGID),\nі відпустити оболонку",
         "#eaf0fd", NEG),
        ("2. setsid()",
         "Дитина викликає setsid()\n\nСтворюється новий сеанс:\nSID = PID, PGID = PID\nДитина — лідер сеансу.\nКерівний термінал скинуто",
         "#eef7f0", FIELD),
        ("3. Другий fork()",
         "Лідер сеансу: exit(0)\nОнук: продовжує\n\nМета: онук не є лідером\nсеансу (PID != SID),\nтому ніколи не захопить\nтермінал через open()",
         "#fdecea", POS),
        ("4. Очищення",
         "umask(0) — повний контроль\nchdir(\"/\") — розблокувати ФС\n\nclose(0, 1, 2) або\ndup2(/dev/null, 0, 1, 2)\nІзоляція від спадщини",
         FILL, LINE),
    ]

    for i, (title, body, fill_c, stroke_c) in enumerate(steps):
        x = xs[i]
        f.append(rect(x, y0, bw, bh, fill=fill_c, stroke=stroke_c, sw=2, rx=6))
        f.append(text(x + bw / 2, y0 + 26, title, size=14, bold=True, color=stroke_c))
        f.append(fitbox(x + 10, y0 + 40, bw - 20, bh - 50, body, size=12, fill=BG, stroke=MUTED, sw=1))

    # Стрілки між етапами
    for i in range(3):
        f.append(arrow(xs[i] + bw + 5, y0 + bh / 2, xs[i + 1] - 5, y0 + bh / 2, sw=2.2))

    # Нижня аналітична плашка
    f.append(rect(30, 275, 1065, 150, fill="#fdfefe", stroke=MUTED, sw=1.5, rx=6))
    f.append(text(W / 2, 305, "Ключова різниця між першим та другим fork у стандарті POSIX / System V:", size=14, bold=True))
    f.append(mtext(W / 2, 340,
                   ["• Без першого fork виклик setsid() поверне EPERM, якщо процес запущено як лідер групи в пайплайні оболонки.",
                    "• Без другого fork лідер сеансу на системах System V при відкритті будь-якого модему чи tty без прапорця O_NOCTTY",
                    "  автоматично робить його новим керуючим терміналом сеансу і знову стає вразливим до сигналів SIGHUP."],
                   size=13, color=INK))

    f.append(text(W / 2, 455, "Подвійний fork перетворює процес на сироту без прав лідера сеансу, унеможливлюючи повернення термінала", size=13, color=MUTED))

    render(os.path.join(IMG, 'double-fork-steps.svg'), W, H, *f)


def fig_stdio_buffering_trap():
    """Пастка буферизації стандартного виводу: термінал проти каналу або файлу."""
    W, H = 1080, 480
    f = []

    f.append(text(W / 2, 38, "Пастка буферизації stdio: чому зникають логи в неінтерактивному середовищі", size=16, bold=True))

    # Верхній блок: TTY активний
    ty = 75
    f.append(rect(40, ty, 1000, 160, fill="#f8fafc", stroke=FIELD, sw=2, rx=8))
    f.append(text(80, ty + 30, "Інтерактивний запуск у терміналі (isatty(fileno(stdout)) == 1)", size=14.5, bold=True, color=FIELD, anchor="start"))

    f.append(fitbox(60, ty + 50, 260, 85,
                    "printf(\"Processing batch...\\n\");\n\nlibc визначає:\nпристрій є терміналом",
                    size=12.5, fill=BG))

    f.append(arrow(330, ty + 92, 410, ty + 92, sw=2, color=FIELD))
    f.append(text(370, ty + 80, "Символ '\\n'", size=12, color=FIELD))

    f.append(fitbox(420, ty + 50, 310, 85,
                    "Режим _IOLBF (Line Buffered):\nБуфер скидається негайно\nпри кожному переході рядка",
                    size=12.5, fill="#eef7f0", stroke=FIELD))

    f.append(arrow(740, ty + 92, 820, ty + 92, sw=2, color=FIELD))

    f.append(fitbox(830, ty + 50, 190, 85,
                    "Термінал / Екран\n\nКористувач бачить\nрядок миттєво",
                    size=12.5, fill=BG))

    # Нижній блок: Headless середовище
    by = 265
    f.append(rect(40, by, 1000, 160, fill="#f8fafc", stroke=POS, sw=2, rx=8))
    f.append(text(80, by + 30, "Запуск у cron / systemd / пайпі Docker (isatty(fileno(stdout)) == 0)", size=14.5, bold=True, color=POS, anchor="start"))

    f.append(fitbox(60, by + 50, 260, 85,
                    "printf(\"Processing batch...\\n\");\n\nlibc визначає:\nвихід перенаправлено",
                    size=12.5, fill=BG))

    f.append(arrow(330, by + 92, 410, by + 92, sw=2, color=POS))
    f.append(text(370, by + 80, "Буфер чекає", size=12, color=POS))

    f.append(fitbox(420, by + 50, 310, 85,
                    "Режим _IOFBF (Fully Buffered):\nБуфер розміром 4096 байтів\nутримує рядки всередині пам'яті",
                    size=12.5, fill="#fdecea", stroke=POS))

    f.append(arrow(740, by + 92, 820, by + 92, sw=2, color=POS))

    f.append(fitbox(830, by + 50, 190, 85,
                    "Журнал / Файл / Pipe\n\nПорожньо до 4 КіБ\nабо до падіння процесу",
                    size=12.5, fill=BG))

    f.append(text(W / 2, 455, "Лікування: setvbuf(stdout, NULL, _IOLBF, 0) або явний fflush(stdout) після кожного запису логу", size=13, color=MUTED))

    render(os.path.join(IMG, 'stdio-buffering-trap.svg'), W, H, *f)


if __name__ == '__main__':
    fig_process_terminal_link()
    fig_double_fork_steps()
    fig_stdio_buffering_trap()
    print("ok")
