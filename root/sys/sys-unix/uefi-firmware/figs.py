# -*- coding: utf-8 -*-
"""Фігури до теми «UEFI: прошивка як середовище виконання»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)

GREEN_FILL = "#eaf7ef"
RED_FILL = "#fdecea"
BLUE_FILL = "#eaf0fd"
GREY_FILL = "#f4f6f8"


# ── 1. Системна таблиця як корінь і різна доля її гілок ────────────────────
def fig_system_table():
    W, H = 1400, 560
    f = []

    f.append(text(222, 78, "EFI_SYSTEM_TABLE — усе, що дістає точка входу",
                  size=13, color=MUTED, bold=True))
    f.append(text(942, 78, "що за цим стоїть і скільки воно живе",
                  size=13, color=MUTED, bold=True))

    left = [
        (100, "ConIn / ConOut\nготова консоль без драйвера", GREY_FILL, MUTED),
        (190, "BootServices\nпослуги завантаження", GREEN_FILL, FIELD),
        (280, "RuntimeServices\nпослуги виконання", BLUE_FILL, NEG),
        (370, "ConfigurationTable[]\nтаблиці налаштувань", GREY_FILL, INK),
    ]
    for y, s, fill, stroke in left:
        f.append(fitbox(60, y, 324, 64, s, size=13, fill=fill, stroke=stroke))

    panels = [
        (165, "пам'ять · події й таймери · дескриптори та протоколи · запуск образів · вихід",
         GREEN_FILL, FIELD, "зникають у мить ExitBootServices: покажчики стають недійсними"),
        (285, "змінні незалежної пам'яті · годинник · перезавантаження · оновлення прошивки",
         BLUE_FILL, NEG, "лишаються, поки жива система, і переїжджають в адресний простір ядра"),
        (405, "ACPI · SMBIOS — адреси структур даних, а не функцій",
         GREY_FILL, INK, "ядро перечитує їх і звільняє ту пам'ять, яку дозволено звільнити"),
    ]
    for y, s, fill, stroke, note in panels:
        f.append(fitbox(552, y, 780, 72, s, size=13, fill=fill, stroke=stroke))
        f.append(text(942, y + 96, note, size=12, color=MUTED))

    f.append(arrow(390, 222, 546, 201))
    f.append(arrow(390, 312, 546, 321))
    f.append(arrow(390, 402, 546, 441))

    render(os.path.join(IMG, 'system-table.svg'), W, H, *f,
           title="Системна таблиця EFI: три гілки з різною тривалістю життя")


# ── 2. Дескриптори й протоколи: пошук за іменем ────────────────────────────
def fig_handles_protocols():
    W, H = 1400, 530
    f = []

    f.append(text(200, 100, "програма", size=13, color=MUTED, bold=True))
    f.append(text(1040, 100, "база дескрипторів прошивки", size=13, color=MUTED, bold=True))

    f.append(fitbox(50, 120, 300, 80,
                    "завантажувач:\n«хто вміє читати файли?»", size=13,
                    fill=GREY_FILL, stroke=INK))
    f.append(arrow(200, 206, 200, 244))
    f.append(fitbox(50, 250, 300, 70, "LocateProtocol(ім'я)", size=13,
                    fill=GREEN_FILL, stroke=FIELD))

    rows = [
        (130, "дескриптор диска",
         "блоковий доступ  ·  шлях до пристрою", GREY_FILL, MUTED),
        (250, "дескриптор розділу",
         "проста файлова система  ·  блоковий доступ\nшлях до пристрою", GREEN_FILL, FIELD),
        (370, "дескриптор відеовиходу",
         "графічний вивід  ·  шлях до пристрою", GREY_FILL, MUTED),
    ]
    for y, h, p, fill, stroke in rows:
        f.append(fitbox(500, y, 230, 70, h, size=13, fill=BG, stroke=INK))
        f.append(fitbox(760, y, 560, 70, p, size=13, fill=fill, stroke=stroke))

    f.append(arrow(356, 285, 754, 285))
    f.append(text(555, 264, "збіг за іменем", size=12, color=MUTED))
    f.append(arrow(756, 320, 736, 320))

    f.append(text(700, 480,
                  "ім'я протоколу — випадкове 128-бітне число, тож нові послуги додають, "
                  "ні з ким не домовляючись",
                  size=12, color=MUTED))

    render(os.path.join(IMG, 'handles-protocols.svg'), W, H, *f,
           title="Дескриптори й протоколи: пошук потрібної послуги за іменем")


# ── 3. Вихід із послуг завантаження ────────────────────────────────────────
def fig_exit_boot_services():
    W, H = 1400, 640
    f = []

    f.append(text(700, 66, "передача керування", size=13, color=MUTED, bold=True))

    f.append(fitbox(60, 88, 380, 64, "GetMemoryMap → карта і ключ", size=13,
                    fill=GREY_FILL, stroke=INK))
    f.append(fitbox(520, 88, 380, 64, "ExitBootServices(образ, ключ)", size=13,
                    fill=GREEN_FILL, stroke=FIELD))
    f.append(fitbox(980, 88, 360, 64, "успіх: машина ваша", size=13,
                    fill=BLUE_FILL, stroke=NEG))
    f.append(arrow(446, 120, 514, 120))
    f.append(arrow(906, 120, 974, 120))

    f.append(line(710, 152, 710, 200, color=POS))
    f.append(line(710, 200, 250, 200, color=POS))
    f.append(arrow(250, 200, 250, 158, color=POS))
    f.append(text(480, 232,
                  "ключ застарів — карту перечитують, і між читанням та виходом не роблять нічого",
                  size=12, color=POS))

    sides = [
        (60, "поки живуть послуги завантаження", GREEN_FILL, FIELD,
         ["пам'яттю розпоряджається прошивка",
          "таймерні події спрацьовують",
          "пристроями керують драйвери прошивки",
          "ConOut малює текст на екрані"]),
        (740, "після виходу", BLUE_FILL, NEG,
         ["пам'ять типів Loader* і BootServices* вільна",
          "покажчики на послуги завантаження недійсні",
          "консолі немає: друк = чорний екран",
          "лишилися послуги виконання й карта пам'яті"]),
    ]
    for x, head, fill, stroke, items in sides:
        f.append(fitbox(x, 300, 600, 48, head, size=14, fill=fill, stroke=stroke, bold=True))
        for i, s in enumerate(items):
            f.append(fitbox(x, 364 + i * 60, 600, 52, s, size=13, fill=BG, stroke=MUTED))

    render(os.path.join(IMG, 'exit-boot-services.svg'), W, H, *f,
           title="Вихід із послуг завантаження: ключ карти пам'яті й стан машини до і після")


# ── 4. Часова смуга: від Boot Initiative до UEFI 2.11 ──────────────────────
def fig_efi_timeline():
    W, H = 1320, 900
    f = []

    f.append(text(660, 46, "Хто веде специфікацію: сірий — Intel сам · зелений — консорціум UEFI Forum",
                  size=13, color=MUTED, bold=True))

    rows = [
        ("1994", "HP і Intel оголошують спільну роботу над архітектурою IA-64", GREY_FILL, MUTED),
        ("1998", "Intel Boot Initiative: прошивку переписують з нуля, згодом назва — EFI", GREY_FILL, MUTED),
        ("2000", "EFI 1.02 у перших робочих станціях і серверах Itanium", GREY_FILL, MUTED),
        ("2002", "EFI 1.10 — остання версія, яку веде Intel", GREY_FILL, MUTED),
        ("2004", "Intel відкриває код прошивки: Tiano, далі EDK і EDK II", GREY_FILL, MUTED),
        ("липень 2005", "Intel передає специфікацію новоутвореному UEFI Forum", GREEN_FILL, FIELD),
        ("31.01.2006", "UEFI 2.0 — перша версія від консорціуму", GREEN_FILL, FIELD),
        ("2006", "перші Intel-Mac: EFI уперше приходить на настільну машину", GREEN_FILL, FIELD),
        ("2011", "UEFI 2.3.1 — версія, на яку послалися вимоги сертифікації Windows 8", GREEN_FILL, FIELD),
        ("грудень 2024", "UEFI 2.11 — чинна редакція", GREEN_FILL, FIELD),
    ]
    y = 92
    for year, what, fill, stroke in rows:
        f.append(fitbox(60, y, 240, 58, year, size=13, fill=fill, stroke=stroke, bold=True))
        f.append(fitbox(330, y, 930, 58, what, size=13, fill=BG, stroke=MUTED))
        y += 78

    render(os.path.join(IMG, 'efi-timeline.svg'), W, H, *f,
           title="Від Intel Boot Initiative до UEFI 2.11: хто і коли вів специфікацію")


# ── 5. Дві дороги збірки до одного PE32+ (вставка proj-hello-uefi) ─────────
def fig_build_pipeline():
    W, H = 1380, 660
    f = []

    f.append(fitbox(510, 56, 360, 52, "hello.c\nжодного #include <stdio.h>",
                    size=13, fill=GREY_FILL, stroke=INK, bold=True))
    f.append(arrow(600, 108, 385, 144))
    f.append(arrow(780, 108, 1000, 144))

    f.append(fitbox(95, 146, 550, 44, "Дорога 1 — gnu-efi: спершу ELF, потім переклеїти",
                    size=13, fill=GREEN_FILL, stroke=FIELD, bold=True))
    f.append(fitbox(735, 146, 550, 44, "Дорога 2 — clang і lld: PE одразу",
                    size=13, fill=BLUE_FILL, stroke=NEG, bold=True))

    left = [
        (210, "gcc -ffreestanding -fshort-wchar -mno-red-zone\n-fpic -DGNU_EFI_USE_MS_ABI -c hello.c"),
        (296, "ld -shared -Bsymbolic -T elf_x86_64_efi.lds\ncrt0-efi-x86_64.o hello.o -lefi   →   hello.so (ELF!)"),
        (382, "objcopy --target efi-app-x86_64 hello.so hello.efi\nсекції переносить, підсистему пише 10"),
    ]
    for y, s in left:
        f.append(fitbox(95, y, 550, 76, s, size=12, fill=BG, stroke=FIELD))

    right = [
        (210, "clang -target x86_64-unknown-windows\n-ffreestanding -mno-red-zone -c hello.c"),
        (296, "lld-link -subsystem:efi_application\n-entry:efi_main -nodefaultlib hello.o"),
    ]
    for y, s in right:
        f.append(fitbox(735, y, 550, 76, s, size=12, fill=BG, stroke=NEG))
    f.append(fitbox(735, 382, 550, 76,
                    "CHAR16 і ms-угода про виклик тут уже рідні:\nціль сама «віндова», окремих ключів не треба",
                    size=12, fill=GREY_FILL, stroke=MUTED, color=MUTED))

    f.append(arrow(370, 462, 560, 470))
    f.append(arrow(1010, 462, 820, 470))

    f.append(fitbox(300, 474, 780, 68,
                    "hello.efi — PE32+ · Subsystem = 10 (застосунок UEFI)\n"
                    "AddressOfEntryPoint веде в efi_main, переміщення дають покласти образ будь-куди",
                    size=13, fill=GREEN_FILL, stroke=FIELD, bold=True))

    f.append(arrow(560, 546, 400, 568))
    f.append(fitbox(150, 572, 500, 64, "розділ EFI, файлова система FAT:\n\\EFI\\hello\\hello.efi",
                    size=13, fill=BG, stroke=INK))
    f.append(arrow(656, 604, 728, 604))
    f.append(fitbox(735, 572, 500, 64, "запуск: UEFI Shell · efibootmgr\n· QEMU з OVMF",
                    size=13, fill=BG, stroke=INK))

    render(os.path.join(IMG, 'build-pipeline.svg'), W, H, *f,
           title="Дві дороги збірки застосунку UEFI і спільний кінець")


# ── 6. Розкладка EFI_LOAD_OPTION по байтах (вставка api-efi-variables) ─────
def fig_load_option():
    W, H = 1400, 540
    f = []

    f.append(text(700, 62,
                  "У файлі efivarfs перші 4 байти — прапорці змінної; сам запис починається з п'ятого",
                  size=13, color=MUTED, bold=True))

    cols = [
        (60, "Attributes", "UINT32 · 4 Б", GREEN_FILL, FIELD,
         "LOAD_OPTION_ACTIVE\nі решта прапорців варіанта"),
        (320, "FilePathListLength", "UINT16 · 2 Б", GREEN_FILL, FIELD,
         "довжина шляху до пристрою\nу байтах"),
        (580, "Description", "CHAR16[] · змінна", BLUE_FILL, NEG,
         "напис у меню прошивки,\nUTF-16LE до нуля 0x0000"),
        (840, "FilePathList", "байтів рівно\nFilePathListLength", BLUE_FILL, NEG,
         "ланцюг вузлів пристрою,\nостанній — End (7f ff 04 00)"),
        (1100, "OptionalData", "решта змінної", GREY_FILL, MUTED,
         "аргументи образу; для ядра\nз EFI-заглушкою — командний рядок"),
    ]
    for x, head, size_s, fill, stroke, note in cols:
        f.append(fitbox(x, 92, 240, 44, head, size=14, fill=fill, stroke=stroke, bold=True))
        f.append(fitbox(x, 136, 240, 44, size_s, size=12, fill=BG, stroke=stroke))
        f.append(line(x + 120, 180, x + 120, 204, color=MUTED))
        f.append(fitbox(x, 204, 240, 74, note, size=12, fill=BG, stroke=MUTED))

    f.append(fitbox(60, 316, 1280, 62,
                    "зсув OptionalData = 4 + 2 + (довжина Description у байтах) + FilePathListLength",
                    size=14, fill=GREY_FILL, stroke=INK, bold=True))
    f.append(fitbox(60, 396, 1280, 62,
                    "довжина OptionalData = розмір даних змінної − цей зсув; жодного поля довжини для неї немає",
                    size=14, fill=GREY_FILL, stroke=INK))
    f.append(text(700, 500,
                  "зелений — сталий розмір · синій — змінний, читається послідовно · сірий — те, що лишилося",
                  size=12, color=MUTED))

    render(os.path.join(IMG, 'load-option.svg'), W, H, *f,
           title="EFI_LOAD_OPTION: чотири поля поспіль, три з них без сталого зсуву")


if __name__ == '__main__':
    fig_system_table()
    fig_handles_protocols()
    fig_exit_boot_services()
    fig_efi_timeline()
    fig_build_pipeline()
    fig_load_option()
    print("ok")
