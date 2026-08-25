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


# ── 1. Автомат станів життєвого циклу юніта ──────────────────────────────────
def fig_unit_lifecycle_states():
    W, H = 1080, 580
    p = []

    p.append(text(540, 36, "АВТОМАТ СТАНІВ ЮНІТА SYSTEMD: ВІД ЗАПУСКУ ДО ЗБОЮ", size=15, color=INK, bold=True))

    # Стан 1: Inactive (dead)
    p.append(rect(40, 70, 200, 160, fill=SOFT, stroke=MUTED, sw=1.8, rx=8))
    p.append(text(140, 96, "INACTIVE", size=13, color=MUTED, bold=True))
    p.append(text(140, 116, "SubState: dead", size=11, color=INK, bold=True))
    p.append(mtext(140, 142, [
        "Процес не запущено",
        "Ресурси cgroup вивільнено",
        "Очікування команди start",
        "або активації за сокетом"
    ], size=11, color=INK, lh=1.3))

    p.append(arrow(240, 150, 290, 150, color=MUTED, sw=2))
    p.append(text(265, 140, "start", size=10.5, color=MUTED, bold=True))

    # Стан 2: Activating (start / start-pre)
    p.append(rect(292, 70, 240, 160, fill=WARN, stroke=WARN_STROKE, sw=1.8, rx=8))
    p.append(text(412, 96, "ACTIVATING", size=13, color=WARN_STROKE, bold=True))
    p.append(text(412, 116, "SubState: start / start-pre", size=11, color=INK, bold=True))
    p.append(mtext(412, 142, [
        "Виконання ExecStartPre=",
        "Створення cgroup і просторів",
        "fork() + execve(ExecStart)",
        "Очікування READY=1 / PID"
    ], size=11, color=INK, lh=1.3))

    # Успіх запуску -> Active (running)
    p.append(arrow(532, 150, 582, 150, color=FIELD, sw=2))
    p.append(text(557, 140, "успіх", size=10.5, color=FIELD, bold=True))

    # Стан 3: Active (running / exited)
    p.append(rect(584, 70, 220, 160, fill=GREENFILL, stroke=FIELD, sw=1.8, rx=8))
    p.append(text(694, 96, "ACTIVE", size=13, color=FIELD, bold=True))
    p.append(text(694, 116, "SubState: running / exited", size=11, color=INK, bold=True))
    p.append(mtext(694, 142, [
        "Головний PID активний",
        "Type=simple: після execve",
        "Type=notify: після READY=1",
        "Type=oneshot: active (exited)"
    ], size=11, color=INK, lh=1.3))

    # Збій при старті -> Failed
    p.append(line(412, 230, 412, 330, color=POS, sw=2))
    p.append(arrow(412, 330, 412, 350, color=POS, sw=2))
    p.append(text(446, 280, "помилка execve / таймаут", size=10, color=POS, bold=True))

    # Аварія під час роботи -> Deactivating / Failed
    p.append(arrow(694, 230, 694, 350, color=POS, sw=2))
    p.append(text(744, 280, "аварія / crash / SIGKILL", size=10, color=POS, bold=True))

    # Стан 4: Auto-Restart (фаза очікування)
    p.append(rect(834, 70, 206, 160, fill=COLD, stroke=NEG, sw=1.8, rx=8))
    p.append(text(937, 96, "AUTO-RESTART", size=13, color=NEG, bold=True))
    p.append(text(937, 116, "SubState: auto-restart", size=11, color=INK, bold=True))
    p.append(mtext(937, 142, [
        "Restart=always / on-failure",
        "Таймер RestartSec=...",
        "Очікування паузи",
        "Перезапуск -> activating"
    ], size=11, color=INK, lh=1.3))

    p.append(arrow(804, 130, 834, 130, color=NEG, sw=1.8))
    p.append(line(937, 70, 937, 48, color=NEG, sw=1.8))
    p.append(line(937, 48, 412, 48, color=NEG, sw=1.8))
    p.append(arrow(412, 48, 412, 70, color=NEG, sw=1.8))
    p.append(text(674, 42, "повторний запуск після RestartSec=", size=10, color=NEG, bold=True))

    # Стан 5: Failed (Збій)
    p.append(rect(340, 350, 480, 190, fill="none", stroke=POS, sw=2, rx=8))
    p.append(text(580, 378, "FAILED (ЗБІЙНИЙ СТАН ЮНІТА)", size=14, color=POS, bold=True))
    p.append(text(580, 400, "SubState: failed", size=12, color=INK, bold=True))

    p.append(rect(360, 416, 210, 108, fill=WARM, stroke=POS, sw=1.2, rx=6))
    p.append(text(465, 436, "Причини помилки запуску:", size=11, color=POS, bold=True))
    p.append(mtext(465, 456, [
        "• status=203/EXEC (нема файлу/+x)",
        "• status=217/USER (нема юзера)",
        "• status=226/NAMESPACE (пісочниця)",
        "• status=1/FAILURE (код застосунку)"
    ], size=10.5, color=INK, lh=1.3))

    p.append(rect(590, 416, 210, 108, fill=WARM, stroke=POS, sw=1.2, rx=6))
    p.append(text(695, 436, "Блокування рестарт-петлі:", size=11, color=POS, bold=True))
    p.append(mtext(695, 456, [
        "• Result: start-limit-hit",
        "• Перевищено StartLimitBurst",
        "• Спроби зупинено менеджером",
        "• Потрібен systemctl reset-failed"
    ], size=10.5, color=INK, lh=1.3))

    # Відновлення: reset-failed
    p.append(arrow(340, 445, 140, 445, color=MUTED, sw=2))
    p.append(line(140, 445, 140, 230, color=MUTED, sw=2))
    p.append(text(230, 435, "systemctl reset-failed / start", size=10.5, color=MUTED, bold=True))

    render(os.path.join(OUT, "unit-lifecycle-states.svg"), W, H, *p)


# ── 2. Механізм рестарт-петлі та обмежувач швидкості ─────────────────────────
def fig_restart_loop_rate_limiter():
    W, H = 1080, 520
    p = []

    p.append(text(540, 36, "РЕСТАРТ-ПЕТЛЯ (CRASHLOOP) ТА ОБМЕЖУВАЧ STARTLIMITBURST", size=15, color=INK, bold=True))

    # Часова шкала
    p.append(line(60, 120, 1020, 120, color=LINE, sw=2.5))
    p.append(arrow(1010, 120, 1030, 120, color=LINE, sw=2.5))
    p.append(text(1040, 125, "t (сек)", size=12, color=INK, bold=True))

    # Вікно StartLimitIntervalSec = 10s
    p.append(rect(100, 70, 720, 180, fill="none", stroke=POS, sw=1.5, rx=8))
    p.append(text(460, 92, "Вікно лімітера: StartLimitIntervalSec = 10s (ліміт: StartLimitBurst = 5)", size=12, color=POS, bold=True))

    # Спроби 1..5
    attempts = [
        (140, "Спроба 1", "t = 0.0s", "exit 1"),
        (280, "Спроба 2", "t = 0.5s", "exit 1"),
        (420, "Спроба 3", "t = 1.0s", "exit 1"),
        (560, "Спроба 4", "t = 1.5s", "exit 1"),
        (700, "Спроба 5", "t = 2.0s", "exit 1")
    ]

    for x, label, t_val, res in attempts:
        p.append(circle(x, 120, 7, fill=POS, stroke=LINE, sw=1.5))
        p.append(line(x, 127, x, 160, color=POS, sw=1.2, dash="3,2"))
        p.append(fitbox(x - 55, 165, 110, 68,
                        "%s\n%s\n%s\nRestartSec=100ms" % (label, t_val, res),
                        size=10, fill=WARM, stroke=POS, sw=1.2))

    # Точка 6: Спрацювання лімітера
    p.append(circle(850, 120, 9, fill="#7b1113", stroke=LINE, sw=2))
    p.append(line(850, 129, 850, 160, color="#7b1113", sw=1.8))
    p.append(fitbox(770, 165, 160, 75,
                    "Спроба 6 (Блокування)\nstart-limit-hit!\nЛіміт 5 вичерпано у межах 10с\nСлужбу заблоковано",
                    size=10, fill=WARM, stroke="#7b1113", sw=1.5, bold=True, color="#7b1113"))

    # Нижня частина: Порівняння поведінки
    p.append(rect(60, 270, 450, 220, fill=WARM, stroke=POS, sw=1.5, rx=8))
    p.append(text(285, 298, "НАСЛІДКИ НЕКОНТРОЛЬОВАНОГО CRASHLOOP", size=12.5, color=POS, bold=True))
    p.append(mtext(285, 326, [
        "1. Безконтрольний випал CPU на fork() та execve()",
        "2. Засмічення дискового журналу journald тисячами записів",
        "3. Перевантаження D-Bus та системного диспетчера PID 1",
        "4. Вичерпання доступних PID у системній таблиці ядер",
        "5. Зависання залежних служб у черзі очікування"
    ], size=11, color=INK, lh=1.35))

    p.append(rect(540, 270, 480, 220, fill=GREENFILL, stroke=FIELD, sw=1.5, rx=8))
    p.append(text(780, 298, "ПРАВИЛЬНИЙ АЛГОРИТМ ВИХОДУ З ПЕТЛІ", size=12.5, color=FIELD, bold=True))
    p.append(mtext(780, 326, [
        "1. Зупинити спроби: systemctl stop unit.service",
        "2. Прочитати точний лог падіння: journalctl -u unit.service -e -b",
        "3. Виправити першопричину (конфіг, права, файл, порт)",
        "4. Скинути блокуючий лічильник помилок:",
        "   systemctl reset-failed unit.service",
        "5. Виконати чистий запуск: systemctl start unit.service"
    ], size=11, color=INK, lh=1.35))

    render(os.path.join(OUT, "restart-loop-rate-limiter.svg"), W, H, *p)


# ── 3. Діагностичне дерево розбору несправностей ──────────────────────────────
def fig_systemd_failure_decision_tree():
    W, H = 1080, 620
    p = []

    p.append(text(540, 34, "ДІАГНОСТИЧНЕ ДЕРЕВО: РОЗБІР СЛУЖБИ, ЩО НЕ ПІДНЯЛАСЯ", size=15, color=INK, bold=True))

    # Корінь: systemctl status
    p.append(rect(390, 60, 300, 60, fill=COLD, stroke=NEG, sw=2, rx=8))
    p.append(text(540, 84, "systemctl status <unit>.service", size=13, color=NEG, bold=True))
    p.append(text(540, 104, "Аналіз полів Active:, Process: (code=, status=)", size=10.5, color=INK))

    # Гілка 1: status=203/EXEC
    p.append(line(420, 120, 130, 170, color=LINE, sw=1.5))
    p.append(arrow(130, 170, 130, 190, color=LINE, sw=1.5))
    p.append(rect(30, 190, 200, 170, fill=WARM, stroke=POS, sw=1.5, rx=6))
    p.append(text(130, 212, "status=203/EXEC", size=12, color=POS, bold=True))
    p.append(text(130, 230, "Помилка execve()", size=10.5, color=MUTED))
    p.append(mtext(130, 252, [
        "1. Перевірити шлях бінарника",
        "2. Перевірити біт +x",
        "3. Перевірити шебанг (#!)",
        "4. Перевірити /lib64 лінкер",
        "5. Перевірити опцію noexec"
    ], size=10, color=INK, lh=1.3))

    # Гілка 2: status=217/USER
    p.append(line(480, 120, 370, 170, color=LINE, sw=1.5))
    p.append(arrow(370, 170, 370, 190, color=LINE, sw=1.5))
    p.append(rect(270, 190, 200, 170, fill=WARM, stroke=POS, sw=1.5, rx=6))
    p.append(text(370, 212, "status=217/USER", size=12, color=POS, bold=True))
    p.append(text(370, 230, "Помилка setuid/setgid", size=10.5, color=MUTED))
    p.append(mtext(370, 252, [
        "1. Користувач у User= відсутній",
        "2. Перевірити /etc/passwd",
        "3. Мережевий NSS (LDAP/SSSD)",
        "   стартує пізніше служби",
        "4. Додати After=sssd.service"
    ], size=10, color=INK, lh=1.3))

    # Гілка 3: status=1/FAILURE (код застосунку)
    p.append(line(600, 120, 610, 170, color=LINE, sw=1.5))
    p.append(arrow(610, 170, 610, 190, color=LINE, sw=1.5))
    p.append(rect(510, 190, 200, 170, fill=WARN, stroke=WARN_STROKE, sw=1.5, rx=6))
    p.append(text(610, 212, "status=1/FAILURE", size=12, color=WARN_STROKE, bold=True))
    p.append(text(610, 230, "Збій коду застосунку", size=10.5, color=MUTED))
    p.append(mtext(610, 252, [
        "1. journalctl -u <unit> -b -e",
        "2. Помилка конфігурації YAML/JSON",
        "3. Порт TCP зайнятий (EADDRINUSE)",
        "4. Відсутнє підключення до БД",
        "5. Брак прав на файл логу/даних"
    ], size=10, color=INK, lh=1.3))

    # Гілка 4: code=killed, status=SIGKILL / SIGABRT
    p.append(line(660, 120, 850, 170, color=LINE, sw=1.5))
    p.append(arrow(850, 170, 850, 190, color=LINE, sw=1.5))
    p.append(rect(750, 190, 200, 170, fill=WARM, stroke=POS, sw=1.5, rx=6))
    p.append(text(850, 212, "code=killed (SIG...)", size=12, color=POS, bold=True))
    p.append(text(850, 230, "Знищення ядром / сигналом", size=10.5, color=MUTED))
    p.append(mtext(850, 252, [
        "1. SIGKILL -> cgroup OOM killer",
        "   (перевірити MemoryMax=)",
        "2. SIGABRT -> abort() в C/C++",
        "3. SIGSEGV -> помилка пам'яті",
        "4. TimeoutStartSec -> таймаут"
    ], size=10, color=INK, lh=1.3))

    # Нижній рівень: Спеціальні сценарії (Залежності та Пісочниця)
    p.append(rect(50, 390, 460, 200, fill=SOFT, stroke=NEG, sw=1.5, rx=8))
    p.append(text(280, 416, "СЛУЖБА ЗАВИСЛА В ACTIVATING (START)", size=12.5, color=NEG, bold=True))
    p.append(mtext(280, 444, [
        "• Type=notify: застосунок не викликав sd_notify(\"READY=1\")",
        "• Type=forking: батько не створив PIDFile або PID не збігається",
        "• ExecStartPre=: попередній скрипт завис на мережевому очікуванні",
        "• Залежність Requires= стартувала паралельно без After= і заблокувала вхід"
    ], size=11, color=INK, lh=1.35))

    p.append(rect(550, 390, 480, 200, fill=SOFT, stroke=MUTED, sw=1.5, rx=8))
    p.append(text(790, 416, "ПРИХОВАНІ ОБМЕЖЕННЯ ПІСОЧНИЦІ ТА CGROUPS", size=12.5, color=MUTED, bold=True))
    p.append(mtext(790, 444, [
        "• ProtectSystem=strict: спроба запису на диск повертає EROFS",
        "• PrivateTmp=true: файл сокета створено в ізольованому /tmp",
        "• LimitNOFILE=: вичерпано 1024 дескриптори -> помилка EMFILE",
        "• TasksMax=: пул потоків перевищив ліміт -> pthread_create EAGAIN"
    ], size=11, color=INK, lh=1.35))

    render(os.path.join(OUT, "systemd-failure-decision-tree.svg"), W, H, *p)


if __name__ == "__main__":
    fig_unit_lifecycle_states()
    fig_restart_loop_rate_limiter()
    fig_systemd_failure_decision_tree()
    print("All figures generated successfully.")
