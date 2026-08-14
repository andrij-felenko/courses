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

# ── 1. Схема життєвого циклу та потоку виконання генераторів systemd ─────────
def fig_generator_execution_flow():
    W, H = 1350, 720
    p = []

    p.append(text(675, 40, "Життєвий цикл та фази виконання генераторів у системному менеджері systemd", size=18, bold=True))

    # Фаза 1: Тригер запуску
    p.append(rect(40, 80, 360, 580, fill="#ffffff", stroke="#cfd8dc", sw=1.5))
    p.append(text(220, 115, "1. Тригер виконання", size=16, bold=True))

    p.append(fitbox(60, 145, 320, 110, "Ранній boot системи:\nPID 1 старт у initramfs або після switch_root", size=13, fill=BLUE))
    p.append(fitbox(60, 275, 320, 110, "Команда адміністратора:\nsystemctl daemon-reload", size=13, fill=BLUE))
    p.append(fitbox(60, 405, 320, 110, "Перехід між цілями:\nЗміна ранніх системних boot targets", size=13, fill=BLUE))
    p.append(fitbox(60, 535, 320, 100, "Очищення каталогу /run:\nвидалення старого виводу у /run/systemd/generator*", size=13, fill=RED))

    p.append(arrow(400, 350, 440, 350, color=LINE, sw=2))

    # Фаза 2: Сканування та виконання генераторів
    p.append(rect(450, 80, 450, 580, fill="#ffffff", stroke="#cfd8dc", sw=1.5))
    p.append(text(675, 115, "2. Паралельне виконання (PID 1)", size=16, bold=True))

    p.append(fitbox(470, 145, 410, 80, "Сканування каталогів генераторів:\n/run, /etc, /usr/local/lib, /lib", size=13, fill=PURPLE))
    p.append(line(675, 225, 675, 255, color=LINE, sw=1.5))

    p.append(fitbox(470, 255, 410, 110, "Паралельний fork() + execve():\n- systemd-fstab-generator\n- systemd-gpt-auto-generator\n- systemd-cryptsetup-generator\n- custom-generators...", size=13, bold=True, fill=WARM))

    p.append(arrow(675, 365, 675, 395, color=LINE, sw=1.5))

    p.append(fitbox(470, 395, 410, 120, "Аргументи виклику:\n$1 = /run/systemd/generator\n$2 = /run/systemd/generator.early\n$3 = /run/systemd/generator.late", size=13, fill=GREY))

    p.append(line(675, 515, 675, 545, color=LINE, sw=1.5))

    p.append(fitbox(470, 545, 410, 90, "Синхронне очікування:\nPID 1 блокує boot до завершення усіх генераторів", size=13, fill=RED))

    p.append(arrow(900, 350, 940, 350, color=LINE, sw=2))

    # Фаза 3: Побудова графа залежностей
    p.append(rect(950, 80, 360, 580, fill="#ffffff", stroke="#cfd8dc", sw=1.5))
    p.append(text(1130, 115, "3. Завантаження юнітів", size=16, bold=True))

    p.append(fitbox(970, 145, 320, 140, "Зчитування згенерованих файлів:\n- *.mount, *.service, *.target\n- симлінки .wants/ та .requires/", size=13, fill=GREEN))
    p.append(arrow(1130, 285, 1130, 315, color=LINE, sw=1.5))

    p.append(fitbox(970, 315, 320, 140, "Злиття з юнітами диска:\nпоєднання з /etc/systemd/system та /lib/systemd/system", size=13, fill=GREEN))
    p.append(arrow(1130, 455, 1130, 485, color=LINE, sw=1.5))

    p.append(fitbox(970, 485, 320, 150, "Побудова DAG графа:\nактивація транзакцій запусків та старт системних служб", size=13, bold=True, fill=GREEN))

    render(os.path.join(IMG, 'generator-execution-flow.svg'), W, H, *p)


# ── 2. Ієрархія каталогів генераторів та порядок перекриття юнітів ───────────
def fig_generator_directory_hierarchy():
    W, H = 1350, 680
    p = []

    p.append(text(675, 40, "Ієрархія каталогів пошуку генераторів та порядок пріоритету виводу ($1, $2, $3)", size=18, bold=True))

    # Лівий блок — Каталоги бінарників генераторів
    p.append(rect(40, 80, 620, 560, fill="#ffffff", stroke="#cfd8dc", sw=1.5))
    p.append(text(350, 115, "Каталоги розташування виконуваних генераторів", size=16, bold=True))

    g1_txt = "1. /run/systemd/system-generators/\nДинамічні генератори рантайму (найвищий пріоритет)"
    g2_txt = "2. /etc/systemd/system-generators/\nАдміністративні кастомні генератори системи"
    g3_txt = "3. /usr/local/lib/systemd/system-generators/\nЛокально встановлені генератори розробника"
    g4_txt = "4. /lib/systemd/system-generators/ (або /usr/lib/...)\nСистемні генератори з пакетів дистрибутива (fstab, cryptsetup)"

    p.append(fitbox(60, 145, 580, 95, g1_txt, size=13, bold=True, fill=RED))
    p.append(arrow(350, 240, 350, 260, color=LINE, sw=1.5))

    p.append(fitbox(60, 260, 580, 95, g2_txt, size=13, bold=True, fill=WARM))
    p.append(arrow(350, 355, 350, 375, color=LINE, sw=1.5))

    p.append(fitbox(60, 375, 580, 95, g3_txt, size=13, fill=PURPLE))
    p.append(arrow(350, 470, 350, 490, color=LINE, sw=1.5))

    p.append(fitbox(60, 490, 580, 125, g4_txt, size=13, fill=BLUE))

    # Правий блок — Ієрархія згенерованих каталогів у PID 1
    p.append(rect(690, 80, 620, 560, fill="#ffffff", stroke="#cfd8dc", sw=1.5))
    p.append(text(1000, 115, "Порядок завантаження юнітів у пам'ять PID 1", size=16, bold=True))

    u1_txt = "1. /run/systemd/generator.early (Аргумент $2)\nПерекриває навіть стабільні конфіги у /etc/systemd/system!"
    u2_txt = "2. /etc/systemd/system\nСтатичні адміністративні юніти системи"
    u3_txt = "3. /run/systemd/system\nДинамічні рантайм юніти"
    u4_txt = "4. /run/systemd/generator (Аргумент $1)\nСтандартний вивід генераторів (fstab, gpt-auto)"
    u5_txt = "5. /usr/lib/systemd/system або /lib/systemd/system\nПакетні дефолтні юніти дистрибутива"
    u6_txt = "6. /run/systemd/generator.late (Аргумент $3)\nФолбек-юніти (найнижчий пріоритет завантаження)"

    p.append(fitbox(710, 145, 580, 70, u1_txt, size=13, bold=True, fill=RED))
    p.append(fitbox(710, 225, 580, 65, u2_txt, size=13, fill=WARM))
    p.append(fitbox(710, 300, 580, 65, u3_txt, size=13, fill=PURPLE))
    p.append(fitbox(710, 375, 580, 70, u4_txt, size=13, bold=True, fill=GREEN))
    p.append(fitbox(710, 455, 580, 65, u5_txt, size=13, fill=BLUE))
    p.append(fitbox(710, 530, 580, 70, u6_txt, size=13, fill=GREY))

    render(os.path.join(IMG, 'generator-directory-hierarchy.svg'), W, H, *p)


if __name__ == '__main__':
    fig_generator_execution_flow()
    fig_generator_directory_hierarchy()
    print("Successfully generated all SVG figures for systemd-generator-architecture!")
