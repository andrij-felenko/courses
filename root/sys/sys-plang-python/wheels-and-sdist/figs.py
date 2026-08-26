# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми 'sdist, wheel і бінарні колеса'."""

import os
import sys

# Шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, text, mtext, rect, line, arrow, circle, textbox, fitbox,
    INK, MUTED, LINE, FILL, BG, POS, NEG, FIELD, FONT
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_sdist_vs_wheel():
    """Порівняння життєвого циклу встановлення sdist та wheel."""
    w, h = 980, 520
    frags = []

    frags.append(text(w / 2, 28, "Порівняння розгортання пакунка: вихідний архів (sdist) проти wheel (.whl)", size=15, bold=True))

    col_w = 430
    col_h = 440
    y_top = 55
    x_sdist = 40
    x_wheel = 510

    # Колонка 1: sdist
    frags.append(rect(x_sdist, y_top, col_w, col_h, fill="#fff8f6", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(x_sdist + col_w / 2, y_top + 26, "Source Distribution (.tar.gz / sdist)", size=13, bold=True, color=NEG))
    frags.append(line(x_sdist + 15, y_top + 38, x_sdist + col_w - 15, y_top + 38, color=NEG, sw=1.0))

    sdist_steps = [
        ("1. Завантаження архіву", "pip викачує вихідний код і pyproject.toml з PyPI", "#ffffff", NEG),
        ("2. Ізоляція середовища збирання", "Створення тимчасового venv і встановлення build-backend", "#ffffff", NEG),
        ("3. Виклик C/C++ компілятора", "Компіляція .c/.cpp -> потрібні Python.h, gcc/clang, make/cmake", "#fdecea", NEG),
        ("4. Компонування модуля розширення", "Лінкування .so/.pyd з системними бібліотеками клієнта", "#fdecea", NEG),
        ("5. Генерація колісного архіву й копіювання", "Упакування у тимчасовий .whl та розпакування в site-packages", "#ffffff", NEG),
    ]

    box_h = 62
    for i, (stitle, sdesc, sfill, scolor) in enumerate(sdist_steps):
        bx = x_sdist + 20
        by = y_top + 52 + i * 76
        frags.append(rect(bx, by, col_w - 40, box_h, fill=sfill, stroke=scolor, sw=1.2, rx=6))
        frags.append(text(bx + 12, by + 20, stitle, size=11, bold=True, color=scolor, anchor="start"))
        frags.append(text(bx + 12, by + 42, sdesc, size=10, color=INK, anchor="start"))
        if i < len(sdist_steps) - 1:
            frags.append(arrow(bx + (col_w - 40) / 2, by + box_h + 1, bx + (col_w - 40) / 2, by + box_h + 12, color=NEG, sw=1.5))

    # Колонка 2: wheel
    frags.append(rect(x_wheel, y_top, col_w, col_h, fill="#f4faf6", stroke=POS, sw=1.5, rx=8))
    frags.append(text(x_wheel + col_w / 2, y_top + 26, "Built Distribution (.whl / PEP 427)", size=13, bold=True, color=POS))
    frags.append(line(x_wheel + 15, y_top + 38, x_wheel + col_w - 15, y_top + 38, color=POS, sw=1.0))

    wheel_steps = [
        ("1. Перевірка тегів сумісності", "pip звіряє cp312-abi3-manylinux_2_28_x86_64 з середовищем", "#ffffff", POS),
        ("2. Завантаження готового wheel", "Викачування попередньо скомпільованого zip-архіву з PyPI", "#ffffff", POS),
        ("3. Пряме розпакування файлів", "Атомарне копіювання .py, .so та .dist-info прямо в site-packages", "#e8f8f0", POS),
        ("4. Валідація контрольних сум", "Звірка хешів SHA-256 файлів із записами у файлі RECORD", "#e8f8f0", POS),
        ("5. Готовність до імпорту (0 с компіляції)", "Модуль миттєво доступний інтерпретатору без компілятора", "#ffffff", POS),
    ]

    for i, (wtitle, wdesc, wfill, wcolor) in enumerate(wheel_steps):
        bx = x_wheel + 20
        by = y_top + 52 + i * 76
        frags.append(rect(bx, by, col_w - 40, box_h, fill=wfill, stroke=wcolor, sw=1.2, rx=6))
        frags.append(text(bx + 12, by + 20, wtitle, size=11, bold=True, color=wcolor, anchor="start"))
        frags.append(text(bx + 12, by + 42, wdesc, size=10, color=INK, anchor="start"))
        if i < len(wheel_steps) - 1:
            frags.append(arrow(bx + (col_w - 40) / 2, by + box_h + 1, bx + (col_w - 40) / 2, by + box_h + 12, color=POS, sw=1.5))

    render(os.path.join(OUT_DIR, "sdist-vs-wheel.svg"), w, h, *frags)


def fig_wheel_structure():
    """Внутрішня анатомія архіву .whl за стандартом PEP 427."""
    w, h = 980, 520
    frags = []

    frags.append(text(w / 2, 28, "Анатомія wheel-пакета (ZIP-архів із розширенням .whl)", size=15, bold=True))

    # Зовнішній контейнер
    frags.append(rect(40, 50, 900, 445, fill="#fcfcfd", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(65, 75, "example_pkg-1.2.0-cp312-cp312-manylinux_2_28_x86_64.whl (ZIP Container)", size=12, bold=True, color=INK, anchor="start"))

    # Блок 1: Корисне навантаження пакунка
    frags.append(rect(65, 95, 410, 380, fill="#f8fafc", stroke=FIELD, sw=1.3, rx=6))
    frags.append(text(270, 120, "Корисне навантаження (Package Payload)", size=12, bold=True, color=FIELD))
    frags.append(line(80, 132, 460, 132, color=FIELD, sw=0.8))

    payload_items = [
        ("example_pkg/", "Основний каталог Python-пакета", "#e2e8f0"),
        ("├── __init__.py", "Точка входу пакета з публічним API", "#ffffff"),
        ("├── core.py", "Високорівнева обгортка та логіка", "#ffffff"),
        ("└── _native.so", "Скомпільоване C-розширення (shared object)", "#eaf0fd"),
        ("example_pkg.libs/", "Каталог ізольованих динамічних бібліотек", "#fef9e7"),
        ("└── libbundled.so.1", "Vendored .so з унікальним soname", "#ffffff"),
    ]

    for i, (fname, fdesc, fbg) in enumerate(payload_items):
        py = 145 + i * 53
        frags.append(rect(80, py, 380, 44, fill=fbg, stroke="#cbd5e1", sw=1.0, rx=4))
        frags.append(text(92, py + 18, fname, size=10.5, bold=True, color=INK, anchor="start"))
        frags.append(text(92, py + 34, fdesc, size=9.5, color=MUTED, anchor="start"))

    # Блок 2: Службовий каталог .dist-info
    frags.append(rect(505, 95, 410, 380, fill="#f8fafc", stroke=POS, sw=1.3, rx=6))
    frags.append(text(710, 120, "Метадані інсталяції (.dist-info/)", size=12, bold=True, color=POS))
    frags.append(line(520, 132, 900, 132, color=POS, sw=0.8))

    meta_items = [
        ("METADATA (PEP 566 / PEP 643)", "Metadata-Version: 2.1 | Name: example_pkg | Version: 1.2.0", "Requires-Dist: numpy>=1.24"),
        ("WHEEL (PEP 427)", "Wheel-Version: 1.0 | Generator: hatchling | Root-Is-Purelib: false", "Tag: cp312-cp312-manylinux_2_28_x86_64"),
        ("RECORD (PEP 376 / PEP 627)", "example_pkg/core.py,sha256=47DEQpj8...,1240", "example_pkg-1.2.0.dist-info/RECORD,,"),
        ("entry_points.txt (PEP 517)", "[console_scripts]", "example-cli = example_pkg.core:main"),
    ]

    for i, (mtitle, mline1, mline2) in enumerate(meta_items):
        my = 145 + i * 80
        frags.append(rect(520, my, 380, 70, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
        frags.append(text(532, my + 18, mtitle, size=10.5, bold=True, color=POS, anchor="start"))
        frags.append(text(532, my + 36, mline1, size=9.5, color=INK, anchor="start"))
        frags.append(text(532, my + 52, mline2, size=9.5, color=INK, anchor="start"))

    render(os.path.join(OUT_DIR, "wheel-structure.svg"), w, h, *frags)


def fig_manylinux_auditwheel():
    """Схема ізоляції бібліотек через auditwheel, RPATH та $ORIGIN."""
    w, h = 980, 520
    frags = []

    frags.append(text(w / 2, 28, "Трансформація двійкового модуля інструментом auditwheel (manylinux)", size=15, bold=True))

    box_w = 260
    box_h = 410
    y_b = 55

    # Крок 1: Початковий стан
    bx1 = 40
    frags.append(rect(bx1, y_b, box_w, box_h, fill="#fff8f6", stroke=NEG, sw=1.4, rx=8))
    frags.append(text(bx1 + box_w / 2, y_b + 24, "1. Зібраний C-модуль", size=12, bold=True, color=NEG))
    frags.append(line(bx1 + 15, y_b + 36, bx1 + box_w - 15, y_b + 36, color=NEG, sw=0.8))

    frags.append(rect(bx1 + 15, y_b + 48, box_w - 30, 85, fill="#ffffff", stroke="#fca5a5", sw=1, rx=4))
    frags.append(text(bx1 + 25, y_b + 68, "_extension.so", size=11, bold=True, color=INK, anchor="start"))
    frags.append(text(bx1 + 25, y_b + 88, "DT_NEEDED: libdata.so.2", size=9.5, color=NEG, anchor="start"))
    frags.append(text(bx1 + 25, y_b + 108, "DT_RUNPATH: порожній", size=9.5, color=MUTED, anchor="start"))

    frags.append(rect(bx1 + 15, y_b + 145, box_w - 30, 115, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(bx1 + 25, y_b + 165, "Системні шляхи хоста:", size=10, bold=True, color=INK, anchor="start"))
    frags.append(text(bx1 + 25, y_b + 185, "/usr/lib/libdata.so.2", size=9.5, color=NEG, anchor="start"))
    frags.append(text(bx1 + 25, y_b + 205, "/lib64/libc.so.6 (glibc)", size=9.5, color=MUTED, anchor="start"))
    frags.append(text(bx1 + 25, y_b + 225, "Збій на чужих Linux!", size=9.5, color=NEG, anchor="start"))

    frags.append(rect(bx1 + 15, y_b + 272, box_w - 30, 115, fill="#fef2f2", stroke="#f87171", sw=1, rx=4))
    frags.append(text(bx1 + 25, y_b + 295, "Проблема:", size=10.5, bold=True, color=NEG, anchor="start"))
    frags.append(text(bx1 + 25, y_b + 318, "На машині клієнта немає", size=9.5, color=INK, anchor="start"))
    frags.append(text(bx1 + 25, y_b + 338, "libdata.so.2 або версія", size=9.5, color=INK, anchor="start"))
    frags.append(text(bx1 + 25, y_b + 358, "glibc старіша за збірку.", size=9.5, color=INK, anchor="start"))

    # Стрілка 1 -> 2
    frags.append(arrow(bx1 + box_w + 5, y_b + box_h / 2, bx1 + box_w + 35, y_b + box_h / 2, color=LINE, sw=2))

    # Крок 2: Дія auditwheel
    bx2 = 360
    frags.append(rect(bx2, y_b, box_w, box_h, fill="#fefce8", stroke="#ca8a04", sw=1.4, rx=8))
    frags.append(text(bx2 + box_w / 2, y_b + 24, "2. Аудит і патчинг", size=12, bold=True, color="#ca8a04"))
    frags.append(line(bx2 + 15, y_b + 36, bx2 + box_w - 15, y_b + 36, color="#ca8a04", sw=0.8))

    audit_steps = [
        ("Аналіз символів ELF", "Звірка версій GLIBC_X.Y за білим списком manylinux"),
        ("Копіювання бібліотек", "Пошук libdata.so.2 та копіювання у pkg.libs/"),
        ("Унікалізація soname", "libdata.so.2 -> libdata-9f3a12.so.2"),
        ("Патчинг patchelf", "DT_RUNPATH = $ORIGIN/../pkg.libs"),
    ]

    for i, (atitle, adesc) in enumerate(audit_steps):
        ay = y_b + 48 + i * 85
        frags.append(rect(bx2 + 15, ay, box_w - 30, 75, fill="#ffffff", stroke="#fde047", sw=1, rx=4))
        frags.append(text(bx2 + 25, ay + 20, atitle, size=10.5, bold=True, color="#854d0e", anchor="start"))
        frags.append(text(bx2 + 25, ay + 40, adesc[:28], size=9.5, color=INK, anchor="start"))
        if len(adesc) > 28:
            frags.append(text(bx2 + 25, ay + 56, adesc[28:].strip(), size=9.5, color=INK, anchor="start"))

    # Стрілка 2 -> 3
    frags.append(arrow(bx2 + box_w + 5, y_b + box_h / 2, bx2 + box_w + 35, y_b + box_h / 2, color=LINE, sw=2))

    # Крок 3: Результат у Wheel
    bx3 = 680
    frags.append(rect(bx3, y_b, box_w, box_h, fill="#f0fdf4", stroke=POS, sw=1.4, rx=8))
    frags.append(text(bx3 + box_w / 2, y_b + 24, "3. Автономний manylinux", size=12, bold=True, color=POS))
    frags.append(line(bx3 + 15, y_b + 36, bx3 + box_w - 15, y_b + 36, color=POS, sw=0.8))

    frags.append(rect(bx3 + 15, y_b + 48, box_w - 30, 95, fill="#ffffff", stroke="#86efac", sw=1, rx=4))
    frags.append(text(bx3 + 25, y_b + 68, "_extension.so", size=11, bold=True, color=INK, anchor="start"))
    frags.append(text(bx3 + 25, y_b + 88, "DT_NEEDED: libdata-9f.so.2", size=9.5, color=POS, anchor="start"))
    frags.append(text(bx3 + 25, y_b + 108, "DT_RUNPATH: $ORIGIN/../libs", size=9.5, color=POS, anchor="start"))
    frags.append(text(bx3 + 25, y_b + 128, "Завантажувач шукає поруч", size=9.5, color=MUTED, anchor="start"))

    frags.append(rect(bx3 + 15, y_b + 155, box_w - 30, 95, fill="#ffffff", stroke="#86efac", sw=1, rx=4))
    frags.append(text(bx3 + 25, y_b + 175, "pkg.libs/ (ізольовані .so)", size=10, bold=True, color=INK, anchor="start"))
    frags.append(text(bx3 + 25, y_b + 195, "└── libdata-9f3a12.so.2", size=9.5, color=POS, anchor="start"))
    frags.append(text(bx3 + 25, y_b + 215, "Повна ізоляція від хоста", size=9.5, color=MUTED, anchor="start"))
    frags.append(text(bx3 + 25, y_b + 233, "й інших пакетів Python.", size=9.5, color=MUTED, anchor="start"))

    frags.append(rect(bx3 + 15, y_b + 265, box_w - 30, 125, fill="#dcfce7", stroke="#4ade80", sw=1, rx=4))
    frags.append(text(bx3 + 25, y_b + 290, "Результат:", size=10.5, bold=True, color=POS, anchor="start"))
    frags.append(text(bx3 + 25, y_b + 312, "Wheel працює на будь-якій", size=9.5, color=INK, anchor="start"))
    frags.append(text(bx3 + 25, y_b + 332, "системі Linux із сумісною", size=9.5, color=INK, anchor="start"))
    frags.append(text(bx3 + 25, y_b + 352, "версією glibc без збоїв.", size=9.5, color=INK, anchor="start"))

    render(os.path.join(OUT_DIR, "manylinux-auditwheel.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_sdist_vs_wheel()
    fig_wheel_structure()
    fig_manylinux_auditwheel()
    print("All figures generated successfully.")
