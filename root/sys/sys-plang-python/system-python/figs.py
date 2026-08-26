# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми 'Системний Python і чому його не чіпають'."""

import os
import sys

# Шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, text, mtext, rect, line, arrow, circle,
    INK, MUTED, LINE, FILL, BG, POS, NEG, FIELD, FONT
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_system_python_ecosystem():
    """Архітектурна роль системного Python у стеку дистрибутива Linux."""
    w, h = 940, 520
    frags = []

    frags.append(text(w / 2, 28, "Архітектурна роль системного Python у складі операційної системи", size=15, bold=True))

    # Ліва колонка: Системні служби ОС
    col1_x, col1_y, col1_w, col1_h = 35, 60, 260, 420
    frags.append(rect(col1_x, col1_y, col1_w, col1_h, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(col1_x + col1_w / 2, col1_y + 24, "Критичні підсистеми ОС", size=13, bold=True, color=NEG))
    frags.append(line(col1_x + 10, col1_y + 36, col1_x + col1_w - 10, col1_y + 36, color=NEG, sw=1.0))

    services = [
        ("Пакетні менеджери", "DNF, APT-інструменти, YUM", "#e0e7ff", "#3730a3"),
        ("Мережа та безпека", "firewall-cmd, ufw, fail2ban", "#fee2e2", POS),
        ("Хмарна ініціалізація", "cloud-init, netplan-генератори", "#fef3c7", "#b45309"),
        ("Автентифікація", "authselect, sssd-інструменти", "#d1fae5", FIELD),
        ("Діагностика заліза", "ubuntu-drivers, sosreport", "#f3f4f6", INK),
    ]

    for idx, (s_title, s_desc, fill_c, stroke_c) in enumerate(services):
        sy = col1_y + 50 + idx * 72
        frags.append(rect(col1_x + 12, sy, col1_w - 24, 60, fill=fill_c, stroke=stroke_c, sw=1.2, rx=6))
        frags.append(text(col1_x + col1_w / 2, sy + 22, s_title, size=11, bold=True, color=stroke_c))
        frags.append(text(col1_x + col1_w / 2, sy + 44, s_desc, size=9, color=INK))

    # Центральна частина: Системний інтерпретатор і середовище
    col2_x, col2_y, col2_w, col2_h = 335, 60, 270, 420
    frags.append(rect(col2_x, col2_y, col2_w, col2_h, fill="#eff6ff", stroke=NEG, sw=1.8, rx=8))
    frags.append(text(col2_x + col2_w / 2, col2_y + 24, "Системний інтерпретатор", size=13, bold=True, color=NEG))
    frags.append(line(col2_x + 10, col2_y + 36, col2_x + col2_w - 10, col2_y + 36, color=NEG, sw=1.0))

    py_blocks = [
        ("Бінарний файл CPython", "/usr/bin/python3\n(динамічно лінкований з libc)", "#ffffff", NEG),
        ("Стандартна бібліотека", "/usr/lib/python3.X/\n(os, sys, ssl, ctypes, subprocess)", "#ffffff", INK),
        ("Системні пакунки ОС", "/usr/lib/python3/dist-packages\n(rpm / dpkg керовані файли)", "#ffffff", POS),
        ("Захисний маркер PEP 668", "EXTERNALLY-MANAGED\n(блокує пряме втручання pip)", "#fee2e2", POS),
    ]

    for idx, (b_title, b_desc, fill_c, stroke_c) in enumerate(py_blocks):
        by = col2_y + 50 + idx * 90
        frags.append(rect(col2_x + 12, by, col2_w - 24, 76, fill=fill_c, stroke=stroke_c, sw=1.2, rx=6))
        frags.append(text(col2_x + col2_w / 2, by + 20, b_title, size=11, bold=True, color=stroke_c))
        lines = b_desc.split("\n")
        frags.append(text(col2_x + col2_w / 2, by + 40, lines[0], size=9, color=INK))
        frags.append(text(col2_x + col2_w / 2, by + 56, lines[1], size=9, color=MUTED))

    # Права частина: Системний пакетний менеджер (DPKG/RPM)
    col3_x, col3_y, col3_w, col3_h = 645, 60, 260, 420
    frags.append(rect(col3_x, col3_y, col3_w, col3_h, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(col3_x + col3_w / 2, col3_y + 24, "Менеджер пакунків ОС", size=13, bold=True, color=FIELD))
    frags.append(line(col3_x + 10, col3_y + 36, col3_x + col3_w - 10, col3_y + 36, color=FIELD, sw=1.0))

    pkg_items = [
        ("База цілісності файлів", "dpkg (/var/lib/dpkg/status)\nrpm (/var/lib/rpm/rpmdb.sqlite)", "#ffffff", FIELD),
        ("Контрольні суми та права", "Перевірка md5/sha256\nта власника файлів (root:root)", "#ffffff", INK),
        ("Граф системних залежностей", "Розв'язання через SAT-солвер\n(libsolv / libapt-pkg)", "#ffffff", INK),
        ("Атомарні транзакції", "Оновлення системи без стану\nрозірваних пакетів і модулів", "#ffffff", FIELD),
    ]

    for idx, (p_title, p_desc, fill_c, stroke_c) in enumerate(pkg_items):
        py_box = col3_y + 50 + idx * 90
        frags.append(rect(col3_x + 12, py_box, col3_w - 24, 76, fill=fill_c, stroke=stroke_c, sw=1.2, rx=6))
        frags.append(text(col3_x + col3_w / 2, py_box + 20, p_title, size=11, bold=True, color=stroke_c))
        lines = p_desc.split("\n")
        frags.append(text(col3_x + col3_w / 2, py_box + 40, lines[0], size=9, color=INK))
        frags.append(text(col3_x + col3_w / 2, py_box + 56, lines[1], size=9, color=MUTED))

    # Стрілки між колонками
    frags.append(arrow(col1_x + col1_w, col1_y + 110, col2_x, col2_y + 110, color=NEG, sw=1.8))
    frags.append(arrow(col1_x + col1_w, col1_y + 250, col2_x, col2_y + 250, color=NEG, sw=1.8))
    frags.append(arrow(col3_x, col3_y + 250, col2_x + col2_w, col2_y + 250, color=FIELD, sw=1.8))

    frags.append(text(w / 2, 500, "Системні утиліти спираються на детерміновану версію Python та строгий контроль файлів через DPKG/RPM", size=11, color=MUTED, italic=True))

    path = os.path.join(OUT_DIR, "system-python-ecosystem.svg")
    render(path, w, h, *frags)


def fig_path_shadowing_conflict():
    """Механізм затінення пакетів через пріоритети sys.path."""
    w, h = 940, 480
    frags = []

    frags.append(text(w / 2, 28, "Механізм затінення системних бібліотек (sys.path Shadowing)", size=15, bold=True))

    # Лівий блок: Дія адміністратора
    bx1, by1, bw1, bh1 = 35, 60, 260, 370
    frags.append(rect(bx1, by1, bw1, bh1, fill="#fee2e2", stroke=POS, sw=1.5, rx=8))
    frags.append(text(bx1 + bw1 / 2, by1 + 24, "1. Свавільне встановлення pip", size=12, bold=True, color=POS))
    frags.append(line(bx1 + 10, by1 + 36, bx1 + bw1 - 10, by1 + 36, color=POS, sw=1.0))

    cmd_steps = [
        "Користувач виконує:",
        "sudo pip install requests==2.32",
        "pip розміщує файли у:",
        "/usr/local/lib/python3.X/",
        "dist-packages/requests",
        "Результат:",
        "Нові файли не враховані",
        "в базі dpkg/rpm!"
    ]
    for idx, c_line in enumerate(cmd_steps):
        is_cmd = (idx == 1 or idx == 3 or idx == 4)
        c_size = 10 if is_cmd else 10
        c_bold = is_cmd
        c_col = POS if is_cmd else INK
        frags.append(text(bx1 + 14, by1 + 65 + idx * 34, c_line, size=c_size, bold=c_bold, color=c_col, anchor="start"))

    # Центральний блок: Порядок обходу sys.path
    bx2, by2, bw2, bh2 = 330, 60, 280, 370
    frags.append(rect(bx2, by2, bw2, bh2, fill="#eff6ff", stroke=NEG, sw=1.8, rx=8))
    frags.append(text(bx2 + bw2 / 2, by2 + 24, "2. Пріоритет пошуку у sys.path", size=12, bold=True, color=NEG))
    frags.append(line(bx2 + 10, by2 + 36, bx2 + bw2 - 10, by2 + 36, color=NEG, sw=1.0))

    path_items = [
        ("[1] Поточний каталог / скрипт", "Локальний каталог (якщо не -P)", "#ffffff", INK),
        ("[2] /usr/local/lib/.../dist-packages", "Знайдено requests 2.32 (pip) -> СТОП", "#fee2e2", POS),
        ("[3] /usr/lib/python3/dist-packages", "requests 2.25 (ОС) ЗАТІНЕНО!", "#f3f4f6", MUTED),
        ("[4] /usr/lib/python3.X (stdlib)", "Стандартна бібліотека CPython", "#ffffff", INK),
    ]

    for idx, (p_head, p_sub, f_col, s_col) in enumerate(path_items):
        py_box = by2 + 50 + idx * 76
        frags.append(rect(bx2 + 10, py_box, bw2 - 20, 64, fill=f_col, stroke=s_col, sw=1.4, rx=6))
        frags.append(text(bx2 + 20, py_box + 24, p_head, size=10, bold=True, color=s_col, anchor="start"))
        frags.append(text(bx2 + 20, py_box + 46, p_sub, size=9, color=INK if s_col == POS else MUTED, anchor="start"))

    # Правий блок: Наслідки для системи
    bx3, by3, bw3, bh3 = 645, 60, 260, 370
    frags.append(rect(bx3, by3, bw3, bh3, fill="#fef2f2", stroke=POS, sw=1.5, rx=8))
    frags.append(text(bx3 + bw3 / 2, by3 + 24, "3. Фатальний крах утиліт ОС", size=12, bold=True, color=POS))
    frags.append(line(bx3 + 10, by3 + 36, bx3 + bw3 - 10, by3 + 36, color=POS, sw=1.0))

    crash_steps = [
        "1. Запуск системного DNF/APT",
        "2. Імпорт urllib3 і requests",
        "3. Завантаження несумісних версій:",
        "   urllib3 (із /usr/lib) +",
        "   requests (із /usr/local)",
        "4. AttributeError / ImportError:",
        "   urllib3.exceptions не знайдено",
        "5. Повна зупинка оновлень ОС!"
    ]
    for idx, cr_line in enumerate(crash_steps):
        is_err = (idx >= 5)
        frags.append(text(bx3 + 14, by3 + 65 + idx * 34, cr_line, size=9, bold=is_err, color=POS if is_err else INK, anchor="start"))

    # Стрілки
    frags.append(arrow(bx1 + bw1, by1 + 150, bx2, by2 + 150, color=POS, sw=1.8))
    frags.append(arrow(bx2 + bw2, by2 + 150, bx3, by3 + 150, color=POS, sw=1.8))

    frags.append(text(w / 2, 455, "Пакет із /usr/local завантажується першим і несумісний зі старими системними залежностями з /usr/lib", size=11, color=POS, bold=True))

    path = os.path.join(OUT_DIR, "path-shadowing-conflict.svg")
    render(path, w, h, *frags)


def fig_pep668_decision_flow():
    """Алгоритм перевірки PEP 668 клієнтом pip."""
    w, h = 920, 520
    frags = []

    frags.append(text(w / 2, 28, "Алгоритм захисту PEP 668 під час запуску pip install", size=15, bold=True))

    # Крок 1: Вхід
    k1_x, k1_y, k1_w, k1_h = 340, 60, 240, 48
    frags.append(rect(k1_x, k1_y, k1_w, k1_h, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(k1_x + k1_w / 2, k1_y + 29, "Виклик pip install <пакунок>", size=11, bold=True, color=NEG))

    frags.append(arrow(k1_x + k1_w / 2, k1_y + k1_h, k1_x + k1_w / 2, 140, color=LINE, sw=1.5))

    # Крок 2: Перевірка віртуального середовища
    k2_x, k2_y, k2_w, k2_h = 290, 140, 340, 60
    frags.append(rect(k2_x, k2_y, k2_w, k2_h, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(k2_x + k2_w / 2, k2_y + 24, "Чи активне віртуальне середовище?", size=11, bold=True))
    frags.append(text(k2_x + k2_w / 2, k2_y + 44, "sys.prefix != sys.base_prefix або pyvenv.cfg", size=9, color=MUTED))

    # Гілка ТАК (у venv)
    frags.append(arrow(k2_x + k2_w, k2_y + 30, 750, k2_y + 30, color=FIELD, sw=1.6))
    frags.append(text(680, k2_y + 20, "ТАК (venv)", size=10, bold=True, color=FIELD))

    v_box_x, v_box_y, v_box_w, v_box_h = 750, 120, 140, 100
    frags.append(rect(v_box_x, v_box_y, v_box_w, v_box_h, fill="#d1fae5", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(v_box_x + v_box_w / 2, v_box_y + 35, "БЕЗПЕЧНО", size=12, bold=True, color=FIELD))
    frags.append(text(v_box_x + v_box_w / 2, v_box_y + 60, "Встановлення у", size=9, color=INK))
    frags.append(text(v_box_x + v_box_w / 2, v_box_y + 78, "ізольований venv", size=9, color=INK))

    # Гілка НІ (системний Python)
    frags.append(arrow(k2_x + k2_w / 2, k2_y + k2_h, k2_x + k2_w / 2, 240, color=LINE, sw=1.5))
    frags.append(text(k2_x + k2_w / 2 + 25, 220, "НІ", size=10, bold=True, color=POS))

    # Крок 3: Пошук EXTERNALLY-MANAGED
    k3_x, k3_y, k3_w, k3_h = 280, 240, 360, 60
    frags.append(rect(k3_x, k3_y, k3_w, k3_h, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(k3_x + k3_w / 2, k3_y + 24, "Чи є файл EXTERNALLY-MANAGED?", size=11, bold=True))
    frags.append(text(k3_x + k3_w / 2, k3_y + 44, "у каталозі sysconfig (stdlib / platstdlib)", size=9, color=MUTED))

    # Гілка НІ (старий або некерований дистрибутив)
    leg_x, leg_y, leg_w, leg_h = 25, 210, 160, 110
    frags.append(arrow(k3_x, k3_y + 30, leg_x + leg_w + 4, k3_y + 30, color=MUTED, sw=1.5))
    frags.append(text((k3_x + leg_x + leg_w) / 2, k3_y + 20, "НІ (немає)", size=9, bold=True, color=MUTED))

    frags.append(rect(leg_x, leg_y, leg_w, leg_h, fill="#fef3c7", stroke="#b45309", sw=1.4, rx=6))
    frags.append(text(leg_x + leg_w / 2, leg_y + 30, "Застаріла поведінка", size=10, bold=True, color="#b45309"))
    frags.append(text(leg_x + leg_w / 2, leg_y + 55, "Прямий запис у", size=9, color=INK))
    frags.append(text(leg_x + leg_w / 2, leg_y + 73, "site-packages (ризик)", size=9, color=POS))
    frags.append(text(leg_x + leg_w / 2, leg_y + 92, "Legacy Linux / Windows", size=9, color=MUTED))

    # Гілка ТАК (є маркер PEP 668)
    frags.append(arrow(k3_x + k3_w / 2, k3_y + k3_h, k3_x + k3_w / 2, 340, color=POS, sw=1.5))
    frags.append(text(k3_x + k3_w / 2 + 25, 320, "ТАК", size=10, bold=True, color=POS))

    # Крок 4: Перевірка прапорця аварійного обходу
    k4_x, k4_y, k4_w, k4_h = 270, 340, 380, 60
    frags.append(rect(k4_x, k4_y, k4_w, k4_h, fill="#fff1f2", stroke=POS, sw=1.5, rx=6))
    frags.append(text(k4_x + k4_w / 2, k4_y + 24, "Перевірка прапорця примусового обходу", size=11, bold=True, color=POS))
    frags.append(text(k4_x + k4_w / 2, k4_y + 44, "--break-system-packages або PIP_BREAK_SYSTEM_PACKAGES", size=9, color=INK))

    # Гілка НІ (Блокування!)
    frags.append(arrow(k4_x + k4_w / 2, k4_y + k4_h, k4_x + k4_w / 2, 430, color=POS, sw=1.8))
    frags.append(text(k4_x + k4_w / 2 + 25, 415, "НІ", size=10, bold=True, color=POS))

    err_x, err_y, err_w, err_h = 240, 430, 440, 60
    frags.append(rect(err_x, err_y, err_w, err_h, fill="#fee2e2", stroke=POS, sw=2.0, rx=6))
    frags.append(text(err_x + err_w / 2, err_y + 24, "ПОМИЛКА: externally-managed-environment", size=11, bold=True, color=POS))
    frags.append(text(err_x + err_w / 2, err_y + 44, "pip припиняє роботу й виводить інструкцію дистрибутива", size=9, color=INK))

    # Гілка ТАК (Примусовий запис)
    frags.append(arrow(k4_x + k4_w, k4_y + 30, 746, k4_y + 30, color=POS, sw=1.6))
    frags.append(text(690, k4_y + 20, "ТАК", size=10, bold=True, color=POS))

    brk_x, brk_y, brk_w, brk_h = 750, 320, 140, 95
    frags.append(rect(brk_x, brk_y, brk_w, brk_h, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    frags.append(text(brk_x + brk_w / 2, brk_y + 25, "НЕБЕЗПЕЧНО", size=11, bold=True, color=POS))
    frags.append(text(brk_x + brk_w / 2, brk_y + 48, "Прямий перезапис", size=9, color=INK))
    frags.append(text(brk_x + brk_w / 2, brk_y + 66, "системних модулів", size=9, color=INK))
    frags.append(text(brk_x + brk_w / 2, brk_y + 84, "(лише для CI/Docker)", size=9, color=MUTED))

    path = os.path.join(OUT_DIR, "pep668-decision-flow.svg")
    render(path, w, h, *frags)


def fig_isolation_architectures():
    """Чотири моделі ізоляції середовищ Python."""
    w, h = 960, 460
    frags = []

    frags.append(text(w / 2, 28, "Чотири архітектурні моделі ізоляції середовищ Python", size=15, bold=True))

    cards = [
        {
            "title": "1. Віртуальне середовище (venv)",
            "sub": "Ізоляція проєкту",
            "bullets": [
                "Каталог .venv у проєкті",
                "Симлінк на системний python3",
                "pyvenv.cfg перемикає prefix",
                "Власний каталог site-packages",
                "Ідеально: для коду та тестів"
            ],
            "fill": "#eff6ff",
            "stroke": NEG
        },
        {
            "title": "2. Ізоляція утиліт (pipx)",
            "sub": "Ізоляція CLI-інструментів",
            "bullets": [
                "Окремий venv на кожен CLI-пакунок",
                "Збереження у ~/.local/pipx/venvs/",
                "Симлінки команд у ~/.local/bin/",
                "Жодних перехресних конфліктів",
                "Ідеально: black, flake8, ansible"
            ],
            "fill": "#f0fdf4",
            "stroke": FIELD
        },
        {
            "title": "3. Незалежні рантайми (uv / pyenv)",
            "sub": "Ізоляція версій інтерпретатора",
            "bullets": [
                "CPython збирається / качається в home",
                "Шляхи ~/.local/share/uv/python/",
                "Повна незалежність від /usr/bin",
                "Будь-які версії (3.10, 3.12, 3.13t)",
                "Ідеально: версіонування розробки"
            ],
            "fill": "#fef9e7",
            "stroke": "#b45309"
        },
        {
            "title": "4. OCI-контейнери (Docker / Podman)",
            "sub": "Повна ізоляція операційної системи",
            "bullets": [
                "Власна файлова система rootfs",
                "Ізоляція процесів (namespaces)",
                "Окремий менеджер пакунків",
                "Дозволено --break-system-packages",
                "Ідеально: продакшн і мікросервіси"
            ],
            "fill": "#fdf2f8",
            "stroke": "#9d174d"
        }
    ]

    card_w = 210
    card_h = 360
    x_gap = 20
    start_x = 30
    card_y = 60

    for i, c in enumerate(cards):
        cx = start_x + i * (card_w + x_gap)
        cy = card_y

        frags.append(rect(cx, cy, card_w, card_h, fill=c["fill"], stroke=c["stroke"], sw=1.6, rx=8))
        frags.append(text(cx + card_w / 2, cy + 24, c["title"][:24], size=10, bold=True, color=c["stroke"]))
        if len(c["title"]) > 24:
            frags.append(text(cx + card_w / 2, cy + 40, c["title"][24:], size=10, bold=True, color=c["stroke"]))
            line_y = cy + 50
        else:
            line_y = cy + 36

        frags.append(line(cx + 8, line_y, cx + card_w - 8, line_y, color=c["stroke"], sw=1.0))
        frags.append(text(cx + card_w / 2, line_y + 18, c["sub"], size=9, bold=True, color=MUTED))

        for b_idx, bullet in enumerate(c["bullets"]):
            by = line_y + 44 + b_idx * 48
            frags.append(text(cx + 10, by, "• " + bullet[:24], size=9, anchor="start", color=INK))
            if len(bullet) > 24:
                frags.append(text(cx + 18, by + 16, bullet[24:], size=9, anchor="start", color=INK))

    frags.append(text(w / 2, 442, "Вибір стратегії ізоляції залежить від рівня абстракції: від окремого скрипту до повного образу ОС", size=11, color=MUTED, italic=True))

    path = os.path.join(OUT_DIR, "isolation-architectures.svg")
    render(path, w, h, *frags)


if __name__ == "__main__":
    fig_system_python_ecosystem()
    fig_path_shadowing_conflict()
    fig_pep668_decision_flow()
    fig_isolation_architectures()
    print("All figures generated successfully.")
