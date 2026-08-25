# -*- coding: utf-8 -*-
"""Фігури до теми «Канали й FIFO в Unix/Linux (Pipes and Named Pipes)»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_pipe_kernel_ring_buffer():
    """Архітектура кільцевого буфера pipe_inode_info у ядрі Linux."""
    W, H = 1000, 480
    g = []

    # Заголовок та опис зверху
    g.append(fitbox(40, 20, 920, 52,
                    "Кільцевий буфер каналу в пам'яті ядра: struct pipe_inode_info\n"
                    "Масив покажчиків pipe_buffer на сторінки пам'яті (за замовчуванням 16 слотів по 4 КіБ = 64 КіБ)",
                    size=13, fill="#eef2f7", bold=False))

    # Секція Writers (зліва)
    g.append(fitbox(40, 100, 200, 60,
                    "Процес-письменник\n(write / splice)",
                    size=13, fill="#eaf7ee", stroke=FIELD))
    g.append(arrow(240, 130, 310, 130))
    g.append(text(275, 120, "запис", size=11, color=MUTED))

    # Секція Readers (справа)
    g.append(arrow(690, 130, 760, 130))
    g.append(text(725, 120, "читання", size=11, color=MUTED))
    g.append(fitbox(760, 100, 200, 60,
                    "Процес-читач\n(read / splice)",
                    size=13, fill="#eaf0fd", stroke=NEG))

    # Вказівники head і tail
    g.append(fitbox(310, 95, 180, 70,
                    "pipe->head = 9\n(позиція запису)\nhead % 16 = слот 9",
                    size=12, fill="#fdecea", stroke=POS))

    g.append(fitbox(510, 95, 180, 70,
                    "pipe->tail = 5\n(позиція читання)\ntail % 16 = слот 5",
                    size=12, fill="#eaf0fd", stroke=NEG))

    # Відображення 8 слотів кільцевого буфера для наочності
    slot_w = 105
    start_x = 80
    y_slots = 200
    h_slots = 90

    g.append(text(500, 190, "Кільцевий масив pipe_buffer (head − tail = 4 зайняті сторінки з 16)", size=12, bold=True))

    for i in range(8):
        x = start_x + i * slot_w
        # Стан слота: 5, 6, 7, 8 зайняті
        slot_idx = i + 4
        if 5 <= slot_idx <= 8:
            fill_col = "#eaf7ee"
            stroke_col = FIELD
            status_text = f"Слот {slot_idx}\nЗайнято\n4096 Б"
        elif slot_idx == 4:
            fill_col = "#f4f6f8"
            stroke_col = MUTED
            status_text = f"Слот {slot_idx}\nЗвільнено\n(tail був тут)"
        elif slot_idx == 9:
            fill_col = "#fdecea"
            stroke_col = POS
            status_text = f"Слот {slot_idx}\nНаступний\n(head вказує)"
        else:
            fill_col = "#ffffff"
            stroke_col = LINE
            status_text = f"Слот {slot_idx}\nВільний\n(порожньо)"

        g.append(fitbox(x, y_slots, slot_w - 10, h_slots, status_text, size=11, fill=fill_col, stroke=stroke_col))

    # Стрілки вказівників на конкретні слоти
    g.append(arrow(600, 165, 230, 200, color=NEG))
    g.append(arrow(400, 165, 650, 200, color=POS))

    # Нижня плашка: деталі структури pipe_buffer
    g.append(fitbox(80, 320, 840, 130,
                    "Вміст кожного елемента struct pipe_buffer:\n"
                    "• struct page *page — покажчик на фізичну сторінку пам'яті (виділяється ядром за потребою);\n"
                    "• unsigned int offset — зміщення першого дійсного байта даних у сторінці (після часткового read);\n"
                    "• unsigned int len — кількість доступних байтів у цій сторінці;\n"
                    "• const struct pipe_buf_operations *ops — операції зі сторінкою (звільнення, отримання посилання, крадіжка);\n"
                    "• unsigned int flags — прапорці (наприклад, PIPE_BUF_FLAG_CAN_MERGE для дозапису малих порцій).",
                    size=12, fill="#fdfbf7", stroke=MUTED))

    render(os.path.join(IMG, 'pipe-kernel-ring-buffer.svg'), W, H, *g,
           title="Архітектура кільцевого буфера pipe_inode_info")


def fig_pipe_vs_fifo_vfs():
    """Порівняння анонімного каналу та FIFO у віртуальній файловій системі VFS."""
    W, H = 1000, 460
    g = []

    # Ліва колонка: Anonymous Pipe
    g.append(fitbox(40, 20, 430, 50,
                    "Анонімний канал (pipe / pipe2)\nСтворюється в пам'яті, доступний через успадкування",
                    size=13, fill="#eef2f7", bold=True))

    g.append(fitbox(40, 85, 430, 70,
                    "1. pipe(fds) виділяє анонімний інод у pipefs\n"
                    "(спеціальна псевдо-ФС ядра без точки монтування)\n"
                    "Інод не має імені в каталогах ФС (dentry = NULL)",
                    size=12))

    g.append(arrow(255, 155, 255, 185))

    g.append(fitbox(40, 185, 430, 70,
                    "2. Ядро повертає 2 дескриптори одному процесу:\n"
                    "fds[0] (читання) та fds[1] (запис).\n"
                    "Обидва вказують на спільний struct pipe_inode_info",
                    size=12))

    g.append(arrow(255, 255, 255, 285))

    g.append(fitbox(40, 285, 430, 70,
                    "3. Передача між процесами тільки через fork():\n"
                    "Нащадок успадковує таблицю дескрипторів.\n"
                    "Сторонній неспоріднений процес під'єднатися не може",
                    size=12))

    # Права колонка: Named Pipe / FIFO
    g.append(fitbox(530, 20, 430, 50,
                    "Іменований канал / FIFO (mkfifo)\nМає ім'я у файловій системі, доступний усім",
                    size=13, fill="#fdf3e7", bold=True))

    g.append(fitbox(530, 85, 430, 70,
                    "1. mkfifo(\"/tmp/my_fifo\", 0666) створює інод у звичайній ФС\n"
                    "Тип інода: S_IFIFO. Розмір на диску: 0 байтів.\n"
                    "Має ім'я (dentry), права доступу та власника (UID/GID)",
                    size=12))

    g.append(arrow(745, 155, 745, 185))

    g.append(fitbox(530, 185, 430, 70,
                    "2. Непов'язані процеси викликають open(\"/tmp/my_fifo\"):\n"
                    "VFS відкриває файл і підставляє fifo_open().\n"
                    "Інод пов'язується з тим самим struct pipe_inode_info",
                    size=12))

    g.append(arrow(745, 255, 745, 285))

    g.append(fitbox(530, 285, 430, 70,
                    "3. Рукостискання (rendezvous) при відкритті:\n"
                    "open(O_RDONLY) блокується, доки хтось не відкриє O_WRONLY.\n"
                    "Будь-який процес із правами доступу може під'єднатися",
                    size=12))

    # Спільний підсумок внизу
    g.append(fitbox(40, 380, 920, 60,
                    "Спільна основа: після успішного відкриття VFS направляє read() та write()\n"
                    "в одну й ту саму функцію ядра (pipe_read / pipe_write) та однаковий кільцевий буфер у RAM.",
                    size=12, fill="#eaf7ee", stroke=FIELD))

    render(os.path.join(IMG, 'pipe-vs-fifo-vfs.svg'), W, H, *g,
           title="Анонімний канал проти іменованого каналу FIFO у VFS")


def fig_atomic_pipe_buf_interleaving():
    """Атомарність запису в канал: межа PIPE_BUF (4096 байтів)."""
    W, H = 1000, 480
    g = []

    # Верхній заголовок
    g.append(fitbox(40, 15, 920, 45,
                    "Атомарність записів у канал: межа PIPE_BUF (на Linux = 4096 байтів)\n"
                    "Кілька паралельних письменників ведуть запис в один канал чи FIFO",
                    size=13, fill="#eef2f7"))

    # Лівий випадок: Запис <= PIPE_BUF (Атомарно)
    g.append(fitbox(40, 75, 430, 50,
                    "Випадок 1: Порція запису ≤ PIPE_BUF (наприклад, 1024 Б)\n"
                    "ГАРАНТІЯ POSIX: запис неподільний",
                    size=12, fill="#eaf7ee", stroke=FIELD, bold=True))

    g.append(fitbox(40, 135, 430, 70,
                    "Письменник А: write(fd, msgA, 1024)\n"
                    "Письменник Б: write(fd, msgB, 1024)\n"
                    "Ядро захоплює pipe->mutex на весь обсяг запису",
                    size=12))

    g.append(arrow(255, 205, 255, 235))

    g.append(fitbox(40, 235, 430, 95,
                    "Буфер каналу (читач бачить чисті повідомлення):\n\n"
                    "[  Повідомлення А (1024 Б)  ]  [  Повідомлення Б (1024 Б)  ]",
                    size=12, fill="#eaf7ee", stroke=FIELD))

    g.append(fitbox(40, 345, 430, 110,
                    "Результат: Повідомлення ніколи не змішуються.\n"
                    "Ідеально для логування від багатьох процесів у спільний FIFO:\n"
                    "кожен рядок або JSON-об'єкт до 4 КіБ записується як єдине ціле.",
                    size=11, fill="#ffffff", stroke=MUTED))

    # Правий випадок: Запис > PIPE_BUF (Розщеплення та чергування)
    g.append(fitbox(530, 75, 430, 50,
                    "Випадок 2: Порція запису > PIPE_BUF (наприклад, 8192 Б)\n"
                    "НЕМАЄ ГАРАНТІЇ АТОМАРНОСТІ: дані чергуються",
                    size=12, fill="#fdecea", stroke=POS, bold=True))

    g.append(fitbox(530, 135, 430, 70,
                    "Письменник А: write(fd, dataA, 8192)\n"
                    "Письменник Б: write(fd, dataB, 8192)\n"
                    "Ядро розбиває запис на шматки, звільняючи м'ютекс між ними",
                    size=12))

    g.append(arrow(745, 205, 745, 235))

    g.append(fitbox(530, 235, 430, 95,
                    "Буфер каналу (фрагменти змішано!):\n\n"
                    "[ А-частина 1 ] [ Б-частина 1 ] [ А-частина 2 ] [ Б-частина 2 ]",
                    size=12, fill="#fdecea", stroke=POS))

    g.append(fitbox(530, 345, 430, 110,
                    "Результат: Пошкодження структури протоколу.\n"
                    "Читач отримує перемішані байти від двох процесів.\n"
                    "Для передачі великих повідомлень потрібен зовнішній м'ютекс або окремі FIFO.",
                    size=11, fill="#ffffff", stroke=MUTED))

    render(os.path.join(IMG, 'atomic-pipe-buf-interleaving.svg'), W, H, *g,
           title="Атомарність записів PIPE_BUF та чергування даних")


def fig_pipeline_descriptor_lifecycle():
    """Життєвий цикл дескрипторів у конвеєрі cmd1 | cmd2 та закриття невикористаних кінців."""
    W, H = 1000, 510
    g = []

    g.append(fitbox(40, 15, 920, 45,
                    "Життєвий цикл дескрипторів конвеєра: cmd1 | cmd2\n"
                    "Чому критично закривати невикористані кінці в батьківському та дочірніх процесах",
                    size=13, fill="#eef2f7"))

    # Етап 1: pipe()
    g.append(fitbox(40, 75, 280, 90,
                    "1. Батьківський процес (Shell)\n"
                    "pipe(pfd) → pfd[0] (читання), pfd[1] (запис)\n"
                    "Лічильник читачів = 1, письменників = 1",
                    size=11))

    # Етап 2: fork cmd1
    g.append(fitbox(360, 75, 280, 90,
                    "2. fork() → Дочірній 1 (cmd1)\n"
                    "Успадковує pfd[0] і pfd[1].\n"
                    "dup2(pfd[1], STDOUT_FILENO)\n"
                    "close(pfd[0]), close(pfd[1])",
                    size=11, fill="#eaf7ee"))

    # Етап 3: fork cmd2
    g.append(fitbox(680, 75, 280, 90,
                    "3. fork() → Дочірній 2 (cmd2)\n"
                    "Успадковує pfd[0] і pfd[1].\n"
                    "dup2(pfd[0], STDIN_FILENO)\n"
                    "close(pfd[0]), close(pfd[1])",
                    size=11, fill="#eaf0fd"))

    # Стрілка до етапу 4
    g.append(arrow(180, 165, 180, 205))
    g.append(arrow(500, 165, 500, 205))
    g.append(arrow(820, 165, 820, 205))

    # Етап 4: Батьківський процес закриває свої копії
    g.append(fitbox(40, 205, 920, 75,
                    "4. ГОЛОВНИЙ КРОК: Батьківський процес викликає close(pfd[0]) та close(pfd[1])\n"
                    "Тепер єдиним письменником є cmd1 (через свій stdout), а єдиним читачем — cmd2 (через свій stdin).\n"
                    "Батьківський процес викликає waitpid() для обох нащадків.",
                    size=12, fill="#fdf3e7", stroke=LINE, bold=True))

    # Дві гілки наслідків
    g.append(arrow(300, 280, 300, 320))
    g.append(arrow(700, 280, 700, 320))

    # Правильна поведінка
    g.append(fitbox(40, 320, 430, 160,
                    "Усі невикористані кінці закрито (ПРАВИЛЬНО):\n\n"
                    "1. cmd1 закінчує роботу та завершується (exit);\n"
                    "2. Ядро автоматично закриває його stdout;\n"
                    "3. Кількість відкритих дескрипторів на запис стає 0;\n"
                    "4. Наступний read() у cmd2 повертає 0 байтів (EOF);\n"
                    "5. cmd2 коректно завершує обробку та виходить.",
                    size=11, fill="#eaf7ee", stroke=FIELD))

    # Помилка: забутий дескриптор
    g.append(fitbox(530, 320, 430, 160,
                    "Батько забув викликати close(pfd[1]) (ТИПОВИЙ БАГ):\n\n"
                    "1. cmd1 завершується (exit);\n"
                    "2. У системі все ще лишається 1 відкритий pfd[1] у батька;\n"
                    "3. Кількість письменників не дорівнює нулю!\n"
                    "4. read() у cmd2 БЛОКУЄТЬСЯ НАЗАВЖДИ в очікуванні даних;\n"
                    "5. Весь конвеєр зависає намертво.",
                    size=11, fill="#fdecea", stroke=POS))

    render(os.path.join(IMG, 'pipeline-descriptor-lifecycle.svg'), W, H, *g,
           title="Життєвий цикл дескрипторів у конвеєрі")


if __name__ == '__main__':
    fig_pipe_kernel_ring_buffer()
    fig_pipe_vs_fifo_vfs()
    fig_atomic_pipe_buf_interleaving()
    fig_pipeline_descriptor_lifecycle()
    print("All figures generated successfully.")
