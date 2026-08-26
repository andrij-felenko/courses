# -*- coding: utf-8 -*-
"""Генератор векторних SVG-фігур для теми open-source-licenses.
Вимоги: pure Python, svgkit, перевірка через svgcheck.py.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори розширеної палітри теми
BG_PERM   = "#eaf5ea"  # Світло-зелений (Permissive)
BORDER_PERM = "#27ae60"
BG_WEAK   = "#eef2ff"  # Світло-синій (Weak Copyleft)
BORDER_WEAK = "#2563eb"
BG_STRONG = "#fff7ed"  # Світло-помаранчевий (Strong Copyleft)
BORDER_STRONG = "#ea580c"
BG_NET    = "#fef2f2"  # Світло-червоний (Network Copyleft)
BORDER_NET = "#dc2626"
BG_PROP   = "#f3f4f6"  # Світло-сірий (Proprietary)
BORDER_PROP = "#4b5563"


def fig1_license_spectrum():
    """Фігура 1: Спектр ліцензій відкритого коду від Public Domain до Proprietary."""
    w, h = 940, 480
    parts = []

    # Заголовок зверху
    parts.append(text(w / 2, 32, "Правовий спектр ліцензій: від повного відчуження прав до пропрієтарного замикання", size=15, bold=True))

    # Стрілка спектру (градієнт зобов'язань розкриття вихідного коду)
    parts.append(line(60, 68, 880, 68, color=LINE, sw=2))
    parts.append(text(60, 86, "← Мінімальні обмеження (дозвільні)", size=11, color=FIELD, anchor="start", bold=True))
    parts.append(text(880, 86, "Максимальні вимоги взаємності (копілефт) →", size=11, color=POS, anchor="end", bold=True))

    # 5 стовпців категорій
    cols = [
        ("Суспільне надбання\nта Permissive", ["Unlicense, CC0", "MIT, BSD (2/3-Cl.)", "Apache 2.0, ISC"],
         "Вільне поширення, право закривати код", "Обов'язок зберегти копірайт", BG_PERM, BORDER_PERM, 60),
        ("Слабкий копілефт\n(Weak Copyleft)", ["LGPL v2.1 / v3.0", "MPL 2.0", "EPL 2.0 / CDDL"],
         "Межа файлу чи бібліотеки", "Зміни в бібліотеці — відкриті", BG_WEAK, BORDER_WEAK, 230),
        ("Сильний копілефт\n(Strong Copyleft)", ["GPL v2.0", "GPL v3.0"],
         "Межа всього бінарного образу", "Увесь комбінований твір — GPL", BG_STRONG, BORDER_STRONG, 400),
        ("Мережевий копілефт\n(Network Copyleft)", ["AGPL v3.0", "SSPL (non-OSI)"],
         "Межа мережевого доступу (SaaS)", "Розкриття коду через мережу", BG_NET, BORDER_NET, 570),
        ("Пропрієтарні та\nКомерційні EULA", ["Комерційні ліцензії", "All Rights Reserved", "NDAs / NDA-only SDK"],
         "Повна заборона розкриття коду", "Виключний контроль вендора", BG_PROP, BORDER_PROP, 740),
    ]

    col_w = 140
    for title, lics, scope, oblig, bg_c, brd_c, x in cols:
        # Картка категорії
        parts.append(rect(x, 110, col_w, 330, fill=bg_c, stroke=brd_c, sw=1.8, rx=8))
        # Заголовок категорії
        parts.append(mtext(x + col_w / 2, 134, title, size=12, color=INK, bold=True, lh=1.2))
        parts.append(line(x + 10, 166, x + col_w - 10, 166, color=brd_c, sw=1, dash="2,2"))

        # Перелік ліцензій
        parts.append(text(x + col_w / 2, 185, "Приклади ліцензій:", size=10, color=MUTED, bold=True))
        for i, lic in enumerate(lics):
            parts.append(text(x + col_w / 2, 204 + i * 18, lic, size=11, color=INK, bold=True))

        parts.append(line(x + 10, 264, x + col_w - 10, 264, color=brd_c, sw=1, dash="2,2"))

        # Межа зараження
        parts.append(text(x + col_w / 2, 282, "Межа ізоляції:", size=10, color=MUTED, bold=True))
        parts.append(mtext(x + col_w / 2, 300, scope, size=10, color=INK, bold=False, lh=1.2))

        parts.append(line(x + 10, 342, x + col_w - 10, 342, color=brd_c, sw=1, dash="2,2"))

        # Зобов'язання
        parts.append(text(x + col_w / 2, 360, "Головне зобов'язання:", size=10, color=MUTED, bold=True))
        parts.append(mtext(x + col_w / 2, 378, oblig, size=10, color=INK, bold=False, lh=1.2))

    render(os.path.join(OUT, "license-spectrum.svg"), w, h, *parts)


def fig2_license_compatibility_matrix():
    """Фігура 2: Матриця та спрямований граф сумісності ліцензій."""
    w, h = 900, 470
    parts = []

    parts.append(text(w / 2, 28, "Спрямовані потоки та сумісність поєднання ліцензійних сімейств", size=15, bold=True))

    # Вузли (ліцензійні блоки)
    # 1. Permissive (MIT, BSD-2/3)
    p1 = fitbox(40, 70, 200, 80, "MIT / BSD-2/3 / ISC\n• Дозвільні ліцензії\n• Сумісні майже з усім", size=12, fill=BG_PERM, stroke=BORDER_PERM)
    # 2. Apache 2.0
    p2 = fitbox(40, 220, 200, 90, "Apache 2.0\n• Дозвільна + патентний грант\n• Застереження про відсіч\n• Конфлікт із GPL v2", size=12, fill=BG_PERM, stroke=BORDER_PERM)
    # 3. LGPL v2.1 / v3.0
    p3 = fitbox(350, 70, 200, 80, "LGPL v2.1 / v3.0\n• Слабкий копілефт\n• Дозволяє пропрієтарний лінк\n• Реліцензування у GPL", size=12, fill=BG_WEAK, stroke=BORDER_WEAK)
    # 4. GPL v2.0-only
    p4 = fitbox(350, 220, 200, 90, "GPL v2.0-only\n• Сильний копілефт (1991)\n• Заборона нових обмежень (§6)\n• НЕСУМІСНА з Apache 2.0", size=12, fill=BG_STRONG, stroke=BORDER_STRONG)
    # 5. GPL v3.0
    p5 = fitbox(660, 140, 200, 90, "GPL v3.0-only\n• Сильний копілефт (2007)\n• Антитайвоізація (§6)\n• СУМІСНА з Apache 2.0", size=12, fill=BG_STRONG, stroke=BORDER_STRONG)
    # 6. AGPL v3.0
    p6 = fitbox(660, 310, 200, 80, "AGPL v3.0\n• Мережевий копілефт\n• Сумісна з GPL v3 через §13\n• Максимальне поглинання", size=12, fill=BG_NET, stroke=BORDER_NET)

    parts.extend([p1, p2, p3, p4, p5, p6])

    # Зв'язки / стрілки
    # MIT -> Apache 2.0
    parts.append(arrow(140, 150, 140, 220, color=BORDER_PERM, sw=2))
    parts.append(text(148, 185, "Поглинається", size=10, color=FIELD, anchor="start"))

    # MIT -> LGPL
    parts.append(arrow(240, 110, 350, 110, color=BORDER_PERM, sw=2))
    parts.append(text(295, 102, "Дозволено", size=10, color=FIELD))

    # LGPL -> GPL v3
    parts.append(arrow(550, 110, 660, 160, color=BORDER_WEAK, sw=2))
    parts.append(text(605, 126, "Реліцензування", size=10, color=BORDER_WEAK))

    # LGPL -> GPL v2
    parts.append(arrow(450, 150, 450, 220, color=BORDER_WEAK, sw=2))
    parts.append(text(458, 185, "§3 (GPL v2)", size=10, color=BORDER_WEAK, anchor="start"))

    # Apache 2.0 -> GPL v3 (СУМІСНО)
    parts.append(arrow(240, 265, 660, 195, color=FIELD, sw=2.2))
    parts.append(text(450, 248, "Сумісно: Apache 2.0 → GPL v3", size=11, color=FIELD, bold=True))

    # Apache 2.0 <x> GPL v2 (НЕСУМІСНО!)
    parts.append(line(240, 280, 350, 280, color=POS, sw=2, dash="4,3"))
    parts.append(text(295, 274, "НЕСУМІСНО ✖", size=11, color=POS, bold=True))
    parts.append(text(295, 296, "Патентні вимоги §3", size=9, color=POS))

    # GPL v3 -> AGPL v3
    parts.append(arrow(760, 230, 760, 310, color=BORDER_STRONG, sw=2))
    parts.append(text(768, 270, "§13 AGPL", size=10, color=BORDER_STRONG, anchor="start"))

    # Пояснювальний блок унизу
    box_legend = fitbox(40, 380, 580, 70, "Правило односторонньої сумісності (One-Way Compatibility):\nКод під більш дозвільною ліцензією може входити до проєкту під більш суворою ліцензією,\nале результуючий бінарний комбінований артефакт підпорядковується найсуворішим умовам.", size=11, fill="#f8fafc", stroke="#94a3b8")
    parts.append(box_legend)

    render(os.path.join(OUT, "license-compatibility-matrix.svg"), w, h, *parts)


def fig3_linking_and_derivative_work():
    """Фігура 3: Межі похідного твору (статичне, динамічне лінкування, IPC, RPC)."""
    w, h = 920, 480
    parts = []

    parts.append(text(w / 2, 28, "Архітектурні межі програми та глибина поширення копілефту", size=15, bold=True))

    # Ліва половина: Пряме зачеплення (Combined/Derivative Work) -> Інфекція
    parts.append(rect(40, 60, 400, 390, fill="#fff1f2", stroke="#f43f5e", sw=2, rx=10))
    parts.append(text(240, 85, "Єдиний адресний простір (Похідний твір)", size=13, color=POS, bold=True))

    # Статичне лінкування
    box_s = fitbox(60, 110, 360, 80, "1. Статичне компонування (.a / .o)\n• Спільний файл ELF / PE\n• Символи та структури склеєні лінкером\n➔ Обов'язкове розкриття всього коду під GPL", size=11, fill="#ffe4e6", stroke="#e11d48")
    # Динамічне лінкування
    box_d = fitbox(60, 205, 360, 105, "2. Динамічне завантаження (.so / .dll)\n• DT_NEEDED, dlopen() та спільна пам'ять\n• Обмін внутрішніми C/C++ структурами даних\n➔ За версією FSF створює комбінований твір\n(Виняток: LGPL дозволяє динамічний лінк)", size=11, fill="#ffe4e6", stroke="#e11d48")
    # Макроси й шаблони C++
    box_t = fitbox(60, 325, 360, 105, "3. C++ Templates / Inline Headers\n• Тіла функцій компілюються прямо у ваш .o\n• Істотний обсяг чужого коду в бінарнику\n➔ Інфікує пропрієтарний об'єктний код\n(Вимагає Header-only винятків, напр. LLVM)", size=11, fill="#ffe4e6", stroke="#e11d48")
    parts.extend([box_s, box_d, box_t])

    # Права половина: Ізольовані процеси (Separate Works) -> Без інфекції
    parts.append(rect(480, 60, 400, 390, fill="#f0fdf4", stroke="#22c55e", sw=2, rx=10))
    parts.append(text(680, 85, "Розділені адресні простори (Незалежні твори)", size=13, color=FIELD, bold=True))

    # Міжпроцесна взаємодія (IPC / Pipes / Sockets)
    box_ipc = fitbox(500, 110, 360, 80, "1. UNIX Sockets / Pipes / IPC\n• Окремі PID процесів у ядрі\n• Серіалізований текстовий або бінарний потік\n➔ Процеси залишаються юридично незалежними", size=11, fill="#dcfce7", stroke="#16a34a")
    # Мережевий REST / gRPC API
    box_net = fitbox(500, 205, 360, 105, "2. Мережевий виклик (REST / gRPC / RPC)\n• Стандартизований відкритий протокол\n• Фізично незалежні сервери / мікросервіси\n➔ GPL v2/v3 НЕ вимагає відкриття клієнта\n(Увага: AGPL вимагає відкриття серверної частини)", size=11, fill="#dcfce7", stroke="#16a34a")
    # Форк і execve CLI
    box_cli = fitbox(500, 325, 360, 105, "3. Виклик утиліти через fork() + execve()\n• Взаємодія через argv[] та stdout/stdin\n• Використання як окремого інструменту ОС\n➔ Не створює похідного твору (Arms-Length)\nпри умові загального стандарту обміну", size=11, fill="#dcfce7", stroke="#16a34a")
    parts.extend([box_ipc, box_net, box_cli])

    render(os.path.join(OUT, "linking-and-derivative-work.svg"), w, h, *parts)


def fig4_spdx_sbom_pipeline():
    """Фігура 4: Конвеєр аудиту ліцензій та генерації SBOM у CI/CD."""
    w, h = 920, 440
    parts = []

    parts.append(text(w / 2, 28, "Автоматизований конвеєр аудиту ліцензійної чистоти та SBOM у CI/CD", size=15, bold=True))

    # Крок 1: Вхідні артефакти
    s1 = fitbox(40, 70, 170, 110, "1. Вхідні дані\n• Вихідний код git\n• Залежності (conan/vcpkg)\n• Бінарний образ ELF\n• .comment / .note секції", size=11, fill=FILL, stroke=LINE)
    # Крок 2: Сканери метаданих
    s2 = fitbox(250, 70, 180, 110, "2. Сканери ліцензій\n• SPDX-ідентифікатори\n• Fossology / ScanCode\n• DT_NEEDED парсер\n• syft / trivy сканер", size=11, fill=BG_WEAK, stroke=BORDER_WEAK)
    # Крок 3: Парсер виразів та матриця політик
    s3 = fitbox(470, 70, 200, 110, "3. Двигун ліцензійних правил\n• Парсер виразів (AND, OR, WITH)\n• Матриця несумісностей\n• Перевірка Allow/Deny-list\n• Виявлення прихованого GPL", size=11, fill=BG_STRONG, stroke=BORDER_STRONG)
    # Крок 4: Результат і генерація артефактів
    s4 = fitbox(710, 70, 170, 110, "4. Вихідні артефакти\n• SBOM (SPDX 2.3 / 3.0)\n• CycloneDX JSON\n• Compliance Report\n• Відкриті коди (tar.gz)", size=11, fill=BG_PERM, stroke=BORDER_PERM)

    parts.extend([s1, s2, s3, s4])

    # Стрілки конвеєра
    parts.append(arrow(210, 125, 250, 125, color=LINE, sw=2))
    parts.append(arrow(430, 125, 470, 125, color=LINE, sw=2))
    parts.append(arrow(670, 125, 710, 125, color=LINE, sw=2))

    # Нижня частина: Шлюзи перевірки (Gate Fail vs Gate Pass)
    parts.append(rect(40, 220, 840, 190, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(460, 245, "Критерії автоматичного блокування збірки (CI/CD Quality Gate)", size=13, color=INK, bold=True))

    # Червоний блок блокування
    box_fail = fitbox(60, 265, 380, 130, "✖ БЛОКУВАННЯ ЗБІРКИ (Gate FAILED):\n• GPL/AGPL статично влінковано у комерційний образ\n• Поєднання Apache 2.0 із кодом GPL-2.0-only\n• Відсутня атрибуція та обов'язковий текст ліцензії\n• Нерозпізнаний або невалідний вираз ліцензії", size=11, fill="#fef2f2", stroke=POS)
    # Зелений блок дозволу
    box_pass = fitbox(480, 265, 380, 130, "✔ УСПІШНИЙ ПРОХІД (Gate PASSED):\n• Усі залежності входять до дозволеного списку (Allowlist)\n• Для LGPL забезпечено динамічний лінк (.so)\n• Згенеровано повний SBOM для технічного файлу\n• Сформовано юридичний пакет ліцензій та копірайтів", size=11, fill="#f0fdf4", stroke=FIELD)

    parts.extend([box_fail, box_pass])

    render(os.path.join(OUT, "spdx-sbom-pipeline.svg"), w, h, *parts)


if __name__ == "__main__":
    fig1_license_spectrum()
    fig2_license_compatibility_matrix()
    fig3_linking_and_derivative_work()
    fig4_spdx_sbom_pipeline()
    print("Всі 4 фігури успішно згенеровано.")
