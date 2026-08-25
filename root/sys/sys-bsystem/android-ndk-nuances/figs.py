# -*- coding: utf-8 -*-
"""Фігури до теми «Нюанси Android: NDK, ABI, рівень API»."""
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


# ── 1. Архітектура NDK Toolchain, Sysroot та Bionic ─────────────────────────
def fig_ndk_toolchain_sysroot():
    W, H = 1040, 530
    frags = []

    frags.append(text(520, 30, "Архітектура крос-компіляції Android NDK: від джерела до Bionic на пристрої", size=16, bold=True))

    # Лівий блок: Хостовий компілятор NDK
    body, _, _ = textbox(170, 115, [
        "Хостовий компілятор NDK",
        "clang / clang++ (LLVM)",
        "Тріплет компілятора:",
        "aarch64-linux-android29-clang",
        "Фіксує архітектуру та API level",
    ], size=11.5, fill=ACCENT_FILL, stroke=NEG)
    frags.append(body)

    # Центральний верхній блок: NDK Sysroot (Заголовки + Заглушки)
    body, _, _ = textbox(520, 115, [
        "NDK Sysroot (Час збірки на хості)",
        "1. Уніфіковані заголовки: sysroot/usr/include",
        "   Містять макроси __INTRODUCED_IN(api_level)",
        "2. Бібліотеки-заглушки (Stub libs):",
        "   platforms/android-29/arch-arm64/usr/lib/libc.so",
        "   Лише таблиця символів для lld (без тіл функцій)",
    ], size=11.5, fill=OK_FILL, stroke=FIELD)
    frags.append(body)

    frags.append(arrow(295, 115, 345, 115))

    # Правий верхній блок: Результуючий бінарник
    body, _, _ = textbox(865, 115, [
        "Цільова бібліотека ELF",
        "libapp.so (ARM64)",
        "DT_NEEDED: libc.so",
        "DT_NEEDED: libm.so",
        "Потребує Bionic API >= 29",
    ], size=11.5, fill=FILL, stroke=LINE)
    frags.append(body)

    frags.append(arrow(695, 115, 755, 115))

    # Стрілка вниз до цільового пристрою з підписом збоку
    frags.append(arrow(865, 175, 865, 275))
    frags.append(text(745, 225, "Пакування в APK / adb install", size=11, color=MUTED, bold=True))

    # Розділювач хост / пристрій
    frags.append(line(40, 255, 1000, 255, color=LINE, dash="4,4"))
    frags.append(text(120, 246, "ХОСТ (ЕТАП ЗБІРКИ)", size=10.5, color=MUTED, bold=True))
    frags.append(text(130, 270, "ПРИСТРІЙ (ANDROID RUNTIME)", size=10.5, color=MUTED, bold=True))

    # Нижній блок 1: Динамічний лінкер Android
    body, _, _ = textbox(240, 395, [
        "Динамічний лінкер пристрою",
        "/system/bin/linker64",
        "• Linker Namespaces (ізоляція)",
        "• Зчитує DT_NEEDED та розв'язує символи",
        "• Завантажує залежності з APEX/System",
    ], size=11.5, fill=FILL, stroke=LINE)
    frags.append(body)

    # Нижній блок 2: Системні бібліотеки Bionic
    body, _, _ = textbox(620, 395, [
        "Справжній Bionic libc (Цільовий пристрій)",
        "/apex/com.android.runtime/lib64/bionic/libc.so",
        "• Повноцінна реалізація системних викликів",
        "• Аллокатор Scudo / jemalloc із MTE захистом",
        "• Пряма взаємодія з ядром Linux",
    ], size=11.5, fill=OK_FILL, stroke=FIELD)
    frags.append(body)

    frags.append(arrow(390, 395, 450, 395))

    # Нижній блок 3: Ядро Linux
    body, _, _ = textbox(900, 395, [
        "Ядро Linux",
        "Syscall Dispatcher",
        "SELinux / Seccomp",
    ], size=11.5, fill=FILL, stroke=MUTED)
    frags.append(body)

    frags.append(arrow(790, 395, 830, 395))

    # З'єднувальна стрілка від лінкера до бібліотеки застосунку
    frags.append(arrow(865, 335, 390, 365))
    frags.append(text(640, 335, "dlopen(\"libapp.so\") через Linker", size=11, color=NEG, bold=True))

    render(os.path.join(IMG, "ndk-toolchain-sysroot.svg"), W, H, *frags,
           title="Архітектура крос-компіляції Android NDK: від джерела до Bionic на пристрої")


# ── 2. ODR-катастрофа з libc++_static проти libc++_shared ───────────────────
def fig_libcxx_odr_collision():
    W, H = 1040, 530
    frags = []

    frags.append(text(520, 30, "Конфлікт ODR та стану RTTI при використанні libc++_static у кількох .so", size=16, bold=True))

    # Ліва частина: Небезпечна конфігурація libc++_static
    frags.append(text(260, 68, "НЕБЕЗПЕЧНО: libc++_static у кількох модулях", size=13, color=POS, bold=True))

    body, _, _ = textbox(135, 160, [
        "libcore.so",
        "Вшито копію STL #1:",
        "• Власний стан iostreams",
        "• typeinfo(std::runtime_error) [A]",
        "• throw std::runtime_error()",
    ], size=11, fill=WARN_FILL, stroke=POS)
    frags.append(body)

    body, _, _ = textbox(385, 160, [
        "libplugin.so",
        "Вшито копію STL #2:",
        "• Власний стан iostreams",
        "• typeinfo(std::runtime_error) [B]",
        "• catch (const std::exception&)",
    ], size=11, fill=WARN_FILL, stroke=POS)
    frags.append(body)

    # Стрілка помилки без перетину з текстом
    frags.append(arrow(240, 160, 275, 160, color=POS))
    frags.append(text(260, 140, "throw", size=11, color=POS, bold=True))

    body, _, _ = textbox(260, 360, [
        "НАСЛІДКИ ПОДВІЙНОГО СТАТИЧНОГО РАНТАЙМУ:",
        "1. Збій RTTI: Адреса typeinfo [A] != typeinfo [B]",
        "   catch не впізнає тип винятку -> виклик std::terminate()",
        "2. Порушення ODR: дублювання статичних буферів та пулів пам'яті",
        "3. Збільшення розміру кожного .so на вагу коду STL",
    ], size=11.5, fill=WARN_FILL, stroke=POS)
    frags.append(body)

    frags.append(arrow(260, 235, 260, 290, color=POS))

    # Розділювач
    frags.append(line(520, 55, 520, 495, color=LINE, dash="4,4"))

    # Права частина: Правильна конфігурація libc++_shared
    frags.append(text(780, 68, "ПРАВИЛЬНО: єдиний libc++_shared.so", size=13, color=FIELD, bold=True))

    body, _, _ = textbox(650, 160, [
        "libcore.so",
        "Без власного коду STL",
        "DT_NEEDED:",
        "libc++_shared.so",
    ], size=11, fill=OK_FILL, stroke=FIELD)
    frags.append(body)

    body, _, _ = textbox(910, 160, [
        "libplugin.so",
        "Без власного коду STL",
        "DT_NEEDED:",
        "libc++_shared.so",
    ], size=11, fill=OK_FILL, stroke=FIELD)
    frags.append(body)

    # Центральний спільний STL
    body, _, _ = textbox(780, 295, [
        "libc++_shared.so (Єдиний спільний рантайм)",
        "• Єдина таблиця RTTI / typeinfo для всіх модулів",
        "• Коректна передача винятків через межі .so бібліотек",
        "• Єдиний стан потоків введення/виведення та пулів пам'яті",
    ], size=11.5, fill=OK_FILL, stroke=FIELD)
    frags.append(body)

    frags.append(arrow(650, 215, 720, 255, color=FIELD))
    frags.append(arrow(910, 215, 840, 255, color=FIELD))

    body, _, _ = textbox(780, 430, [
        "Результат: стабільна робота, передбачуваний перехоплювач",
        "винятків та мінімальний підсумковий розмір APK",
    ], size=11.5, fill=OK_FILL, stroke=FIELD)
    frags.append(body)

    frags.append(arrow(780, 350, 780, 395, color=FIELD))

    render(os.path.join(IMG, "libcxx-odr-collision.svg"), W, H, *frags,
           title="Конфлікт ODR та стану RTTI при використанні libc++_static у кількох .so")


# ── 3. Вирівнювання сегментів ELF для сторінок 16 KB ─────────────────────────
def fig_elf_page_alignment_16k():
    W, H = 1040, 530
    frags = []

    frags.append(text(520, 30, "Вимога вирівнювання сегментів ELF під розмір сторінки 16 KB (Android 15+)", size=16, bold=True))

    # Ліва частина: Старе 4 KB вирівнювання (збій на ядрі з 16 KB)
    frags.append(text(260, 68, "Старе вирівнювання (max-page-size = 4096)", size=13, color=POS, bold=True))

    body, _, _ = textbox(260, 160, [
        "ELF Заголовки (PT_LOAD сегменти)",
        "Сегмент #1 (Code): Offset 0x0000 -> VAddr 0x0000 (Aligned 4 KB)",
        "Сегмент #2 (Data): Offset 0x1000 -> VAddr 0x6000 (Aligned 4 KB)",
        "Зміщення 0x1000 НЕ кратне 16 KB (0x4000)!",
    ], size=11, fill=WARN_FILL, stroke=POS)
    frags.append(body)

    frags.append(arrow(260, 215, 260, 275, color=POS))

    body, _, _ = textbox(260, 365, [
        "Спроба завантаження на ядрі з 16 KB сторінками:",
        "mmap() ядра вимагає рівності залишків:",
        "p_vaddr % PageSize == p_offset % PageSize",
        "0x6000 % 16384 != 0x1000 % 16384 -> конфлікт сторінок пам'яті!",
        "Помилка динамічного лінкера:",
        "dlopen failed: ... LOAD segment not page-aligned",
    ], size=11, fill=WARN_FILL, stroke=POS)
    frags.append(body)

    # Розділювач
    frags.append(line(520, 55, 520, 495, color=LINE, dash="4,4"))

    # Права частина: 16 KB сумісне вирівнювання
    frags.append(text(780, 68, "16 KB сумісне вирівнювання (-Wl,-z,max-page-size=16384)", size=13, color=FIELD, bold=True))

    body, _, _ = textbox(780, 160, [
        "ELF Заголовки (PT_LOAD сегменти)",
        "Сегмент #1 (Code): Offset 0x0000 -> VAddr 0x0000 (Aligned 16 KB)",
        "Сегмент #2 (Data): Offset 0x4000 -> VAddr 0x8000 (Aligned 16 KB)",
        "Зміщення у файлі та VAddr вирівняно на межу 16384 байти",
    ], size=11, fill=OK_FILL, stroke=FIELD)
    frags.append(body)

    frags.append(arrow(780, 215, 780, 275, color=FIELD))

    body, _, _ = textbox(780, 365, [
        "Завантаження на будь-якому ядрі (4 KB або 16 KB):",
        "• Працює без модифікацій на старих 4 KB ядрах",
        "  (16384 ділиться на 4096 без залишку)",
        "• Успішно завантажується mmap() на нових 16 KB ядрах",
        "• zipalign -p 16384 гарантує правильне зміщення всередині APK",
        "Результат: сумісність з Android 15 та майбутніми версіями",
    ], size=11, fill=OK_FILL, stroke=FIELD)
    frags.append(body)

    render(os.path.join(IMG, "elf-page-alignment-16k.svg"), W, H, *frags,
           title="Вимога вирівнювання сегментів ELF під розмір сторінки 16 KB (Android 15+)")


if __name__ == "__main__":
    fig_ndk_toolchain_sysroot()
    fig_libcxx_odr_collision()
    fig_elf_page_alignment_16k()
    print("Фігури згенеровано успішно.")
