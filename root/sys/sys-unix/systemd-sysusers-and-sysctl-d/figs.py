# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
GREY_FILL = "#eceff1"


# 1. sysusers provisioning flow
def fig_sysusers_flow():
    W, H = 1200, 520
    p = []

    p.append(text(600, 40, "Етапи виконання systemd-sysusers під час раннього завантаження", size=16, bold=True))

    steps = [
        (40, "1 · Зчитування .d", "Сканування каталогів\n/etc/sysusers.d\n/run/sysusers.d\n/usr/lib/sysusers.d", WARM_FILL, MUTED),
        (330, "2 · Блокування БД", "Виклик lckpwdf()\nСтворення locks\n/etc/.pwd.lock", RED_FILL, POS),
        (620, "3 · Виділення UID/GID", "Перевірка існуючих\nUID у /etc/passwd\nВибір вільних з діапазону", BLUE_FILL, NEG),
        (910, "4 · Запис у /etc", "Атомарний запис:\n/etc/passwd\n/etc/group\n/etc/shadow", GREEN_FILL, FIELD),
    ]

    for x, title_str, desc, fill_c, stroke_c in steps:
        p.append(rect(x, 75, 250, 360, fill=BG, stroke=MUTED, sw=1.2, rx=10))
        p.append(text(x + 125, 110, title_str, size=15, bold=True))
        p.append(fitbox(x + 15, 140, 220, 260, desc, size=14, fill=fill_c, stroke=stroke_c))

    p.append(arrow(290, 255, 330, 255))
    p.append(arrow(580, 255, 620, 255))
    p.append(arrow(870, 255, 910, 255))

    p.append(text(600, 485, "Гарантує наявність системних облікових записів до запуску основних служб", size=14, color=MUTED))

    render(os.path.join(IMG, 'sysusers-provisioning-flow.svg'), W, H, *p,
           title="Процес обробки sysusers.d та оновлення бази користувачів")


# 2. sysctl VFS translation
def fig_sysctl_translation():
    W, H = 1240, 540
    p = []

    p.append(text(620, 40, "Трансляція конфігураційного ключа sysctl у системний виклик VFS", size=16, bold=True))

    p.append(rect(40, 75, 360, 400, fill=BG, stroke=MUTED, sw=1.2, rx=10))
    p.append(text(220, 110, "Конфігураційний контент", size=15, bold=True))
    p.append(fitbox(60, 140, 320, 110, "Файл: /etc/sysctl.d/99-custom.conf\n\nnet.ipv4.ip_forward = 1\nfs.file-max = 2097152", size=14, fill=WARM_FILL, stroke=MUTED))
    p.append(fitbox(60, 270, 320, 180, "Парсер systemd-sysctl:\n1. Видаляє пробіли\n2. Перетворює крапки на /\n3. Додає префікс /proc/sys/\n4. Обробляє маску '-'", size=14, fill=GREY_FILL, stroke=MUTED))

    p.append(arrow(400, 275, 470, 275))

    p.append(rect(470, 75, 300, 400, fill=BG, stroke=MUTED, sw=1.2, rx=10))
    p.append(text(620, 110, "Транслятор шляху", size=15, bold=True))
    p.append(fitbox(490, 160, 260, 90, "Ключ: net.ipv4.ip_forward\n↓\n/proc/sys/net/ipv4/ip_forward", size=14, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(490, 290, 260, 90, "Ключ: fs.file-max\n↓\n/proc/sys/fs/file-max", size=14, fill=BLUE_FILL, stroke=NEG))

    p.append(arrow(770, 275, 840, 275))

    p.append(rect(840, 75, 360, 400, fill=BG, stroke=MUTED, sw=1.2, rx=10))
    p.append(text(1020, 110, "Віртуальна ФС ядра (/proc)", size=15, bold=True))
    p.append(fitbox(860, 160, 320, 90, "open(\"/proc/sys/net/ipv4/ip_forward\", O_WRONLY)\nwrite(fd, \"1\\n\", 2)", size=14, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(860, 290, 320, 90, "open(\"/proc/sys/fs/file-max\", O_WRONLY)\nwrite(fd, \"2097152\\n\", 8)", size=14, fill=GREEN_FILL, stroke=FIELD))

    p.append(text(620, 510, "Зміна значень /proc/sys негайно змінює параметри працюючого ядра Linux", size=14, color=MUTED))

    render(os.path.join(IMG, 'sysctl-vfs-translation.svg'), W, H, *p,
           title="Трансляція sysctl ключів у файлові операції над /proc/sys")


# 3. dot-d precedence hierarchy
def fig_dot_d_precedence():
    W, H = 1200, 560
    p = []

    p.append(text(600, 40, "Ієрархія каталогів .d та правила перекриття (Override / Masking)", size=16, bold=True))

    layers = [
        (40, "/etc/*.d/ (Адміністратор)", "Найвищий пріоритет.\nПерекриває імені файли з /run та /usr/lib.\nСимлінк на /dev/null блокує конфігурацію.", RED_FILL, POS),
        (420, "/run/*.d/ (Динамічний стан)", "Середній пріоритет.\nТимчасові конфігурації, створені під час роботи системи.\nЗникає після перезавантаження.", WARM_FILL, MUTED),
        (800, "/usr/lib/*.d/ (Провайдер/Пакунки)", "Найнижчий пріоритет.\nЗаводські налаштування дистрибутива та встановлених пакетів.\nНе редагується руками.", BLUE_FILL, NEG),
    ]

    for x, title_str, desc, fill_c, stroke_c in layers:
        p.append(rect(x, 75, 360, 220, fill=BG, stroke=MUTED, sw=1.2, rx=10))
        p.append(text(x + 180, 110, title_str, size=15, bold=True))
        p.append(fitbox(x + 20, 135, 320, 140, desc, size=14, fill=fill_c, stroke=stroke_c))

    p.append(arrow(340, 315, 340, 365))
    p.append(arrow(600, 315, 600, 365))
    p.append(arrow(860, 315, 860, 365))

    p.append(rect(40, 370, 1120, 130, fill=BG, stroke=MUTED, sw=1.2, rx=10))
    p.append(text(600, 400, "Алгоритм об'єднання: лексикографічне сортування за базовим ім'ям", size=15, bold=True))
    p.append(fitbox(60, 420, 1080, 65,
                    "1. Збираються файли з усіх каталогів  2. Для файлів з однаковими іменами перемагає каталог із вищим пріоритетом\n"
                    "3. Порожній файл або посилання на /dev/null повністю маскує (блокує) параметр",
                    size=14, fill=GREEN_FILL, stroke=FIELD))

    render(os.path.join(IMG, 'dot-d-precedence-hierarchy.svg'), W, H, *p,
           title="Ієрархія пріоритетів та затінення конфігураційних каталогів .d")


# 4. stateless boot provisioning
def fig_stateless_boot():
    W, H = 1200, 520
    p = []

    p.append(text(600, 40, "Безстанове завантаження (Stateless Boot) та ініціалізація порожнього /etc", size=16, bold=True))

    p.append(rect(40, 75, 340, 380, fill=BG, stroke=MUTED, sw=1.2, rx=10))
    p.append(text(210, 110, "Початковий стан ФС", size=15, bold=True))
    p.append(fitbox(60, 140, 300, 100, "/usr (Read-Only)\nМістить заводські шаблони:\n/usr/lib/sysusers.d/*.conf\n/usr/lib/sysctl.d/*.conf", size=14, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(60, 260, 300, 170, "/etc (Empty tmpfs або ext4)\nНе містить /etc/passwd\nНе містить /etc/group\nНе містить /etc/sysctl.conf", size=14, fill=RED_FILL, stroke=POS))

    p.append(arrow(380, 265, 440, 265))

    p.append(rect(440, 75, 320, 380, fill=BG, stroke=MUTED, sw=1.2, rx=10))
    p.append(text(600, 110, "Ранні служби systemd", size=15, bold=True))
    p.append(fitbox(460, 140, 280, 130, "systemd-sysusers.service\n\nЗчитує /usr/lib/sysusers.d\nСтворює мінімальні /etc/passwd та /etc/group", size=14, fill=WARM_FILL, stroke=MUTED))
    p.append(fitbox(460, 290, 280, 140, "systemd-sysctl.service\n\nЗчитує /usr/lib/sysctl.d\nЗастосовує налаштування ядра через /proc/sys", size=14, fill=WARM_FILL, stroke=MUTED))

    p.append(arrow(760, 265, 820, 265))

    p.append(rect(820, 75, 340, 380, fill=BG, stroke=MUTED, sw=1.2, rx=10))
    p.append(text(990, 110, "Готова система", size=15, bold=True))
    p.append(fitbox(840, 140, 300, 130, "Створено системні акаунти:\nroot:x:0:0:...\nsystemd-journal:x:999:...\n/etc/passwd готовий до входу", size=14, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(840, 290, 300, 140, "Ядро налаштовано:\n/proc/sys/net/... готовий\nБезпечні ліміти пам'яті та ФС активовано", size=14, fill=GREEN_FILL, stroke=FIELD))

    p.append(text(600, 485, "Дозволяє розгортати ідентичні образи систем без збереження стану в /etc", size=14, color=MUTED))

    render(os.path.join(IMG, 'stateless-boot-provisioning.svg'), W, H, *p,
           title="Автоматична ініціалізація конфігурації при безстановому завантаженні")


if __name__ == '__main__':
    fig_sysusers_flow()
    fig_sysctl_translation()
    fig_dot_d_precedence()
    fig_stateless_boot()
    print("ok")
