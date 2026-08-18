# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фіг. 1: Модель «потік на з'єднання» проти однопотокового Reactor ─────────
def fig_c10k_thread_vs_event():
    W, H = 960, 520
    p = []

    # Ліва панель: Багатопотокова модель (Thread-per-connection)
    lx, ly, pw, ph = 30.0, 40.0, 430.0, 400.0
    p.append(rect(lx, ly, pw, ph, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
    p.append(fitbox(lx + 20, ly + 16, pw - 40, 32, "Модель «потік на з'єднання» (Thread-per-Connection)",
                    size=13.5, bold=True, fill="#fdecea", stroke=POS, color=POS))

    # Клієнти ліворуч
    p.append(text(lx + 50, ly + 80, "10 000 клієнтів", size=12, color=MUTED, bold=True))
    for i in range(4):
        cy = ly + 115 + i * 55
        p.append(rect(lx + 25, cy - 16, 75, 32, fill="#eef2f8", stroke="#9fb3c8", sw=1.2, rx=4))
        p.append(text(lx + 62, cy + 4, f"Сокет {i+1}", size=11, color=INK))
        p.append(arrow(lx + 105, cy, lx + 160, cy, color=MUTED, sw=1.3))

    # Потоки ядра
    p.append(text(lx + 225, ly + 80, "10 000 системних потоків", size=12, color=POS, bold=True))
    for i in range(4):
        cy = ly + 115 + i * 55
        p.append(rect(lx + 165, cy - 20, 235, 40, fill="#fdf0dc", stroke="#e08a1e", sw=1.3, rx=6))
        p.append(text(lx + 215, cy - 2, f"Потік {i+1} (pthread)", size=11, color=INK, bold=True))
        p.append(text(lx + 215, cy + 13, "Стек 8 МБ + task_struct", size=9.5, color=MUTED))
        p.append(rect(lx + 310, cy - 14, 80, 28, fill="#fdecea", stroke=POS, sw=1.1, rx=4))
        p.append(text(lx + 350, cy + 4, "Спить у read()", size=9.5, color=POS, bold=True))

    # Підсумок лівої панелі
    p.append(fitbox(lx + 15, ly + ph - 62, pw - 30, 48,
                    "Витрати: 10 000 × 8 МБ стеків ≈ 80 ГБ віртуальної пам'яті,\nтисячі перемикань контексту на секунду, спустошення L1/L2 кешу.",
                    size=10.5, bold=False, fill="#fdecea", stroke=POS, color=INK))

    # Права панель: Однопотоковий Reactor на epoll
    rx = 500.0
    p.append(rect(rx, ly, pw, ph, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
    p.append(fitbox(rx + 20, ly + 16, pw - 40, 32, "Подієва модель: 1 потік на всі з'єднання (Reactor)",
                    size=13.5, bold=True, fill="#eef7f0", stroke=FIELD, color=FIELD))

    # Клієнти праворуч
    p.append(text(rx + 50, ly + 80, "10 000 клієнтів", size=12, color=MUTED, bold=True))
    for i in range(4):
        cy = ly + 115 + i * 55
        p.append(rect(rx + 25, cy - 16, 75, 32, fill="#eef2f8", stroke="#9fb3c8", sw=1.2, rx=4))
        p.append(text(rx + 62, cy + 4, f"Сокет {i+1}", size=11, color=INK))
        p.append(arrow(rx + 105, cy, rx + 160, cy, color=MUTED, sw=1.3))

    # Центральний диспетчер Reactor
    p.append(rect(rx + 165, ly + 95, 240, 220, fill="#eef7f0", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(rx + 285, ly + 120, "ЄДИНИЙ робочий потік", size=12.5, color=FIELD, bold=True))
    p.append(rect(rx + 180, ly + 138, 210, 48, fill="#ffffff", stroke="#9fb3c8", sw=1.2, rx=4))
    p.append(text(rx + 285, ly + 158, "epoll_wait(epfd, ...)", size=11.5, color=INK, bold=True))
    p.append(text(rx + 285, ly + 174, "Спить, доки немає активності", size=9.5, color=MUTED))

    p.append(rect(rx + 180, ly + 196, 210, 52, fill="#ffffff", stroke="#9fb3c8", sw=1.2, rx=4))
    p.append(text(rx + 285, ly + 215, "Неблокуючий ввід-вивід", size=11, color=INK, bold=True))
    p.append(text(rx + 285, ly + 233, "Обробка готових дескрипторів", size=9.5, color=FIELD, bold=True))

    p.append(rect(rx + 180, ly + 258, 210, 44, fill="#ffffff", stroke="#9fb3c8", sw=1.2, rx=4))
    p.append(text(rx + 285, ly + 276, "Таблиця станів сесій", size=11, color=INK))
    p.append(text(rx + 285, ly + 292, "Буфери користувача в heap", size=9.5, color=MUTED))

    # Підсумок правої панелі
    p.append(fitbox(rx + 15, ly + ph - 62, pw - 30, 48,
                    "Витрати: 1 стек (8 МБ), 0 зайвих перемикань контексту CPU,\nпам'ять витрачається лише на фактичні буфери активних сесій.",
                    size=10.5, bold=False, fill="#eef7f0", stroke=FIELD, color=INK))

    # Нижній висновок
    p.append(fitbox(30, 460, W - 60, 36,
                    "Перехід від моделі «потік на клієнта» до єдиного подієвого циклу усуває паразитні накладні витрати ядра при масштабуванні до десятків тисяч з'єднань.",
                    size=12, bold=True, fill="#fff6e6", stroke="#e08a1e", color=INK))

    render(os.path.join(OUT, "c10k-thread-vs-event.svg"), W, H, *p,
           title="Порівняння архітектури: потік на з'єднання проти подієвого Reactor")


# ── Фіг. 2: select/poll O(N) проти epoll O(1) ─────────────────────────────────
def fig_select_poll_vs_epoll():
    W, H = 960, 520
    p = []

    # Ліва колонка: select / poll (лінійне сканування O(N))
    lx, ly, pw, ph = 30.0, 40.0, 430.0, 400.0
    p.append(rect(lx, ly, pw, ph, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
    p.append(fitbox(lx + 20, ly + 16, pw - 40, 32, "select(2) та poll(2) — складність O(N)",
                    size=13.5, bold=True, fill="#fdecea", stroke=POS, color=POS))

    # Кроки select/poll
    steps_left = [
        ("1. Підготовка масиву FD", "Програма заповнює масив із N дескрипторів\n(наприклад, 10 000 елементів struct pollfd).", "#eef2f8"),
        ("2. Копіювання в ядро", "Системний виклик копіює весь масив 10 000 FD\nіз простору користувача в пам'ять ядра.", "#fdecea"),
        ("3. Лінійне опитування ядром", "Ядро проходить циклом по всіх 10 000 FD,\nреєструючи колбеки в чергах очікування сокетів.", "#fdecea"),
        ("4. Сканування після пробудження", "Програма перебирає весь масив 10 000 FD,\nщоб знайти 2 сокети, де revents != 0.", "#fdecea"),
    ]

    for i, (stitle, sdesc, sfill) in enumerate(steps_left):
        sy = ly + 65 + i * 72
        p.append(rect(lx + 20, sy, pw - 40, 62, fill=sfill, stroke="#9fb3c8" if sfill != "#fdecea" else POS, sw=1.2, rx=6))
        p.append(text(lx + 32, sy + 18, stitle, size=11.5, color=POS if sfill == "#fdecea" else INK, bold=True, anchor="start"))
        lines = sdesc.split("\n")
        p.append(text(lx + 32, sy + 36, lines[0], size=10, color=INK, anchor="start"))
        p.append(text(lx + 32, sy + 50, lines[1], size=10, color=MUTED, anchor="start"))

    # Права колонка: epoll (подієвий диспетчер O(1))
    rx = 500.0
    p.append(rect(rx, ly, pw, ph, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
    p.append(fitbox(rx + 20, ly + 16, pw - 40, 32, "epoll(7) — складність O(активні)",
                    size=13.5, bold=True, fill="#eef7f0", stroke=FIELD, color=FIELD))

    # Кроки epoll
    steps_right = [
        ("1. Реєстрація через epoll_ctl", "Дескриптор додається в ядро один раз у\nчервоно-чорне дерево інтересів (struct eventpoll.rbr).", "#eef7f0"),
        ("2. Асинхронний колбек ядра", "При надходженні пакета драйвер викликає\nep_poll_callback, що додає FD у список готових (rdllist).", "#eef7f0"),
        ("3. Виклик epoll_wait", "Ядро перевіряє тільки зв'язний список rdllist.\nНемає сканування неактивних дескрипторів!", "#eef7f0"),
        ("4. Повернення лише готових подій", "Ядро копіює користувачеві виключно готові\nподії (наприклад, 2 елементи замість 10 000).", "#eef7f0"),
    ]

    for i, (stitle, sdesc, sfill) in enumerate(steps_right):
        sy = ly + 65 + i * 72
        p.append(rect(rx + 20, sy, pw - 40, 62, fill=sfill, stroke=FIELD, sw=1.2, rx=6))
        p.append(text(rx + 32, sy + 18, stitle, size=11.5, color=FIELD, bold=True, anchor="start"))
        lines = sdesc.split("\n")
        p.append(text(rx + 32, sy + 36, lines[0], size=10, color=INK, anchor="start"))
        p.append(text(rx + 32, sy + 50, lines[1], size=10, color=MUTED, anchor="start"))

    # Нижній висновок
    p.append(fitbox(30, 460, W - 60, 36,
                    "epoll замінює постійне копіювання і перебір N дескрипторів на постійне дерево реєстрації та пряме повернення списку готових подій.",
                    size=12, bold=True, fill="#eef7f0", stroke=FIELD, color=INK))

    render(os.path.join(OUT, "select-poll-vs-epoll.svg"), W, H, *p,
           title="Порівняння механізмів: O(N) сканування у poll проти O(1) черги готових у epoll")


# ── Фіг. 3: Level-Triggered (LT) проти Edge-Triggered (ET) ───────────────────
def fig_level_vs_edge_triggered():
    W, H = 960, 520
    p = []

    # Верхня панель: Level-Triggered (за рівнем)
    lx, ly, pw, ph = 30.0, 40.0, 900.0, 195.0
    p.append(rect(lx, ly, pw, ph, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
    p.append(fitbox(lx + 20, ly + 14, 380, 28, "Level-Triggered (LT) — сповіщення за рівнем",
                    size=13, bold=True, fill="#eaf0fd", stroke=NEG, color=NEG))

    # Схема LT
    p.append(rect(lx + 30, ly + 55, 230, 60, fill="#ffffff", stroke="#9fb3c8", sw=1.2, rx=6))
    p.append(text(lx + 145, ly + 76, "Буфер сокета в ядрі", size=11, color=MUTED))
    p.append(text(lx + 145, ly + 96, "Є 4096 байтів даних", size=12, color=INK, bold=True))

    p.append(arrow(lx + 270, ly + 85, lx + 330, ly + 85, color=INK, sw=1.5))

    p.append(rect(lx + 340, ly + 55, 250, 60, fill="#eaf0fd", stroke=NEG, sw=1.3, rx=6))
    p.append(text(lx + 465, ly + 76, "epoll_wait() повертає EPOLLIN", size=11.5, color=NEG, bold=True))
    p.append(text(lx + 465, ly + 96, "Прочитано лише 1024 байти", size=10.5, color=INK))

    p.append(arrow(lx + 600, ly + 85, lx + 660, ly + 85, color=INK, sw=1.5))

    p.append(rect(lx + 670, ly + 55, 200, 60, fill="#fdecea", stroke=POS, sw=1.3, rx=6))
    p.append(text(lx + 770, ly + 76, "Наступний epoll_wait()", size=11.5, color=POS, bold=True))
    p.append(text(lx + 770, ly + 96, "Знову негайно будить!", size=10.5, color=POS, bold=True))

    p.append(fitbox(lx + 30, ly + 130, pw - 60, 48,
                    "Поки в буфері лишаються невичитані байти (рівень > 0), epoll_wait продовжує повертати готовність дескриптора.\nБезпечно до помилок у логіці читання, але може створювати зайві пробудження ядра.",
                    size=11, bold=False, fill="#eaf0fd", stroke=NEG, color=INK))

    # Нижня панель: Edge-Triggered (за фронтом/перепадом)
    ey = 255.0
    p.append(rect(lx, ey, pw, ph, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
    p.append(fitbox(lx + 20, ey + 14, 400, 28, "Edge-Triggered (ET, EPOLLET) — сповіщення за фронтом",
                    size=13, bold=True, fill="#eef7f0", stroke=FIELD, color=FIELD))

    # Схема ET
    p.append(rect(lx + 30, ey + 55, 230, 60, fill="#ffffff", stroke="#9fb3c8", sw=1.2, rx=6))
    p.append(text(lx + 145, ey + 76, "Прибув новий TCP-сегмент", size=11, color=MUTED))
    p.append(text(lx + 145, ey + 96, "Фронт: перехід 0 → дані", size=12, color=FIELD, bold=True))

    p.append(arrow(lx + 270, ey + 85, lx + 330, ey + 85, color=INK, sw=1.5))

    p.append(rect(lx + 340, ey + 55, 250, 60, fill="#eef7f0", stroke=FIELD, sw=1.3, rx=6))
    p.append(text(lx + 465, ey + 76, "epoll_wait() будить 1 РАЗ", size=11.5, color=FIELD, bold=True))
    p.append(text(lx + 465, ey + 96, "Обов'язковий цикл до EAGAIN!", size=10.5, color=POS, bold=True))

    p.append(arrow(lx + 600, ey + 85, lx + 660, ey + 85, color=INK, sw=1.5))

    p.append(rect(lx + 670, ey + 55, 200, 60, fill="#ffffff", stroke="#9fb3c8", sw=1.2, rx=6))
    p.append(text(lx + 770, ey + 76, "Якщо не дочитати все:", size=11.5, color=POS, bold=True))
    p.append(text(lx + 770, ey + 96, "Наступний виклик засне!", size=10.5, color=POS))

    p.append(fitbox(lx + 30, ey + 130, pw - 60, 48,
                    "Сповіщення надходить виключно в момент зміни стану (прибуття нових байтів або звільнення буфера передачі).\nВимагає неблокуючого сокета та вичитування в циклі while ((n = read(...)) > 0) до отримання помилки EAGAIN.",
                    size=11, bold=False, fill="#eef7f0", stroke=FIELD, color=INK))

    # Підсумок знизу
    p.append(fitbox(30, 465, W - 60, 36,
                    "LT прощає часткове вичитування за рахунок повторних викликів; ET вимагає суворого циклу до EAGAIN, але мінімізує системні виклики.",
                    size=12, bold=True, fill="#fff6e6", stroke="#e08a1e", color=INK))

    render(os.path.join(OUT, "level-vs-edge-triggered.svg"), W, H, *p,
           title="Різниця тригерів epoll: рівневий (Level-Triggered) проти фронтового (Edge-Triggered)")


# ── Фіг. 4: Архітектура патерну Reactor / Event Loop ─────────────────────────
def fig_reactor_event_loop_architecture():
    W, H = 960, 530
    p = []

    # Фон
    p.append(rect(20, 20, W - 40, H - 40, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=12))
    p.append(fitbox(40, 35, W - 80, 32, "Анатомія патерну Reactor: однопотоковий цикл подій (Event Loop)",
                    size=14, bold=True, fill="#eef7f0", stroke=FIELD, color=FIELD))

    # Джерела подій (зліва)
    sx, sy = 50.0, 90.0
    p.append(fitbox(sx, sy, 170, 28, "Джерела подій (FD)", size=12, bold=True, fill="#eaf0fd", stroke=NEG, color=NEG))
    sources = [
        ("Слухаючий TCP сокет", "accept() нових клієнтів"),
        ("Клієнтські TCP сокети", "read() запитів / write()"),
        ("timerfd (Таймери)", "Таймаути та інтервали"),
        ("signalfd (Сигнали)", "SIGINT, SIGTERM, SIGHUP"),
        ("eventfd (Міжпотокові)", "Завдання з пулу потоків"),
    ]
    for i, (st, sd) in enumerate(sources):
        box_y = sy + 38 + i * 54
        p.append(rect(sx, box_y, 170, 46, fill="#ffffff", stroke="#9fb3c8", sw=1.1, rx=5))
        p.append(text(sx + 85, box_y + 18, st, size=10.5, color=INK, bold=True))
        p.append(text(sx + 85, box_y + 34, sd, size=9, color=MUTED))
        p.append(arrow(sx + 175, box_y + 23, sx + 235, 235, color=MUTED, sw=1.2))

    # Центральний демультиплексор (Demultiplexer / epoll)
    dx, dy = 245.0, 110.0
    p.append(rect(dx, dy, 250, 260, fill="#eef7f0", stroke=FIELD, sw=1.6, rx=8))
    p.append(fitbox(dx + 15, dy + 15, 220, 30, "Синхронний демультиплексор", size=12, bold=True, fill="#ffffff", stroke=FIELD, color=FIELD))
    p.append(rect(dx + 15, dy + 55, 220, 65, fill="#ffffff", stroke="#9fb3c8", sw=1.1, rx=4))
    p.append(text(dx + 125, dy + 78, "epoll_wait(epfd, ...)", size=12, color=INK, bold=True))
    p.append(text(dx + 125, dy + 98, "Блокується до появи подій", size=10, color=MUTED))

    p.append(rect(dx + 15, dy + 130, 220, 110, fill="#ffffff", stroke="#9fb3c8", sw=1.1, rx=4))
    p.append(text(dx + 125, dy + 152, "Готові події (Ready List)", size=11, color=FIELD, bold=True))
    p.append(text(dx + 125, dy + 172, "• FD 4: EPOLLIN", size=10.5, color=INK))
    p.append(text(dx + 125, dy + 192, "• FD 9: EPOLLOUT", size=10.5, color=INK))
    p.append(text(dx + 125, dy + 212, "• FD 12 (timer): EPOLLIN", size=10.5, color=INK))

    p.append(arrow(dx + 255, 235, dx + 305, 235, color=INK, sw=1.8))

    # Диспетчер та обробники подій (Event Handlers)
    hx, hy = 560.0, 90.0
    p.append(fitbox(hx, hy, 350, 28, "Диспетчер подій (Event Dispatcher)", size=12, bold=True, fill="#fdf0dc", stroke="#e08a1e", color="#e08a1e"))

    handlers = [
        ("Acceptor Handler (FD слухання)", "Викликає accept4(O_NONBLOCK), реєструє нового клієнта в epoll"),
        ("Read Handler (Вхідні дані)", "Вичитує байти в буфер сесії до EAGAIN, передає в парсер протоколу"),
        ("Write Handler (Вихідні дані)", "Скидає вихідний буфер сесії в сокет; знімає EPOLLOUT, коли порожньо"),
        ("Timer Handler (Таймери)", "Очищає неактивні з'єднання (Idle Timeout), надсилає Heartbeat"),
        ("Signal Handler (Сигнали)", "Вичитує signalfd, запускає коректну зупинку (Graceful Shutdown)"),
    ]

    for i, (ht, hd) in enumerate(handlers):
        box_y = hy + 38 + i * 54
        p.append(rect(hx, box_y, 350, 46, fill="#ffffff", stroke="#9fb3c8", sw=1.1, rx=5))
        p.append(text(hx + 175, box_y + 18, ht, size=11, color=INK, bold=True))
        p.append(text(hx + 175, box_y + 34, hd, size=9.5, color=MUTED))

    # Фази одного такту циклу подій (внизу)
    p.append(fitbox(40, 390, W - 80, 80,
                    "Фази одного такту Event Loop:\n"
                    "1. Опитування таймерів → 2. epoll_wait() з обчисленим таймаутом → 3. Послідовний виклик зареєстрованих обробників\n"
                    "→ 4. Скидання буферів неблокуючого запису → 5. Виконання відкладених завдань і повтор циклу.",
                    size=11, bold=True, fill="#eef7f0", stroke=FIELD, color=INK))

    p.append(fitbox(40, 480, W - 80, 30,
                    "Головне правило Reactor: обробники НЕ повинні блокуватися (жодного синхронного диску чи важких обчислень у головному потоці).",
                    size=11.5, bold=True, fill="#fdecea", stroke=POS, color=POS))

    render(os.path.join(OUT, "reactor-event-loop-architecture.svg"), W, H, *p,
           title="Архітектура та фази виконання патерну Reactor")


if __name__ == "__main__":
    fig_c10k_thread_vs_event()
    fig_select_poll_vs_epoll()
    fig_level_vs_edge_triggered()
    fig_reactor_event_loop_architecture()
    print("OK figs")
