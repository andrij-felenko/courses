# -*- coding: utf-8 -*-
"""Фігури до теми «Інтерфейс seq_file: ітератор текстового виводу ядра»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

ZONE_OLD = "#fdeeec"    # стара проблемна модель
ZONE_NEW = "#eff7ef"    # сучасна модель seq_file
ZONE_BUF = "#eef4fb"    # буфер пам'яті
ZONE_CTX = "#f3f0fa"    # контекст виконання / блокування
ZONE_WRN = "#fef9e7"    # попередження / переповнення


def box(cx, cy, s, size=13, **kw):
    body, w, h = textbox(cx, cy, s, size=size, **kw)
    return body


# ── 1. Порівняння старого read_proc та seq_file ─────────────────────────────
def fig_old_vs_new():
    W, H = 1200, 680
    f = []

    # Ліва колонка: Старий read_proc
    f.append(rect(40, 60, 530, 560, fill=ZONE_OLD, stroke=MUTED, sw=1.2))
    f.append(text(305, 95, "Старий інтерфейс: read_proc_t (Linux 2.2 / 2.4)", size=15, bold=True, color=POS))

    f.append(fitbox(65, 125, 480, 75,
                    "Виклик ядра: драйвер отримує фіксовану сторінку пам'яті\nchar *page = PAGE_SIZE (4096 байтів)",
                    size=13, fill=BG, stroke=LINE))

    f.append(fitbox(65, 220, 480, 85,
                    "sprintf(page + len, ...)\nДрайвер форматує всі записи ядра в один суцільний буфер.\nЯкщо тексту більше ніж 4 КБ — затирання пам'яті ядра!",
                    size=12, fill="#fdedec", stroke=POS))

    f.append(fitbox(65, 325, 480, 115,
                    "Ручна розбивка на сторінки (пагінація):\n• Зсув off рахується в байтах, а довжина рядків змінна\n• *start та *eof обчислюються кожним автором вручну\n• Результат: зсув lseek ламається, рядки дублюються або зникають",
                    size=12, fill=BG, stroke=MUTED))

    f.append(fitbox(65, 460, 480, 130,
                    "Небезпека перегонів даних (race conditions):\nМіж системними викликами read(1024) стан списку змінюється,\nбайтовий зсув off вказує на середину чужого рядка.\nПідсумок: падіння системи або пошкодження пам'яті.",
                    size=12, fill="#fdf2e9", stroke=POS))

    # Права колонка: seq_file
    f.append(rect(630, 60, 530, 560, fill=ZONE_NEW, stroke=MUTED, sw=1.2))
    f.append(text(895, 95, "Сучасний інтерфейс: seq_file (починаючи з 2.4.15)", size=15, bold=True, color=FIELD))

    f.append(fitbox(655, 125, 480, 75,
                    "Абстракція послідовності: struct seq_operations\nstart() -> show() -> next() -> stop()\nЯдро оперує логічними об'єктами, а не сирими байтами",
                    size=13, fill=BG, stroke=LINE))

    f.append(fitbox(655, 220, 480, 85,
                    "Динамічний буфер з авторозширенням:\nseq_printf(m, ...) пише в буфер struct seq_file.\nПри переповненні буфер подвоюється (4K -> 8K -> 16K -> 32K...)",
                    size=12, fill="#eafaf1", stroke=FIELD))

    f.append(fitbox(655, 325, 480, 115,
                    "Логічне позиціонування (*pos):\n• *pos є номером запису (0, 1, 2...) або ID об'єкта\n• lseek крокує послідовністю за допомогою start() та next()\n• Повне позбавлення від ручного підрахунку байтів",
                    size=12, fill=BG, stroke=MUTED))

    f.append(fitbox(655, 460, 480, 130,
                    "Надійна синхронізація та безпека:\n• seq_file->lock (м'ютекс) захищає файл від гонитви читачів\n• Замки структури / RCU захоплюються у start() і знімаються у stop()\n• Коректна поведінка при зміні списку між читаннями",
                    size=12, fill="#eef4fb", stroke=FIELD))

    f.append(text(600, 645, "Перехід від низькорівневого копіювання до повноцінного ітератора структур ядра",
                  size=13, color=MUTED, bold=False))

    render(os.path.join(OUT, "seq-file-old-vs-new.svg"), W, H, *f,
           title="Порівняння старого підходу read_proc та підсистеми seq_file")


# ── 2. Життєвий цикл seq_read() та обробка переповнення ────────────────────
def fig_seq_lifecycle():
    W, H = 1200, 780
    f = []

    # Верхній блок: Вхід із простору користувача
    f.append(fitbox(380, 30, 440, 60,
                    "Системний виклик: read(fd, user_buf, count)\nVFS викликає seq_read_iter() / seq_read()",
                    size=13, bold=True, fill=ZONE_BUF, stroke=LINE))

    f.append(arrow(600, 90, 600, 115, color=INK, sw=1.6))

    # Захоплення м'ютексу
    f.append(fitbox(410, 115, 380, 45,
                    "mutex_lock(&m->lock) — блокування дескриптора файлу",
                    size=12, fill=ZONE_CTX, stroke=MUTED))

    f.append(arrow(600, 160, 600, 185, color=INK, sw=1.6))

    # Крок 1: start()
    f.append(fitbox(360, 185, 480, 60,
                    "1. op->start(m, &pos)\nЗахоплює замок підсистеми / RCU, знаходить елемент v за індексом pos",
                    size=12, bold=True, fill=BG, stroke=FIELD))

    f.append(arrow(600, 245, 600, 275, color=INK, sw=1.6))

    # Ромб / перевірка кінця списку
    f.append(fitbox(450, 275, 300, 50, "Чи знайдено елемент?\n(v != NULL та !IS_ERR(v))",
                    size=12, fill=ZONE_WRN, stroke=LINE))

    # Гілка НІ (кінець даних)
    f.append(arrow(750, 300, 980, 300, color=MUTED, sw=1.5))
    f.append(text(850, 290, "НІ (EOF)", size=11, color=MUTED))
    f.append(line(980, 300, 980, 565, color=MUTED, sw=1.5))
    f.append(arrow(980, 565, 840, 565, color=MUTED, sw=1.5))

    # Гілка ТАК (продовження)
    f.append(arrow(600, 325, 600, 355, color=INK, sw=1.6))
    f.append(text(615, 342, "ТАК", size=11, color=FIELD, bold=True))

    # Крок 2: show()
    f.append(fitbox(360, 355, 480, 60,
                    "2. op->show(m, v)\nФорматує об'єкт у m->buf функціями seq_printf(), seq_puts()",
                    size=12, bold=True, fill=BG, stroke=FIELD))

    f.append(arrow(600, 415, 600, 445, color=INK, sw=1.6))

    # Перевірка переповнення буфера
    f.append(fitbox(420, 445, 360, 50,
                    "Перевірка: seq_has_overflowed(m)?\n(Текст не вмістився у виділений розмір)",
                    size=12, fill=ZONE_WRN, stroke=POS))

    # Гілка переповнення (ВЛІВО)
    f.append(arrow(420, 470, 310, 470, color=POS, sw=1.8))
    f.append(text(365, 458, "ТАК: переповнення", size=11, color=POS, bold=True))

    f.append(fitbox(40, 400, 260, 140,
                    "Реакція на переповнення:\n1. op->stop(m, v) — зняти замки\n2. Скинути вміст буфера (count = 0)\n3. Подвоїти розмір: size <<= 1\n4. kvmalloc() новий більший буфер\n5. Рестарт із op->start(m, &pos)!",
                    size=11, fill=ZONE_OLD, stroke=POS))

    f.append(line(170, 400, 170, 215, color=POS, sw=1.6, dash="4 4"))
    f.append(arrow(170, 215, 360, 215, color=POS, sw=1.6))

    # Гілка без переповнення (ВНИЗ)
    f.append(arrow(600, 495, 600, 525, color=INK, sw=1.6))
    f.append(text(615, 512, "НІ", size=11, color=FIELD, bold=True))

    # Крок 3: next()
    f.append(fitbox(360, 525, 480, 55,
                    "3. op->next(m, v, &pos)\nЗбільшує логічний індекс (*pos)++, повертає наступний елемент v",
                    size=12, bold=True, fill=BG, stroke=FIELD))

    # Петля на наступний елемент
    f.append(line(360, 552, 320, 552, color=FIELD, sw=1.5))
    f.append(line(320, 552, 320, 385, color=FIELD, sw=1.5))
    f.append(arrow(320, 385, 360, 385, color=FIELD, sw=1.5))
    f.append(text(300, 465, "наступний", size=11, color=FIELD, anchor="end"))

    # Крок 4: stop()
    f.append(fitbox(400, 610, 400, 55,
                    "4. op->stop(m, v)\nЗавершення ітерації: звільнення замків / rcu_read_unlock()",
                    size=12, bold=True, fill=ZONE_CTX, stroke=LINE))

    f.append(arrow(600, 580, 600, 610, color=INK, sw=1.6))
    f.append(arrow(600, 665, 600, 695, color=INK, sw=1.6))

    # Фінал: Копіювання в юзерспейс і розблокування
    f.append(fitbox(350, 695, 500, 60,
                    "Копіювання даних: copy_to_user() з m->buf у буфер процесу\nmutex_unlock(&m->lock) -> повернення кількості прочитаних байтів",
                    size=12, bold=True, fill=ZONE_BUF, stroke=LINE))

    render(os.path.join(OUT, "seq-file-lifecycle.svg"), W, H, *f,
           title="Життєвий цикл seq_read: ітерація, виявлення переповнення та подвоєння буфера")


# ── 3. Синхронізація, RCU та життєвий цикл блокувань ───────────────────────
def fig_seq_locking():
    W, H = 1200, 680
    f = []

    # Рівень 1: М'ютекс структури seq_file
    f.append(rect(50, 50, 1100, 130, fill=ZONE_BUF, stroke=MUTED, sw=1.2))
    f.append(text(80, 80, "Рівень файлового дескриптора: struct seq_file->lock (Mutex)", size=14, bold=True, anchor="start"))
    f.append(fitbox(80, 100, 490, 65,
                    "Захоплюється під час входу в seq_read() / seq_lseek()\nЗахищає буфер m->buf, m->count, m->from від одночасних read()",
                    size=12, fill=BG, stroke=LINE))
    f.append(fitbox(610, 100, 510, 65,
                    "Гарантує послідовність викликів start/show/next/stop для одного struct file\n(Запобігає пошкодженню стану ітератора спільними потоками)",
                    size=12, fill=BG, stroke=LINE))

    # Рівень 2: Блокування структур даних ядра (RCU / Spinlock)
    f.append(rect(50, 210, 1100, 240, fill=ZONE_NEW, stroke=FIELD, sw=1.5))
    f.append(text(80, 240, "Рівень даних ядра: межі критичної секції start() ... stop()", size=14, bold=True, color=FIELD, anchor="start"))

    f.append(fitbox(80, 265, 300, 160,
                    "op->start(m, &pos)\n\n• rcu_read_lock()\nабо spin_lock_irqsave()\n• Пошук вузла за pos\n• Повертає вказівник v",
                    size=12, bold=True, fill=BG, stroke=FIELD))

    f.append(arrow(380, 345, 440, 345, color=FIELD, sw=2.0))

    f.append(fitbox(440, 265, 320, 160,
                    "op->show() та op->next()\n\nВиконуються ВСЕРЕДИНІ замка:\n• Безпечне читання полів структури\n• m->buf вже виділено, тому seq_printf не спить і не виділяє пам'ять",
                    size=12, fill=BG, stroke=LINE))

    f.append(arrow(760, 345, 820, 345, color=FIELD, sw=2.0))

    f.append(fitbox(820, 265, 300, 160,
                    "op->stop(m, v)\n\n• rcu_read_unlock()\nабо spin_unlock_irqrestore()\n• Очищення локального контексту\n• Кличеться ЗАВЖДИ у фіналі",
                    size=12, bold=True, fill=BG, stroke=FIELD))

    # Рівень 3: Зміна стану між системними викликами read()
    f.append(rect(50, 480, 1100, 160, fill=ZONE_CTX, stroke=MUTED, sw=1.2))
    f.append(text(80, 510, "Між викликами read(): замок даних ЗВІЛЬНЕНО, але логічний індекс *pos збережено", size=14, bold=True, anchor="start"))

    f.append(fitbox(80, 530, 320, 90,
                    "Виклик 1: read(fd, buf, 512)\nЧитає елементи pos: 0..15\nstop() знімає RCU lock.\nЯдро віддає керування в юзерспейс.",
                    size=12, fill=BG, stroke=MUTED))

    f.append(fitbox(440, 530, 320, 90,
                    "Інший потік ядра модифікує список:\nlist_del_rcu(елемент 8)\nlist_add_tail_rcu(новий елемент)\nПам'ять видаленого жива до grace period",
                    size=12, fill="#fdedec", stroke=POS))

    f.append(fitbox(800, 530, 320, 90,
                    "Виклик 2: read(fd, buf, 512)\nstart(m, pos=16) знову бере RCU lock.\nПозиція pos=16 знаходиться надійно\nбез падінь та виходу за межі пам'яті.",
                    size=12, fill=BG, stroke=FIELD))

    f.append(arrow(400, 575, 440, 575, color=INK, sw=1.5))
    f.append(arrow(760, 575, 800, 575, color=INK, sw=1.5))

    render(os.path.join(OUT, "seq-file-rcu-locking.svg"), W, H, *f,
           title="Межі синхронізації та захист структур ядра під час ітерації seq_file")


if __name__ == '__main__':
    fig_old_vs_new()
    fig_seq_lifecycle()
    fig_seq_locking()
    print("All figures generated successfully.")
