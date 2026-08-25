# -*- coding: utf-8 -*-
"""Фігури до теми «Цільовий тріплет і sysroot»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

WARN_FILL = "#fdecea"
OK_FILL = "#eaf5ec"
ACCENT_FILL = "#eef4fd"


# ── 1. Анатомія цільового тріплета (Target Triple) ───────────────────────────
def fig_target_triple_anatomy():
    W, H = 1060, 560
    frags = []

    frags.append(text(530, 32, "Анатомія та декомпозиція цільового кортежу (Target Triple)", size=16, bold=True))

    # Загальний шаблон: arch - vendor - os - abi
    body, _, _ = textbox(160, 80, [
        "1. Архітектура (arch)",
        "ISA, розрядність, порядок байтів",
        "Приклади: x86_64, aarch64,",
        "armv7-a, riscv64, thumbv7em",
    ], size=12, fill=ACCENT_FILL, stroke=NEG)
    frags.append(body)

    body, _, _ = textbox(405, 80, [
        "2. Виробник (vendor)",
        "Організація / постачальник",
        "Приклади: unknown, none,",
        "pc, w64, apple, poky",
    ], size=12, fill=FILL, stroke=LINE)
    frags.append(body)

    body, _, _ = textbox(655, 80, [
        "3. Операційна система (os)",
        "Ядро або системне середовище",
        "Приклади: linux, none (bare-metal),",
        "windows, darwin, android",
    ], size=12, fill=ACCENT_FILL, stroke=NEG)
    frags.append(body)

    body, _, _ = textbox(905, 80, [
        "4. Двійковий інтерфейс (abi/libc)",
        "Конвенція викликів, плаваюча кома, libc",
        "Приклади: gnu (glibc), musl,",
        "eabi, gnueabihf, msvc, android",
    ], size=12, fill=OK_FILL, stroke=FIELD)
    frags.append(body)

    # Сполучні лінії між компонентами у заголовку
    frags.append(text(282, 80, "—", size=20, color=MUTED, bold=True))
    frags.append(text(530, 80, "—", size=20, color=MUTED, bold=True))
    frags.append(text(780, 80, "—", size=20, color=MUTED, bold=True))

    # Розділювач
    frags.append(line(40, 140, 1020, 140, color=LINE, dash="4,4"))

    # Приклади розбору конкретних тріплетів
    frags.append(text(530, 165, "Типові канонічні кортежі та їхній вплив на кодогенерацію", size=14, bold=True))

    # Приклад 1: aarch64-unknown-linux-gnu
    body, _, _ = textbox(270, 245, [
        "aarch64-unknown-linux-gnu",
        "• arch: 64-бітний ARMv8-A Little-Endian",
        "• vendor: unknown (універсальний дистрибутив)",
        "• os: Linux (системні виклики через svc)",
        "• abi: GNU EABI64 з бібліотекою GNU C (glibc)",
        "Ціль: Сервери та SBC (Raspberry Pi 4, Ubuntu/Debian)",
    ], size=11.5, fill=OK_FILL, stroke=FIELD)
    frags.append(body)

    # Приклад 2: arm-none-eabi
    body, _, _ = textbox(790, 245, [
        "arm-none-eabi",
        "• arch: 32-бітний ARM (Cortex-M / Cortex-R)",
        "• vendor: none (немає прив'язки до вендора)",
        "• os: none (Bare-metal, автономна прошивка)",
        "• abi: ARM EABI (Newlib/Picolibc, софтварна FPU)",
        "Ціль: Мікроконтролери STM32, NXP, RP2040",
    ], size=11.5, fill=ACCENT_FILL, stroke=NEG)
    frags.append(body)

    # Приклад 3: arm-linux-gnueabihf
    body, _, _ = textbox(270, 395, [
        "arm-linux-gnueabihf",
        "• arch: 32-бітний ARMv7-A",
        "• os: Linux",
        "• abi: GNU EABI + Hard-Float (hf)",
        "Регістри: апаратні VFP/NEON для аргументів float",
        "Несумісний бінарно з arm-linux-gnueabi (Soft-Float)!",
    ], size=11.5, fill=WARN_FILL, stroke=POS)
    frags.append(body)

    # Приклад 4: x86_64-w64-mingw32
    body, _, _ = textbox(790, 395, [
        "x86_64-w64-mingw32",
        "• arch: 64-бітний x86-64 (AMD64)",
        "• vendor: w64 (проєкт MinGW-w64)",
        "• os: Windows (Win32/Win64 API, підсистема PE/COFF)",
        "• abi: Microsoft x64 calling convention (MSVCRT/UCRT)",
        "Ціль: Крос-компіляція Windows .exe/.dll з-під Linux",
    ], size=11.5, fill=FILL, stroke=LINE)
    frags.append(body)

    # Нижній висновок
    body, _, _ = textbox(530, 505, [
        "Тулчейн формує префікс команд: <triple>-gcc, <triple>-ld, <triple>-objcopy (GCC)",
        "або передається єдиному компілятору через прапорець clang --target=<triple>",
    ], size=12, fill=FILL, stroke=LINE)
    frags.append(body)

    render(os.path.join(IMG, "target-triple-anatomy.svg"), W, H, *frags,
           title="Анатомія та декомпозиція цільового кортежу (Target Triple)")


# ── 2. Концепція Sysroot та ізоляція системних файлів ────────────────────────
def fig_sysroot_directory_structure():
    W, H = 1060, 560
    frags = []

    frags.append(text(530, 32, "Концепція Sysroot: ізоляція цільових заголовків та бібліотек від хоста", size=16, bold=True))

    # Ліва колонка: Хостова система (Host Root: /)
    body, _, _ = textbox(240, 95, [
        "Хостова файлова система (/)",
        "Архітектура комп'ютера збірки (x86_64)",
    ], size=13, fill=FILL, stroke=LINE, bold=True)
    frags.append(body)

    body, _, _ = textbox(240, 215, [
        "/usr/include",
        "• Заголовки хостового glibc 2.38",
        "• x86_64 системні типи та макроси",
        "• struct stat з 64-бітними зсувами",
    ], size=11.5, fill=WARN_FILL, stroke=POS)
    frags.append(body)

    body, _, _ = textbox(240, 355, [
        "/usr/lib / /lib",
        "• x86_64 ELF динамічні бібліотеки",
        "• libc.so.6, libm.so.6 (x86_64 ABI)",
        "• Несумісні з цільовим процесором!",
    ], size=11.5, fill=WARN_FILL, stroke=POS)
    frags.append(body)

    # Центральний блок: Прапорець компілятора
    body, _, _ = textbox(530, 285, [
        "Крос-компілятор / Лінкер",
        "Прапорець: --sysroot=/opt/sysroot-arm64",
        "Перенаправляє абсолютні системні",
        "шляхи /usr/include та /usr/lib",
        "усередину ізольованого каталогу",
    ], size=12, fill=ACCENT_FILL, stroke=NEG)
    frags.append(body)

    # Стрілка блокування хоста
    frags.append(arrow(400, 285, 335, 285, color=POS))
    frags.append(text(370, 270, "блокує", size=11, color=POS, bold=True))

    # Стрілка звернення до sysroot
    frags.append(arrow(660, 285, 725, 285, color=FIELD))
    frags.append(text(690, 270, "дозволяє", size=11, color=FIELD, bold=True))

    # Права колонка: Ізольований Sysroot цілі (/opt/sysroot-arm64)
    body, _, _ = textbox(820, 95, [
        "Цільовий Sysroot (/opt/sysroot-arm64)",
        "Архітектура цільового пристрою (AArch64)",
    ], size=13, fill=OK_FILL, stroke=FIELD, bold=True)
    frags.append(body)

    body, _, _ = textbox(820, 215, [
        "/opt/sysroot-arm64/usr/include",
        "• Заголовки цільової системи (ARM64)",
        "• Відповідають цільовому ядру та libc",
        "• Коректні типи time_t, розкладки struct",
    ], size=11.5, fill=OK_FILL, stroke=FIELD)
    frags.append(body)

    body, _, _ = textbox(820, 355, [
        "/opt/sysroot-arm64/usr/lib",
        "• AArch64 ELF бібліотеки",
        "• libc.so.6, libpthread.so (AArch64 ABI)",
        "• Відносні symlink: libz.so -> libz.so.1",
    ], size=11.5, fill=OK_FILL, stroke=FIELD)
    frags.append(body)

    # Нижня плашка: Пастка абсолютних символічних посилань
    body, _, _ = textbox(530, 480, [
        "Пастка абсолютних symlink: посилання libfoo.so -> /lib/libfoo.so.1 усередині sysroot втече на хост!",
        "Рішення: санація посилань у відносні (relative: libfoo.so -> ../../lib/libfoo.so.1) або використання ld --sysroot",
    ], size=11.5, fill=FILL, stroke=LINE)
    frags.append(body)

    render(os.path.join(IMG, "sysroot-directory-structure.svg"), W, H, *frags,
           title="Концепція Sysroot: ізоляція цільових заголовків та бібліотек від хоста")


# ── 3. Маршрутизація пошуку в CMake через CMAKE_FIND_ROOT_PATH ───────────────
def fig_cmake_find_root_path_matrix():
    W, H = 1060, 560
    frags = []

    frags.append(text(530, 32, "Політики маршрутизації пошуку в CMake: CMAKE_FIND_ROOT_PATH_MODE_*", size=16, bold=True))

    # Лівий блок: Команди пошуку CMake
    body, _, _ = textbox(180, 160, [
        "find_program(PROTOC protoc)",
        "find_program(PYTHON python3)",
        "Ціль: інструменти генерації коду",
        "Мусять запускатися на хості!",
    ], size=12, fill=ACCENT_FILL, stroke=NEG)
    frags.append(body)

    body, _, _ = textbox(180, 380, [
        "find_path(OPENSSL_INCLUDE openssl/ssl.h)",
        "find_library(OPENSSL_LIB ssl)",
        "find_package(ZLIB REQUIRED)",
        "Ціль: заголовки й бібліотеки лінкування",
    ], size=12, fill=ACCENT_FILL, stroke=NEG)
    frags.append(body)

    # Центральний блок: Політики CMake Toolchain
    body, _, _ = textbox(530, 160, [
        "CMAKE_FIND_ROOT_PATH_MODE_PROGRAM = NEVER",
        "• Ігнорує CMAKE_SYSROOT та CMAKE_FIND_ROOT_PATH",
        "• Шукає виключно в хостових /usr/bin, /usr/local/bin",
        "• Результат: виконуваний x86_64 бінарник на хості",
    ], size=11.5, fill=OK_FILL, stroke=FIELD)
    frags.append(body)

    body, _, _ = textbox(530, 380, [
        "CMAKE_FIND_ROOT_PATH_MODE_INCLUDE = ONLY",
        "CMAKE_FIND_ROOT_PATH_MODE_LIBRARY = ONLY",
        "CMAKE_FIND_ROOT_PATH_MODE_PACKAGE = ONLY",
        "• Додає CMAKE_SYSROOT префікс до кожного шляху",
        "• Повністю блокує хостові /usr/include та /usr/lib",
    ], size=11.5, fill=OK_FILL, stroke=FIELD)
    frags.append(body)

    # Стрілки
    frags.append(arrow(310, 160, 360, 160))
    frags.append(arrow(310, 380, 360, 380))

    frags.append(arrow(700, 160, 750, 160))
    frags.append(arrow(700, 380, 750, 380))

    # Правий блок: Результат резолвінгу
    body, _, _ = textbox(885, 160, [
        "Хостовий бінарник",
        "/usr/bin/protoc",
        "Архітектура: x86_64",
        "Виконується генератором",
    ], size=11.5, fill=FILL, stroke=LINE)
    frags.append(body)

    body, _, _ = textbox(885, 380, [
        "Цільові артефакти",
        "${SYSROOT}/usr/include/openssl",
        "${SYSROOT}/usr/lib/libssl.so",
        "Архітектура: AArch64",
    ], size=11.5, fill=FILL, stroke=LINE)
    frags.append(body)

    # Попередження про небезпеку режиму BOTH
    body, _, _ = textbox(530, 495, [
        "Небезпека режиму BOTH: якщо бібліотека відсутня в sysroot, CMake тихо підхопить хостову x86_64 бібліотеку,",
        "що спричинить збій на стадії компонування. Для цільових залежностей завжди використовуйте режим ONLY!",
    ], size=11.5, fill=WARN_FILL, stroke=POS)
    frags.append(body)

    render(os.path.join(IMG, "cmake-find-root-path-matrix.svg"), W, H, *frags,
           title="Політики маршрутизації пошуку в CMake: CMAKE_FIND_ROOT_PATH_MODE_*")


if __name__ == "__main__":
    fig_target_triple_anatomy()
    fig_sysroot_directory_structure()
    fig_cmake_find_root_path_matrix()
    print("Фігури для target-triple-sysroot згенеровано успішно.")
