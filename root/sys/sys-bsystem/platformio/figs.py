# -*- coding: utf-8 -*-
"""Фігури до теми «PlatformIO: збірка під будь-який МК»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

DIRTY = "#fdecea"     # червонуватий акцент
CLEAN = "#eaf7ef"     # зеленуватий акцент
BLUE_BG = "#eef4ff"   # синій акцент
WARN_BG = "#fff9db"   # жовтуватий акцент


def node(cx, cy, label, fill=FILL, stroke=LINE, bold=False, size=13.5, sw=1.5, min_w=0):
    frag, w, h = textbox(cx, cy, label, size=size, fill=fill, stroke=stroke,
                         bold=bold, sw=sw, min_w=min_w)
    return frag, (cx, cy, w, h)


def down_arr(a, b, color=LINE, sw=1.8):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return arrow(ax, ay + ah / 2 + 3, bx, by - bh / 2 - 5, color=color, sw=sw)


def right_arr(a, b, color=LINE, sw=1.8):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return arrow(ax + aw / 2 + 3, ay, bx - bw / 2 - 5, by, color=color, sw=sw)


# ── 1. Архітектурний конвеєр збірки PlatformIO ──────────────────────────────
def fig_pio_architecture():
    W, H = 1000, 520
    parts = []

    # Контейнер конфігурації та CLI
    parts.append(rect(30, 45, 270, 440, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    parts.append(text(165, 75, "1. Декларативний шар", size=15, bold=True, color=NEG))

    c1, g_c1 = node(165, 130, "platformio.ini\n[env:esp32] platform, board, ...\n[env:stm32] platform, board, ...", size=12, fill=BLUE_BG, stroke=NEG)
    c2, g_c2 = node(165, 235, "PlatformIO Core (CLI)\nПарсинг оточень,\nвибір активного таргета", size=12, fill=BG, stroke=MUTED)
    c3, g_c3 = node(165, 360, "Пакетний менеджер\nАвтоматичне завантаження:\nplatforms, toolchains, frameworks", size=12, fill=CLEAN, stroke=FIELD)

    parts += [c1, c2, c3, down_arr(g_c1, g_c2, color=NEG), down_arr(g_c2, g_c3, color=FIELD)]

    # Контейнер рушія збірки SCons
    parts.append(rect(330, 45, 340, 440, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    parts.append(text(500, 75, "2. Рушій збірки SCons", size=15, bold=True, color=FIELD))

    e1, g_e1 = node(500, 130, "Ініціалізація env (SCons)\nВстановлення препроцесорних прапорців\n(-D, -I, -Wl, скрипти лінкера .ld)", size=12, fill=BG, stroke=MUTED)
    e2, g_e2 = node(500, 235, "LDF (Library Finder)\nСканування #include директив,\nвирішення дерева залежностей", size=12, fill=BLUE_BG, stroke=NEG)
    e3, g_e3 = node(500, 360, "Python extra_scripts\nPre/Post хуки генерації бінарників,\nвпровадження хешів і карти пам'яті", size=12, fill=WARN_BG, stroke=LINE)

    parts += [e1, e2, e3, down_arr(g_e1, g_e2, color=NEG), down_arr(g_e2, g_e3, color=LINE)]

    # Контейнер компіляції та артефактів
    parts.append(rect(700, 45, 270, 440, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    parts.append(text(835, 75, "3. Генерація та вивід", size=15, bold=True, color=POS))

    o1, g_o1 = node(835, 130, "Крос-компілятор (GCC / Clang)\nxtensa-esp32-elf-gcc\narm-none-eabi-gcc", size=12, fill=BG, stroke=MUTED)
    o2, g_o2 = node(835, 235, "Компонувальник (ld)\nОб'єднання .o + SDK HAL\nгенерація firmware.elf", size=12, fill=BG, stroke=MUTED)
    o3, g_o3 = node(835, 360, "Фінальні артефакти\nfirmware.bin / firmware.hex\nЗавантаження (esptool / openocd)", size=12, fill=DIRTY, stroke=POS, bold=True)

    parts += [o1, o2, o3, down_arr(g_o1, g_o2, color=MUTED), down_arr(g_o2, g_o3, color=POS)]

    # Міжпанельні зв'язки
    parts.append(right_arr(g_c2, g_e1, color=NEG))
    parts.append(right_arr(g_e2, g_o1, color=FIELD))
    parts.append(right_arr(g_e3, g_o3, color=POS))

    render(os.path.join(IMG, "pio-architecture-flow.svg"), W, H, *parts,
           title="Архітектурний конвеєр PlatformIO: від конфігурації до машинної прошивки")


# ── 2. Алгоритм роботи Library Dependency Finder (LDF) ───────────────────────
def fig_ldf_modes():
    W, H = 1020, 480
    parts = []

    # Колонка 1: Режими без препроцесора (chain / deep)
    parts.append(rect(35, 50, 455, 395, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    parts.append(text(262, 80, "Лексичне сканування (chain / deep)", size=14.5, bold=True, color=POS))

    l1, g_l1 = node(262, 135, "Вихідний файл (.cpp / .c)\n#include <WiFi.h>\n#ifdef USE_BLE\n  #include <BLEDevice.h>\n#endif", size=12, fill=BG, stroke=MUTED)
    l2, g_l2 = node(262, 240, "Аналізатор регулярних виразів LDF\nЗчитує ВСІ рядки #include наосліп,\nігнорує умови препроцесора (#ifdef)", size=12, fill=DIRTY, stroke=POS)
    l3, g_l3 = node(262, 355, "Результат:\n+ Максимальна швидкість сканування\n− Хибні залежності: тягне BLEDevice.h\nнавіть коли USE_BLE вимкнено", size=12, fill=DIRTY, stroke=POS, bold=True)

    parts += [l1, l2, l3, down_arr(g_l1, g_l2, color=POS), down_arr(g_l2, g_l3, color=POS)]

    # Колонка 2: Режими з препроцесором (chain+ / deep+)
    parts.append(rect(530, 50, 455, 395, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    parts.append(text(757, 80, "Препроцесорний аналіз (chain+ / deep+)", size=14.5, bold=True, color=FIELD))

    p1, g_p1 = node(757, 135, "Вихідний файл (.cpp / .c)\n#include <WiFi.h>\n#ifdef USE_BLE\n  #include <BLEDevice.h>\n#endif", size=12, fill=BG, stroke=MUTED)
    p2, g_p2 = node(757, 240, "Запуск C-препроцесора (gcc -E)\nРозкриття макросів, врахування build_flags:\n-D USE_WIFI=1 (USE_BLE не визначено)", size=12, fill=BLUE_BG, stroke=NEG)
    p3, g_p3 = node(757, 355, "Результат:\n+ 100% точність графа бібліотек\n+ Жодних зайвих об'єктних файлів\n− Повільніша збірка (витрати на запуск cpp)", size=12, fill=CLEAN, stroke=FIELD, bold=True)

    parts += [p1, p2, p3, down_arr(g_p1, g_p2, color=NEG), down_arr(g_p2, g_p3, color=FIELD)]

    render(os.path.join(IMG, "ldf-dependency-modes.svg"), W, H, *parts,
           title="Режими аналізу залежностей LDF: швидке парсування проти точного препроцесингу")


# ── 3. Герметична ізоляція тулчейнів і пакетів ──────────────────────────────
def fig_packages_isolation():
    W, H = 1000, 490
    parts = []

    # Традиційний підхід
    parts.append(rect(35, 50, 440, 400, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    parts.append(text(255, 80, "Традиційний підхід (глобальний стан)", size=14.5, bold=True, color=POS))

    t1, g_t1 = node(255, 135, "Глобальний системний PATH\n/usr/bin, C:\\Keil, C:\\STM32CubeIDE", size=12, fill=DIRTY, stroke=POS)
    t2, g_t2 = node(255, 230, "Невідтворюване оточення:\n• Різні версії GCC у розробників\n• Конфлікти версій Python та SDK\n• Важкі GUI IDE на серверах CI/CD", size=12, fill=DIRTY, stroke=POS)
    t3, g_t3 = node(255, 345, "Проблема: «Працює лише на моїй машині»\nПомилки лінкування через зміщення символів", size=12, fill=BG, stroke=POS, bold=True)

    parts += [t1, t2, t3, down_arr(g_t1, g_t2, color=POS), down_arr(g_t2, g_t3, color=POS)]

    # Герметичний підхід PlatformIO
    parts.append(rect(525, 50, 440, 400, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    parts.append(text(745, 80, "Герметична ізоляція PlatformIO", size=14.5, bold=True, color=FIELD))

    p1, g_p1 = node(745, 135, "Ізольоване сховище: ~/.platformio/\npackages/toolchain-gccarmnoneeabi@1.90301.200702\npackages/toolchain-xtensa-esp32@8.4.0\npackages/framework-arduinoespressif32@3.20014.0", size=11.5, fill=BLUE_BG, stroke=NEG)
    p2, g_p2 = node(745, 240, "Локальні залежності: .pio/libdeps/<env>/\nБібліотеки ізольовані для кожного таргету,\nжорстка фіксація версій у platformio.ini", size=12, fill=CLEAN, stroke=FIELD)
    p3, g_p3 = node(745, 345, "Результат: 100% відтворюваність збірки\nДетермінізм у безголовому CI/CD Docker-контейнері", size=12, fill=CLEAN, stroke=FIELD, bold=True)

    parts += [p1, p2, p3, down_arr(g_p1, g_p2, color=NEG), down_arr(g_p2, g_p3, color=FIELD)]

    render(os.path.join(IMG, "packages-isolation.svg"), W, H, *parts,
           title="Організація пакетів і тулчейнів: системний хаос проти герметичної ізоляції")


if __name__ == "__main__":
    fig_pio_architecture()
    fig_ldf_modes()
    fig_packages_isolation()
    print("All figures generated successfully.")
