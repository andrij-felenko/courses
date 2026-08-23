# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми shipping-a-linux-app."""
import sys, os

# Додаємо scripts/ до шляху пошуку модулів
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def fig_distribution_spectrum(out_dir):
    """Фігура 1: Спектр форматів дистрибуції ПЗ у Linux."""
    w, h = 920, 440
    frags = []

    # Фон і загальна назва
    frags.append(rect(10, 10, 900, 420, fill="#fafbfc", stroke="#d1d5db", sw=1.5, rx=8))
    frags.append(text(460, 40, "Спектр моделей пакування та доставки програм у Linux", size=16, bold=True))

    # 4 стовпці: Системні пакунки, Статичні бінарники, Автономні бандли, Контейнери
    cols = [
        {
            "x": 30, "w": 200, "title": "Системні пакунки", "sub": "deb, rpm, apk",
            "color": NEG, "bg": "#eff6ff",
            "items": [
                "Спільні системні .so",
                "Жорстка прив'язка до ОС",
                "Менеджер залежностей",
                "FHS стандартизація",
                "Матриця збірок під версії"
            ],
            "target": "Базова ОС та сервери"
        },
        {
            "x": 250, "w": 200, "title": "Статичні бінарники", "sub": "Go, Rust, C/musl",
            "color": FIELD, "bg": "#f0fdf4",
            "items": [
                "Один автономний ELF",
                "libc вшита в бінарник",
                "Нуль зовнішніх .so",
                "Працює на будь-якому ядрі",
                "Складніший dlopen / NSS"
            ],
            "target": "CLI утиліти та мікросервіси"
        },
        {
            "x": 470, "w": 200, "title": "Десктоп-бандли", "sub": "AppImage, Flatpak, Snap",
            "color": "#d97706", "bg": "#fffbeb",
            "items": [
                "SquashFS або runtime",
                "XDG / Desktop інтеграція",
                "Пісочниця (Bubblewrap)",
                "Доступ через Portals",
                "Усі GUI-бібліотеки всередині"
            ],
            "target": "Десктопні GUI-застосунки"
        },
        {
            "x": 690, "w": 200, "title": "OCI Контейнери", "sub": "Docker, Podman, containerd",
            "color": POS, "bg": "#fef2f2",
            "items": [
                "Власна rootfs та оточення",
                "Ізоляція Namespaces/cgroups",
                "Оркестрація (K8s)",
                "Накладні витрати на I/O",
                "Повна повторюваність"
            ],
            "target": "Хмарні та серверні бекенди"
        }
    ]

    for c in cols:
        cx, cw = c["x"], c["w"]
        frags.append(rect(cx, 70, cw, 290, fill=c["bg"], stroke=c["color"], sw=1.5, rx=6))
        frags.append(text(cx + cw/2, 98, c["title"], size=14, bold=True, color=c["color"]))
        frags.append(text(cx + cw/2, 118, c["sub"], size=12, italic=True, color=MUTED))
        frags.append(line(cx + 12, 132, cx + cw - 12, 132, color=c["color"], sw=1, dash="3,3"))

        # Items
        for idx, it in enumerate(c["items"]):
            iy = 156 + idx * 26
            frags.append(circle(cx + 20, iy - 4, 3, fill=c["color"], stroke=c["color"]))
            frags.append(text(cx + 30, iy, it, size=11, anchor="start", color=INK))

        # Target badge
        frags.append(rect(cx + 10, 312, cw - 20, 36, fill="#ffffff", stroke="#9ca3af", sw=1, rx=4))
        frags.append(text(cx + cw/2, 334, c["target"], size=11, bold=True, color=INK))

    # Стрілка знизу: Автономність та ізоляція
    frags.append(line(50, 395, 870, 395, color=LINE, sw=1.5))
    frags.append(arrow(850, 395, 875, 395, color=LINE, sw=1.5))
    frags.append(text(460, 385, "Зростання автономності, розміру дистрибутиву та рівня ізоляції оточення →", size=12, bold=True, color=LINE))

    path = os.path.join(out_dir, "distribution-spectrum.svg")
    render(path, w, h, *frags)
    print(f"Generated: {path}")

def fig_glibc_version_trap(out_dir):
    """Фігура 2: Пастка версіонування символів glibc."""
    w, h = 880, 380
    frags = []

    frags.append(rect(10, 10, 860, 360, fill="#fafbfc", stroke="#d1d5db", sw=1.5, rx=8))
    frags.append(text(440, 38, "Механізм несумісності бінарників: пастка версій glibc", size=16, bold=True))

    # Лівий блок: Хост збірки (Build Host)
    frags.append(rect(30, 70, 370, 240, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(215, 96, "Машина розробника / CI (Ubuntu 24.04)", size=13, bold=True, color=NEG))
    frags.append(text(215, 116, "Системна libc: glibc 2.38", size=12, italic=True, color=MUTED))
    frags.append(line(45, 128, 385, 128, color=NEG, sw=1, dash="2,2"))

    frags.append(text(50, 150, "1. Компіляція бінарника myapp:", size=11, bold=True, anchor="start"))
    frags.append(text(60, 170, "$ gcc -O2 main.c -o myapp", size=11, anchor="start", color="#1e3a8a"))

    frags.append(text(50, 200, "2. Лінкер записує вимоги версій символів:", size=11, bold=True, anchor="start"))
    frags.append(rect(50, 212, 330, 80, fill="#ffffff", stroke="#93c5fd", sw=1, rx=4))
    frags.append(text(60, 232, "ELF .gnu.version_r (VERNEED):", size=10, bold=True, anchor="start", color=MUTED))
    frags.append(text(60, 252, "• memcpy@GLIBC_2.14", size=10, anchor="start", color=INK))
    frags.append(text(60, 272, "• fcntl@GLIBC_2.28, statx@GLIBC_2.38", size=10, anchor="start", color=POS))

    # Стрілка посередині
    frags.append(line(405, 190, 475, 190, color=LINE, sw=1.8))
    frags.append(arrow(460, 190, 475, 190, color=LINE, sw=1.8))
    frags.append(text(440, 175, "SCP / scp", size=11, italic=True, color=MUTED))
    frags.append(text(440, 210, "Перенесення", size=11, bold=True, color=LINE))

    # Правий блок: Цільовий хост (Target Host)
    frags.append(rect(480, 70, 370, 240, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    frags.append(text(665, 96, "Цільовий сервер (Debian 11 / RHEL 8)", size=13, bold=True, color=POS))
    frags.append(text(665, 116, "Системна libc: glibc 2.31", size=12, italic=True, color=MUTED))
    frags.append(line(495, 128, 835, 128, color=POS, sw=1, dash="2,2"))

    frags.append(text(500, 150, "3. Спроба запуску ./myapp:", size=11, bold=True, anchor="start"))
    frags.append(text(510, 170, "ld-linux.so.2 відкриває libc.so.6 (2.31)", size=11, anchor="start", color=INK))

    frags.append(text(500, 200, "4. Динамічний лінкер падає до main():", size=11, bold=True, anchor="start"))
    frags.append(rect(500, 212, 330, 80, fill="#fee2e2", stroke=POS, sw=1, rx=4))
    frags.append(text(510, 234, "./myapp: /lib/x86_64-linux-gnu/libc.so.6:", size=9, bold=True, anchor="start", color=POS))
    frags.append(text(510, 252, "version `GLIBC_2.38' not found", size=10, bold=True, anchor="start", color=POS))
    frags.append(text(510, 272, "(required by ./myapp) -> АВАРІЙНИЙ ВИХІД", size=9, bold=True, anchor="start", color=POS))

    # Висновок внизу
    frags.append(rect(30, 325, 820, 35, fill="#f0fdf4", stroke=FIELD, sw=1, rx=4))
    frags.append(text(440, 347, "Висновок: glibc має зворотну сумісність, але НЕ пряму. Збирати треба на найстарішій підтримуваній системі.", size=11, bold=True, color="#15803d"))

    path = os.path.join(out_dir, "glibc-version-trap.svg")
    render(path, w, h, *frags)
    print(f"Generated: {path}")

def fig_production_lifecycle(out_dir):
    """Фігура 3: Життєвий цикл продакшен-сервісу під керуванням systemd."""
    w, h = 900, 410
    frags = []

    frags.append(rect(10, 10, 880, 390, fill="#fafbfc", stroke="#d1d5db", sw=1.5, rx=8))
    frags.append(text(450, 38, "Життєвий цикл та протокол взаємодії сервісу з systemd", size=16, bold=True))

    steps = [
        {
            "x": 30, "w": 190, "num": "1", "title": "Ізоляція та старт",
            "color": NEG, "bg": "#eff6ff",
            "lines": [
                "Створення cgroup v2",
                "Виділення DynamicUser",
                "Монтування ProtectSystem",
                "Застосування Seccomp",
                "Виклик execve(binary)"
            ]
        },
        {
            "x": 245, "w": 195, "num": "2", "title": "Ініціалізація",
            "color": FIELD, "bg": "#f0fdf4",
            "lines": [
                "Зчитування /etc конфігів",
                "Відкриття портів / сокетів",
                "Прогрів пулу з'єднань",
                "sd_notify(\"READY=1\\n\")",
                "systemd переводить в active"
            ]
        },
        {
            "x": 465, "w": 195, "num": "3", "title": "Робота та Watchdog",
            "color": "#d97706", "bg": "#fffbeb",
            "lines": [
                "Обробка запитів клієнтів",
                "Логи у stdout (journald)",
                "sd_notify(\"WATCHDOG=1\")",
                "Якщо завис — systemd",
                "перезапустить сервіс"
            ]
        },
        {
            "x": 685, "w": 185, "num": "4", "title": "Graceful Shutdown",
            "color": POS, "bg": "#fef2f2",
            "lines": [
                "systemd надсилає SIGTERM",
                "Припинення прийому нових",
                "Дообробка активних задач",
                "Закриття сокетів/БД",
                "Вихід exit(0) до таймауту"
            ]
        }
    ]

    for s in steps:
        sx, sw = s["x"], s["w"]
        frags.append(rect(sx, 70, sw, 250, fill=s["bg"], stroke=s["color"], sw=1.5, rx=6))

        # Header with number
        frags.append(circle(sx + 24, 98, 12, fill=s["color"], stroke=s["color"]))
        frags.append(text(sx + 24, 103, s["num"], size=12, bold=True, color="#ffffff"))
        frags.append(text(sx + 42, 103, s["title"], size=13, bold=True, anchor="start", color=s["color"]))
        frags.append(line(sx + 10, 120, sx + sw - 10, 120, color=s["color"], sw=1, dash="2,2"))

        for idx, ln in enumerate(s["lines"]):
            ly = 145 + idx * 30
            frags.append(circle(sx + 18, ly - 4, 2.5, fill=s["color"], stroke=s["color"]))
            frags.append(text(sx + 26, ly, ln, size=11, anchor="start", color=INK))

    # Стрілки між етапами
    frags.append(arrow(225, 195, 245, 195, color=LINE, sw=1.5))
    frags.append(arrow(440, 195, 465, 195, color=LINE, sw=1.5))
    frags.append(arrow(660, 195, 685, 195, color=LINE, sw=1.5))

    # Нижня панель: таймаут аварійного завершення
    frags.append(rect(30, 335, 840, 50, fill="#fef2f2", stroke=POS, sw=1, rx=4))
    frags.append(text(450, 355, "Захисний механізм: Якщо сервіс не завершив роботу за TimeoutStopSec (типово 90с) після SIGTERM,", size=11, bold=True, color=POS))
    frags.append(text(450, 372, "ядро надсилає неперехоплюваний SIGKILL і примусово звільняє всі ресурси процесу в cgroup.", size=11, color=POS))

    path = os.path.join(out_dir, "production-lifecycle.svg")
    render(path, w, h, *frags)
    print(f"Generated: {path}")

def main():
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    fig_distribution_spectrum(out_dir)
    fig_glibc_version_trap(out_dir)
    fig_production_lifecycle(out_dir)

if __name__ == "__main__":
    main()
