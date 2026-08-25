# -*- coding: utf-8 -*-
"""Фігури до теми «Мультиплексор термінала: сеанс, що переживає розрив»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_multiplexer_architecture():
    """Архітектура термінального мультиплексора: клієнт, UNIX-сокет, сервер і PTY."""
    W, H = 1000, 580
    g = []

    # Верхній блок: Клієнтська сторона
    g.append(rect(40, 50, 920, 110, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    g.append(text(500, 72, "Клієнтське середовище (локальний емулятор або віддалений SSH-сеанс)", size=14, bold=True, color="#334155"))
    
    g.append(fitbox(60, 88, 380, 58, "Емулятор термінала користувача\n/dev/pts/0 · сирий режим (raw mode: ~ICANON, ~ECHO)", size=12, fill="#e2e8f0", stroke="#94a3b8"))
    g.append(fitbox(560, 88, 380, 58, "Клієнтський процес (tmux attach)\nчитає клавіші stdin · пише вивід у stdout", size=12, fill="#e2e8f0", stroke="#94a3b8"))
    g.append(arrow(440, 117, 560, 117, color=LINE, sw=1.5))

    # Зв'язуючий UNIX-сокет
    g.append(arrow(750, 146, 750, 159, color=POS, sw=2))
    g.append(fitbox(640, 160, 220, 36, "UNIX-сокет: /tmp/tmux-UID/default", size=11, bold=True, fill="#fdecea", stroke=POS))
    g.append(arrow(750, 197, 750, 200, color=POS, sw=2))

    # Нижній блок: Демон сервера tmux
    g.append(rect(40, 200, 920, 350, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    g.append(text(500, 225, "Серверний демон (tmux-server) — фоновий сеанс без керуючого TTY (повна ізоляція)", size=14, bold=True, color="#166534"))

    # Внутрішні компоненти сервера
    g.append(fitbox(60, 245, 260, 90, "Цикл подій (libevent / poll)\nОбробка клієнтських з'єднань,\nтаймерів і дескрипторів PTY", size=12, fill="#dcfce7", stroke="#86efac"))
    g.append(fitbox(340, 245, 300, 90, "Емулятор термінала та буфери\nМашина станів VT100/xterm,\nматриця комірок екрана й scrollback", size=12, fill="#dcfce7", stroke="#86efac"))
    g.append(fitbox(660, 245, 280, 90, "Диспетчер розкладок (Layout)\nДерево розбиття вікон на панелі,\nобчислення геометрії (рядки/стовпці)", size=12, fill="#dcfce7", stroke="#86efac"))

    # Потоки до PTY
    g.append(arrow(190, 335, 190, 375, color=FIELD, sw=1.5))
    g.append(arrow(490, 335, 490, 375, color=FIELD, sw=1.5))
    g.append(arrow(800, 335, 800, 375, color=FIELD, sw=1.5))

    # Пари PTY для кожної панелі
    # Панель 1
    g.append(fitbox(60, 375, 260, 70, "Ведучий PTY (master fd 1)\n\nПідлеглий PTY: /dev/pts/10", size=11, fill="#ffffff", stroke="#22c55e"))
    g.append(fitbox(80, 465, 220, 65, "Панель 1 (Pane 1)\nОболонка zsh (PID 1042)\nробочий сеанс", size=11, bold=True, fill="#e0f2fe", stroke=NEG))
    g.append(arrow(190, 445, 190, 465, color=NEG, sw=1.5))

    # Панель 2
    g.append(fitbox(360, 375, 260, 70, "Ведучий PTY (master fd 2)\n\nПідлеглий PTY: /dev/pts/11", size=11, fill="#ffffff", stroke="#22c55e"))
    g.append(fitbox(380, 465, 220, 65, "Панель 2 (Pane 2)\nРедактор vim (PID 1088)\nвідкриті буфери коду", size=11, bold=True, fill="#e0f2fe", stroke=NEG))
    g.append(arrow(490, 445, 490, 465, color=NEG, sw=1.5))

    # Панель 3
    g.append(fitbox(660, 375, 260, 70, "Ведучий PTY (master fd 3)\n\nПідлеглий PTY: /dev/pts/12", size=11, fill="#ffffff", stroke="#22c55e"))
    g.append(fitbox(680, 465, 220, 65, "Панель 3 (Pane 3)\nЗбірка cargo build (PID 1150)\nтривалий фоновий процес", size=11, bold=True, fill="#e0f2fe", stroke=NEG))
    g.append(arrow(790, 445, 790, 465, color=NEG, sw=1.5))

    return render(os.path.join(IMG, 'multiplexer-architecture.svg'), W, H, *g,
                  title="Архітектура мультиплексора: клієнт, сокет, сервер і дерево PTY")


def fig_detach_attach_lifecycle():
    """Життєвий цикл сеансу: активне з'єднання, розрив мережі і перепідключення."""
    W, H = 1000, 520
    g = []

    col_w = 280
    c1_x = 40
    c2_x = 360
    c3_x = 680

    # Заголовки колонок
    g.append(fitbox(c1_x, 50, col_w, 42, "1. Звичайний робочий сеанс", size=13, bold=True, fill="#eaf0fd", stroke=NEG))
    g.append(fitbox(c2_x, 50, col_w, 42, "2. Розрив мережі (Detach)", size=13, bold=True, fill="#fdecea", stroke=POS))
    g.append(fitbox(c3_x, 50, col_w, 42, "3. Перепідключення (Attach)", size=13, bold=True, fill="#eaf7ee", stroke=FIELD))

    # Етап 1: Активний сеанс
    g.append(fitbox(c1_x, 105, col_w, 70, "Клієнт SSH (pts/0)\nПередає натискання клавіш\nчерез UNIX-сокет до tmux-server", size=11, fill="#ffffff", stroke=LINE))
    g.append(arrow(c1_x + col_w / 2, 175, c1_x + col_w / 2, 205, color=LINE, sw=1.5))
    g.append(fitbox(c1_x, 205, col_w, 80, "tmux-server (без TTY)\nОтримує байти, направляє у master PTY,\nперемальовує віртуальну сітку", size=11, fill="#ffffff", stroke=LINE))
    g.append(arrow(c1_x + col_w / 2, 285, c1_x + col_w / 2, 315, color=LINE, sw=1.5))
    g.append(fitbox(c1_x, 315, col_w, 80, "Дочірній процес (на pts/1)\nОтримує ввід, виконує задачу,\nпише результат у slave PTY", size=11, fill="#f8fafc", stroke=LINE))
    g.append(fitbox(c1_x, 415, col_w, 75, "Стан: з'єднання активне\nКористувач бачить живий екран,\nвсі потоки синхронізовані", size=11, fill="#eff6ff", stroke=NEG))

    # Етап 2: Розрив
    g.append(fitbox(c2_x, 105, col_w, 70, "SSH клієнт відпав ✖\nМережеве з'єднання скинуто,\nклієнтський процес завершено", size=11, fill="#fef2f2", stroke=POS))
    g.append(line(c2_x + col_w / 2, 175, c2_x + col_w / 2, 205, color=POS, sw=1.5, dash="4 4"))
    g.append(fitbox(c2_x, 205, col_w, 80, "tmux-server (живий)\nЗакриває сокет клієнта,\nале master PTY лишає відкритими", size=11, fill="#ffffff", stroke=POS))
    g.append(arrow(c2_x + col_w / 2, 285, c2_x + col_w / 2, 315, color=FIELD, sw=1.5))
    g.append(fitbox(c2_x, 315, col_w, 80, "Дочірній процес (на pts/1)\nНЕ отримує SIGHUP!\nПродовжує рахувати у буфер", size=11, bold=True, fill="#f0fdf4", stroke=FIELD))
    g.append(fitbox(c2_x, 415, col_w, 75, "Стан: ізольований фоновий біг\nДані не втрачено, буфер збирає\nвивід у пам'ять сервера", size=11, fill="#fef2f2", stroke=POS))

    # Етап 3: Перепідключення
    g.append(fitbox(c3_x, 105, col_w, 70, "Новий клієнт (tmux attach)\nПідключається з іншої машини,\nпередає новий розмір вікна", size=11, fill="#ffffff", stroke=FIELD))
    g.append(arrow(c3_x + col_w / 2, 175, c3_x + col_w / 2, 205, color=FIELD, sw=1.5))
    g.append(fitbox(c3_x, 205, col_w, 80, "tmux-server\nСкидає повний зліпок екрана,\nнадсилає SIGWINCH на master PTY", size=11, fill="#ffffff", stroke=FIELD))
    g.append(arrow(c3_x + col_w / 2, 285, c3_x + col_w / 2, 315, color=FIELD, sw=1.5))
    g.append(fitbox(c3_x, 315, col_w, 80, "Дочірній процес (на pts/1)\nАдаптує розкладку під новий розмір,\nпродовжує інтерактивну роботу", size=11, fill="#f8fafc", stroke=FIELD))
    g.append(fitbox(c3_x, 415, col_w, 75, "Стан: сеанс відновлено\nПовний контекст на місці,\nжоден байт не загублено", size=11, bold=True, fill="#f0fdf4", stroke=FIELD))

    return render(os.path.join(IMG, 'detach-attach-lifecycle.svg'), W, H, *g,
                  title="Збереження стану сеансу при розриві мережі та перепідключенні")


def fig_diff_rendering_pipeline():
    """Конвеєр емуляції термінала та диференційного перемальовування."""
    W, H = 1000, 480
    g = []

    # 4 послідовні блоки
    bx = 40
    bw = 200
    gap = 45

    # 1. Джерело виводу
    g.append(fitbox(bx, 70, bw, 45, "1. Потік процесу", size=13, bold=True, fill="#f1f5f9", stroke="#475569"))
    g.append(fitbox(bx, 130, bw, 240,
                    "Дочірня програма\n(vim / top / bash)\n\nпише у slave PTY:\n\nтекст UTF-8 та\nкеруючі коди ANSI\n(\\033[31m, \\033[2J)",
                    size=12, fill="#ffffff", stroke=LINE))
    g.append(arrow(bx + bw, 250, bx + bw + gap, 250, color=LINE, sw=1.8))

    # 2. Емулятор VT100
    bx += bw + gap
    g.append(fitbox(bx, 70, bw, 45, "2. Парсер емулятора", size=13, bold=True, fill="#fef3c7", stroke="#d97706"))
    g.append(fitbox(bx, 130, bw, 240,
                    "Машина станів tmux\n\nрозбирає ESC-коди:\n• координати курсора\n• кольори (24-bit RGB)\n• атрибути стилю\n\nОновлює матрицю\nкомірок (grid_cell)",
                    size=12, fill="#ffffff", stroke="#d97706"))
    g.append(arrow(bx + bw, 250, bx + bw + gap, 250, color=LINE, sw=1.8))

    # 3. Diff Engine
    bx += bw + gap
    g.append(fitbox(bx, 70, bw, 45, "3. Механізм Diff", size=13, bold=True, fill="#e0e7ff", stroke="#4f46e5"))
    g.append(fitbox(bx, 130, bw, 240,
                    "Порядкове порівняння\n\nПоточна матриця вікна\nпроти\nПопереднього стану\nекрана клієнта\n\nВиявлення мінімальних\nзмінених фрагментів",
                    size=12, fill="#ffffff", stroke="#4f46e5"))
    g.append(arrow(bx + bw, 250, bx + bw + gap, 250, color=LINE, sw=1.8))

    # 4. Клієнтський TTY
    bx += bw + gap
    g.append(fitbox(bx, 70, bw, 45, "4. Вивід клієнту", size=13, bold=True, fill="#dcfce7", stroke=FIELD))
    g.append(fitbox(bx, 130, bw, 240,
                    "Мінімізований потік\n\nСервер генерує:\n\\033[row;colH + оновлення\n\nКлієнт малює лише\nзмінені ділянки\n(економія трафіку)",
                    size=12, fill="#ffffff", stroke=FIELD))

    g.append(fitbox(40, 395, 920, 55,
                    "Оптимізація: замість пересилки 80×24 = 1920 комірок при кожному оновленні, сервер надсилає лічені байти змінених координат і символів",
                    size=12, bold=True, fill="#f8fafc", stroke=MUTED))

    return render(os.path.join(IMG, 'diff-rendering-pipeline.svg'), W, H, *g,
                  title="Конвеєр емуляції та диференційного перемальовування екрана")


if __name__ == '__main__':
    fig_multiplexer_architecture()
    fig_detach_attach_lifecycle()
    fig_diff_rendering_pipeline()
    print("OK: generated 3 figures.")
