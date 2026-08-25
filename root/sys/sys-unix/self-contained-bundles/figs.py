# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
GREY_FILL = "#eceff1"


def fig_appimage():
    W, H = 1240, 560
    p = []

    # Title
    p.append(text(W / 2, 40, "Архітектура AppImage: ELF-лаунчер та змонтована SquashFS", size=18, bold=True))

    # Left Column: File Layout
    p.append(text(240, 80, "Структура файлу .AppImage", size=15, bold=True))
    p.append(rect(60, 100, 360, 420, fill=GREY_FILL, stroke=MUTED, sw=1.5, rx=8))

    p.append(fitbox(80, 120, 320, 100,
                    "1. ELF Header + AppRun\n"
                    "Бінарний лаунчер (executable)\n"
                    "зміщення: 0 байт",
                    size=13, fill=BLUE_FILL, stroke=NEG, bold=True))

    p.append(fitbox(80, 240, 320, 260,
                    "2. Стиснений образ SquashFS\n"
                    "• Власні бінарні файли (/usr/bin)\n"
                    "• Залежні бібліотеки (.so)\n"
                    "• Таблиці іконок та .desktop\n"
                    "• Допоміжні ресурси та конфіги",
                    size=13, fill=WARM_FILL, stroke=LINE))

    # Arrow between file layout and execution process
    p.append(arrow(430, 280, 480, 280))
    p.append(text(455, 265, "запуск", size=12, color=MUTED))

    # Right Column: Execution Flow
    p.append(text(850, 80, "Процес виконання та FUSE-монтування", size=15, bold=True))

    p.append(fitbox(500, 110, 680, 70,
                    "Крок 1: Запуск ./application.AppImage\n"
                    "Ядро запускає бінарну частину ELF (AppRun)",
                    size=13, fill=BLUE_FILL))

    p.append(arrow(840, 180, 840, 205))

    p.append(fitbox(500, 205, 680, 90,
                    "Крок 2: Монтування SquashFS через FUSE / squashfuse\n"
                    "Створюється тимчасова тека /tmp/.mount_AppXYZXXXXXX\n"
                    "Вміст образу стає доступним у файловій системі",
                    size=13, fill=GREEN_FILL, stroke=FIELD))

    p.append(arrow(840, 295, 840, 320))

    p.append(fitbox(500, 320, 680, 80,
                    "Крок 3: Налаштування середовища оточення\n"
                    "LD_LIBRARY_PATH=/tmp/.mount_AppXYZ/usr/lib\n"
                    "PATH=/tmp/.mount_AppXYZ/usr/bin:$PATH",
                    size=13, fill=WARM_FILL))

    p.append(arrow(840, 400, 840, 425))

    p.append(fitbox(500, 425, 680, 85,
                    "Крок 4: Виклик execv() цільового бінарника\n"
                    "Програма працює у звичайному просторі користувача.\n"
                    "При виході FUSE-точка демонтується і тека видаляється",
                    size=13, fill=GREEN_FILL, stroke=FIELD, bold=True))

    render(os.path.join(IMG, 'fig-appimage.svg'), W, H, *p)


def fig_flatpak():
    W, H = 1320, 600
    p = []

    p.append(text(W / 2, 38, "Архітектура Flatpak: OSTree, Bubblewrap та Desktop Portals", size=18, bold=True))

    # OSTree Repository Layer
    p.append(fitbox(50, 70, 1220, 75,
                    "Сховище OSTree (Flathub / Локальне сховище)\n"
                    "Атомарні оновлення, дедуплікація блоків даних за хешами content-addressable storage",
                    size=13, fill=GREY_FILL, stroke=MUTED, bold=True))

    p.append(arrow(350, 145, 350, 180))
    p.append(arrow(970, 145, 970, 180))

    # Application vs Runtime
    p.append(fitbox(50, 180, 600, 95,
                    "Застосунок (Application Bundle /app)\n"
                    "Містить специфічні бінарники, конфігурації\n"
                    "та унікальні для програми залежності",
                    size=13, fill=BLUE_FILL, stroke=NEG))

    p.append(fitbox(670, 180, 600, 95,
                    "Спільний рантайм (Shared Runtime /usr)\n"
                    "Базовий стек: GNOME / KDE / Freedesktop SDK\n"
                    "Спільні версії glibc, Mesa, Wayland, Qt/GTK",
                    size=13, fill=WARM_FILL, stroke=LINE))

    # Bubblewrap Sandbox Box
    p.append(rect(50, 310, 780, 260, fill="#fafafa", stroke=POS, sw=2, rx=8))
    p.append(text(440, 335, "Пісочниця Bubblewrap (bwrap)", size=15, bold=True, color=POS))

    p.append(fitbox(70, 355, 350, 85,
                    "Mount Namespace\n"
                    "• /usr ← змонтовано з Runtime (RO)\n"
                    "• /app ← змонтовано з App (RO)\n"
                    "• /var ← ізольовані налаштування",
                    size=12, fill=GREEN_FILL))

    p.append(fitbox(450, 355, 360, 85,
                    "Network & PID Namespaces\n"
                    "Ізольований простір процесів;\n"
                    "доступ до мережі за правилами маніфесту",
                    size=12, fill=GREEN_FILL))

    p.append(fitbox(70, 460, 740, 90,
                    "Ізольований процес застосунку\n"
                    "Не має прямого доступу до файлів хост-системи ($HOME, /etc, /var/log),\n"
                    "системних пристроїв та чужих процесів",
                    size=13, fill=RED_FILL, stroke=POS, bold=True))

    # D-Bus & XDG Desktop Portals Bridge
    p.append(arrow(830, 480, 890, 480))
    p.append(text(860, 465, "D-Bus", size=12, color=MUTED))

    p.append(rect(890, 310, 380, 260, fill=WARM_FILL, stroke=LINE, sw=1.5, rx=8))
    p.append(text(1080, 335, "XDG Desktop Portals", size=15, bold=True))

    p.append(fitbox(910, 355, 340, 195,
                    "Безпечна взаємодія з хостом:\n"
                    "• FileChooser Portal (діалог файлів)\n"
                    "• Camera / Microphones Portal\n"
                    "• ScreenCast / Screenshot Portal\n"
                    "• OpenURI Portal (браузер)\n"
                    "• Print Portal (друк)\n"
                    "Запит підтвердження у користувача",
                    size=12, fill="#ffffff", stroke=MUTED))

    render(os.path.join(IMG, 'fig-flatpak.svg'), W, H, *p)


def fig_snap():
    W, H = 1320, 620
    p = []

    p.append(text(W / 2, 38, "Архітектура Snap: snapd, loop-пристрої та confinement", size=18, bold=True))

    # Top Level: Snap File and Daemon
    p.append(fitbox(50, 70, 580, 100,
                    "Пакунок .snap (SquashFS образ)\n"
                    "Стиснена бінарна файлова система з метаданими snapcraft.yaml,\n"
                    "підписана цифровим підписом Snap Store",
                    size=13, fill=BLUE_FILL, stroke=NEG))

    p.append(arrow(630, 120, 690, 120))
    p.append(text(660, 105, "управління", size=12, color=MUTED))

    p.append(fitbox(690, 70, 580, 100,
                    "Системний демон snapd (systemd service)\n"
                    "Перевіряє підписи, керує loop-пристроями, поверненням версій (revert)\n"
                    "та збіркою AppArmor/seccomp профілів",
                    size=13, fill=GREEN_FILL, stroke=FIELD, bold=True))

    # Loop Mount Subsystem
    p.append(arrow(340, 170, 340, 210))

    p.append(rect(50, 210, 1220, 130, fill=GREY_FILL, stroke=MUTED, sw=1.5, rx=8))
    p.append(text(660, 235, "Ядерне монтування через loop-пристрої (/dev/loopN)", size=14, bold=True))

    p.append(fitbox(70, 255, 360, 70,
                    "Base Snap (напр. core22)\n"
                    "Монтується в /snap/core22/rev\n"
                    "Містить базу Ubuntu / glibc",
                    size=12, fill=WARM_FILL))

    p.append(fitbox(480, 255, 360, 70,
                    "App Snap (напр. firefox)\n"
                    "Монтується в /snap/firefox/rev\n"
                    "Містить бінарний файл застосунку",
                    size=12, fill=BLUE_FILL))

    p.append(fitbox(890, 255, 360, 70,
                    "Shared Mount points\n"
                    "Монтується через bind-mounts у\n"
                    "користувацьке середовище виконання",
                    size=12, fill=GREEN_FILL))

    # Confinement & Interfaces
    p.append(arrow(660, 340, 660, 375))

    p.append(rect(50, 375, 590, 220, fill="#fafafa", stroke=POS, sw=2, rx=8))
    p.append(text(345, 400, "Обмеження безпеки (Confinement)", size=15, bold=True, color=POS))

    p.append(fitbox(70, 420, 550, 160,
                    "• AppArmor Profiles: контроль доступу до файлів, dmesg, ptrace\n"
                    "• Seccomp Filters: обмеження дозволених системних викликів\n"
                    "• Mount Namespaces: ізольоване бачення файлового дерева\n"
                    "• Режими: Strict (повна ізоляція), Classic (повний доступ хоста),\n"
                    "  Devmode (режим розробки без блокувань)",
                    size=12, fill=RED_FILL, stroke=POS))

    p.append(rect(680, 375, 590, 220, fill=WARM_FILL, stroke=LINE, sw=1.5, rx=8))
    p.append(text(975, 400, "Система інтерфейсів (Plugs & Slots)", size=15, bold=True))

    p.append(fitbox(700, 420, 550, 160,
                    "З'єднання між застосунком (Plug) та системою/іншим Snap (Slot):\n"
                    "• home (доступ до тек користувача)\n"
                    "• network / network-bind (мережеві сокети)\n"
                    "• desktop / wayland (графічний вивід)\n"
                    "• removable-media (доступ до /media, /run/media)\n"
                    "Автоматичне або ручне підключення (`snap connect`)",
                    size=12, fill="#ffffff", stroke=MUTED))

    render(os.path.join(IMG, 'fig-snap.svg'), W, H, *p)


if __name__ == '__main__':
    fig_appimage()
    fig_flatpak()
    fig_snap()
    print("ok")
