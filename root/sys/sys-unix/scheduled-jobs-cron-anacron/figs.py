# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
GREY_FILL = "#f4f6f8"


# ── 1. Архітектура та хвилинний цикл демона cron ─────────────────────────────
def fig_cron_architecture():
    W, H = 1000, 500
    frags = []

    # Колонка 1: Джерела розкладів
    frags.append(rect(30, 50, 260, 420, fill=GREY_FILL, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(160, 78, "Джерела розкладів", size=14, bold=True, color=INK))
    frags.append(line(45, 92, 275, 92, color=MUTED, sw=1.0))

    src_boxes = [
        (45, 105, 230, 70, "/etc/crontab\n(системний, з полем user)", BLUE_FILL, NEG),
        (45, 185, 230, 70, "/etc/cron.d/*\n(пакетні конфігурації)", BLUE_FILL, NEG),
        (45, 265, 230, 70, "/var/spool/cron/crontabs/*\n(користувацькі crontab -e)", WARM_FILL, MUTED),
        (45, 345, 230, 110, "Перевірка змін:\n• stat() mtime каталогів\n• inotify події модифікації\n• перезапуск не потрібен", GREEN_FILL, FIELD),
    ]
    for bx, by, bw, bh, btext, bfill, bstroke in src_boxes:
        frags.append(rect(bx, by, bw, bh, fill=bfill, stroke=bstroke, sw=1.2, rx=6))
        frags.append(mtext(bx + bw / 2, by + 22, btext, size=11, color=INK, lh=1.35))

    # Колонка 2: Ядро демона crond (Хвилинний цикл)
    frags.append(rect(330, 50, 340, 420, fill=BG, stroke=NEG, sw=2.0, rx=8))
    frags.append(text(500, 78, "Ядро демона crond", size=14, bold=True, color=NEG))
    frags.append(line(345, 92, 655, 92, color=NEG, sw=1.0))

    loop_steps = [
        (350, 105, 300, 60, "1. Синхронізація з секундою 00\nsleep(60 - now.tm_sec)", WARM_FILL, MUTED),
        (350, 175, 300, 75, "2. Перевірка розкладів\nПарсинг 5 полів часу:\n(хв, год, день, місяць, день_тижня)", BLUE_FILL, NEG),
        (350, 260, 300, 70, "3. Збіг з поточним часом?\nОбчислення бітових масок\nОсобливе правило DOM || DOW", RED_FILL, POS),
        (350, 340, 300, 115, "4. Обробка завершення\n• Сигнал SIGCHLD\n• waitpid(WNOHANG) у циклі\n• запобігання зомбі-процесам", GREEN_FILL, FIELD),
    ]
    for bx, by, bw, bh, btext, bfill, bstroke in loop_steps:
        frags.append(rect(bx, by, bw, bh, fill=bfill, stroke=bstroke, sw=1.2, rx=6))
        frags.append(mtext(bx + bw / 2, by + 22, btext, size=11, color=INK, lh=1.35))

    # Колонка 3: Виконання завдання
    frags.append(rect(710, 50, 260, 420, fill=GREY_FILL, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(840, 78, "Ізоляція та запуск", size=14, bold=True, color=INK))
    frags.append(line(725, 92, 955, 92, color=MUTED, sw=1.0))

    exec_steps = [
        (725, 105, 230, 65, "fork() нащадка\ncrond продовжує цикл", WARM_FILL, MUTED),
        (725, 180, 230, 80, "Зниження привілеїв\nsetgid(), initgroups(),\nsetuid(user), chdir($HOME)", RED_FILL, POS),
        (725, 270, 230, 85, "Оточення й дескриптори\nPATH=/usr/bin:/bin\nstdin -> /dev/null\nstdout/err -> pipe", BLUE_FILL, NEG),
        (725, 365, 230, 90, "execve(/bin/sh, -c, cmd)\nПерехоплення виводу\nВідправка через sendmail\n(якщо задано MAILTO)", GREEN_FILL, FIELD),
    ]
    for bx, by, bw, bh, btext, bfill, bstroke in exec_steps:
        frags.append(rect(bx, by, bw, bh, fill=bfill, stroke=bstroke, sw=1.2, rx=6))
        frags.append(mtext(bx + bw / 2, by + 20, btext, size=11, color=INK, lh=1.35))

    # Стрілки між колонками
    frags.append(arrow(290, 210, 330, 210, color=NEG, sw=2.0))
    frags.append(arrow(670, 295, 710, 295, color=POS, sw=2.0))

    render(os.path.join(IMG, "cron-architecture-loop.svg"), W, H, *frags,
           title="Архітектура та конвеєр виконання завдань демоном cron")


# ── 2. Анатомія полів crontab та логіка зіставлення ──────────────────────────
def fig_crontab_fields():
    W, H = 1000, 480
    frags = []

    # 5 блоків полів часу
    fields = [
        (30, 60, 175, "Хвилини", "0 – 59\n*, */15, 1-30", BLUE_FILL, NEG),
        (220, 60, 175, "Години", "0 – 23\n*, 0-8, 12,18", BLUE_FILL, NEG),
        (410, 60, 175, "День місяця", "1 – 31\n*, 1,15, L", WARM_FILL, MUTED),
        (600, 60, 175, "Місяць", "1 – 12\n*, JAN-DEC", BLUE_FILL, NEG),
        (790, 60, 175, "День тижня", "0 – 7 (0=7=Нд)\n*, 1-5, MON-FRI", WARM_FILL, MUTED),
    ]

    for x, y, w, title, desc, fcolor, scolor in fields:
        frags.append(rect(x, y, w, 110, fill=fcolor, stroke=scolor, sw=1.5, rx=8))
        frags.append(text(x + w / 2, y + 30, title, size=14, bold=True, color=INK))
        frags.append(line(x + 15, y + 44, x + w - 15, y + 44, color=scolor, sw=1.0))
        frags.append(mtext(x + w / 2, y + 68, desc, size=12, color=INK, lh=1.35))

    # Логічні зв'язки (AND / OR)
    frags.append(rect(30, 200, 935, 120, fill=BG, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(500, 226, "Правило об'єднання умов: кон'юнкція проти диз'юнкції (POSIX / Vixie cron)", size=13, bold=True))

    rule_text = (
        "• Хвилини, Години та Місяць завжди перевіряються через логічне «І» (AND).\n"
        "• КРИТИЧНИЙ ВИНЯТОК: Якщо День Місяця (DOM) та День Тижня (DOW) обидва явно обмежені (жоден не є «*»),\n"
        "  вони об'єднуються через логічне «АБО» (OR)! Завдання запускається, якщо виконується ХОЧ ОДНА з умов.\n"
        "• Приклад: «0 2 13 * 5» запускається щоп'ятниці ТА 13-го числа кожного місяця, а не лише «у п'ятницю 13-го»."
    )
    frags.append(mtext(500, 252, rule_text, size=11, color=INK, lh=1.35))

    # Порівняння форматів файлів знизу
    frags.append(rect(30, 340, 455, 115, fill=GREEN_FILL, stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(257, 365, "Користувацький crontab (crontab -e)", size=13, bold=True, color=FIELD))
    frags.append(line(45, 378, 470, 378, color=FIELD, sw=1.0))
    frags.append(mtext(257, 400, "5 полів часу + [команда]\nКористувач визначається власником файлу\nФайли в /var/spool/cron/crontabs/", size=11, color=INK, lh=1.35))

    frags.append(rect(510, 340, 455, 115, fill=WARM_FILL, stroke=POS, sw=1.5, rx=8))
    frags.append(text(737, 365, "Системний crontab (/etc/crontab, /etc/cron.d/*)", size=13, bold=True, color=POS))
    frags.append(line(525, 378, 950, 378, color=POS, sw=1.0))
    frags.append(mtext(737, 400, "5 полів часу + [КОРИСТУВАЧ] + [команда]\nШосте поле явно вказує UID виконання\nЗавантажується автоматично демоном", size=11, color=INK, lh=1.35))

    render(os.path.join(IMG, "crontab-fields-and-matching.svg"), W, H, *frags,
           title="Анатомія синтаксису crontab та логіка перевірки умов")


# ── 3. Порівняння моделей: cron проти anacron ────────────────────────────────
def fig_anacron_vs_cron():
    W, H = 1000, 490
    frags = []

    # Ліва колонка: cron (24/7 сервер)
    frags.append(rect(30, 50, 455, 410, fill=BLUE_FILL, stroke=NEG, sw=1.5, rx=8))
    frags.append(text(257, 80, "Модель cron: неперервний сервер (24/7)", size=14, bold=True, color=NEG))
    frags.append(line(50, 95, 465, 95, color=NEG, sw=1.0))

    cron_details = (
        "• Прив'язка до абсолютного астрономічного часу (година:хвилина).\n"
        "• Демон спить і прокидається на початку кожної хвилини.\n"
        "• Немає пам'яті минулого: якщо машина була вимкнена\n"
        "  або спала в момент розкладу — ЗАВДАННЯ ВТРАЧАЄТЬСЯ.\n\n"
        "• Точність: дискретна, рівно 1 хвилина.\n"
        "• Рівень: системний та окремий для кожного користувача.\n"
        "• Ідеально для: постійно активних серверів та хмарних вузлів."
    )
    frags.append(mtext(257, 125, cron_details, size=12, color=INK, lh=1.4))

    # Права колонка: anacron (ноутбуки та робочі станції)
    frags.append(rect(515, 50, 455, 410, fill=GREEN_FILL, stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(742, 80, "Модель anacron: машини з перервами в роботі", size=14, bold=True, color=FIELD))
    frags.append(line(535, 95, 950, 95, color=FIELD, sw=1.0))

    anacron_details = (
        "• Прив'язка до періоду в днях (1 = щодня, 7 = щотижня, 30 = щомісяця).\n"
        "• Зберігає позначки часу в /var/spool/anacron/<job_id> (YYYYMMDD).\n"
        "• При старті системи виявляє пропущені дні та виконує завдання.\n"
        "• Затримка старту (delay у хвилинах): запобігає піковому\n"
        "  навантаженню на дискову підсистему відразу після ввімкнення.\n\n"
        "• Обмеження: мінімальний інтервал — 1 день (без годин і хвилин).\n"
        "• Працює тільки від імені суперкористувача root."
    )
    frags.append(mtext(742, 125, anacron_details, size=12, color=INK, lh=1.4))

    render(os.path.join(IMG, "anacron-vs-cron-model.svg"), W, H, *frags,
           title="Порівняння парадигм виконання: демон cron проти anacron")


# ── 4. Архітектура та можливості systemd timers ──────────────────────────────
def fig_systemd_timers():
    W, H = 1000, 500
    frags = []

    # Верхній блок: зв'язка юнітів
    frags.append(rect(30, 45, 450, 175, fill=WARM_FILL, stroke=POS, sw=1.5, rx=8))
    frags.append(text(255, 72, "1. Таймер-юніт (*.timer)", size=13, bold=True, color=POS))
    frags.append(line(45, 85, 465, 85, color=POS, sw=1.0))
    timer_txt = (
        "[Timer]\n"
        "OnCalendar=*-*-* 03:00:00        # Календарний розклад\n"
        "OnBootSec=15min                 # Монотонний розклад\n"
        "Persistent=true                 # Виконати пропущене (заміна anacron)\n"
        "RandomizedDelaySec=10m          # Рандомізація пікового навантаження"
    )
    frags.append(mtext(255, 105, timer_txt, size=11, color=INK, lh=1.35))

    frags.append(rect(520, 45, 450, 175, fill=BLUE_FILL, stroke=NEG, sw=1.5, rx=8))
    frags.append(text(745, 72, "2. Сервіс-юніт (*.service)", size=13, bold=True, color=NEG))
    frags.append(line(535, 85, 955, 85, color=NEG, sw=1.0))
    service_txt = (
        "[Service]\n"
        "Type=oneshot\n"
        "ExecStart=/usr/local/bin/backup.sh\n"
        "ProtectSystem=strict            # Пісочниця та ізоляція файлової системи\n"
        "MemoryMax=1G                    # Обмеження ресурсів через cgroups v2"
    )
    frags.append(mtext(745, 105, service_txt, size=11, color=INK, lh=1.35))

    # Стрілка між таймером і сервісом
    frags.append(arrow(480, 130, 520, 130, color=LINE, sw=2.0))

    # Нижній блок: переваги над класичним cron
    frags.append(rect(30, 240, 940, 230, fill=GREEN_FILL, stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(500, 268, "Ключові архітектурні переваги systemd timers над cron / anacron", size=14, bold=True, color=FIELD))
    frags.append(line(50, 282, 950, 282, color=FIELD, sw=1.0))

    adv_text = (
        "• Єдине журналювання: stdout і stderr автоматично потрапляють у journald без потреби в локальному sendmail.\n"
        "• Монотонні таймери: запуск відносно завантаження ядра (OnBootSec) або завершення попереднього запуску (OnUnitActiveSec).\n"
        "• Керування залежностями: директиви After=network-online.target та Requires= гарантують готовність інфраструктури.\n"
        "• Повна ізоляція: контроль ресурсів через cgroups, захист файлової системи (DynamicUser, ProtectHome, PrivateTmp).\n"
        "• Прозорий моніторинг: утиліта «systemctl list-timers» відображає точний час наступного спрацьовування та час очікування."
    )
    frags.append(mtext(500, 310, adv_text, size=12, color=INK, lh=1.45))

    render(os.path.join(IMG, "systemd-timer-architecture.svg"), W, H, *frags,
           title="Архітектура та інтеграція таймерів у підсистему systemd")


if __name__ == "__main__":
    fig_cron_architecture()
    fig_crontab_fields()
    fig_anacron_vs_cron()
    fig_systemd_timers()
    print("Усі 4 фігури згенеровано успішно.")
