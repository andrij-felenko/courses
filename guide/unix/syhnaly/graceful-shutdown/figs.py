# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT = "#fbfcff"
WARM = "#fdecea"
COLD = "#eaf0fd"
GREENFILL = "#eafaf1"
WARN = "#fef9e7"
WARN_STROKE = "#d4ac0d"


# ── 1. П'ять фаз коректного завершення ─────────────────────────────────────────
def fig_shutdown_phases():
    W, H = 1080, 560
    p = []

    # Заголовок зверху
    p.append(text(540, 36, "П'ЯТИФАЗНИЙ ПРОТОКОЛ ШТАТНОГО ВИМИКАННЯ СЕРВІСУ", size=15, color=INK, bold=True))

    # Фаза 1: Перехоплення
    p.append(rect(40, 70, 180, 180, fill=WARM, stroke=POS, sw=1.8, rx=8))
    p.append(text(130, 96, "ФАЗА 1", size=12, color=POS, bold=True))
    p.append(text(130, 116, "Сигнал зупинки", size=13, color=INK, bold=True))
    p.append(mtext(130, 142, [
        "SIGTERM / SIGINT",
        "Перевід стану в STOPPING",
        "Збереження причини",
        "Асинхронний перехід"
    ], size=11, color=INK, lh=1.3))

    p.append(arrow(224, 160, 252, 160, color=MUTED, sw=2))

    # Фаза 2: Зупинка прийому
    p.append(rect(256, 70, 180, 180, fill=WARN, stroke=WARN_STROKE, sw=1.8, rx=8))
    p.append(text(346, 96, "ФАЗА 2", size=12, color=WARN_STROKE, bold=True))
    p.append(text(346, 116, "Зупинка входу", size=13, color=INK, bold=True))
    p.append(mtext(346, 142, [
        "close(listen_fd)",
        "Від'єднання від балансера",
        "Healthcheck -> 503",
        "Відхилення нових запитів"
    ], size=11, color=INK, lh=1.3))

    p.append(arrow(440, 160, 468, 160, color=MUTED, sw=2))

    # Фаза 3: Дренування
    p.append(rect(472, 70, 180, 180, fill=COLD, stroke=NEG, sw=1.8, rx=8))
    p.append(text(562, 96, "ФАЗА 3", size=12, color=NEG, bold=True))
    p.append(text(562, 116, "Дренування робіт", size=13, color=INK, bold=True))
    p.append(mtext(562, 142, [
        "Доопрацювання in-flight",
        "HTTP/2 GOAWAY фрейм",
        "Connection: close",
        "Завершення транзакцій"
    ], size=11, color=INK, lh=1.3))

    p.append(arrow(656, 160, 684, 160, color=MUTED, sw=2))

    # Фаза 4: Оповіщення воркерів
    p.append(rect(688, 70, 180, 180, fill=SOFT, stroke=MUTED, sw=1.8, rx=8))
    p.append(text(778, 96, "ФАЗА 4", size=12, color=MUTED, bold=True))
    p.append(text(778, 116, "Зупинка потоків", size=13, color=INK, bold=True))
    p.append(mtext(778, 142, [
        "stop_token / eventfd",
        "Пробудження фону",
        "pthread_join() / waitpid",
        "Збір дочірніх процесів"
    ], size=11, color=INK, lh=1.3))

    p.append(arrow(872, 160, 900, 160, color=MUTED, sw=2))

    # Фаза 5: Очищення і вихід
    p.append(rect(904, 70, 140, 180, fill=GREENFILL, stroke=FIELD, sw=1.8, rx=8))
    p.append(text(974, 96, "ФАЗА 5", size=12, color=FIELD, bold=True))
    p.append(text(974, 116, "Очищення", size=13, color=INK, bold=True))
    p.append(mtext(974, 142, [
        "fflush() / fsync()",
        "flock(LOCK_UN)",
        "unlink(pidfile)",
        "exit(0)"
    ], size=11, color=INK, lh=1.3))

    # Нижня панель: Контроль часу та примусове переривання
    p.append(rect(40, 276, 1004, 250, fill=SOFT, stroke=LINE, sw=1.5, rx=8))
    p.append(text(540, 304, "Паралельний таймер безпеки (Watchdog vs SIGKILL)", size=14, color=INK, bold=True))

    p.append(rect(70, 328, 430, 172, fill=GREENFILL, stroke=FIELD, sw=1.5, rx=6))
    p.append(text(285, 354, "ШТАТНИЙ СЦЕНАРІЙ (Успіх)", size=13, color=FIELD, bold=True))
    p.append(mtext(285, 382, [
        "1. Усі клієнти отримали коректні відповіді на запити",
        "2. Журнали скинуто на диск без обриву байтів",
        "3. Відкриті з'єднання закриті чотиристороннім FIN-обміном",
        "4. Процес повертає ядру код 0 до вичерпання ліміту часу"
    ], size=11.5, color=INK, lh=1.35))

    p.append(rect(540, 328, 470, 172, fill=WARM, stroke=POS, sw=1.5, rx=6))
    p.append(text(775, 354, "ЕСКАЛАЦІЯ ПРИ ЗАВИСАННІ (Таймаут)", size=13, color=POS, bold=True))
    p.append(mtext(775, 382, [
        "1. Завислий клієнт або заблокований м'ютекс гальмують вихід",
        "2. Внутрішній таймер (timerfd) перериває затяжне дренування",
        "3. Друк аварійного дампу пам'яті / стеку завислих потоків",
        "4. Якщо процес не виходить сам — оркестратор надсилає SIGKILL"
    ], size=11.5, color=INK, lh=1.35))

    render(os.path.join(OUT, "shutdown-phases.svg"), W, H, *p)


# ── 2. Патерни перетворення асинхронного сигналу в подію ───────────────────────
def fig_signal_bridges():
    W, H = 1080, 600
    p = []

    p.append(text(540, 36, "МІСТ МІЖ СИГНАЛОМ ЯДРА ТА ГОЛОВНИМ ЦИКЛОМ ПОДІЙ", size=15, color=INK, bold=True))

    # Схема 1: Атомарний прапорець (Пастка сну)
    p.append(rect(40, 66, 310, 500, fill=WARM, stroke=POS, sw=1.8, rx=8))
    p.append(text(195, 94, "1. Атомарний прапорець", size=13.5, color=POS, bold=True))
    p.append(text(195, 114, "Пастка блокуючого сну", size=11.5, color=MUTED))

    p.append(fitbox(56, 134, 278, 90,
                    "Обробник сигналу:\nstatic volatile sig_atomic_t g_quit = 1;\n(async-signal-safe запис прапорця)",
                    size=11, fill=BG, stroke=POS, sw=1.2))

    p.append(arrow(195, 230, 195, 260, color=POS, sw=1.5))

    p.append(fitbox(56, 266, 278, 120,
                    "Головний потік:\nwhile (!g_quit) {\n    epoll_wait(epfd, evs, 64, -1);\n    // СПИТЬ У ВИКЛИКУ!\n}",
                    size=11, fill=BG, stroke=POS, sw=1.2))

    p.append(fitbox(56, 400, 278, 150,
                    "ДЕФЕКТ: сигнал приходить,\nколи потік спить в epoll_wait.\nЯкщо прапорець виставлено,\nале нових дескрипторів немає —\nпотік не прокинеться і зависне\nдо зовнішньої мережевої події!",
                    size=11, fill=WARM, stroke=POS, sw=1.5, bold=True, color=POS))

    # Схема 2: Self-Pipe Trick (POSIX)
    p.append(rect(385, 66, 310, 500, fill=COLD, stroke=NEG, sw=1.8, rx=8))
    p.append(text(540, 94, "2. Self-Pipe Trick", size=13.5, color=NEG, bold=True))
    p.append(text(540, 114, "Портативний стандарт POSIX", size=11.5, color=MUTED))

    p.append(fitbox(401, 134, 278, 90,
                    "Обробник сигналу:\nwrite(g_pipe_write_fd, \"x\", 1);\n(виклик write є безпечним\nв обробнику сигналу)",
                    size=11, fill=BG, stroke=NEG, sw=1.2))

    p.append(arrow(540, 230, 540, 260, color=NEG, sw=1.5))

    p.append(fitbox(401, 266, 278, 120,
                    "Головний потік в epoll:\n1. epoll_wait прокидається на pipe_read_fd\n2. read(pipe_read_fd, buf, 1)\n3. Запуск штатного вимикання",
                    size=11, fill=BG, stroke=NEG, sw=1.2))

    p.append(fitbox(401, 400, 278, 150,
                    "ПЕРЕВАГИ:\n- Миттєве пробудження epoll\n- Код вимикання виконується\n  у безпечному просторі користувача\n- Повна підтримка heap, locks, C++\n- Працює на Linux, BSD, macOS",
                    size=11, fill=COLD, stroke=NEG, sw=1.5, color=INK))

    # Схема 3: signalfd (Linux Event-Loop Native)
    p.append(rect(730, 66, 310, 500, fill=GREENFILL, stroke=FIELD, sw=1.8, rx=8))
    p.append(text(885, 94, "3. signalfd / Сигнальний потік", size=13.5, color=FIELD, bold=True))
    p.append(text(885, 114, "Ідіоматичний підхід Linux", size=11.5, color=MUTED))

    p.append(fitbox(746, 134, 278, 90,
                    "Блокування сигналів:\npthread_sigmask(SIG_BLOCK, &mask, NULL);\nint sfd = signalfd(-1, &mask, SFD_NONBLOCK);",
                    size=11, fill=BG, stroke=FIELD, sw=1.2))

    p.append(arrow(885, 230, 885, 260, color=FIELD, sw=1.5))

    p.append(fitbox(746, 266, 278, 120,
                    "Дескриптор в epoll:\n1. sfd додається до epoll_ctl()\n2. Сигнал приходить як read-подія\n3. read(sfd, &siginfo, sizeof(siginfo))",
                    size=11, fill=BG, stroke=FIELD, sw=1.2))

    p.append(fitbox(746, 400, 278, 150,
                    "ІДЕАЛЬНА БЕЗПЕКА:\n- Жодного обробника сигналів\n- Нуль ризиків асинхронної реентрабельності\n- Сигнал — це звичайний потік байтів\n- Повні метадані (PID відправника, UID)",
                    size=11, fill=GREENFILL, stroke=FIELD, sw=1.5, color=INK))

    render(os.path.join(OUT, "signal-bridges.svg"), W, H, *p)


# ── 3. Ескалація дедлайнів завершення ─────────────────────────────────────────
def fig_escalation_timeline():
    W, H = 1080, 500
    p = []

    p.append(text(540, 36, "ЧАСОВА ШКАЛА ЕСКАЛАЦІЇ ДЕДЛАЙНІВ ВИМИКАННЯ", size=15, color=INK, bold=True))

    # Вісь часу
    p.append(line(80, 140, 1000, 140, color=LINE, sw=3))
    p.append(arrow(990, 140, 1010, 140, color=LINE, sw=3))
    p.append(text(1020, 145, "Час t", size=13, color=INK, bold=True))

    # Точка 1: T0 (SIGTERM)
    p.append(circle(120, 140, 8, fill=POS, stroke=LINE, sw=1.5))
    p.append(line(120, 90, 120, 130, color=POS, sw=1.8, dash="4,3"))
    p.append(fitbox(45, 50, 150, 38, "t = 0 c\nSIGTERM / SIGINT", size=11, fill=WARM, stroke=POS, bold=True, color=POS))
    p.append(text(120, 170, "Початок зупинки", size=11.5, color=INK, bold=True))
    p.append(text(120, 188, "Закриття listen_fd", size=10.5, color=MUTED))

    # Точка 2: Штатне завершення (Т_drain)
    p.append(circle(360, 140, 8, fill=FIELD, stroke=LINE, sw=1.5))
    p.append(line(360, 90, 360, 130, color=FIELD, sw=1.8, dash="4,3"))
    p.append(fitbox(280, 50, 160, 38, "t = 2.4 c (Штатний вихід)\nexit(0)", size=11, fill=GREENFILL, stroke=FIELD, bold=True, color=FIELD))
    p.append(text(360, 170, "Дренування завершено", size=11.5, color=FIELD, bold=True))
    p.append(text(360, 188, "Всі з'єднання закриті", size=10.5, color=MUTED))

    # Точка 3: Попередження (Т_warn)
    p.append(circle(640, 140, 8, fill=WARN_STROKE, stroke=LINE, sw=1.5))
    p.append(line(640, 90, 640, 130, color=WARN_STROKE, sw=1.8, dash="4,3"))
    p.append(fitbox(560, 50, 160, 38, "t = 15 c (Поріг тривоги)\nWarning / Thread Dump", size=11, fill=WARN, stroke=WARN_STROKE, bold=True, color=WARN_STROKE))
    p.append(text(640, 170, "Виявлено завислі задачі", size=11.5, color=WARN_STROKE, bold=True))
    p.append(text(640, 188, "Логування активних fd", size=10.5, color=MUTED))

    # Точка 4: Внутрішній Watchdog (Т_watchdog)
    p.append(circle(820, 140, 8, fill=POS, stroke=LINE, sw=1.5))
    p.append(line(820, 90, 820, 130, color=POS, sw=1.8, dash="4,3"))
    p.append(fitbox(735, 50, 170, 38, "t = 25 c (Внутрішній ліміт)\nСамозавершення _exit(1)", size=11, fill=WARM, stroke=POS, bold=True, color=POS))
    p.append(text(820, 170, "Watchdog timeout", size=11.5, color=POS, bold=True))
    p.append(text(820, 188, "Екстрене скидання стану", size=10.5, color=MUTED))

    # Точка 5: Зовнішній SIGKILL (Т_kill)
    p.append(circle(960, 140, 8, fill="#7b1113", stroke=LINE, sw=1.5))
    p.append(line(960, 90, 960, 130, color="#7b1113", sw=1.8, dash="4,3"))
    p.append(fitbox(880, 50, 160, 38, "t = 30 c (Жорсткий ліміт)\nНевідворотний SIGKILL", size=11, fill=WARM, stroke="#7b1113", bold=True, color="#7b1113"))
    p.append(text(960, 170, "Примусове вбивство", size=11.5, color="#7b1113", bold=True))
    p.append(text(960, 188, "systemd / Kubernetes", size=10.5, color=MUTED))

    # Нижні деталізовані блоки
    p.append(rect(60, 230, 440, 230, fill=GREENFILL, stroke=FIELD, sw=1.5, rx=8))
    p.append(text(280, 258, "ЗОНА БЕЗПЕКИ ТА ШТАТНОГО ДРЕНУВАННЯ", size=13, color=FIELD, bold=True))
    p.append(mtext(280, 288, [
        "• Процес зупиняє прийом нових запитів негайно після SIGTERM",
        "• Клієнтам надається вікно на завершення передачі даних",
        "• У 99.9% випадків процес самостійно виходить за 0.5 - 3 секунди",
        "• Жодних обірваних транзакцій чи пошкоджених файлів",
        "• Балансувальник навантаження плавно перемикає трафік"
    ], size=11.5, color=INK, lh=1.4))

    p.append(rect(540, 230, 480, 230, fill=WARM, stroke=POS, sw=1.5, rx=8))
    p.append(text(780, 258, "ЗОНА РИЗИКУ ТА ЗАХИСНОЇ ЕСКАЛАЦІЇ", size=13, color=POS, bold=True))
    p.append(mtext(780, 288, [
        "• Зависання трапляється через deadlock, повільний I/O або витік",
        "• Внутрішній таймер (t = 25 c) ПОВИНЕН спрацювати ДО SIGKILL (t = 30 c)",
        "• Це дає шанс зафіксувати причину зависання у логах ядра/сервісу",
        "• Зовнішній SIGKILL знищує процес миттєво без виклику коду очищення,",
        "  залишаючи сміття на диску та скидаючи з'єднання пакетом TCP RST"
    ], size=11.5, color=INK, lh=1.4))

    render(os.path.join(OUT, "escalation-timeline.svg"), W, H, *p)


if __name__ == "__main__":
    fig_shutdown_phases()
    fig_signal_bridges()
    fig_escalation_timeline()
    print("Figures generated successfully.")
