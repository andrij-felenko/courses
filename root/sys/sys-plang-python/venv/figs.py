# -*- coding: utf-8 -*-
"""Генерація SVG-ілюстрацій для теми venv (Віртуальне середовище)."""

import os
import sys

# Підключення svgkit із кореня репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, rect, line, arrow, text, mtext, textbox, fitbox, circle,
    INK, MUTED, LINE, FILL, BG, POS, NEG, FIELD
)

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_directory_structure():
    """Анатомія каталогу віртуального середовища та зв'язок із системним інтерпретатором."""
    w, h = 900, 480
    frags = []

    # Заголовок
    frags.append(text(450, 25, "Анатомія віртуального середовища PEP 405", size=16, bold=True))

    # Ліва колонка: Системний Python (/usr)
    frags.append(rect(40, 50, 360, 400, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    frags.append(text(220, 75, "Системний префікс (sys.base_prefix = /usr)", size=13, bold=True, color=INK))

    # Елементи системного префікса
    b_sys_bin, _, _ = textbox(220, 120, "/usr/bin/python3.12\n(Головний двійковий образ ELF)", size=12, pad=8, min_w=300, fill="#ffffff", stroke=LINE)
    frags.append(b_sys_bin)

    b_sys_lib, _, _ = textbox(220, 210, "/usr/lib/python3.12/\n(Стандартна бібліотека: os, sys, math...)", size=12, pad=8, min_w=300, fill="#ffffff", stroke=LINE)
    frags.append(b_sys_lib)

    b_sys_dyn, _, _ = textbox(220, 295, "/usr/lib/python3.12/lib-dynload/\n(C-розширення: _socket.so, _ssl.so)", size=12, pad=8, min_w=300, fill="#ffffff", stroke=LINE)
    frags.append(b_sys_dyn)

    b_sys_site, _, _ = textbox(220, 380, "/usr/lib/python3/dist-packages/\n(Системні пакунки apt / dnf / pacman)", size=12, pad=8, min_w=300, fill="#ffffff", stroke=MUTED)
    frags.append(b_sys_site)

    # Права колонка: Каталог venv (~/project/.venv)
    frags.append(rect(500, 50, 360, 400, fill="#eff6ff", stroke=NEG, sw=1.8, rx=8))
    frags.append(text(680, 75, "Ізольований префікс (sys.prefix = .venv)", size=13, bold=True, color=NEG))

    # Файл pyvenv.cfg
    b_cfg, _, _ = textbox(680, 125, "pyvenv.cfg\nhome = /usr/bin\ninclude-system-site-packages = false", size=11, pad=8, min_w=300, fill="#fef3c7", stroke="#d97706")
    frags.append(b_cfg)

    # Каталог bin/
    b_venv_bin, _, _ = textbox(680, 215, "bin/python3 -> /usr/bin/python3.12 (symlink)\nbin/activate, bin/pip, bin/pytest", size=11, pad=8, min_w=300, fill="#ffffff", stroke=LINE)
    frags.append(b_venv_bin)

    # Каталог lib/
    b_venv_site, _, _ = textbox(680, 310, "lib/python3.12/site-packages/\nІзольовані пакунки проєкту (pip install)\nrequests, fastapi, pydantic, numpy...", size=11, pad=8, min_w=300, fill="#ecfdf5", stroke=FIELD)
    frags.append(b_venv_site)

    # Каталог include/
    b_venv_inc, _, _ = textbox(680, 395, "include/ (Заголовні файли C/C++ для збірки)", size=11, pad=6, min_w=300, fill="#ffffff", stroke=MUTED)
    frags.append(b_venv_inc)

    # Стрілки взаємодії
    # Симлінк з venv/bin на /usr/bin
    frags.append(arrow(530, 215, 370, 130, color=NEG, sw=1.8))
    frags.append(text(450, 160, "Символічне посилання", size=10, color=NEG, bold=True))

    # Зчитування home з pyvenv.cfg
    frags.append(arrow(530, 125, 370, 120, color="#d97706", sw=1.8))
    frags.append(text(450, 110, "home вказує базу", size=10, color="#d97706", bold=True))

    # Пошук стандартної бібліотеки
    frags.append(arrow(530, 225, 370, 210, color=FIELD, sw=1.8))
    frags.append(text(450, 230, "stdlib береться з бази", size=10, color=FIELD, bold=True))

    render(os.path.join(IMG_DIR, "venv-directory-structure.svg"), w, h, *frags)


def fig_startup_resolution():
    """Покроковий алгоритм виявлення venv та розрахунку префіксів у CPython."""
    w, h = 920, 520
    frags = []

    frags.append(text(460, 25, "Алгоритм ініціалізації шляхів CPython (getpath)", size=16, bold=True))

    # Крок 1: Точка старту
    b1, _, _ = textbox(460, 65, "1. Запуск: execve(\".venv/bin/python3\")\nОтримання argv[0] та обчислення sys.executable", size=12, pad=8, min_w=480, fill="#ffffff", stroke=LINE)
    frags.append(b1)
    frags.append(arrow(460, 95, 460, 125, color=LINE, sw=1.5))

    # Крок 2: Пошук pyvenv.cfg
    b2, _, _ = textbox(460, 155, "2. Пошук pyvenv.cfg\nПеревірка каталогу бінарника (.venv/bin) та батьківського каталогу (.venv)", size=12, pad=8, min_w=480, fill="#ffffff", stroke=LINE)
    frags.append(b2)
    frags.append(arrow(460, 185, 460, 220, color=LINE, sw=1.5))

    # Розгалуження: знайдено чи ні
    b_found, _, _ = textbox(250, 255, "pyvenv.cfg ЗНАЙДЕНО\nРежим PEP 405 venv", size=12, pad=8, min_w=280, fill="#eff6ff", stroke=NEG, bold=True)
    b_not_found, _, _ = textbox(670, 255, "pyvenv.cfg ВІДСУТНІЙ\nСтандартний системний режим", size=12, pad=8, min_w=280, fill="#f8fafc", stroke=MUTED)
    frags.append(b_found)
    frags.append(b_not_found)

    frags.append(arrow(350, 185, 250, 230, color=NEG, sw=1.5))
    frags.append(arrow(570, 185, 670, 230, color=MUTED, sw=1.5))

    # Гілка venv:
    b_v_step, _, _ = textbox(250, 345, "3. Зчитування home з pyvenv.cfg\nsys.base_prefix = home (/usr)\nsys.prefix = .venv\nsys.exec_prefix = .venv", size=11, pad=8, min_w=320, fill="#ffffff", stroke=LINE)
    frags.append(b_v_step)
    frags.append(arrow(250, 285, 250, 315, color=NEG, sw=1.5))

    # Гілка системна:
    b_s_step, _, _ = textbox(670, 345, "3. Пошук орієнтирів (Landmarks: os.py)\nsys.base_prefix = /usr\nsys.prefix = /usr\nsys.exec_prefix = /usr", size=11, pad=8, min_w=320, fill="#ffffff", stroke=LINE)
    frags.append(b_s_step)
    frags.append(arrow(670, 285, 670, 315, color=MUTED, sw=1.5))

    # Злиття у фазу site.py
    frags.append(arrow(250, 385, 400, 430, color=LINE, sw=1.5))
    frags.append(arrow(670, 385, 520, 430, color=LINE, sw=1.5))

    b_site, _, _ = textbox(460, 465, "4. Ініціалізація site.py та формування sys.path\nДодавання sys.prefix + /lib/python3.X/site-packages/\nЯкщо include-system-site-packages = true -> додається також системний site-packages", size=11, pad=8, min_w=640, fill="#ecfdf5", stroke=FIELD)
    frags.append(b_site)

    render(os.path.join(IMG_DIR, "startup-prefix-resolution.svg"), w, h, *frags)


def fig_activation_path_flow():
    """Порівняння шляхів виклику: прямий виклик інтерпретатора проти активованого середовища."""
    w, h = 900, 460
    frags = []

    frags.append(text(450, 25, "Механіка виклику: прямий шлях проти активації через shell", size=16, bold=True))

    # Лівий блок: Прямий запуск
    frags.append(rect(40, 50, 380, 380, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(230, 75, "Варіант А: Прямий виклик бінарника", size=13, bold=True, color=INK))

    b_cmd_a, _, _ = textbox(230, 115, "$ /home/user/app/.venv/bin/python main.py\nабо $ .venv/bin/pytest", size=11, pad=8, min_w=340, fill="#f8fafc", stroke=LINE)
    frags.append(b_cmd_a)

    b_desc_a1, _, _ = textbox(230, 195, "Змінна $PATH: НЕ ЗМІНЮЄТЬСЯ\n(/usr/bin:/bin:/usr/local/bin)", size=11, pad=8, min_w=340, fill="#ffffff", stroke=MUTED)
    frags.append(b_desc_a1)

    b_desc_a2, _, _ = textbox(230, 275, "Пошук pyvenv.cfg: АВТОМАТИЧНО\nCPython обчислює шлях від власного argv[0]\nі самостійно підміняє sys.prefix", size=11, pad=8, min_w=340, fill="#eff6ff", stroke=NEG)
    frags.append(b_desc_a2)

    b_desc_a3, _, _ = textbox(230, 365, "Shebang у консольних скриптах:\n#!/home/user/app/.venv/bin/python\nСкрипти pip/pytest викликають потрібний venv", size=11, pad=8, min_w=340, fill="#ecfdf5", stroke=FIELD)
    frags.append(b_desc_a3)

    # Правий блок: Активований шелл
    frags.append(rect(480, 50, 380, 380, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(670, 75, "Варіант Б: Робота через source bin/activate", size=13, bold=True, color=INK))

    b_cmd_b, _, _ = textbox(670, 115, "$ source .venv/bin/activate\n(.venv) $ python main.py", size=11, pad=8, min_w=340, fill="#f8fafc", stroke=LINE)
    frags.append(b_cmd_b)

    b_desc_b1, _, _ = textbox(670, 195, "Змінна $PATH: МОДИФІКОВАНА\nPATH=\"/home/user/app/.venv/bin:$PATH\"\nКоманда 'python' тепер вказує на .venv/bin", size=11, pad=8, min_w=340, fill="#eff6ff", stroke=NEG)
    frags.append(b_desc_b1)

    b_desc_b2, _, _ = textbox(670, 275, "Змінні середовища:\nVIRTUAL_ENV=\"/home/user/app/.venv\"\nPS1=\"(.venv) $PS1\"\nФункція deactivate() для відкату", size=11, pad=8, min_w=340, fill="#ffffff", stroke=LINE)
    frags.append(b_desc_b2)

    b_desc_b3, _, _ = textbox(670, 365, "Поведінка у підпроцесах:\nДочірні процеси успадковують $PATH,\nпроте ізоляція працює за рахунок pyvenv.cfg", size=11, pad=8, min_w=340, fill="#fef3c7", stroke="#d97706")
    frags.append(b_desc_b3)

    render(os.path.join(IMG_DIR, "activation-path-flow.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_directory_structure()
    fig_startup_resolution()
    fig_activation_path_flow()
    print("Всі фігури згенеровано успішно.")
