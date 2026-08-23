# -*- coding: utf-8 -*-
"""figs.py — генератор SVG-ілюстрацій для теми tracing-one-call."""

import os
import sys

# Шлях до спільного модуля svgkit у scripts/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_tracing_layers_overview():
    """Повний наскрізний шлях виклику write(1, msg, 6): від юзерспейсу до заліза й назад."""
    w, h = 880, 680
    frags = []

    # Заголовок / розділення областей
    frags.append(rect(20, 20, 840, 160, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(40, 42, "ПРОСТІР КОРИСТУВАЧА (User Space / Ring 3)", size=12, color=MUTED, anchor="start", bold=True))

    frags.append(rect(20, 190, 840, 410, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(40, 212, "ПРОСТІР ЯДРА (Kernel Space / Ring 0)", size=12, color=FIELD, anchor="start", bold=True))

    frags.append(rect(20, 610, 840, 55, fill="#fef2f2", stroke="#fca5a5", sw=1.5, rx=8))
    frags.append(text(40, 632, "АПАРАТНИЙ РІВЕНЬ (Hardware / UART / Memory)", size=12, color=POS, anchor="start", bold=True))

    # Ліва колонка: Шлях «Вниз» (Вхід і виконання запису)
    frags.append(fitbox(50, 55, 340, 44, "1. Застосунок: write(1, \"hello\\n\", 6)\nВиклик функції C / C++", size=11, fill="#ffffff", stroke="#94a3b8", bold=True))
    frags.append(arrow(220, 99, 220, 115, color=LINE, sw=2))

    frags.append(fitbox(50, 115, 340, 55, "2. glibc: обгортка системного виклику\n%rax=1, %rdi=1, %rsi=buf, %rdx=6 -> syscall", size=11, fill="#ffffff", stroke="#94a3b8", bold=True))
    frags.append(arrow(220, 170, 220, 225, color=POS, sw=2.5))
    frags.append(text(275, 198, "syscall (пастка CPU)", size=11, color=POS, bold=True))

    frags.append(fitbox(50, 225, 340, 60, "3. Точка входу: entry_SYSCALL_64\nswapgs -> стек ядра -> збереження pt_regs -> do_syscall_64()", size=11, fill="#ffffff", stroke="#86efac", bold=True))
    frags.append(arrow(220, 285, 220, 305, color=LINE, sw=2))

    frags.append(fitbox(50, 305, 340, 60, "4. Диспетчер викликів ядра\nsys_call_table[1] -> ksys_write(1, buf, 6)\nfget_light() -> пошук struct file за fd=1", size=11, fill="#ffffff", stroke="#86efac", bold=True))
    frags.append(arrow(220, 365, 220, 385, color=LINE, sw=2))

    frags.append(fitbox(50, 385, 340, 60, "5. Шар VFS: vfs_write()\nПеревірка прав доступу, rw_verify_area()\nfile->f_op->write_iter() (вибір драйвера)", size=11, fill="#ffffff", stroke="#86efac", bold=True))
    frags.append(arrow(220, 445, 220, 465, color=LINE, sw=2))

    frags.append(fitbox(50, 465, 340, 60, "6. Дисципліна лінії TTY: n_tty_write()\nОбробка символів, transl OPOST/ONLCR ('\\n' -> '\\r\\n')\ncopy_from_user(kbuf, ubuf, 6) зі SMAP", size=11, fill="#ffffff", stroke="#86efac", bold=True))
    frags.append(arrow(220, 525, 220, 545, color=LINE, sw=2))

    frags.append(fitbox(50, 545, 340, 48, "7. Драйвер пристрою: uart_write() / 8250\nЗапис байтів у кільцевий буфер драйвера порта", size=11, fill="#ffffff", stroke="#86efac", bold=True))
    frags.append(arrow(220, 593, 220, 620, color=POS, sw=2))

    frags.append(fitbox(50, 620, 340, 38, "8. Контролер UART: запис у FIFO передавача\nАпаратний зсувний регістр відправляє біти по дроту TX", size=10, fill="#ffffff", stroke="#fca5a5", bold=True))

    # Перехід знизу вправо
    frags.append(arrow(390, 638, 490, 638, color=FIELD, sw=2))
    frags.append(text(440, 628, "готово (6 Б)", size=10, color=FIELD, bold=True))

    # Права колонка: Шлях «Вгору» (Повернення результату)
    frags.append(fitbox(490, 545, 340, 48, "Драйвер підтверджує передачу\nПовернення кількості записаних байтів: ret = 6", size=11, fill="#ffffff", stroke="#86efac", bold=True))
    frags.append(arrow(660, 545, 660, 525, color=LINE, sw=2))

    frags.append(fitbox(490, 465, 340, 60, "VFS оновлює стан\nОновлення f_pos, mtime/ctime для файлів,\nзвільнення посилання на struct file (fdput)", size=11, fill="#ffffff", stroke="#86efac", bold=True))
    frags.append(arrow(660, 465, 660, 365, color=LINE, sw=2))

    frags.append(fitbox(490, 305, 340, 60, "Підготовка виходу з ядра: syscall_exit_work\nПеревірка сигналів, перепланування (need_resched),\npt_regs->rax = 6 (або -errno)", size=11, fill="#ffffff", stroke="#86efac", bold=True))
    frags.append(arrow(660, 305, 660, 225, color=LINE, sw=2))

    frags.append(fitbox(490, 225, 340, 55, "Повернення в Ring 3: sysretq\nВідновлення RIP <- RCX, RFLAGS <- R11,\nвідновлення стека користувача RSP", size=11, fill="#ffffff", stroke="#86efac", bold=True))
    frags.append(arrow(660, 225, 660, 170, color=FIELD, sw=2.5))
    frags.append(text(715, 198, "sysretq (вихід у Ring 3)", size=11, color=FIELD, bold=True))

    frags.append(fitbox(490, 115, 340, 55, "glibc: перевірка %rax\nЯкщо rax in [-4095..-1] -> errno = -rax, ret = -1\nІнакше -> повернення 6 без змін", size=11, fill="#ffffff", stroke="#94a3b8", bold=True))
    frags.append(arrow(660, 115, 660, 99, color=LINE, sw=2))

    frags.append(fitbox(490, 55, 340, 44, "Застосунок продовжує виконання\nОтримано результат 6, наступний рядок коду", size=11, fill="#ffffff", stroke="#94a3b8", bold=True))

    render(os.path.join(OUT_DIR, "tracing-layers-overview.svg"), w, h, *frags)


def fig_fd_to_driver_dispatch():
    """Схема диспетчеризації всередині ядра: від fd до struct file, f_op та конкретного драйвера."""
    w, h = 860, 460
    frags = []

    # task_struct та files_struct
    frags.append(fitbox(30, 40, 220, 90, "struct task_struct (поточний потік)\npid = 1420, comm = \"app\"\nstruct files_struct *files\nstruct mm_struct *mm", size=11, fill="#ffffff", stroke="#94a3b8", bold=True))
    frags.append(arrow(250, 85, 290, 85, color=LINE, sw=2))

    # files_struct & fdtable
    frags.append(fitbox(290, 40, 230, 110, "struct files_struct\nstruct fdtable *fdt\nstruct file *fd_array[64]\n  fd 0 -> stdin (tty)\n  fd 1 -> stdout (tty)\n  fd 2 -> stderr (tty)", size=11, fill="#ffffff", stroke="#94a3b8", bold=True))
    frags.append(arrow(520, 105, 570, 105, color=LINE, sw=2))

    # struct file
    frags.append(fitbox(570, 40, 260, 130, "struct file (опис відкритого файлу)\nloff_t f_pos = 0\nfmode_t f_mode = FMODE_WRITE\nstruct inode *f_inode\nconst struct file_operations *f_op", size=11, fill="#f0fdf4", stroke="#86efac", bold=True))

    # Стрілка вниз до f_op
    frags.append(arrow(700, 170, 700, 210, color=LINE, sw=2))

    # struct file_operations
    frags.append(fitbox(540, 210, 300, 95, "struct file_operations (віртуальна таблиця VFS)\n.read_iter = tty_read\n.write_iter = tty_write / redirected\n.unlocked_ioctl = tty_ioctl\n.open = tty_open", size=11, fill="#ffffff", stroke="#cbd5e1", bold=True))

    # Розгалуження f_op->write_iter на різні типи об'єктів
    frags.append(line(700, 305, 700, 330, color=LINE, sw=1.5))
    frags.append(line(120, 330, 750, 330, color=LINE, sw=1.5))

    frags.append(arrow(120, 330, 120, 360, color=LINE, sw=1.5))
    frags.append(fitbox(30, 360, 180, 70, "Термінал / TTY\ntty_write()\nn_tty_write()\nuart_write()", size=11, fill="#ffffff", stroke="#94a3b8", bold=True))

    frags.append(arrow(330, 330, 330, 360, color=LINE, sw=1.5))
    frags.append(fitbox(240, 360, 180, 70, "Файл на диску (ext4)\next4_file_write_iter()\ngeneric_perform_write()\nPage Cache / BIO", size=11, fill="#ffffff", stroke="#94a3b8", bold=True))

    frags.append(arrow(540, 330, 540, 360, color=LINE, sw=1.5))
    frags.append(fitbox(450, 360, 180, 70, "Мережевий сокет\nsock_write_iter()\ntcp_sendmsg()\nsk_buff / IP стек", size=11, fill="#ffffff", stroke="#94a3b8", bold=True))

    frags.append(arrow(750, 330, 750, 360, color=LINE, sw=1.5))
    frags.append(fitbox(660, 360, 180, 70, "Анонімний канал\npipe_write()\npipe_buffer кільце\nwake_up_interruptible()", size=11, fill="#ffffff", stroke="#94a3b8", bold=True))

    render(os.path.join(OUT_DIR, "fd-to-driver-dispatch.svg"), w, h, *frags)


def fig_boundary_crossing_registers():
    """Схема переходу межі: збереження регістрів у pt_regs, копіювання з юзерспейсу зі SMAP."""
    w, h = 860, 470
    frags = []

    # Ліва колонка: Простір користувача (регістри перед syscall)
    frags.append(rect(30, 30, 360, 410, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(50, 55, "ПРОСТІР КОРИСТУВАЧА (Стек і пам'ять програми)", size=12, color=MUTED, anchor="start", bold=True))

    frags.append(fitbox(50, 75, 320, 130, "Регістри процесу перед інструкцією syscall\nRAX = 1              (номер виклику write)\nRDI = 1              (дескриптор stdout)\nRSI = 0x7ffdb84a1010 (вказівник на буфер)\nRDX = 6              (розмір у байтах)\nRSP = 0x7ffdb84a0f80 (стек програми)\nRIP = 0x7f3b8a120400 (адреса syscall)", size=11, fill="#ffffff", stroke="#cbd5e1", bold=True))

    frags.append(fitbox(50, 240, 320, 80, "Буфер у віртуальній пам'яті процесу\nАдреса: 0x7ffdb84a1010 .. 0x7ffdb84a1016\nВміст: ['h', 'e', 'l', 'l', 'o', '\\n']\nДоступ: доступний для читання програмі", size=11, fill="#ffffff", stroke="#cbd5e1", bold=True))

    frags.append(fitbox(50, 350, 320, 70, "Повернення після sysretq\nRAX = 6 (успіх) або -1 (якщо помилка, errno)\nRIP відновлено з RCX, RFLAGS з R11\nПродовження виконання в Ring 3", size=11, fill="#ffffff", stroke="#86efac", bold=True))

    # Центральні стрілки переходу
    frags.append(arrow(370, 140, 470, 140, color=POS, sw=2))
    frags.append(text(420, 128, "syscall", size=11, color=POS, bold=True))

    frags.append(arrow(470, 385, 370, 385, color=FIELD, sw=2))
    frags.append(text(420, 373, "sysretq", size=11, color=FIELD, bold=True))

    # Права колонка: Простір ядра (Ядерний стек і pt_regs)
    frags.append(rect(470, 30, 360, 410, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(490, 55, "ПРОСТІР ЯДРА (Ядерний стек потоку)", size=12, color=FIELD, anchor="start", bold=True))

    frags.append(fitbox(490, 75, 320, 150, "struct pt_regs на ядерному стеку\npt_regs->di = 1, pt_regs->si = 0x7ffdb84a1010\npt_regs->dx = 6, pt_regs->ax = 1\npt_regs->cx = 0x7f3b8a120402 (адреса ret)\npt_regs->r11 = RFLAGS (прапорці процесора)\npt_regs->sp = 0x7ffdb84a0f80 (стек користувача)\npt_regs->ip = 0x7f3b8a120400", size=11, fill="#ffffff", stroke="#86efac", bold=True))

    # Доступ до пам'яті через SMAP
    frags.append(fitbox(490, 240, 320, 95, "copy_from_user(kbuf, ubuf, 6)\n1. access_ok(ubuf, 6) — перевірка діапазону\n2. stac — зняття апаратної заборони SMAP\n3. Копіювання 6 байтів у буфер ядра kbuf\n4. clac — відновлення захисту SMAP", size=11, fill="#ffffff", stroke="#86efac", bold=True))

    frags.append(arrow(490, 285, 370, 285, color=FIELD, sw=2))
    frags.append(text(430, 275, "читання kbuf", size=10, color=FIELD, bold=True))

    render(os.path.join(OUT_DIR, "boundary-crossing-registers.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_tracing_layers_overview()
    fig_fd_to_driver_dispatch()
    fig_boundary_crossing_registers()
    print("Figures generated successfully.")
