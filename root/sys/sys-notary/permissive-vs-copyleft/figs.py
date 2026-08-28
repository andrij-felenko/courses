# -*- coding: utf-8 -*-
"""Генератор векторних SVG-фігур для теми permissive-vs-copyleft.
Вимоги: pure Python, svgkit, перевірка через svgcheck.py.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра кольорів
BG_PERM     = "#eafaf1"  # Світло-зелений (Permissive)
BORDER_PERM = "#27ae60"
BG_WEAK     = "#eef2ff"  # Світло-синій (Weak Copyleft)
BORDER_WEAK = "#2563eb"
BG_STRONG   = "#fff7ed"  # Світло-помаранчевий (Strong Copyleft)
BORDER_STRONG = "#ea580c"
BG_NET      = "#fef2f2"  # Світло-червоний (Network Copyleft)
BORDER_NET  = "#dc2626"
BG_PROP     = "#f3f4f6"  # Світло-сірий (Proprietary)
BORDER_PROP = "#4b5563"
BG_CARD     = "#ffffff"


def fig1_license_philosophies():
    """Фігура 1: Фундаментальне розходження філософій пермісивних і копілефтних ліцензій."""
    w, h = 940, 480
    parts = []

    # Головний заголовок
    parts.append(text(w / 2, 28, "Філософське розходження: Свобода розробника проти Свободи вихідного коду", size=15, bold=True))

    # Лівий блок: Пермісивна філософія (BSD / MIT / Apache 2.0)
    parts.append(rect(40, 55, 410, 400, fill=BG_PERM, stroke=BORDER_PERM, sw=2, rx=8))
    parts.append(text(245, 82, "ПЕРМІСИВНА МОДЕЛЬ (Permissive)", size=13, color=BORDER_PERM, bold=True))
    parts.append(text(245, 102, "«Свобода розробника / інженера»", size=11, color=MUTED, italic=True))

    b_p1 = fitbox(60, 120, 370, 70, "Головний принцип:\nАвтор дає максимальні права й мінімум обов'язків.\nКод можна приватизувати й закрити в комерційному рішенні.", size=11, fill=BG_CARD, stroke=BORDER_PERM)
    b_p2 = fitbox(60, 200, 370, 75, "Єдине ключове зобов'язання:\n• Збереження рядка копірайту та авторської атрибуції\n• Збереження відмови від гарантій (Disclaimer)\n• Заборона звинувачувати авторів у збитках", size=11, fill=BG_CARD, stroke=BORDER_PERM)
    b_p3 = fitbox(60, 285, 370, 75, "Правовий наслідок для бізнесу:\n• Можливість випуску закритого пропрієтарного бінарника\n• Відсутність обов'язку повертати правки авторам\n• Повна сумісність із комерційними EULA", size=11, fill=BG_CARD, stroke=BORDER_PERM)
    b_p4 = fitbox(60, 370, 370, 65, "Типові представники:\nMIT, BSD-2-Clause, BSD-3-Clause, Apache 2.0, ISC, 0BSD", size=11, fill="#dcfce7", stroke=BORDER_PERM, bold=True)
    parts.extend([b_p1, b_p2, b_p3, b_p4])

    # Правий блок: Копілефтна філософія (GPL / LGPL / MPL / AGPL)
    parts.append(rect(490, 55, 410, 400, fill=BG_STRONG, stroke=BORDER_STRONG, sw=2, rx=8))
    parts.append(text(695, 82, "КОПІЛЕФТНА МОДЕЛЬ (Copyleft)", size=13, color=BORDER_STRONG, bold=True))
    parts.append(text(695, 102, "«Свобода коду та кінцевого користувача»", size=11, color=MUTED, italic=True))

    b_c1 = fitbox(510, 120, 370, 70, "Головний принцип (Взаємність / Reciprocity):\nАвтор захищає публічне надбання від закриття.\nКористувач бінарника має отримати повний вихідний код.", size=11, fill=BG_CARD, stroke=BORDER_STRONG)
    b_c2 = fitbox(510, 200, 370, 75, "Ключові зобов'язання дистриб'ютора:\n• Надання повного відповідного сирцевого коду (Source)\n• Заборона додавати додаткові обмеження на похідний твір\n• Збереження ліцензії для всіх модифікацій і зв'язок", size=11, fill=BG_CARD, stroke=BORDER_STRONG)
    b_c3 = fitbox(510, 285, 370, 75, "Правовий наслідок для бізнесу:\n• Будь-яке статичне компонування розкриває весь код\n• Неможливість приховати пропрієтарні алгоритми в образі\n• Ризик судових позовів за поширення без сирців", size=11, fill=BG_CARD, stroke=BORDER_STRONG)
    b_c4 = fitbox(510, 370, 370, 65, "Типові представники:\nGPLv2, GPLv3, AGPLv3, LGPLv2.1/v3, MPL 2.0", size=11, fill="#ffedd5", stroke=BORDER_STRONG, bold=True)
    parts.extend([b_c1, b_c2, b_c3, b_c4])

    render(os.path.join(OUT, "license-philosophies.svg"), w, h, *parts)


def fig2_viral_infection_boundaries():
    """Фігура 2: Механіка ліцензійного зараження та архітектурні межі коду."""
    w, h = 940, 490
    parts = []

    parts.append(text(w / 2, 26, "Механізм ліцензійного зараження (Viral Effect) та ізоляційні межі архітектури", size=15, bold=True))

    # Верхня зона: Похідний твір (Єдиний адресний простір) -> ЗАРАЖЕННЯ
    parts.append(rect(40, 50, 860, 195, fill="#fff1f2", stroke="#f43f5e", sw=2, rx=8))
    parts.append(text(470, 72, "ЗОНА ПОХІДНОГО ТВОРУ: Спільний адресний простір процесу ➔ ЗАРАЖЕННЯ GPL", size=12, color=POS, bold=True))

    box1 = fitbox(60, 85, 260, 145, "1. Статичне компонування (.a)\n\n• Символи об'єднані лінкером\n• Єдиний ELF / PE бінарник\n• Спільна таблиця релокацій\n➔ 100% комбінований твір,\nвесь продукт стає GPL", size=11, fill="#ffe4e6", stroke="#e11d48")
    box2 = fitbox(340, 85, 260, 145, "2. Динамічне лінкування (.so)\n\n• DT_NEEDED, dlopen()\n• Обмін структурами в RAM\n• Взаємозалежні типи C/C++\n➔ Позиція FSF: комбінований твір\n(Виняток: LGPL дозволяє .so)", size=11, fill="#ffe4e6", stroke="#e11d48")
    box3 = fitbox(620, 85, 260, 145, "3. C++ Templates та Inline\n\n• Тіла функцій в заголовках .h\n• Код компілюється в чужий .o\n• Істотне фізичне запозичення\n➔ Інфікує об'єктний код\nбезпосередньо компілятором", size=11, fill="#ffe4e6", stroke="#e11d48")
    parts.extend([box1, box2, box3])

    # Нижня зона: Незалежні твори (Розділені процеси) -> ЧИСТОТА
    parts.append(rect(40, 260, 860, 210, fill="#f0fdf4", stroke="#22c55e", sw=2, rx=8))
    parts.append(text(470, 282, "ЗОНА НЕЗАЛЕЖНИХ ТВОРІВ: Розділені адресні простори ОС ➔ ЗБЕРЕЖЕННЯ ЗАКРИТОСТІ", size=12, color=FIELD, bold=True))

    box4 = fitbox(60, 295, 260, 160, "1. Міжпроцесний обмін (IPC)\n\n• UNIX Sockets / Named Pipes\n• Серіалізований протокол\n• Окремі PID процесів у ядрі\n➔ Незалежні програми,\nпропрієтарний код захищено", size=11, fill="#dcfce7", stroke="#16a34a")
    box5 = fitbox(340, 295, 260, 160, "2. Мережевий REST / gRPC API\n\n• Мережевий сокет TCP/IP\n• Формати JSON / Protobuf\n• Фізично або логічно окремо\n➔ Чисто для GPLv2 / GPLv3\n(Увага: AGPL вимагає відкриття)", size=11, fill="#dcfce7", stroke="#16a34a")
    box6 = fitbox(620, 295, 260, 160, "3. Системні виклики ядра\n\n• Інтерфейс syscall (libc)\n• Торвальдсів виняток у COPYING\n• Драйвери через /dev і ioctl\n➔ Простір користувача не\nзаражається ядром GPLv2", size=11, fill="#dcfce7", stroke="#16a34a")
    parts.extend([box4, box5, box6])

    render(os.path.join(OUT, "viral-infection-boundaries.svg"), w, h, *parts)


def fig3_embedded_firmware_matrix():
    """Фігура 3: Матриця сумісності ліцензій у єдиному бінарному образі прошивки."""
    w, h = 940, 480
    parts = []

    parts.append(text(w / 2, 26, "Матриця сумісності поєднання ліцензій у монолітному бінарнику прошивки", size=15, bold=True))

    headers = ["Вхідна ліцензія A", "Вхідна ліцензія B", "Тип компонування", "Результуючий статус", "Юридичні зобов'язання"]
    xs = [40, 200, 360, 520, 710]
    widths = [150, 150, 150, 180, 190]

    # Шапка
    parts.append(rect(40, 50, 860, 32, fill="#1e293b", stroke="#0f172a", rx=4))
    for i, h_text in enumerate(headers):
        parts.append(text(xs[i] + widths[i] / 2, 71, h_text, size=11, color="#ffffff", bold=True))

    rows = [
        ("MIT / BSD", "MIT / BSD", "Статичне (.a / .o)", "MIT / BSD", "Лише збереження копірайту", BG_PERM, BORDER_PERM),
        ("MIT / BSD", "Apache 2.0", "Статичне (.a / .o)", "Apache 2.0", "Копірайт + патентний захист", BG_PERM, BORDER_PERM),
        ("MIT / BSD", "GPL v2.0-only", "Статичне (.a / .o)", "GPL v2.0-only", "Повне розкриття сирців образу", BG_STRONG, BORDER_STRONG),
        ("Apache 2.0", "GPL v2.0-only", "Статичне (.a / .o)", "НЕСУМІСНІ ✖", "Юридична колізія §6 GPLv2 vs §3 Apache", "#fee2e2", "#ef4444"),
        ("Apache 2.0", "GPL v3.0", "Статичне (.a / .o)", "GPL v3.0", "Повне розкриття + патентний пункт", BG_STRONG, BORDER_STRONG),
        ("LGPL v2.1", "Пропрієтарний", "Динамічне (.so)", "Змішаний (OK)", "Бібліотека LGPL відкрита, додаток закритий", BG_WEAK, BORDER_WEAK),
        ("LGPL v2.1", "Пропрієтарний", "Статичне (.a)", "Умовно сумісно", "Потрібно дати .o об'єктники для перелінку", BG_WEAK, BORDER_WEAK),
        ("GPL v2 / v3", "Пропрієтарний", "Статичне (.a)", "НЕЗАКОННО ✖", "Пряме порушення авторських прав", "#fee2e2", "#ef4444"),
        ("MPL 2.0", "Пропрієтарний", "Файловий поділ", "Змішаний (OK)", "Зміни у файлах MPL відкриті, свій код закритий", BG_WEAK, BORDER_WEAK),
    ]

    y_start = 86
    row_h = 37
    for idx, (lic_a, lic_b, link_t, res_s, oblig, bg_c, brd_c) in enumerate(rows):
        y = y_start + idx * row_h
        parts.append(rect(40, y, 860, row_h - 3, fill=bg_c, stroke=brd_c, sw=1, rx=3))
        parts.append(text(xs[0] + widths[0] / 2, y + 21, lic_a, size=11, color=INK, bold=True))
        parts.append(text(xs[1] + widths[1] / 2, y + 21, lic_b, size=11, color=INK, bold=True))
        parts.append(text(xs[2] + widths[2] / 2, y + 21, link_t, size=10, color=MUTED))
        is_err = "✖" in res_s
        parts.append(text(xs[3] + widths[3] / 2, y + 21, res_s, size=11, color=POS if is_err else FIELD if "OK" in res_s or "MIT" in res_s else INK, bold=True))
        parts.append(text(xs[4] + widths[4] / 2, y + 21, oblig, size=10, color=INK))

    # Висновок унизу
    parts.append(rect(40, 425, 860, 45, fill="#f8fafc", stroke="#94a3b8", rx=4))
    parts.append(text(470, 452, "Правило поглинання: Результуючий бінарник підпорядковується найсуворішій ліцензії в ланцюгу компонування.", size=11, color=INK, bold=True))

    render(os.path.join(OUT, "embedded-firmware-matrix.svg"), w, h, *parts)


def fig4_architectural_isolation_patterns():
    """Фігура 4: Архітектурні патерни правової ізоляції коду в реальних системах."""
    w, h = 940, 480
    parts = []

    parts.append(text(w / 2, 26, "Інженерні патерни правової ізоляції: Як зберегти пропрієтарний код у системі з GPL", size=15, bold=True))

    # Патерн 1: Linux Syscall + AOSP HAL
    p1 = rect(40, 55, 415, 195, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8)
    parts.append(p1)
    parts.append(text(247, 78, "Патерн 1: Апаратний прошарок (AOSP HAL Model)", size=12, color="#0f172a", bold=True))
    box1_1 = fitbox(55, 92, 385, 45, "Пропрієтарний додаток / Сервіс (Apache 2.0 / Commercial)\nНе містить GPL-символів, викликає чистий HAL C++ API", size=10, fill=BG_CARD, stroke="#94a3b8")
    box1_2 = fitbox(55, 142, 385, 45, "Vendor HAL (.so плагін закритий) ➔ Linus Exception\nСпілкується з ядром виключно через ioctl() та /dev вузли", size=10, fill=BG_PERM, stroke=BORDER_PERM)
    box1_3 = fitbox(55, 192, 385, 45, "Ядро Linux (GPLv2-only) — Драйвер контролера\nІзольоване межею системних викликів (Syscall Boundary)", size=10, fill=BG_STRONG, stroke=BORDER_STRONG)
    parts.extend([box1_1, box1_2, box1_3])

    # Патерн 2: IPC Daemon Proxy
    p2 = rect(485, 55, 415, 195, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8)
    parts.append(p2)
    parts.append(text(692, 78, "Патерн 2: Демон-проксі через сокет (IPC Proxy)", size=12, color="#0f172a", bold=True))
    box2_1 = fitbox(500, 92, 385, 45, "Пропрієтарний процес (PID 1024, Commercial)\nАлгоритми ноу-хау, закрита математика та ліцензійні ключі", size=10, fill=BG_CARD, stroke="#94a3b8")
    box2_2 = fitbox(500, 142, 385, 45, "Межа ізоляції: UNIX Domain Socket / FIFO Pipe / Protobuf\nОбмін серіалізованими повідомленнями без спільних типів", size=10, fill="#f0fdf4", stroke=FIELD)
    box2_3 = fitbox(500, 192, 385, 45, "Окремий GPL-демон (PID 1025, GPLv3-сервіс)\nПовний вихідний код демона відкрито замовнику", size=10, fill=BG_STRONG, stroke=BORDER_STRONG)
    parts.extend([box2_1, box2_2, box2_3])

    # Патерн 3: CLI Subprocess Bridge
    p3 = rect(40, 265, 415, 195, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8)
    parts.append(p3)
    parts.append(text(247, 288, "Патерн 3: Виклик підпроцесу (fork/execve CLI)", size=12, color="#0f172a", bold=True))
    box3_1 = fitbox(55, 302, 385, 45, "Комерційна програма керування\nФормує текстові аргументи командного рядка argv[]", size=10, fill=BG_CARD, stroke="#94a3b8")
    box3_2 = fitbox(55, 352, 385, 45, "Виклик fork() + execve(\"/usr/bin/ffmpeg\", ...)\nВзаємодія через стандартні дескриптори stdin/stdout", size=10, fill="#f0fdf4", stroke=FIELD)
    box3_3 = fitbox(55, 402, 385, 45, "Стороння автономна утиліта (GPLv3 Binary)\nВикористовується як окремий загальносистемний інструмент", size=10, fill=BG_STRONG, stroke=BORDER_STRONG)
    parts.extend([box3_1, box3_2, box3_3])

    # Патерн 4: LGPL Dynamic Linker Shim
    p4 = rect(485, 265, 415, 195, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8)
    parts.append(p4)
    parts.append(text(692, 288, "Патерн 4: Динамічний шим LGPL (Relinkable Shim)", size=12, color="#0f172a", bold=True))
    box4_1 = fitbox(500, 302, 385, 45, "Пропрієтарний бінарник ELF (Dynamic Linked)\nКомпонується динамічно з .so бібліотекою через PLT/GOT", size=10, fill=BG_CARD, stroke="#94a3b8")
    box4_2 = fitbox(500, 352, 385, 45, "Динамічна бібліотека libcrypto.so (LGPL v2.1)\nКористувач має право замінити .so на власну скомпільовану версію", size=10, fill=BG_WEAK, stroke=BORDER_WEAK)
    box4_3 = fitbox(500, 402, 385, 45, "Обов'язкова умова прошивки:\nФайлова система дозволяє перезапис .so або LD_LIBRARY_PATH", size=10, fill="#fffbeb", stroke="#d97706")
    parts.extend([box4_1, box4_2, box4_3])

    render(os.path.join(OUT, "architectural-isolation-patterns.svg"), w, h, *parts)


if __name__ == "__main__":
    fig1_license_philosophies()
    fig2_viral_infection_boundaries()
    fig3_embedded_firmware_matrix()
    fig4_architectural_isolation_patterns()
    print("Всі 4 фігури успішно згенеровано.")
