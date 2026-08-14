# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL  = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL   = "#fdecea"
WARM_FILL  = "#fff6e5"
GREY_FILL  = "#f4f6f8"


# ── 1. Анатомія пакунка ───────────────────────────────────────────────────
def fig_pkg_structure():
    W, H = 1000, 480
    frags = []

    # Заголовок панелі контейнера
    frags.append(rect(20, 20, 960, 440, fill=BG, stroke=LINE, sw=1.5, rx=10))
    frags.append(text(500, 50, "Структура архіву пакунка (.deb / .rpm)", size=18, bold=True))

    # Стовпчик 1: Метадані
    frags.append(rect(40, 80, 290, 360, fill=BLUE_FILL, stroke=NEG, sw=1.5, rx=8))
    frags.append(text(185, 110, "Метадані (Control / Spec)", size=16, color=NEG, bold=True))
    frags.append(line(55, 125, 315, 125, color=NEG, sw=1.0))

    meta_items = [
        "• Name, Version, Architecture",
        "• Maintainer & License",
        "• Depends, Recommends, Suggests",
        "• Conflicts, Breaks, Replaces",
        "• Virtual Provides (e.g. mta)",
        "• SHA-256 Digest & GPG Sign",
    ]
    for i, item in enumerate(meta_items):
        frags.append(text(60, 160 + i * 42, item, size=13, anchor="start", color=INK))

    # Стовпчик 2: Керуючі скрипти
    frags.append(rect(355, 80, 290, 360, fill=WARM_FILL, stroke="#d97706", sw=1.5, rx=8))
    frags.append(text(500, 110, "Керуючі скрипти (Hooks)", size=16, color="#b45309", bold=True))
    frags.append(line(370, 125, 630, 125, color="#d97706", sw=1.0))

    script_items = [
        ("preinst / %pre", "підготовка середовища, зупинка демона"),
        ("postinst / %post", "налаштування,ldconfig, запуск служб"),
        ("prerm / %preun", "зупинка служб перед видаленням"),
        ("postrm / %postun", "очищення кешу, видалення користувачів"),
        ("triggers", "відкладений виклик обробників"),
    ]
    for i, (name, desc) in enumerate(script_items):
        y_box = 145 + i * 56
        frags.append(rect(370, y_box, 260, 48, fill=BG, stroke="#f59e0b", sw=1.2, rx=6))
        frags.append(text(380, y_box + 20, name, size=13, anchor="start", bold=True, color="#b45309"))
        frags.append(text(380, y_box + 38, desc, size=11, anchor="start", color=MUTED))

    # Стовпчик 3: Payload
    frags.append(rect(670, 80, 290, 360, fill=GREEN_FILL, stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(815, 110, "Корисне навантаження (Payload)", size=16, color=FIELD, bold=True))
    frags.append(line(685, 125, 945, 125, color=FIELD, sw=1.0))

    payload_items = [
        ("/usr/bin/binary", "Виконувані файли програми"),
        ("/usr/lib/libfoo.so", "Динамічні бібліотеки"),
        ("/etc/app/config.conf", "Конфігураційні файли"),
        ("/usr/share/man/", "Документація та мануали"),
        ("/lib/systemd/system/", "Юніти системних служб"),
    ]
    for i, (path_str, desc) in enumerate(payload_items):
        y_box = 145 + i * 56
        frags.append(rect(685, y_box, 260, 48, fill=BG, stroke=FIELD, sw=1.2, rx=6))
        frags.append(text(695, y_box + 20, path_str, size=12, anchor="start", bold=True, color=INK))
        frags.append(text(695, y_box + 38, desc, size=11, anchor="start", color=MUTED))

    render(os.path.join(IMG, 'fig-pkg-structure.svg'), W, H, *frags)


# ── 2. Життєвий цикл інсталяції ─────────────────────────────────────────
def fig_pkg_lifecycle():
    W, H = 1060, 440
    frags = []

    frags.append(rect(20, 20, 1020, 400, fill=BG, stroke=LINE, sw=1.5, rx=10))
    frags.append(text(530, 50, "Автомат станів та життєвий цикл транзакції пакунка", size=18, bold=True))

    # Стани
    states = [
        (60, 180, "Not-Installed", "Пакунок відсутній в системі", GREY_FILL, MUTED),
        (310, 180, "Unpacked", "Файли розпаковано на диск", BLUE_FILL, NEG),
        (560, 180, "Half-Configured", "Виконується postinst/postun", WARM_FILL, "#b45309"),
        (810, 180, "Installed", "Пакунок повністю активний", GREEN_FILL, FIELD),
    ]

    for x, y, title_str, desc_str, fill_c, stroke_c in states:
        frags.append(rect(x, y, 190, 90, fill=fill_c, stroke=stroke_c, sw=1.8, rx=8))
        frags.append(text(x + 95, y + 38, title_str, size=15, bold=True, color=stroke_c))
        frags.append(text(x + 95, y + 64, desc_str, size=11, color=INK))

    # Переходи (Стрілки)
    # 1. Not-Installed -> Unpacked
    frags.append(arrow(250, 210, 310, 210, color=LINE, sw=2.0))
    frags.append(text(280, 195, "1. preinst", size=12, bold=True, color=POS))
    frags.append(text(280, 230, "Розпакування", size=11, color=MUTED))

    # 2. Unpacked -> Half-Configured
    frags.append(arrow(500, 210, 560, 210, color=LINE, sw=2.0))
    frags.append(text(530, 195, "2. postinst", size=12, bold=True, color=POS))
    frags.append(text(530, 230, "Конфігурація", size=11, color=MUTED))

    # 3. Half-Configured -> Installed
    frags.append(arrow(750, 210, 810, 210, color=LINE, sw=2.0))
    frags.append(text(780, 195, "Успіх", size=12, bold=True, color=FIELD))
    frags.append(text(780, 230, "Triggers ok", size=11, color=MUTED))

    # 4. Зворотний шлях (Видалення): Installed -> Not-Installed (дуга знизу)
    path_d = "M 905 270 C 905 370, 155 370, 155 270"
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.0" stroke-dasharray="6 4" marker-end="url(#arrow)"/>' % (path_d, POS))
    frags.append(text(530, 345, "Видалення: prerm → видалення файлів → postrm (Purge)", size=12, color=POS, bold=True))

    # Збій (Rollback)
    frags.append(arrow(655, 270, 155, 270, color=POS, sw=1.5))
    frags.append(text(405, 285, "Помилка скрипту → Rollback до Not-Installed / Half-Installed", size=11, color=POS, italic=True))

    render(os.path.join(IMG, 'fig-pkg-lifecycle.svg'), W, H, *frags)


# ── 3. База даних та атомарна заміна ────────────────────────────────────
def fig_pkg_database_registry():
    W, H = 1040, 460
    frags = []

    frags.append(rect(20, 20, 1000, 420, fill=BG, stroke=LINE, sw=1.5, rx=10))
    frags.append(text(520, 50, "База даних пакетного менеджера та механізм атомарного оновлення", size=18, bold=True))

    # Блок 1: Системна БД (/var/lib/dpkg або /var/lib/rpm)
    frags.append(rect(40, 80, 440, 340, fill=BLUE_FILL, stroke=NEG, sw=1.5, rx=8))
    frags.append(text(260, 110, "Реєстр стану системної бази даних", size=15, color=NEG, bold=True))
    frags.append(line(55, 125, 465, 125, color=NEG, sw=1.0))

    db_boxes = [
        ("Таблиця статусів (Status index)", "Package: nginx | Status: install ok installed | Version: 1.24.0"),
        ("Індекс власництва файлів (Path map)", "/usr/bin/nginx -> package: nginx\n/etc/nginx/nginx.conf -> package: nginx (conffile)"),
        ("Хеш-суми та версіонування (Checksums)", "SHA256(/usr/bin/nginx) = e3b0c44298fc1c149afbf4c8996fb924..."),
    ]

    for i, (title_str, content_str) in enumerate(db_boxes):
        y_box = 140 + i * 90
        frags.append(rect(55, y_box, 410, 78, fill=BG, stroke=NEG, sw=1.2, rx=6))
        frags.append(text(65, y_box + 22, title_str, size=13, anchor="start", bold=True, color=NEG))
        lines = content_str.split("\n")
        for j, ln in enumerate(lines):
            frags.append(text(65, y_box + 44 + j * 18, ln, size=11, anchor="start", color=INK))

    # Стрілка між БД та VFS
    frags.append(arrow(480, 250, 540, 250, color=LINE, sw=2.0))
    frags.append(text(510, 235, "Синхронізація", size=11, bold=True, color=MUTED))

    # Блок 2: Файлова система (VFS) та Атомарний rename
    frags.append(rect(540, 80, 460, 340, fill=GREEN_FILL, stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(770, 110, "Атомарне оновлення у файловій системі (VFS)", size=15, color=FIELD, bold=True))
    frags.append(line(555, 125, 985, 125, color=FIELD, sw=1.0))

    vfs_steps = [
        ("Крок 1: Запис у тимчасовий файл", "open('/usr/bin/nginx.dpkg-new', O_CREAT|O_WRONLY)\nwrite(payload) -> fsync()"),
        ("Крок 2: Перевірка контрольної суми", "SHA256(nginx.dpkg-new) == hash_from_metadata"),
        ("Крок 3: Атомарний системний виклик", "rename('/usr/bin/nginx.dpkg-new', '/usr/bin/nginx')\n(Старий інод замінюється миттєво без проміжного стану)"),
    ]

    for i, (title_str, content_str) in enumerate(vfs_steps):
        y_box = 140 + i * 90
        frags.append(rect(555, y_box, 430, 78, fill=BG, stroke=FIELD, sw=1.2, rx=6))
        frags.append(text(565, y_box + 22, title_str, size=13, anchor="start", bold=True, color=FIELD))
        lines = content_str.split("\n")
        for j, ln in enumerate(lines):
            frags.append(text(565, y_box + 44 + j * 18, ln, size=11, anchor="start", color=INK))

    render(os.path.join(IMG, 'fig-pkg-database-registry.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_pkg_structure()
    fig_pkg_lifecycle()
    fig_pkg_database_registry()
