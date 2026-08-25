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
WHITE = "#ffffff"


# ── 1. Часова шкала завантаження: від Reset Vector до start_kernel ───────────
def fig_timeline():
    W, H = 1440, 720
    p = []

    p.append(text(W / 2, 48, "Хронологічна послідовність завантаження ядра Linux", size=18, bold=True))

    steps = [
        ("1. Reset Vector", "0xFFFFFFF0 / RVBAR_EL3", "Подача живлення POWER GOOD.\nПроцесор запускається у режимі\nініціалізації. Стрибок на BIOS/UEFI.", WARM_FILL),
        ("2. Прошивка", "BIOS / UEFI Firmware", "Ініціалізація RAM, шин PCI/PCIe.\nВибір пристрою завантаження.\nПередача коду завантажувача.", GREY_FILL),
        ("3. Завантажувач", "GRUB / EFI Stub", "Зчитування vmlinuz та initrd.\nЗаповнення boot_params (Zero Page).\nСтрибок у startup_32/64.", BLUE_FILL),
        ("4. Розпакувальник", "extract_kernel()", "Визначення адреси (KASLR).\nРозпакування стиснутого vmlinux.\nПобудова тимчасового MMU.", BLUE_FILL),
        ("5. Голова ядра", "startup_64 (head_64.S)", "Налаштування CR3 (early_top_pgt).\nСтрибок у High Canonical Space\n(0xFFFFFFFF81000000).", GREEN_FILL),
        ("6. C-Вхід ядра", "start_kernel()", "Ініціалізація підсистем пам'яті,\nIDT, переривань, таймерів,\ninitcalls та запуск PID 1.", GREEN_FILL)
    ]

    bw = 200
    gap = 26
    start_x = (W - (len(steps) * bw + (len(steps) - 1) * gap)) / 2
    top_y = 96

    for i, (title, sub, desc, fill) in enumerate(steps):
        x = start_x + i * (bw + gap)
        # Блок етапу
        p.append(rect(x, top_y, bw, 420, fill=WHITE, stroke=MUTED, sw=1.2, rx=10))
        p.append(fitbox(x + 10, top_y + 16, bw - 20, 52, title, size=15, bold=True, fill=fill, stroke=MUTED, sw=1.2))
        p.append(fitbox(x + 10, top_y + 78, bw - 20, 36, sub, size=12, bold=True, fill=WHITE, stroke=MUTED, sw=1.0))
        p.append(fitbox(x + 12, top_y + 126, bw - 24, 274, desc, size=13, fill=WHITE, stroke=WHITE, sw=0.0))

        # Стрілка до наступного
        if i < len(steps) - 1:
            arrow_x1 = x + bw + 2
            arrow_x2 = x + bw + gap - 2
            p.append(arrow(arrow_x1, top_y + 210, arrow_x2, top_y + 210))

    # Нижня узагальнююча панель
    p.append(fitbox(start_x, 546, len(steps) * bw + (len(steps) - 1) * gap, 130,
                    "Ключовий розрив середовища: завантажувач передає керування у фізичному (або ранньому 32/64-бітному) режимі,\n"
                    "тоді як start_kernel() вимагає повністю налаштованого 64-бітного віртуального простору High Canonical Memory.\n"
                    "Увесь ассемблерний код head_64.S існує лише для того, щоб побудувати цей міст без сторонньої допомоги.",
                    size=14, fill=WARM_FILL, stroke=MUTED, sw=1.2))

    render(os.path.join(IMG, 'boot-timeline.svg'), W, H, *p)


# ── 2. Перехід віртуальної пам'яті (Identity Map -> High Canonical) ──────────
def fig_paging():
    W, H = 1400, 760
    p = []

    p.append(text(W / 2, 46, "Подвійне відображення пам'яті під час переходу в High Canonical Space", size=18, bold=True))

    left_x, left_w = 60, 580
    right_x, right_w = 760, 580
    top_y = 86

    # Лівий блок — Фізична пам'ять
    p.append(rect(left_x, top_y, left_w, 480, fill=WHITE, stroke=MUTED, sw=1.2, rx=10))
    p.append(fitbox(left_x + 20, top_y + 16, left_w - 40, 44, "Фізичний простір RAM (Physical Memory)", size=16, bold=True, fill=GREY_FILL, stroke=MUTED, sw=1.2))

    p.append(fitbox(left_x + 30, top_y + 80, left_w - 60, 60, "0x0000000000000000 .. 0x00000000000FFFFF\nНизька пам'ять (Real Mode Vector, BIOS Data Area)", size=13, fill=WHITE, stroke=MUTED, sw=1.0))
    p.append(fitbox(left_x + 30, top_y + 160, left_w - 60, 70, "0x0000000001000000\nРозпакований образ vmlinux (Фізична адреса завантаження)", size=14, bold=True, fill=BLUE_FILL, stroke=NEG, sw=1.4))
    p.append(fitbox(left_x + 30, top_y + 250, left_w - 60, 190, "ранні таблиці сторінок (early_top_pgt):\n"
                                                                "• PML4[0] -> Identity Mapping (0x01000000 -> 0x01000000)\n"
                                                                "  Захист від Page Fault при зміні CR3\n"
                                                                "• PML4[511] -> High Canonical Mapping\n"
                                                                "  (0xFFFFFFFF81000000 -> 0x01000000)", size=13, fill=WARM_FILL, stroke=MUTED, sw=1.2))

    # Правий блок — Віртуальний простір ядра
    p.append(rect(right_x, top_y, right_w, 480, fill=WHITE, stroke=MUTED, sw=1.2, rx=10))
    p.append(fitbox(right_x + 20, top_y + 16, right_w - 40, 44, "Віртуальний простір (64-bit Virtual Space)", size=16, bold=True, fill=GREY_FILL, stroke=MUTED, sw=1.2))

    p.append(fitbox(right_x + 30, top_y + 80, right_w - 60, 90, "Нижня віртуальна адреса (Identity Map / user space):\n0x0000000001000000\n(Тимчасово діє до розриву в secondary_startup_64)", size=13, fill=RED_FILL, stroke=MUTED, sw=1.0))
    p.append(fitbox(right_x + 30, top_y + 200, right_w - 60, 110, "Верхній канонічний простір ядра (Kernel High Mapping):\n0xFFFFFFFF81000000\nСекції ядра: .text, .rodata, .data, .bss, .init.text", size=14, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=1.4))
    p.append(fitbox(right_x + 30, top_y + 330, right_w - 60, 110, "Пряме відображення всієї фізичної пам'яті (page_offset_base):\n0xFFFF888000000000 .. direct mapping zone", size=13, fill=WHITE, stroke=MUTED, sw=1.0))

    # Стрілка між ними
    p.append(arrow(left_x + left_w + 10, top_y + 195, right_x - 10, top_y + 255))
    p.append(text((left_x + left_w + right_x) / 2, top_y + 210, "movabs + jmp", size=14, bold=True, color=NEG))

    # Нижня панель
    p.append(fitbox(left_x, 586, right_x + right_w - left_x, 130,
                    "Перехід у старший канонічний простір відбувається за два кроки:\n"
                    "1. Завантаження CR3 новою таблицею early_top_pgt (поточна інструкція продовжує виконуватися через Identity Map).\n"
                    "2. Абсолютний непрямий стрибок (movabs $secondary_startup_64, %rax; jmp *%rax) переносить виконання на віртуальну адресу 0xFFFFFFFF81000000.\n"
                    "Після цього низькі таблиці Identity Map очищаються і стають недоступними.",
                    size=14, fill=WARM_FILL, stroke=MUTED, sw=1.2))

    render(os.path.join(IMG, 'paging-transition.svg'), W, H, *p)


# ── 3. Анатомія образу vmlinuz (bzImage) ─────────────────────────────────────
def fig_vmlinuz_structure():
    W, H = 1400, 720
    p = []

    p.append(text(W / 2, 46, "Структура образу vmlinuz (bzImage) та завантажувальний заголовок", size=18, bold=True))

    top_y = 86
    fw = 1280
    fx = (W - fw) / 2

    p.append(rect(fx, top_y, fw, 460, fill=WHITE, stroke=MUTED, sw=1.2, rx=10))

    # Заголовок
    p.append(fitbox(fx + 20, top_y + 20, 380, 200,
                    "16-bit Boot Sector & Setup Code\n\n"
                    "• Offset 0x01F1: setup_header\n"
                    "• Header signature: \"HdrS\" (0x53726448)\n"
                    "• Boot protocol version (e.g. 0x020f)\n"
                    "• code32_start (початкова адреса 32-біт)\n"
                    "• cmd_line_ptr & ramdisk_image",
                    size=13, fill=WARM_FILL, stroke=MUTED, sw=1.2))

    # Код розпакування
    p.append(fitbox(fx + 420, top_y + 20, 420, 200,
                    "Decompressor Engine\n(head_64.S + extract_kernel.c)\n\n"
                    "• startup_32 / startup_64 (вхід)\n"
                    "• Алгоритми розпакування: LZ4, ZSTD, XZ\n"
                    "• KASLR розрахунок випадкового зсуву\n"
                    "• Будування ранніх PML4 таблиць сторінок",
                    size=13, fill=BLUE_FILL, stroke=NEG, sw=1.2))

    # Стиснутий payload
    p.append(fitbox(fx + 860, top_y + 20, 400, 200,
                    "Compressed Payload (piggy.o)\n\n"
                    "• Повний ELF-дискрет ядра vmlinux\n"
                    "• Скомпонований під віртуальну адресу\n"
                    "  0xFFFFFFFF81000000\n"
                    "• Розпаковується у RAM функцією\n"
                    "  extract_kernel()",
                    size=13, fill=GREEN_FILL, stroke=FIELD, sw=1.2))

    # Нижня схема результату розпакування
    p.append(fitbox(fx + 20, top_y + 240, fw - 40, 190,
                    "Результат роботи розпакувальника у фізичній пам'яті (RAM):\n\n"
                    "[ Фізичний адресний простір: 0x01000000 (або KASLR Base) ]\n"
                    "┌─────────────────────┬─────────────────────┬─────────────────────┬─────────────────────┐\n"
                    "│ .text (startup_64)  │ .rodata (таблиці)   │ .data (змінні)      │ .init.text (init)   │\n"
                    "└─────────────────────┴─────────────────────┴─────────────────────┴─────────────────────┘\n"
                    "Після розпакування розпакувальник передає керування на розпаковану startup_64 у коді vmlinux.",
                    size=13, fill=GREY_FILL, stroke=MUTED, sw=1.2))

    # Нижня панель
    p.append(fitbox(fx, 566, fw, 120,
                    "Файл vmlinuz — це саморозпаковуваний шар. Він поєднує в одному двійковому файлі стандартизований заголовок boot_params,\n"
                    "автономний розпакувальник зі своїми таблицями сторінок та стиснутий ELF-образ vmlinux.\n"
                    "Це дозволяє завантажувачу працювати за єдиним протоколом незалежно від того, як згодом буде розпаковано ядро.",
                    size=14, fill=WARM_FILL, stroke=MUTED, sw=1.2))

    render(os.path.join(IMG, 'vmlinuz-structure.svg'), W, H, *p)


if __name__ == '__main__':
    fig_timeline()
    fig_paging()
    fig_vmlinuz_structure()
    print("ok")
