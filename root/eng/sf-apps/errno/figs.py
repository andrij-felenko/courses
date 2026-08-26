# -*- coding: utf-8 -*-
"""Фігури до теми «errno та POSIX-коди помилок».
Запуск: python figs.py  → пише SVG у ./img/
Стиль і помічники — зі спільного scripts/svgkit.py.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Механізм передачі помилки: Kernel → %rax → Libc wrapper → TLS errno ────
def fig_errno_tls_mechanism():
    W, H = 880, 480
    f = [text(W / 2, 28, "Шлях коду помилки від ядра до локальної пам'яті нитки (TLS)", size=15, bold=True)]

    # Зона простору користувача (User Space) та простору ядра (Kernel Space)
    f.append(rect(30, 50, 820, 240, fill="#f8fafc", stroke=NEG, sw=1.2, rx=8))
    f.append(text(50, 72, "ПРОСТІР КОРИСТУВАЧА (User Space)", size=11, color=NEG, anchor="start", bold=True))

    f.append(rect(30, 310, 820, 145, fill="#fdfaf6", stroke=POS, sw=1.2, rx=8))
    f.append(text(50, 332, "ПРОСТІР ЯДРА (Kernel Space)", size=11, color=POS, anchor="start", bold=True))

    # Блоки в User Space
    # 1.1 Код програми
    f.append(fitbox(50, 90, 200, 80, "Код програми\nread(fd, buf, n)\nВикликає обгортку libc", size=12, fill="#ffffff", stroke=INK, sw=1.4))

    # 1.2 Libc wrapper
    f.append(fitbox(310, 90, 230, 80, "Обгортка libc (read.S)\n1. Перевіряє %rax у [-4095, -1]\n2. Записує errno = -%rax\n3. Повертає -1 у викликач", size=11, fill="#ffffff", stroke=NEG, sw=1.4))

    # 1.3 TLS область пам'яті
    f.append(rect(600, 85, 230, 190, fill="#eef2f8", stroke=NEG, sw=1.4, rx=6))
    f.append(text(715, 106, "Пам'ять нитки (TLS)", size=12, bold=True, color=NEG))
    f.append(fitbox(615, 120, 200, 65, "Нитка #1 (pthread)\n*__errno_location()\nerrno = 2 (ENOENT)", size=11, fill="#ffffff", stroke=MUTED, sw=1.0))
    f.append(fitbox(615, 195, 200, 65, "Нитка #2 (pthread)\n*__errno_location()\nerrno = 0 (OK)", size=11, fill="#ffffff", stroke=MUTED, sw=1.0))

    # Блок в Kernel Space
    f.append(fitbox(310, 350, 230, 85, "Обробник sys_read()\nВиявив помилку: файл закритий\nПовертає від'ємний код:\nreturn -EBADF (-9)", size=11, fill="#ffffff", stroke=POS, sw=1.4))

    # Стрілки передачі керування
    # 1. Програма -> Libc
    f.append(arrow(250, 130, 310, 130, color=INK, sw=1.8))
    f.append(text(280, 120, "виклик", size=9.5, color=MUTED))

    # 2. Libc -> Ядро (syscall)
    f.append(arrow(380, 170, 380, 350, color=POS, sw=2.0))
    f.append(text(340, 260, "syscall / sysenter\n(інструкція CPU)", size=10, color=POS, bold=True))

    # 3. Ядро -> Libc (%rax)
    f.append(arrow(470, 350, 470, 170, color=POS, sw=2.0))
    f.append(text(515, 260, "%rax = -9 (-EBADF)\nвід'ємний код", size=10, color=POS, bold=True))

    # 4. Libc -> TLS
    f.append(arrow(540, 140, 615, 140, color=NEG, sw=1.8))
    f.append(text(575, 130, "errno = 9", size=10, color=NEG, bold=True))

    # 5. Libc -> Програма (-1)
    f.append(arrow(310, 155, 250, 155, color=INK, sw=1.8))
    f.append(text(280, 172, "повертає -1", size=9.5, color=INK, bold=True))

    render(os.path.join(IMG, "errno-tls-mechanism.svg"), W, H, *f)


# ── 2. Цикл повтору при сигналі: EINTR та SA_RESTART ───────────────────────────
def fig_eintr_restart_loop():
    W, H = 880, 450
    f = [text(W / 2, 28, "Обробка переривання системного виклику сигналом (EINTR)", size=15, bold=True)]

    # Крок 1: Блокуючий виклик
    f.append(fitbox(40, 80, 190, 80, "1. Блокуючий виклик\nread(sock_fd, buf, sz)\nНитка засинає в ядрі\n(TASK_INTERRUPTIBLE)", size=11, fill="#f4f6f8", stroke=INK, sw=1.4))

    # Крок 2: Надходження сигналу
    f.append(fitbox(270, 80, 190, 80, "2. Прибуття сигналу\nСигнал SIGALRM / SIGINT\nЯдро будить нитку,\nвиконує signal handler", size=11, fill="#fef6e7", stroke=POS, sw=1.4))

    # Крок 3: Повернення з ядра
    f.append(fitbox(500, 80, 190, 80, "3. Відповідь ядра\nЯкщо нема SA_RESTART:\nread() повертає -1\nerrno виставляється в EINTR", size=11, fill="#fdecea", stroke=POS, sw=1.4))

    # Крок 4: Розгалуження в програмі
    f.append(fitbox(470, 240, 250, 100, "4. Перевірка результату в коді\nif (res == -1 && errno == EINTR)\n\nЦе не збій пристрою чи мережі,\nа переривання обчислень!", size=11, fill="#eef2f8", stroke=NEG, sw=1.4))

    # Дві гілки
    # Гілка А: Повтор циклу
    f.append(fitbox(100, 250, 220, 80, "Гілка А: Повторити виклик\ncontinue в циклі while\nВідновлення читання сокета\n(дані не втрачено)", size=11, fill="#eef6ef", stroke=FIELD, sw=1.6))

    # Гілка Б: Справжня помилка
    f.append(fitbox(530, 365, 230, 70, "Гілка Б: Інша помилка (EPIPE, EBADF)\nЗавершення збою, логування,\nочищення ресурсів", size=10.5, fill="#ffffff", stroke=POS, sw=1.4))

    # Стрілки
    f.append(arrow(230, 120, 270, 120, color=INK, sw=1.8))
    f.append(arrow(460, 120, 500, 120, color=POS, sw=1.8))
    f.append(arrow(595, 160, 595, 240, color=POS, sw=1.8))

    # Стрілка на повтор
    f.append(arrow(470, 290, 320, 290, color=FIELD, sw=2.0))
    f.append(text(395, 278, "errno == EINTR", size=10, color=FIELD, bold=True))

    f.append(line(210, 250, 210, 200, color=FIELD, sw=1.8))
    f.append(line(210, 200, 135, 200, color=FIELD, sw=1.8))
    f.append(arrow(135, 200, 135, 160, color=FIELD, sw=1.8))
    f.append(text(160, 185, "повтор", size=9.5, color=FIELD, bold=True))

    # Стрілка на іншу помилку
    f.append(arrow(595, 340, 595, 365, color=POS, sw=1.8))
    f.append(text(660, 352, "errno != EINTR", size=9.5, color=POS, bold=True))

    render(os.path.join(IMG, "eintr-restart-loop.svg"), W, H, *f)


# ── 3. Життєвий цикл та правила читання errno ──────────────────────────────────
def fig_errno_lifecycle_rules():
    W, H = 880, 460
    f = [text(W / 2, 28, "Дерево рішень: коли читати errno і як зберігати значення", size=15, bold=True)]

    # Корінь: Виклик функції
    f.append(fitbox(330, 60, 220, 65, "Виклик функції C / POSIX\n(open, read, write, strtol...)", size=12, fill="#f4f6f8", stroke=INK, sw=1.5))

    # Розгалуження на 2 типи функцій
    # Ліва гілка: звичайні системні виклики (open, read, write, socket)
    f.append(fitbox(100, 170, 280, 75, "Типовий системний виклик\nres == -1 (або ptr == NULL)\nЧіткий сигнал збою у return", size=11, fill="#ffffff", stroke=NEG, sw=1.4))

    # Права гілка: функції з повним діапазоном (strtol, getpriority)
    f.append(fitbox(500, 170, 280, 75, "Функції повного діапазону (strtol)\nБудь-яке число — валідний результат!\nНемає унікального числа збою", size=11, fill="#ffffff", stroke=POS, sw=1.4))

    # Правило 1: Ліва гілка
    f.append(fitbox(80, 290, 320, 130, "Правило 1: Читати errno ТІЛЬКИ при збої\n1. Перевірити res == -1\n2. Якщо res >= 0 — errno НЕ ЧИТАТИ!\n   (успіх не скидає старе errno)\n3. Зберегти: int err = errno;\n4. Тільки потім викликати close() / логер", size=10.5, fill="#eef6ef", stroke=FIELD, sw=1.5))

    # Правило 2: Права гілка
    f.append(fitbox(480, 290, 320, 130, "Правило 2: Скидання errno = 0 ДО виклику\n1. errno = 0; (обов'язково перед викликом!)\n2. val = strtol(str, &endptr, 10);\n3. if (errno != 0) -> обробити збій ERANGE\n4. if (endptr == str) -> не число (EINVAL)\n5. Зберегти err = errno перед очищенням", size=10.5, fill="#fef6e7", stroke=POS, sw=1.5))

    # З'єднувальні стрілки
    f.append(arrow(390, 125, 240, 170, color=NEG, sw=1.8))
    f.append(text(285, 140, "код повернення -1", size=9.5, color=NEG, bold=True))

    f.append(arrow(490, 125, 640, 170, color=POS, sw=1.8))
    f.append(text(595, 140, "діапазон значень", size=9.5, color=POS, bold=True))

    f.append(arrow(240, 245, 240, 290, color=FIELD, sw=1.8))
    f.append(arrow(640, 245, 640, 290, color=POS, sw=1.8))

    render(os.path.join(IMG, "errno-lifecycle-rules.svg"), W, H, *f)


if __name__ == "__main__":
    fig_errno_tls_mechanism()
    fig_eintr_restart_loop()
    fig_errno_lifecycle_rules()
    print("Згенеровано 3 фігури у", IMG)
