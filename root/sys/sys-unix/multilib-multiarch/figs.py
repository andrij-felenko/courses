# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def fig_layout():
    W, H = 840, 480
    p = []
    p.append(text(W / 2, 30, "Порівняння ієрархій каталогів у Multilib та Multiarch", size=18, bold=True))

    # --- ЛІВА ПАНЕЛЬ: Multilib (RPM) ---
    lx, ly, lw, lh = 30, 60, 370, 390
    p.append(rect(lx, ly, lw, lh, fill="#fdfefe", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(lx + lw / 2, ly + 26, "RPM Multilib (розподіл за бітністю)", size=15, bold=True, color=POS))

    # Блоки в Multilib
    p.append(fitbox(lx + 20, ly + 50, 330, 75,
                    "/usr/lib/\n32-бітні shared objects (.so)\nПриклад: /usr/lib/libc.so.6",
                    size=12, fill="#fdecea", stroke=POS, sw=1.2))

    p.append(fitbox(lx + 20, ly + 140, 330, 75,
                    "/usr/lib64/\n64-бітні shared objects (.so)\nПриклад: /usr/lib64/libc.so.6",
                    size=12, fill="#eaf0fd", stroke=NEG, sw=1.2))

    p.append(fitbox(lx + 20, ly + 230, 330, 135,
                    "/usr/include/\nСпільні заголовні файли (.h)\nКонфлікти типів sizeof(long), struct stat!\nВирішення: макроси-обгортки #if __WORDSIZE == 64\nі файли типу types-32.h / types-64.h",
                    size=11.5, fill="#fff8e7", stroke="#f39c12", sw=1.5))

    # --- ПРАВА ПАНЕЛЬ: Multiarch (Debian) ---
    rx, ry, rw, rh = 440, 60, 370, 390
    p.append(rect(rx, ry, rw, rh, fill="#fdfefe", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(rx + rw / 2, ry + 26, "Debian Multiarch (GNU-триплети)", size=15, bold=True, color=FIELD))

    # Блоки в Multiarch
    p.append(fitbox(rx + 20, ly + 50, 330, 95,
                    "/usr/lib/x86_64-linux-gnu/\n64-бітні native бібліотеки\n/usr/lib/i386-linux-gnu/\n32-бітні compatibility бібліотеки\n/usr/lib/aarch64-linux-gnu/\nARM64 бібліотеки для крос-компіляції",
                    size=11, fill="#eafaf0", stroke=FIELD, sw=1.2))

    p.append(fitbox(rx + 20, ly + 160, 330, 95,
                    "/usr/include/x86_64-linux-gnu/\n64-бітні заголовки з розрядністю типу\n/usr/include/i386-linux-gnu/\n32-бітні заголовки з розрядністю типу\n/usr/include/\nАрх-незалежні спільні заголовки",
                    size=11, fill="#eafaf0", stroke=FIELD, sw=1.2))

    p.append(fitbox(rx + 20, ly + 270, 330, 95,
                    "Перевага Multiarch:\nНемає конфліктів у /usr/include.\nМожна встановити довільну кількість\nінородних архітектур поруч із нативною.",
                    size=11.5, fill="#f4f6f8", stroke=LINE, sw=1.2))

    render(os.path.join(OUT, "layout.svg"), W, H, *p)

def fig_multiarch_resolution():
    W, H = 840, 420
    p = []
    p.append(text(W / 2, 30, "Маршрутизація комбінованих викликів у Multiarch", size=18, bold=True))

    # Джерело: Компілятор або динамічний завантажувач
    p.append(fitbox(40, 70, 230, 90,
                    "Компілятор / Завантажувач\ngcc -m32  або  gcc -m64\nld-linux.so.2 / ld-linux-x86-64.so.2",
                    size=12, fill="#f4f6f8", stroke=INK, sw=1.5, bold=True))

    # Крок 1: Вхідні прапорці / параметри
    p.append(arrow(270, 115, 340, 115, color=INK, sw=2))
    p.append(text(305, 103, "Архітектура", size=11, color=MUTED))

    # Перемикач триплетів
    p.append(fitbox(340, 70, 160, 90,
                    "GNU Triplet\nSelector\n(i386 vs x86_64\nvs aarch64)",
                    size=12, fill="#fff8e7", stroke="#f39c12", sw=1.5))

    # Відгалуження до 32-біт
    p.append(arrow(500, 95, 570, 95, color=POS, sw=2))
    p.append(fitbox(570, 70, 230, 50,
                    "i386-linux-gnu\n/usr/lib/i386-linux-gnu/\n/usr/include/i386-linux-gnu/",
                    size=11, fill="#fdecea", stroke=POS, sw=1.5))

    # Відгалуження до 64-біт
    p.append(arrow(500, 135, 570, 175, color=NEG, sw=2))
    p.append(fitbox(570, 150, 230, 50,
                    "x86_64-linux-gnu\n/usr/lib/x86_64-linux-gnu/\n/usr/include/x86_64-linux-gnu/",
                    size=11, fill="#eaf0fd", stroke=NEG, sw=1.5))

    # Відгалуження до ARM64 (крос-компіляція)
    p.append(arrow(420, 160, 420, 250, color=FIELD, sw=2))
    p.append(arrow(420, 250, 570, 250, color=FIELD, sw=2))
    p.append(fitbox(570, 225, 230, 50,
                    "aarch64-linux-gnu\n/usr/lib/aarch64-linux-gnu/\n/usr/include/aarch64-linux-gnu/",
                    size=11, fill="#eafaf0", stroke=FIELD, sw=1.5))

    # Пояснювальний блок знизу
    p.append(fitbox(40, 290, 760, 95,
                    "Пакетний менеджер dpkg керує метаданими за допомогою прапорців Multi-Arch:\n"
                    "• Multi-Arch: same — паралельне встановлення бібліотек однакової версії для різних триплетів\n"
                    "• Multi-Arch: foreign — нативна утиліта (наприклад python3), що задовольняє залежності чужої архітектури\n"
                    "• Multi-Arch: allowed — пакет може виступати в обох ролях залежно від запиту залежного пакета",
                    size=11.5, fill="#f9f9f9", stroke=MUTED, sw=1.2))

    render(os.path.join(OUT, "multiarch-resolution.svg"), W, H, *p)

if __name__ == "__main__":
    fig_layout()
    fig_multiarch_resolution()
