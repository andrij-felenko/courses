#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор діаграм для теми pip-install (pip і джерела пакетів)."""

import os
import sys

# Шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, textbox, fitbox, text, mtext, rect, line, arrow, circle,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG, FONT
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_pip_architecture():
    """Повна архітектура конвеєра pip від CLI-запиту до запису dist-info."""
    w, h = 920, 480
    frags = []

    # Заголовок / шапка
    frags.append(text(w / 2, 28, "Архітектурний конвеєр менеджера пакетів pip", size=16, bold=True))

    # Стовпець 1: Вхідні дані та джерела (x: 20..220)
    frags.append(rect(20, 50, 200, 400, fill="#f8fafc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(120, 75, "1. Вхід та Індекси", size=13, bold=True, color=INK))

    b1, _, _ = textbox(120, 120, "CLI / requirements.txt\n--index-url / pip.conf", size=11, fill="#ffffff", stroke=LINE, min_w=170)
    frags.append(b1)

    b2, _, _ = textbox(120, 210, "PEP 503 / 691 Index\nPyPI / Artifactory / devpi\nHTML / JSON API", size=11, fill="#ffffff", stroke=NEG, min_w=170)
    frags.append(b2)

    b3, _, _ = textbox(120, 310, "Локальні джерела\n--find-links <dir|url>\nDirect URL / Wheels", size=11, fill="#ffffff", stroke=LINE, min_w=170)
    frags.append(b3)

    b4, _, _ = textbox(120, 400, "HTTP Response Cache\nhttp-v2 / Wheels Cache\nETag / 304 Not Modified", size=11, fill="#ffffff", stroke=MUTED, min_w=170)
    frags.append(b4)

    # Стрілки від 1 до 2
    frags.append(arrow(205, 120, 250, 120, color=LINE, sw=1.5))
    frags.append(arrow(205, 210, 250, 210, color=LINE, sw=1.5))
    frags.append(arrow(205, 310, 250, 240, color=LINE, sw=1.5))

    # Стовпець 2: Розв'язання залежностей (x: 250..470)
    frags.append(rect(250, 50, 210, 400, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=8))
    frags.append(text(355, 75, "2. Dependency Resolver", size=13, bold=True, color=FIELD))

    r1, _, _ = textbox(355, 125, "resolvelib Engine\nПокроковий генератор\nкандидатів версій", size=11, fill="#ffffff", stroke=FIELD, min_w=180)
    frags.append(r1)

    r2, _, _ = textbox(355, 220, "Backtracking Search\nПеревірка обмежень\nта відкат при конфлікті", size=11, fill="#ffffff", stroke=FIELD, min_w=180)
    frags.append(r2)

    r3, _, _ = textbox(355, 315, "Оцінка метаданих\nPEP 508 Environment\nMarkers (sys_platform)", size=11, fill="#ffffff", stroke=LINE, min_w=180)
    frags.append(r3)

    r4, _, _ = textbox(355, 405, "Фінальний граф\nВсі версії узгоджені\nбез колізій", size=11, fill="#ffffff", stroke=FIELD, bold=True, min_w=180)
    frags.append(r4)

    frags.append(arrow(355, 160, 355, 185, color=FIELD, sw=1.5))
    frags.append(arrow(355, 255, 355, 280, color=FIELD, sw=1.5))
    frags.append(arrow(355, 350, 355, 375, color=FIELD, sw=1.5))

    # Стрілка від 2 до 3
    frags.append(arrow(460, 405, 500, 250, color=LINE, sw=1.8))

    # Стовпець 3: Завантаження та Верифікація (x: 500..690)
    frags.append(rect(500, 50, 190, 400, fill="#fefce8", stroke="#ca8a04", sw=1.2, rx=8))
    frags.append(text(595, 75, "3. Завантаження й Хеші", size=13, bold=True, color="#854d0e"))

    d1, _, _ = textbox(595, 130, "Download Artifacts\n.whl або .tar.gz (sdist)\nПотокове зчитування", size=11, fill="#ffffff", stroke="#ca8a04", min_w=165)
    frags.append(d1)

    d2, _, _ = textbox(595, 240, "Hash-checking Mode\n--require-hashes\nSHA256 хеш-сума", size=11, fill="#ffffff", stroke=POS, bold=True, min_w=165)
    frags.append(d2)

    d3, _, _ = textbox(595, 360, "Перевірка цілісності\nКриптографічний захист\nвід підміни файлів", size=11, fill="#ffffff", stroke=LINE, min_w=165)
    frags.append(d3)

    frags.append(arrow(595, 170, 595, 205, color="#ca8a04", sw=1.5))
    frags.append(arrow(595, 280, 595, 325, color=POS, sw=1.5))

    # Стрілка від 3 до 4
    frags.append(arrow(690, 240, 720, 240, color=LINE, sw=1.8))

    # Стовпець 4: Збирання та Інсталяція (x: 720..900)
    frags.append(rect(720, 50, 180, 400, fill="#eff6ff", stroke=NEG, sw=1.2, rx=8))
    frags.append(text(810, 75, "4. Інсталяція", size=13, bold=True, color=NEG))

    i1, _, _ = textbox(810, 130, "PEP 517/518 Build\nІзольований venv\nЗбирання sdist -> wheel", size=11, fill="#ffffff", stroke=NEG, min_w=155)
    frags.append(i1)

    i2, _, _ = textbox(810, 240, "Розпакування Wheel\nЗапис у site-packages\nГенерація скриптів bin/", size=11, fill="#ffffff", stroke=NEG, min_w=155)
    frags.append(i2)

    i3, _, _ = textbox(810, 365, "dist-info Метадані\nRECORD / METADATA\nINSTALLER / direct_url", size=11, fill="#ffffff", stroke=LINE, min_w=155)
    frags.append(i3)

    frags.append(arrow(810, 170, 810, 205, color=NEG, sw=1.5))
    frags.append(arrow(810, 280, 810, 330, color=NEG, sw=1.5))

    render(os.path.join(OUT_DIR, "pip-architecture.svg"), w, h, *frags)


def fig_dependency_confusion():
    """Механізм атаки Dependency Confusion через --extra-index-url."""
    w, h = 880, 420
    frags = []

    frags.append(text(w / 2, 28, "Вектор атаки Dependency Confusion через --extra-index-url", size=16, bold=True))

    # Блок клієнта pip
    c_box, _, _ = textbox(140, 190, "Клієнт pip\npip install internal-pkg\n--extra-index-url <private>", size=12, fill="#f8fafc", stroke=LINE, bold=True, min_w=200)
    frags.append(c_box)

    # Паралельні запити
    frags.append(arrow(240, 160, 400, 110, color=LINE, sw=1.8))
    frags.append(arrow(240, 220, 400, 270, color=LINE, sw=1.8))

    frags.append(text(315, 120, "Запит 1 (Private)", size=11, color=FIELD, bold=True))
    frags.append(text(315, 275, "Запит 2 (PyPI)", size=11, color=POS, bold=True))

    # Приватний індекс
    p_box, _, _ = textbox(530, 110, "Корпоративний індекс\n(Artifactory / Nexus / devpi)\ninternal-pkg == 1.2.0\nЛегітимний приватний код", size=11, fill="#f0fdf4", stroke=FIELD, min_w=230)
    frags.append(p_box)

    # Публічний PyPI
    pub_box, _, _ = textbox(530, 270, "Публічний індекс PyPI\n(Зловмисник завантажив назву)\ninternal-pkg == 99.0.0\nШкідливий корисний вантаж", size=11, fill="#fef2f2", stroke=POS, min_w=230)
    frags.append(pub_box)

    # Стрілки вибору версії
    frags.append(arrow(650, 110, 740, 170, color=MUTED, sw=1.2))
    frags.append(arrow(650, 270, 740, 210, color=POS, sw=2.0))

    # Блок рішення pip
    dec_box, _, _ = textbox(790, 190, "Вибір версії pip\n99.0.0 > 1.2.0\n(Найвища версія)\nКомпрометація хоста!", size=11, fill="#fee2e2", stroke=POS, bold=True, min_w=150)
    frags.append(dec_box)

    # Попереджувальна плашка внизу
    warn_rect = rect(40, 350, 800, 50, fill="#fffbeb", stroke="#d97706", sw=1.2, rx=6)
    frags.append(warn_rect)
    frags.append(text(440, 372, "Захист: єдиний проксі-індекс (--index-url) з пріоритетом приватних просторів імен", size=12, bold=True, color="#92400e"))
    frags.append(text(440, 390, "або реєстрація зарезервованих назв у публічному PyPI та хеш-піннінг (--require-hashes)", size=11, color="#b45309"))

    render(os.path.join(OUT_DIR, "dependency-confusion-attack.svg"), w, h, *frags)


def fig_wheel_vs_sdist():
    """Порівняння інсталяції Wheel (пряме розпакування) та Sdist (ізольоване збирання)."""
    w, h = 880, 430
    frags = []

    frags.append(text(w / 2, 28, "Порівняння шляхів інсталяції: Wheel проти Sdist", size=16, bold=True))

    # Ліва колонка: Wheel
    frags.append(rect(30, 55, 385, 350, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(222, 85, "Готове бінарне колесо (.whl)", size=14, bold=True, color=FIELD))

    w1, _, _ = textbox(222, 135, "Завантажений .whl (ZIP-архів)\nВже містить скомпільовані C-бібліотеки\nта чистий байткод/модулі", size=11, fill="#ffffff", stroke=FIELD, min_w=330)
    frags.append(w1)

    frags.append(arrow(222, 170, 222, 210, color=FIELD, sw=1.8))
    frags.append(text(245, 192, "1 крок", size=11, color=FIELD, bold=True))

    w2, _, _ = textbox(222, 245, "Пряме розпакування (Unpack)\nКопіювання файлів у site-packages\nГенерація скриптів точки входу", size=11, fill="#ffffff", stroke=FIELD, min_w=330)
    frags.append(w2)

    frags.append(arrow(222, 280, 222, 320, color=FIELD, sw=1.8))

    w3, _, _ = textbox(222, 355, "Запис метаданих .dist-info\nФіксація хешів файлів у RECORD\nГотово до імпорту (Час: ~10-50 мс)", size=11, fill="#ffffff", stroke=FIELD, bold=True, min_w=330)
    frags.append(w3)

    # Права колонка: Sdist
    frags.append(rect(465, 55, 385, 350, fill="#eff6ff", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(657, 85, "Вихідний дистрибутив (.tar.gz sdist)", size=14, bold=True, color=NEG))

    s1, _, _ = textbox(657, 130, "Завантажений sdist (.tar.gz)\nЛише вихідні тексти Python/C/Rust\nта конфігурація pyproject.toml", size=11, fill="#ffffff", stroke=NEG, min_w=330)
    frags.append(s1)

    frags.append(arrow(657, 160, 657, 190, color=NEG, sw=1.5))

    s2, _, _ = textbox(657, 215, "PEP 518 Build Isolation\nСтворення тимчасового venv\nВстановлення build-backend (hatchling/setuptools)", size=11, fill="#ffffff", stroke=NEG, min_w=330)
    frags.append(s2)

    frags.append(arrow(657, 245, 657, 275, color=NEG, sw=1.5))

    s3, _, _ = textbox(657, 300, "PEP 517 build_wheel Hook\nКомпіляція C/C++/Rust розширень\nГенерація локального .whl файлу", size=11, fill="#ffffff", stroke=NEG, min_w=330)
    frags.append(s3)

    frags.append(arrow(657, 330, 657, 360, color=NEG, sw=1.5))

    s4, _, _ = textbox(657, 380, "Розпакування локального Wheel у site-packages", size=10, fill="#ffffff", stroke=NEG, bold=True, min_w=330)
    frags.append(s4)

    render(os.path.join(OUT_DIR, "wheel-unpack-vs-sdist-build.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_pip_architecture()
    fig_dependency_confusion()
    fig_wheel_vs_sdist()
    print("Усі фігури успішно згенеровано.")
