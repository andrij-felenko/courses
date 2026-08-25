# -*- coding: utf-8 -*-
"""Фігури для теми «Що вміє чужа бібліотека: заголовки, pkg-config, nm -D, man 3» (root/course/unix/what-a-foreign-library-offers)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

BLUE_F, BLUE_S     = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S   = "#e9f7ef", "#16a34a"
AMBER_F, AMBER_S   = "#fff6e5", "#d97706"
RED_F, RED_S       = "#fef2f2", "#dc2626"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
GRAY_F, GRAY_S     = "#f8fafc", "#64748b"

def fig_library_dual_nature():
    W, H = 940, 520
    frags = []

    frags.append(rect(10, 10, 920, 500, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(470, 34, "Подвійна природа бібліотеки в Unix: контракт компіляції проти контракту лінкування", size=15, bold=True, color="#0f172a"))

    # Top zone: Compile-time (Headers)
    frags.append(rect(25, 52, 890, 205, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(470, 72, "1. Етап компіляції (Compile-Time) — текстовий контракт інтерфейсу: заголовки .h / .hpp", size=13, bold=True, color="#15803d"))

    # Block 1.1: Source code
    frags.append(rect(45, 88, 220, 150, fill="#ffffff", stroke="#16a34a", sw=1.5, rx=6))
    frags.append(text(155, 108, "Вихідний код (app.c / app.cpp)", size=11.5, bold=True, color="#16a34a"))
    frags.append(line(55, 116, 255, 116, color="#bbf7d0", sw=1.0))
    frags.append(text(155, 134, "#include <zstd.h>", size=11, color="#1e293b"))
    frags.append(text(155, 152, "ZSTD_CCtx* ctx = ...", size=11, color="#1e293b"))
    frags.append(text(155, 170, "ZSTD_compressCCtx(...);", size=11, color="#1e293b"))
    frags.append(text(155, 195, "Потребує: сигнатури,", size=10, italic=True, color="#64748b"))
    frags.append(text(155, 212, "типи, розміри структур", size=10, italic=True, color="#64748b"))

    # Arrow to compiler
    frags.append(arrow(268, 163, 315, 163, color="#16a34a", sw=1.8))

    # Block 1.2: Header file
    frags.append(rect(320, 88, 260, 150, fill="#ffffff", stroke="#059669", sw=1.5, rx=6))
    frags.append(text(450, 108, "Заголовний файл (/usr/include/zstd.h)", size=11.5, bold=True, color="#059669"))
    frags.append(line(330, 116, 570, 116, color="#a7f3d0", sw=1.0))
    frags.append(text(450, 134, "typedef struct ZSTD_CCtx_s ZSTD_CCtx;", size=10.5, color="#1e293b"))
    frags.append(text(450, 152, "size_t ZSTD_compressCCtx(...);", size=10.5, color="#1e293b"))
    frags.append(text(450, 170, "#define ZSTD_VERSION_NUMBER ...", size=10.5, color="#1e293b"))
    frags.append(text(450, 195, "Пакет: libzstd-dev (Compile-time)", size=10, bold=True, color="#059669"))
    frags.append(text(450, 212, "Немає файлу -> fatal error: no file", size=10, italic=True, color="#dc2626"))

    # Arrow to object file
    frags.append(arrow(583, 163, 630, 163, color="#16a34a", sw=1.8))

    # Block 1.3: Object file
    frags.append(rect(635, 88, 260, 150, fill="#ffffff", stroke="#0284c7", sw=1.5, rx=6))
    frags.append(text(765, 108, "Об'єктний файл (app.o)", size=11.5, bold=True, color="#0284c7"))
    frags.append(line(645, 116, 885, 116, color="#bae6fd", sw=1.0))
    frags.append(text(765, 134, "Скомпільований машинний код", size=10.5, color="#1e293b"))
    frags.append(text(765, 152, "Таблиця невизначених символів:", size=10.5, color="#1e293b"))
    frags.append(text(765, 172, "U ZSTD_compressCCtx", size=11, bold=True, color="#dc2626"))
    frags.append(text(765, 195, "Компіляція успішна! Але адреси", size=10, italic=True, color="#475569"))
    frags.append(text(765, 212, "функції ще немає в пам'яті", size=10, italic=True, color="#475569"))

    # Middle divider: Transition
    frags.append(line(35, 268, 905, 268, color="#94a3b8", sw=1.2, dash="4,4"))
    frags.append(text(470, 273, "Розкол інтерфейсу: заголовки перевіряють типи, двійкові об'єкти надають машинний код", size=11, bold=True, color="#64748b"))

    # Bottom zone: Link-time & Run-time (.so/.a)
    frags.append(rect(25, 290, 890, 205, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=8))
    frags.append(text(470, 310, "2. Етап лінкування та завантаження (Link-Time & Run-Time) — двійковий код: .so / .a", size=13, bold=True, color="#1d4ed8"))

    # Block 2.1: Shared Library Binary
    frags.append(rect(45, 326, 260, 150, fill="#ffffff", stroke="#2563eb", sw=1.5, rx=6))
    frags.append(text(175, 346, "Динамічна бібліотека (libzstd.so.1)", size=11.5, bold=True, color="#2563eb"))
    frags.append(line(55, 354, 295, 354, color="#bfdbfe", sw=1.0))
    frags.append(text(175, 372, "Секція .text (машинні інструкції)", size=10.5, color="#1e293b"))
    frags.append(text(175, 390, "Таблиця динамічних символів .dynsym:", size=10.5, color="#1e293b"))
    frags.append(text(175, 410, "T ZSTD_compressCCtx", size=11, bold=True, color="#16a34a"))
    frags.append(text(175, 433, "Пакет: libzstd1 (Runtime)", size=10, bold=True, color="#2563eb"))
    frags.append(text(175, 450, "Немає файлу -> undefined reference", size=10, italic=True, color="#dc2626"))

    # Arrow to Linker / Loader
    frags.append(arrow(308, 401, 355, 401, color="#2563eb", sw=1.8))

    # Block 2.2: Linker resolving
    frags.append(rect(360, 326, 230, 150, fill="#ffffff", stroke="#7c3aed", sw=1.5, rx=6))
    frags.append(text(475, 346, "Лінкер ld (Компонування)", size=11.5, bold=True, color="#7c3aed"))
    frags.append(line(370, 354, 580, 354, color="#ddd6fe", sw=1.0))
    frags.append(text(475, 372, "Зіставлення символів U <-> T", size=10.5, color="#1e293b"))
    frags.append(text(475, 390, "Запис DT_NEEDED у ELF:", size=10.5, color="#1e293b"))
    frags.append(text(475, 410, "NEEDED: libzstd.so.1", size=10.5, bold=True, color="#7c3aed"))
    frags.append(text(475, 433, "Прапорець: -lzstd", size=10.5, bold=True, color="#1e293b"))
    frags.append(text(475, 450, "Генерація таблиць GOT / PLT", size=10, italic=True, color="#64748b"))

    # Arrow to Runtime Executable
    frags.append(arrow(593, 401, 640, 401, color="#2563eb", sw=1.8))

    # Block 2.3: Final Program Run
    frags.append(rect(645, 326, 250, 150, fill="#ffffff", stroke="#16a34a", sw=1.5, rx=6))
    frags.append(text(770, 346, "Виконання програми (ld.so)", size=11.5, bold=True, color="#16a34a"))
    frags.append(line(655, 354, 885, 354, color="#bbf7d0", sw=1.0))
    frags.append(text(770, 372, "Завантажувач шукає libzstd.so.1", size=10.5, color="#1e293b"))
    frags.append(text(770, 390, "через /etc/ld.so.cache", size=10.5, color="#1e293b"))
    frags.append(text(770, 410, "Релокація адреси в GOT", size=10.5, bold=True, color="#15803d"))
    frags.append(text(770, 433, "Прямий перехід на машинний код", size=10, italic=True, color="#475569"))
    frags.append(text(770, 450, "Безпечний та швидкий виклик", size=10, italic=True, color="#475569"))

    out_path = os.path.join(IMG, "fig-library-dual-nature.svg")
    render(out_path, W, H, *frags)

def fig_nm_symbol_anatomy():
    W, H = 940, 520
    frags = []

    frags.append(rect(10, 10, 920, 500, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(470, 34, "Анатомія таблиці динамічних символів nm -D та розшифровка літер типів", size=15, bold=True, color="#0f172a"))

    # Top sample output box
    frags.append(rect(30, 55, 880, 115, fill="#0f172a", stroke="#334155", sw=1.5, rx=8))
    frags.append(text(470, 78, "Структура рядка у виводі: nm -D /usr/lib/x86_64-linux-gnu/libzstd.so.1", size=12, bold=True, color="#94a3b8"))

    # Line breakdown
    frags.append(rect(50, 96, 210, 55, fill="#1e293b", stroke="#3b82f6", sw=1.2, rx=4))
    frags.append(text(155, 118, "000000000001a4e0", size=12.5, bold=True, color="#60a5fa"))
    frags.append(text(155, 138, "Віртуальна адреса / зміщення", size=9.5, color="#94a3b8"))

    frags.append(rect(275, 96, 75, 55, fill="#1e293b", stroke="#22c55e", sw=1.2, rx=4))
    frags.append(text(312, 118, "T", size=14, bold=True, color="#4ade80"))
    frags.append(text(312, 138, "Код типу", size=9.5, color="#94a3b8"))

    frags.append(rect(365, 96, 290, 55, fill="#1e293b", stroke="#eab308", sw=1.2, rx=4))
    frags.append(text(510, 118, "ZSTD_compressCCtx", size=12.5, bold=True, color="#fde047"))
    frags.append(text(510, 138, "Ім'я символу (ідентифікатор API)", size=9.5, color="#94a3b8"))

    frags.append(rect(670, 96, 220, 55, fill="#1e293b", stroke="#a855f7", sw=1.2, rx=4))
    frags.append(text(780, 118, "@@ZSTD_1.4.0", size=12.5, bold=True, color="#c084fc"))
    frags.append(text(780, 138, "Версійна мітка символу ELF", size=9.5, color="#94a3b8"))

    # Middle grid of symbol types
    frags.append(text(470, 195, "Класифікація літер типів символів у виводі nm (велика = глобальний/експорт, мала = локальний)", size=12.5, bold=True, color="#1e293b"))

    cards = [
        ("T / t", "Text (Код)", "Функція у секції .text.\nT — публічний експорт API;\nt — внутрішня static функція.", GREEN_F, GREEN_S),
        ("U", "Undefined", "Невизначений імпорт.\nБібліотека викликає функцію,\nяку має надати libc або інша .so.", RED_F, RED_S),
        ("D / d", "Data (Ініціалізовано)", "Глобальні змінні у .data.\nМають початкове ненульове\nзначення в бінарнику.", BLUE_F, BLUE_S),
        ("B / b", "BSS (Неініціалізовано)", "Змінні у секції .bss.\nОбнуляються ядром під час\nзавантаження сторінки в RAM.", AMBER_F, AMBER_S),
        ("R / r", "Read-Only Data", "Константи у секції .rodata.\nРядки, таблиці підстановки,\nзахищені від запису сторінки.", PURPLE_F, PURPLE_S),
        ("W / w", "Weak (Слабкий)", "Слабкий символ.\nМоже бути перекритий звичайною\nфункцією з головної програми.", GRAY_F, GRAY_S),
    ]

    card_w = 135
    card_h = 135
    start_x = 30
    gap_x = 14
    y_card = 212

    for i, (sym, label, desc, bg_c, str_c) in enumerate(cards):
        cx = start_x + i * (card_w + gap_x)
        mid_x = cx + card_w / 2

        frags.append(rect(cx, y_card, card_w, card_h, fill=bg_c, stroke=str_c, sw=1.5, rx=6))
        frags.append(text(mid_x, y_card + 24, sym, size=15, bold=True, color=str_c))
        frags.append(text(mid_x, y_card + 42, label, size=10.5, bold=True, color="#0f172a"))
        frags.append(line(cx + 8, y_card + 50, cx + card_w - 8, y_card + 50, color=str_c, sw=0.8))

        lines = desc.split("\n")
        for j, ln in enumerate(lines):
            frags.append(text(mid_x, y_card + 68 + j * 17, ln, size=9.5, color="#334155"))

    # Bottom box: C++ Name Mangling
    frags.append(rect(30, 362, 880, 130, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(470, 384, "Деманглінг C++ імен: перетворення спаплюжених імен на сигнатури (nm -C -D або c++filt)", size=12.5, bold=True, color="#0f172a"))

    frags.append(rect(50, 400, 380, 75, fill="#fee2e2", stroke="#ef4444", sw=1.2, rx=6))
    frags.append(text(240, 420, "Сире спаплюжене ім'я (Raw Mangled Symbol)", size=11, bold=True, color="#b91c1c"))
    frags.append(text(240, 442, "_ZN6Engine8Renderer11draw_spriteERK7Textureii", size=11, bold=True, color="#7f1d1d"))
    frags.append(text(240, 460, "Кодування ABI: простір імен, клас, метод, типи параметрів", size=9.5, italic=True, color="#991b1b"))

    frags.append(arrow(438, 437, 490, 437, color="#64748b", sw=2.0))
    frags.append(text(464, 428, "c++filt", size=10, bold=True, color="#475569"))

    frags.append(rect(500, 400, 390, 75, fill="#dcfce7", stroke="#22c55e", sw=1.2, rx=6))
    frags.append(text(695, 420, "Демангльоване ім'я C++ (nm -C -D)", size=11, bold=True, color="#15803d"))
    frags.append(text(695, 442, "Engine::Renderer::draw_sprite(Texture const&, int, int)", size=10.5, bold=True, color="#14532d"))
    frags.append(text(695, 460, "Зрозуміла сигнатура методу для розробника", size=9.5, italic=True, color="#166534"))

    out_path = os.path.join(IMG, "fig-nm-symbol-anatomy.svg")
    render(out_path, W, H, *frags)

if __name__ == "__main__":
    fig_library_dual_nature()
    fig_nm_symbol_anatomy()
    print("Generated 2 SVG figures in img/")
