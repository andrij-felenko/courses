# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE   = "#eaf0fd"
GREEN  = "#eaf6ef"
RED    = "#fdecea"
WARM   = "#fff6e5"
GREY   = "#eceff1"
PURPLE = "#f3e5f5"

# ── 1. Ієрархія пошуку та оверридів unit-файлів ─────────────────────────────
def fig_unit_file_precedence():
    W, H = 1400, 680
    p = []

    p.append(text(700, 45, "Пріоритет пошуку юнітів та механізм перекриття Drop-in (.d/*.conf)", size=18, bold=True))

    # Ліва колонка — Ієрархія каталогів
    p.append(rect(40, 80, 620, 560, fill="#ffffff", stroke="#cfd8dc", sw=1.5))
    p.append(text(350, 115, "Ієрархія каталогів юнітів (від вищого пріоритету)", size=16, bold=True))

    r1_fill, r1_txt = RED, "1. /run/systemd/system/\nТимчасові юніти, згенеровані під час виконання та transient-юніти (systemd-run)"
    r2_fill, r2_txt = WARM, "2. /etc/systemd/system/\nАдміністративні юніти, симлінки увімкнення та дроп-ін оверриди (.d/)"
    r3_fill, r3_txt = BLUE, "3. /usr/lib/systemd/system/ (або /lib/)\nПочаткові юніти за замовчуванням від пакета дистрибутива"

    p.append(fitbox(60, 140, 580, 110, r1_txt, size=14, bold=True, fill=r1_fill))
    p.append(arrow(350, 250, 350, 275, color=POS, sw=2))
    p.append(text(380, 266, "перекриває", size=13, color=POS, italic=True))

    p.append(fitbox(60, 280, 580, 110, r2_txt, size=14, bold=True, fill=r2_fill))
    p.append(arrow(350, 390, 350, 415, color=NEG, sw=2))
    p.append(text(380, 406, "перекриває", size=13, color=NEG, italic=True))

    p.append(fitbox(60, 420, 580, 110, r3_txt, size=14, bold=True, fill=r3_fill))

    # Спеціальні маскування
    p.append(fitbox(60, 550, 580, 70, "Маскування (Masking):\nсимвольне посилання у /etc/.../foo.service -> /dev/null блокує юніт повністю", size=13, fill=GREY))

    # Права колонка — Процес злиття Drop-in
    p.append(rect(720, 80, 640, 560, fill="#ffffff", stroke="#cfd8dc", sw=1.5))
    p.append(text(1040, 115, "Формування конфігурації у пам'яті PID 1", size=16, bold=True))

    p.append(fitbox(740, 140, 600, 80, "Базовий файл пакету:\n/lib/systemd/system/nginx.service\n(ExecStart=/usr/sbin/nginx, MemoryMax=1G)", size=13, fill=BLUE))
    p.append(line(1040, 220, 1040, 250, color=LINE, sw=1.5))
    p.append(text(1040, 240, "+", size=18, bold=True, color=LINE))

    p.append(fitbox(740, 260, 600, 90, "Дроп-ін файл 1:\n/etc/systemd/system/nginx.service.d/10-env.conf\n(Environment=\"ENV=prod\")", size=13, fill=WARM))
    p.append(line(1040, 350, 1040, 380, color=LINE, sw=1.5))
    p.append(text(1040, 370, "+", size=18, bold=True, color=LINE))

    p.append(fitbox(740, 390, 600, 90, "Дроп-ін файл 2 (вищий номер):\n/etc/systemd/system/nginx.service.d/20-limits.conf\n(ExecStart=, ExecStart=/usr/local/bin/custom-nginx, MemoryMax=2G)", size=13, fill=WARM))
    p.append(arrow(1040, 480, 1040, 515, color=FIELD, sw=2))

    p.append(fitbox(740, 520, 600, 100, "Підсумковий результуючий юніт у пам'яті PID 1:\n- ExecStart=/usr/local/bin/custom-nginx (перезаписано)\n- MemoryMax=2G (перезаписано)\n- Environment=\"ENV=prod\" (об'єднано)", size=13, bold=True, fill=GREEN))

    render(os.path.join(IMG, 'unit-file-precedence.svg'), W, H, *p)


# ── 2. Архітектура взаємодії systemctl та systemd через D-Bus ───────────────
def fig_systemctl_dbus_architecture():
    W, H = 1400, 640
    p = []

    p.append(text(700, 40, "Архітектура взаємодії systemctl з PID 1 та підсистемами ядра", size=18, bold=True))

    # Утиліта systemctl (Клієнт)
    p.append(fitbox(60, 100, 320, 180, "Клієнтський шар:\nsystemctl CLI / утиліти\n\n1. Формує D-Bus метод (StartUnit, StopUnit, Reload)\n2. Читає/пише симлінки у /etc/", size=14, bold=True, fill=BLUE))

    # D-Bus системна шина
    p.append(fitbox(460, 100, 300, 180, "IPC Шар D-Bus:\n/run/systemd/system/bus\n(або /run/systemd/private)\n\nІнтерфейси:\norg.freedesktop.systemd1.Manager\norg.freedesktop.systemd1.Unit", size=14, bold=True, fill=PURPLE))

    # PID 1 systemd Manager
    p.append(fitbox(840, 100, 500, 180, "Системний менеджер (PID 1):\norg.freedesktop.systemd1\n\n1. Обчислює граф залежностей (DAG)\n2. Створює транзакційні роботи (Jobs)\n3. Відстежує стани (ActiveState, SubState)", size=14, bold=True, fill=GREEN))

    # Стрілки клієнт -> dbus -> manager
    p.append(arrow(380, 190, 450, 190, color=NEG, sw=2))
    p.append(arrow(760, 190, 830, 190, color=FIELD, sw=2))

    # Нижня частина — Взаємодія з ядрами та файловою системою
    p.append(fitbox(80, 380, 360, 200, "Файлова система (/etc, /usr, /run):\n\n- unit-файли (INI)\n- drop-in оверриди (.d/)\n- символьні посилання автозапуску\n(wants/, requires/)", size=14, fill=WARM))

    p.append(fitbox(520, 380, 380, 200, "Підсистема cgroups v2:\n/sys/fs/cgroup/system.slice/...\n\n- Точне відстеження процесів демона\n- Гарантована зупинка (SIGKILL групи)\n- Обмеження ресурсів (CPU, Memory, IO)", size=14, fill=GREY))

    p.append(fitbox(960, 380, 380, 200, "Системні події та логування:\n\n- systemd-journald (stdout/stderr)\n- udev (події пристроїв .device)\n- systemd-logind (сесії)", size=14, fill=GREY))

    # Зв'язки між PID 1 та ніжніми підсистемами
    p.append(arrow(880, 290, 260, 370, color=LINE, sw=1.8))
    p.append(arrow(1090, 290, 710, 370, color=LINE, sw=1.8))
    p.append(arrow(1200, 290, 1150, 370, color=LINE, sw=1.8))

    render(os.path.join(IMG, 'systemctl-dbus-architecture.svg'), W, H, *p)


# ── 3. Стейт-машина станів юніта ────────────────────────────────────────────
def fig_unit_lifecycle_states():
    W, H = 1400, 620
    p = []

    p.append(text(700, 40, "Діаграма станів юніта (ActiveState та SubState)", size=18, bold=True))

    # Стан Inactive
    p.append(fitbox(80, 240, 240, 140, "INACTIVE\n(SubState: dead)\n\nСлужба не виконується,\nпроцеси відсутні", size=14, bold=True, fill=GREY))

    # Стан Activating
    p.append(fitbox(420, 100, 260, 140, "ACTIVATING\n(SubState: start-pre, start)\n\nВиконуються командні рядки\nExecStartPre, ExecStart", size=14, bold=True, fill=WARM))

    # Стан Active
    p.append(fitbox(780, 240, 260, 140, "ACTIVE\n(SubState: running, exited)\n\nГоловний процес працює або\noneshot успішно завершився", size=14, bold=True, fill=GREEN))

    # Стан Deactivating
    p.append(fitbox(420, 380, 260, 140, "DEACTIVATING\n(SubState: stop, stop-post)\n\nВиконуються ExecStop,\nExecStopPost", size=14, bold=True, fill=WARM))

    # Стан Failed
    p.append(fitbox(1100, 240, 240, 140, "FAILED\n(SubState: failed)\n\nПроцес упав або повернув\nнезапланований код помилки", size=14, bold=True, fill=RED))

    # Переходи (Стрілки)
    # Inactive -> Activating
    p.append(arrow(200, 230, 410, 170, color=NEG, sw=2))
    p.append(text(280, 185, "systemctl start / запуск", size=13, color=NEG, bold=True))

    # Activating -> Active
    p.append(arrow(690, 170, 770, 230, color=FIELD, sw=2))
    p.append(text(750, 185, "успішний запуск", size=13, color=FIELD, bold=True))

    # Active -> Deactivating
    p.append(arrow(800, 390, 690, 430, color=POS, sw=2))
    p.append(text(770, 425, "systemctl stop", size=13, color=POS, bold=True))

    # Deactivating -> Inactive
    p.append(arrow(410, 430, 200, 390, color=LINE, sw=2))
    p.append(text(280, 425, "зупинка завершена", size=13, color=LINE))

    # Activating / Active -> Failed
    p.append(arrow(690, 130, 1110, 230, color=POS, sw=1.8))
    p.append(arrow(1040, 270, 1090, 270, color=POS, sw=2))
    p.append(text(960, 255, "аварія / помилка", size=13, color=POS, bold=True))

    # Failed -> Activating (Restart)
    p.append(arrow(1110, 380, 560, 400, color=NEG, sw=1.8))
    p.append(text(850, 415, "автоперезапуск (Restart=)", size=13, color=NEG, italic=True))

    render(os.path.join(IMG, 'unit-lifecycle-states.svg'), W, H, *p)


if __name__ == '__main__':
    fig_unit_file_precedence()
    fig_systemctl_dbus_architecture()
    fig_unit_lifecycle_states()
    print("Успішно згенеровано 3 SVG-фігури.")
