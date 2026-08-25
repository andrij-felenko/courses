# -*- coding: utf-8 -*-
"""Фігури до теми «Крос-компіляція: хост, ціль і що між ними»."""
import sys, os

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

WARN_FILL = "#fdecea"
OK_FILL = "#eaf5ec"
ACCENT_FILL = "#eef4fd"


# ── 1. Матриця конфігурацій GNU: Build, Host, Target ────────────────────────
def fig_gnu_triplets_matrix():
    W, H = 1040, 560
    frags = []

    frags.append(text(520, 30, "Канонічна тріада GNU: Build, Host і Target у конфігураціях збірки", size=16, bold=True))

    # Визначення трьох ролей зверху
    roles = [
        ("Build (Складальник)", "Машина, на якій запускається процес компілятора", "Робоча станція x86_64", 190),
        ("Host (Виконавець)", "Машина, на якій запускатиметься зібраний бінарник", "Сервер або робоча станція", 520),
        ("Target (Ціль коду)", "Архітектура, для якої компілятор створює код", "MCU, SBC або сервер", 850),
    ]
    for title, desc, ex, cx in roles:
        body, _, _ = textbox(cx, 85, [
            title,
            desc,
            f"Приклад: {ex}",
        ], size=11.5, fill=ACCENT_FILL, stroke=NEG, min_w=300)
        frags.append(body)

    frags.append(line(40, 140, 1000, 140, color=MUTED, sw=1, dash="4,4"))

    # Чотири конфігурації нижче
    configs = [
        (
            "1. Нативна збірка (Native)",
            "Build == Host == Target",
            "x86_64 -> x86_64 -> x86_64",
            "Компілятор збирається на x86_64, працює на x86_64 і генерує код для x86_64.",
            OK_FILL, FIELD, 40, 170
        ),
        (
            "2. Крос-компілятор (Cross)",
            "Build == Host != Target",
            "x86_64 -> x86_64 -> aarch64",
            "Компілятор працює на x86_64, але транслює код для процесора AArch64 (ARM64).",
            OK_FILL, FIELD, 540, 170
        ),
        (
            "3. Крос-нативна збірка (Cross-native)",
            "Build != Host == Target",
            "x86_64 -> aarch64 -> aarch64",
            "Збірка нативного компілятора для ARM64 на швидкій робочій станції x86_64.",
            ACCENT_FILL, NEG, 40, 350
        ),
        (
            "4. Канадська збірка (Canadian Cross)",
            "Build != Host != Target",
            "x86_64 -> x86_64-w64-mingw32 -> arm-none-eabi",
            "Збірка на Linux (Build) компілятора під Windows (Host), який компілюватиме під ARM (Target).",
            WARN_FILL, POS, 540, 350
        ),
    ]

    for title, rule, triple, desc, fill_c, stroke_c, x, y in configs:
        b_rect = rect(x, y, 460, 140, fill=fill_c, stroke=stroke_c, sw=1.5)
        t_title = text(x + 230, y + 26, title, size=13, bold=True, color=INK)
        t_rule = text(x + 230, y + 50, f"Рівність систем: {rule}", size=11.5, bold=True, color=stroke_c)
        t_trip = text(x + 230, y + 74, f"Тріплет: {triple}", size=11, color=LINE)
        t_desc = text(x + 230, y + 104, desc, size=10.5, color=MUTED)
        frags.extend([b_rect, t_title, t_rule, t_trip, t_desc])

    render(os.path.join(IMG, "gnu-triplets-matrix.svg"), W, H, *frags,
           title="Канонічна тріада GNU: Build, Host і Target")


# ── 2. Порядок байтів (Endianness) та моделі даних ──────────────────────────
def fig_endianness_and_data_models():
    W, H = 1040, 500
    frags = []

    frags.append(text(520, 30, "Архітектурні розбіжності: порядок байтів (Endianness) і моделі даних розрядності", size=16, bold=True))

    # Ліва колонка: Порядок байтів
    frags.append(rect(40, 60, 460, 410, fill=FILL, stroke=LINE, sw=1.2))
    frags.append(text(270, 85, "Розподіл байтів числа 0x12345678 у пам'яті", size=13.5, bold=True))

    # Little Endian
    frags.append(text(270, 118, "Little-Endian (x86_64, ARM, RISC-V): молодший байт за меншою адресою", size=10, color=FIELD, bold=True))
    le_bytes = [("0x78 (LSB)", "0x00"), ("0x56", "0x01"), ("0x34", "0x02"), ("0x12 (MSB)", "0x03")]
    for i, (b_val, addr) in enumerate(le_bytes):
        bx = 65 + i * 100
        frags.append(rect(bx, 135, 95, 45, fill=OK_FILL, stroke=FIELD, sw=1.2))
        frags.append(text(bx + 47, 155, b_val, size=11, bold=True))
        frags.append(text(bx + 47, 172, f"Адреса {addr}", size=9.5, color=MUTED))

    # Big Endian
    frags.append(text(270, 222, "Big-Endian (MIPS, SPARC, мережа): старший байт за меншою адресою", size=10, color=NEG, bold=True))
    be_bytes = [("0x12 (MSB)", "0x00"), ("0x34", "0x01"), ("0x56", "0x02"), ("0x78 (LSB)", "0x03")]
    for i, (b_val, addr) in enumerate(be_bytes):
        bx = 65 + i * 100
        frags.append(rect(bx, 240, 95, 45, fill=ACCENT_FILL, stroke=NEG, sw=1.2))
        frags.append(text(bx + 47, 260, b_val, size=11, bold=True))
        frags.append(text(bx + 47, 277, f"Адреса {addr}", size=9.5, color=MUTED))

    # Пастка прямого приведення вказівників
    trap_box, _, _ = textbox(270, 370, [
        "Пастка крос-платформного коду:",
        "uint32_t val = 0x12345678; uint8_t first = *(uint8_t*)&val;",
        "Little-Endian: first == 0x78",
        "Big-Endian:    first == 0x12 (небезпека прихованих помилок!)",
    ], size=10.5, fill=WARN_FILL, stroke=POS, min_w=420)
    frags.append(trap_box)

    # Права колонка: Моделі даних розрядності
    frags.append(rect(540, 60, 460, 410, fill=FILL, stroke=LINE, sw=1.2))
    frags.append(text(770, 85, "Моделі розрядності: розміри базових типів (у байтах)", size=13.5, bold=True))

    # Таблиця
    headers = ["Тип даних", "ILP32 (32-bit)", "LP64 (64-bit Linux)", "LLP64 (64-bit Win)"]
    col_x = [560, 675, 785, 905]

    for j, h in enumerate(headers):
        frags.append(text(col_x[j], 120, h, size=10.5, bold=True, color=INK, anchor="start" if j == 0 else "middle"))
    frags.append(line(555, 130, 985, 130, color=MUTED, sw=1))

    rows = [
        ("short", "2", "2", "2"),
        ("int", "4", "4", "4"),
        ("long", "4", "8 (увага!)", "4"),
        ("long long", "8", "8", "8"),
        ("pointer (void*)", "4", "8", "8"),
        ("size_t", "4", "8", "8"),
    ]

    for i, r in enumerate(rows):
        ry = 155 + i * 32
        fill_row = ACCENT_FILL if (i % 2 == 1) else FILL
        frags.append(rect(555, ry - 18, 430, 28, fill=fill_row, stroke="none"))
        frags.append(text(col_x[0], ry, r[0], size=11, bold=True, color=LINE, anchor="start"))
        frags.append(text(col_x[1], ry, r[1], size=11, color=INK))
        frags.append(text(col_x[2], ry, r[2], size=11, color=POS if "увага" in r[2] else INK, bold=("увага" in r[2])))
        frags.append(text(col_x[3], ry, r[3], size=11, color=INK))

    info_box, _, _ = textbox(770, 400, [
        "Наслідок для крос-компіляції:",
        "sizeof(long) відрізняється між 32-bit ціллю та 64-bit хостом,",
        "а також між Linux та Windows на одній 64-бітній архітектурі.",
    ], size=10.5, fill=OK_FILL, stroke=FIELD, min_w=420)
    frags.append(info_box)

    render(os.path.join(IMG, "endianness-and-data-models.svg"), W, H, *frags,
           title="Порядок байтів та моделі даних розрядності")


# ── 3. Вирівнювання та пакування структур даних у пам'яті ───────────────────
def fig_struct_alignment_padding():
    W, H = 1040, 480
    frags = []

    frags.append(text(520, 30, "Розбіжності вирівнювання (ABI Alignment) для однакової структури C", size=16, bold=True))

    code_box, _, _ = textbox(520, 80, [
        "struct NetworkPacket {",
        "    uint32_t header;  // 4 байти",
        "    uint64_t payload; // 8 байтів",
        "    uint16_t footer;  // 2 байти",
        "};",
    ], size=11, fill=FILL, stroke=LINE, min_w=340)
    frags.append(code_box)

    # 1. x86-32 System V ABI (4-byte alignment для uint64_t)
    frags.append(rect(40, 160, 960, 130, fill=FILL, stroke=LINE, sw=1.2))
    frags.append(text(520, 185, "x86-32 ABI (вирівнювання uint64_t за 4-байтовою межею) — розмір 16 байтів", size=12.5, bold=True, color=NEG))

    # Смужки байтів x86-32
    # 0..3: header (4B)
    frags.append(rect(80, 205, 220, 45, fill=OK_FILL, stroke=FIELD, sw=1.2))
    frags.append(text(190, 225, "header (uint32_t)", size=11, bold=True))
    frags.append(text(190, 240, "Байти 0..3 (зміщення 0)", size=9.5, color=MUTED))

    # 4..11: payload (8B)
    frags.append(rect(300, 205, 440, 45, fill=ACCENT_FILL, stroke=NEG, sw=1.2))
    frags.append(text(520, 225, "payload (uint64_t)", size=11, bold=True))
    frags.append(text(520, 240, "Байти 4..11 (зміщення 4 — вирівняно на 4 байти)", size=9.5, color=MUTED))

    # 12..13: footer (2B)
    frags.append(rect(740, 205, 110, 45, fill=OK_FILL, stroke=FIELD, sw=1.2))
    frags.append(text(795, 225, "footer", size=11, bold=True))
    frags.append(text(795, 240, "Байти 12..13", size=9.5, color=MUTED))

    # 14..15: padding (2B)
    frags.append(rect(850, 205, 110, 45, fill=WARN_FILL, stroke=POS, sw=1.2))
    frags.append(text(905, 225, "Padding (2B)", size=10.5, color=POS, bold=True))
    frags.append(text(905, 240, "Байти 14..15", size=9.5, color=MUTED))

    # 2. ARM AAPCS (32-bit та 64-bit) (8-byte alignment для uint64_t)
    frags.append(rect(40, 310, 960, 140, fill=FILL, stroke=LINE, sw=1.2))
    frags.append(text(520, 335, "ARM AAPCS / x86_64 ABI (вирівнювання uint64_t строго за 8-байтовою межею) — розмір 24 байти!", size=12.5, bold=True, color=POS))

    # 0..3: header (4B)
    frags.append(rect(80, 355, 150, 45, fill=OK_FILL, stroke=FIELD, sw=1.2))
    frags.append(text(155, 375, "header (uint32_t)", size=10.5, bold=True))
    frags.append(text(155, 390, "Байти 0..3 (зміщення 0)", size=9, color=MUTED))

    # 4..7: Padding (4B)
    frags.append(rect(230, 355, 150, 45, fill=WARN_FILL, stroke=POS, sw=1.2))
    frags.append(text(305, 375, "Padding (4B!)", size=10.5, color=POS, bold=True))
    frags.append(text(305, 390, "Байти 4..7 (діра)", size=9, color=MUTED))

    # 8..15: payload (8B)
    frags.append(rect(380, 355, 300, 45, fill=ACCENT_FILL, stroke=NEG, sw=1.2))
    frags.append(text(530, 375, "payload (uint64_t)", size=11, bold=True))
    frags.append(text(530, 390, "Байти 8..15 (зміщення 8 — зсув поля!)", size=9.5, color=MUTED))

    # 16..17: footer (2B)
    frags.append(rect(680, 355, 100, 45, fill=OK_FILL, stroke=FIELD, sw=1.2))
    frags.append(text(730, 375, "footer", size=10.5, bold=True))
    frags.append(text(730, 390, "Байти 16..17", size=9, color=MUTED))

    # 18..23: Tail Padding (6B)
    frags.append(rect(780, 355, 180, 45, fill=WARN_FILL, stroke=POS, sw=1.2))
    frags.append(text(870, 375, "Tail Padding (6B!)", size=10.5, color=POS, bold=True))
    frags.append(text(870, 390, "Байти 18..23 (доведення до 24B)", size=9, color=MUTED))

    frags.append(text(520, 430, "Передача сирої пам'яті struct між x86-32 та ARM призведе до читання сміття у полі payload!", size=11, bold=True, color=POS))

    render(os.path.join(IMG, "struct-alignment-padding.svg"), W, H, *frags,
           title="Розбіжності вирівнювання структур даних ABI")


# ── 4. Пастка кодогенераторів і подвійний тулчейн ───────────────────────────
def fig_dual_toolchain_pipeline():
    W, H = 1040, 520
    frags = []

    frags.append(text(520, 30, "Конвеєр подвійного тулчейну: генератори коду хоста та бінарники цілі", size=16, bold=True))

    # Ліва гілка: Генератор коду (Host Tool)
    frags.append(rect(40, 60, 460, 430, fill=FILL, stroke=LINE, sw=1.2))
    frags.append(text(270, 85, "Етап 1: Інструмент хоста (Host Tool)", size=13.5, bold=True, color=NEG))

    b1, _, _ = textbox(270, 130, [
        "Вихідні коди утиліти",
        "codegen_tool.c / parser.cpp",
    ], size=11, fill=ACCENT_FILL, stroke=NEG, min_w=280)
    frags.append(b1)

    frags.append(arrow(270, 160, 270, 195))

    b2, _, _ = textbox(270, 225, [
        "Нативний компілятор хоста",
        "CMAKE_C_COMPILER (Host GCC/Clang)",
        "Складання для x86_64",
    ], size=11, fill=FILL, stroke=LINE, min_w=280)
    frags.append(b2)

    frags.append(arrow(270, 260, 270, 295))

    b3, _, _ = textbox(270, 325, [
        "Виконуваний файл хоста",
        "build-host/bin/codegen",
        "Запускається прямо на робочій станції",
    ], size=11, fill=OK_FILL, stroke=FIELD, min_w=280)
    frags.append(b3)

    frags.append(arrow(270, 360, 270, 395))

    b4, _, _ = textbox(270, 430, [
        "Генерація джерельних файлів",
        "./codegen -o generated_tables.c",
        "Створює таблиці констант / парсер",
    ], size=11, fill=OK_FILL, stroke=FIELD, min_w=280)
    frags.append(b4)

    # Зв'язок між гілками: згенерований файл передається направо
    frags.append(arrow(425, 430, 615, 330, color=POS, sw=2))
    frags.append(text(520, 370, "Згенерований C/C++", size=10.5, color=POS, bold=True))

    # Права гілка: Цільовий артефакт (Target Binary)
    frags.append(rect(540, 60, 460, 430, fill=FILL, stroke=LINE, sw=1.2))
    frags.append(text(770, 85, "Етап 2: Цільова прошивка / застосунок (Target)", size=13.5, bold=True, color=FIELD))

    t1, _, _ = textbox(770, 130, [
        "Вихідні коди проєкту",
        "main.c + app_logic.cpp",
    ], size=11, fill=ACCENT_FILL, stroke=NEG, min_w=280)
    frags.append(t1)

    frags.append(arrow(770, 160, 770, 195))

    t2, _, _ = textbox(770, 235, [
        "Крос-компілятор цілі",
        "CMAKE_TOOLCHAIN_FILE",
        "aarch64-linux-gnu-gcc / arm-none-eabi-gcc",
        "Лінкування з цільовим sysroot",
    ], size=11, fill=FILL, stroke=LINE, min_w=300)
    frags.append(t2)

    frags.append(arrow(770, 280, 770, 315))

    t3, _, _ = textbox(770, 345, [
        "Компіляція згенерованого коду",
        "generated_tables.c + main.c",
    ], size=11, fill=ACCENT_FILL, stroke=NEG, min_w=280)
    frags.append(t3)

    frags.append(arrow(770, 375, 770, 410))

    t4, _, _ = textbox(770, 440, [
        "Кінцевий цільовий бінарник",
        "firmware.elf / app-arm64",
        "Працює на цільовому пристрої (ARM/RISC-V)",
    ], size=11, fill=OK_FILL, stroke=FIELD, min_w=300)
    frags.append(t4)

    render(os.path.join(IMG, "dual-toolchain-pipeline.svg"), W, H, *frags,
           title="Конвеєр подвійного тулчейну та кодогенерація")


# ── 5. Емуляція простору користувача QEMU User Mode та binfmt_misc ──────────
def fig_qemu_user_emulation():
    W, H = 1040, 500
    frags = []

    frags.append(text(520, 30, "Прозора емуляція цільових двійкових файлів: Linux binfmt_misc і QEMU User Mode", size=16, bold=True))

    # Схема виконання: Розробник / CTest запускає цільовий ARM бінарник
    b_start, _, _ = textbox(160, 120, [
        "1. Запуск двійкового файлу",
        "ctest / ./test_runner_arm64",
        "Бінарник скомпільовано під AArch64",
    ], size=11.5, fill=ACCENT_FILL, stroke=NEG, min_w=240)
    frags.append(b_start)

    frags.append(arrow(280, 120, 370, 120))

    # Ядро Linux
    b_kernel, _, _ = textbox(520, 120, [
        "2. Ядро Linux (x86_64 Host)",
        "Перевірка магічних байтів заголовка ELF",
        "e_machine = 0xB7 (AArch64) != 0x3E (x86_64)",
    ], size=11.5, fill=FILL, stroke=LINE, min_w=260)
    frags.append(b_kernel)

    frags.append(arrow(650, 120, 740, 120))

    # Модуль binfmt_misc
    b_binfmt, _, _ = textbox(880, 120, [
        "3. Модуль binfmt_misc",
        "Перехоплює непідтримуваний ELF",
        "Маршрутизує виклик на зареєстрований емулятор",
    ], size=11.5, fill=OK_FILL, stroke=FIELD, min_w=240)
    frags.append(b_binfmt)

    # Стрілка вниз до QEMU
    frags.append(arrow(880, 160, 880, 220))

    # QEMU User Mode
    frags.append(rect(40, 230, 960, 160, fill=FILL, stroke=LINE, sw=1.2))
    frags.append(text(520, 255, "4. qemu-aarch64-static (Простір користувача хоста)", size=13.5, bold=True, color=NEG))

    q1, _, _ = textbox(270, 320, [
        "Динамічна трансляція коду (TCG)",
        "Перетворює інструкції ARM64 у мікрооперації,",
        "а потім у нативний машинний код x86_64",
    ], size=10.5, fill=ACCENT_FILL, stroke=NEG, min_w=380)
    frags.append(q1)

    q2, _, _ = textbox(770, 320, [
        "Трансляція системних викликів (Syscall Mapping)",
        "Конвертує номери syscall, порядок байтів та структури",
        "і передає виконання нативному ядру Linux x86_64",
    ], size=10.5, fill=OK_FILL, stroke=FIELD, min_w=380)
    frags.append(q2)

    # Стрілка вниз до результату
    frags.append(arrow(520, 390, 520, 425))

    b_res, _, _ = textbox(520, 455, [
        "5. Повернення результату в CTest / консоль",
        "Тести виконуються прозоро на робочій станції та в CI без фізичної цільової плати!",
    ], size=11.5, fill=OK_FILL, stroke=FIELD, min_w=620)
    frags.append(b_res)

    render(os.path.join(IMG, "qemu-user-emulation.svg"), W, H, *frags,
           title="Емуляція QEMU User Mode та binfmt_misc")


if __name__ == "__main__":
    fig_gnu_triplets_matrix()
    fig_endianness_and_data_models()
    fig_struct_alignment_padding()
    fig_dual_toolchain_pipeline()
    fig_qemu_user_emulation()
    print("Всі 5 фігур успішно згенеровано.")
