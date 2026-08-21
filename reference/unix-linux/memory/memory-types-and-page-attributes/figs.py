# -*- coding: utf-8 -*-
"""Фігури для теми «Тип пам'яті в записі таблиці сторінок: кешованість, PAT і MAIR»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

GRN_F = "#eafaf0"
BLU_F = "#eaf0fd"
RED_F = "#fdecea"
YEL_F = "#fff5e0"
PUR_F = "#f3e8fd"


# ── 1. Декодування атрибутів: x86 PAT та ARM64 MAIR ─────────────────────────
def fig_pat_index_resolution():
    W, H = 1320, 840
    F = []

    # ── Секція 1: x86-64 (PAT / PCD / PWT) ──
    F.append(fitbox(40, 50, 1240, 360, "", fill=FILL, stroke=MUTED, sw=1, rx=8))
    F.append(text(660, 75, "x86-64: Формування 3-бітового індексу з PTE в регістр IA32_PAT MSR (0x277)",
                  size=15, bold=True, color=INK))

    # PTE 4 КіБ рядок
    F.append(text(190, 115, "Запис таблиці PTE (4 КіБ сторінка):", size=13, bold=True, anchor="start"))
    F.append(fitbox(190, 130, 300, 44, "Фізична адреса кадру [51:12]", size=12, fill=FILL))
    F.append(fitbox(490, 130, 70, 44, "PAT\nбіт 7", size=11, bold=True, fill=RED_F, stroke=POS, sw=1.4))
    F.append(fitbox(560, 130, 50, 44, "D/A", size=11, fill=FILL))
    F.append(fitbox(610, 130, 70, 44, "PCD\nбіт 4", size=11, bold=True, fill=BLU_F, stroke=NEG, sw=1.4))
    F.append(fitbox(680, 130, 70, 44, "PWT\nбіт 3", size=11, bold=True, fill=GRN_F, stroke=FIELD, sw=1.4))
    F.append(fitbox(750, 130, 70, 44, "U/S, R/W, P\nбіти 2:0", size=11, fill=FILL))

    # Примітка про 2 МБ сторінки
    F.append(fitbox(840, 130, 400, 44, "У 2 МБ / 1 ГБ записах (PDE/PDPTE) біт 7 — це PS,\nа біт PAT перенесено на позицію біта 12!",
                    size=11, fill=YEL_F, stroke=MUTED, sw=1))

    # Стрілки збирання 3-бітового індексу
    F.append(arrow(525, 174, 525, 215, color=POS))
    F.append(arrow(645, 174, 645, 215, color=NEG))
    F.append(arrow(715, 174, 715, 215, color=FIELD))

    F.append(fitbox(460, 215, 340, 40, "3-бітовий індекс = { PAT, PCD, PWT } (значення 000₂ … 111₂)",
                    size=13, bold=True, fill=PUR_F, stroke=MUTED, sw=1.2))

    F.append(arrow(630, 255, 630, 280))

    # Таблиця IA32_PAT MSR
    F.append(text(660, 298, "Регістр IA32_PAT MSR: вісім 8-бітових полів (PA0 … PA7)", size=13, bold=True))
    entries_x86 = [
        ("PA0 (000)", "WB", GRN_F),
        ("PA1 (001)", "WT", BLU_F),
        ("PA2 (010)", "UC-", YEL_F),
        ("PA3 (011)", "UC", RED_F),
        ("PA4 (100)", "WB", GRN_F),
        ("PA5 (101)", "WT", BLU_F),
        ("PA6 (110)", "UC-", YEL_F),
        ("PA7 (111)", "WC", PUR_F),
    ]
    for i, (name, val, cfill) in enumerate(entries_x86):
        ex = 90 + i * 142
        F.append(fitbox(ex, 315, 136, 68, f"{name}\n{val}", size=12, bold=True, fill=cfill, stroke=LINE, sw=1.2))

    # ── Секція 2: ARM64 (MAIR_EL1) ──
    F.append(fitbox(40, 430, 1240, 375, "", fill=FILL, stroke=MUTED, sw=1, rx=8))
    F.append(text(660, 455, "ARMv8/v9: Дескриптор VMSAv8-64 та індексація регістра MAIR_EL1",
                  size=15, bold=True, color=INK))

    # Дескриптор сторінки ARM64
    F.append(text(190, 495, "Дескриптор сторінки Stage-1 (64 біти):", size=13, bold=True, anchor="start"))
    F.append(fitbox(190, 510, 220, 46, "Атрибути верхнього рівня\n[63:48] UXN, PXN", size=11, fill=FILL))
    F.append(fitbox(410, 510, 270, 46, "Фізична адреса вихідного кадру\n[47:12] OA[47:12]", size=11, fill=FILL))
    F.append(fitbox(680, 510, 110, 46, "SH[1:0]\nбіти 9:8 (Share)", size=11, bold=True, fill=YEL_F, stroke=MUTED, sw=1.2))
    F.append(fitbox(790, 510, 60, 46, "AP, NS\n7:6, 5", size=11, fill=FILL))
    F.append(fitbox(850, 510, 140, 46, "AttrIndx[2:0]\nбіти 4:2 (MAIR)", size=12, bold=True, fill=RED_F, stroke=POS, sw=1.5))
    F.append(fitbox(990, 510, 100, 46, "Type / Valid\nбіти 1:0", size=11, fill=FILL))

    # Стрілка з AttrIndx до MAIR_EL1
    F.append(arrow(920, 556, 920, 620, color=POS))
    F.append(text(935, 590, "3-бітовий індекс (0 … 7)", size=12, color=POS, anchor="start", bold=True))

    # MAIR_EL1 регістр
    F.append(text(660, 638, "Регістр MAIR_EL1: 8 конфігурованих байтових слотів (Attr0 … Attr7)", size=13, bold=True))
    entries_arm = [
        ("Attr0 (000)", "Device-nGnRnE\n(0x00)", RED_F),
        ("Attr1 (001)", "Device-nGnRE\n(0x04)", YEL_F),
        ("Attr2 (010)", "Device-nGRE\n(0x08)", YEL_F),
        ("Attr3 (011)", "Device-GRE\n(0x0C)", YEL_F),
        ("Attr4 (100)", "Normal-NC\n(0x44)", PUR_F),
        ("Attr5 (101)", "Normal-WT\n(0xBB)", BLU_F),
        ("Attr6 (110)", "Normal-WB-iNC\n(0x4F)", BLU_F),
        ("Attr7 (111)", "Normal-WB-WA\n(0xFF)", GRN_F),
    ]
    for i, (name, val, cfill) in enumerate(entries_arm):
        ex = 70 + i * 146
        F.append(fitbox(ex, 655, 140, 80, f"{name}\n{val}", size=11, bold=True, fill=cfill, stroke=LINE, sw=1.2))

    F.append(text(660, 768, "Поле SH[1:0] задає домен когерентності: Non-shareable (00), Outer Shareable (10) або Inner Shareable (11)",
                  size=12, color=MUTED, italic=True))

    return render(os.path.join(IMG, "pat-index-resolution.svg"), W, H, *F,
                  title="Декодування типів пам'яті: x86 PAT та ARM64 MAIR_EL1")


# ── 2. Спектр типів пам'яті за поведінкою ────────────────────────────────────
def fig_memory_types_spectrum():
    W, H = 1320, 680
    F = []

    # Заголовок осі
    F.append(text(660, 60, "Спектр типів пам'яті: баланс між суворою черговістю доступу та швидкістю кешування",
                  size=15, bold=True))

    # Стрілка спектру
    F.append(arrow(100, 100, 1220, 100, color=LINE, sw=2.5))
    F.append(text(100, 85, "Максимальна суворість (MMIO)", size=12, bold=True, color=POS, anchor="start"))
    F.append(text(1220, 85, "Максимальна продуктивність (RAM)", size=12, bold=True, color=FIELD, anchor="end"))

    types = [
        {
            "x": 60, "w": 280,
            "name": "UC / Strong Uncacheable\n(ARM: Device-nGnRnE)",
            "color": RED_F, "stroke": POS,
            "items": [
                "• Кеш повністю вимкнено",
                "• Строгий порядок інструкцій",
                "• Заборонено злиття записів",
                "• Заборонено спекулятивні зчитування",
                "• Прямі поодинокі транзакції на шині",
                "Призначення: Регістри керування MMIO, апаратні FIFO, скидання переривань"
            ]
        },
        {
            "x": 365, "w": 280,
            "name": "WC / Write-Combining\n(ARM: Normal Non-Cacheable)",
            "color": PUR_F, "stroke": MUTED,
            "items": [
                "• Кеш L1/L2/L3 вимкнено",
                "• Слабкий порядок запису (Weak)",
                "• Записи зливаються в буфері (64 Б)",
                "• Відправлення пакетом (Burst PCIe)",
                "• Дозволено спекулятивне читання",
                "Призначення: Відеопам'ять (Framebuffers), текстури GPU, PCIe BAR буфери"
            ]
        },
        {
            "x": 670, "w": 280,
            "name": "WT / Write-Through\n(ARM: Normal Write-Through)",
            "color": BLU_F, "stroke": NEG,
            "items": [
                "• Читання кешується в L1/L2/L3",
                "• Запис оновлює кеш І відразу шину",
                "• Немає брудних (Dirty) рядків",
                "• Дані в RAM завжди актуальні",
                "• Нижча швидкість запису за WB",
                "Призначення: Спільна пам'ять із контролерами без апаратного snoop-протоколу"
            ]
        },
        {
            "x": 975, "w": 280,
            "name": "WB / Write-Back\n(ARM: Normal Write-Back)",
            "color": GRN_F, "stroke": FIELD,
            "items": [
                "• Повне кешування L1/L2/L3",
                "• Виділення рядка на запис і читання",
                "• Брудні рядки скидаються при витісненні",
                "• Когерентність MESI / MOESI",
                "• Максимальна пропускна здатність",
                "Призначення: Звичайна оперативна пам'ять процесу (стек, купа, код, ядро)"
            ]
        },
    ]

    for t in types:
        F.append(fitbox(t["x"], 120, t["w"], 60, t["name"], size=13, bold=True,
                        fill=t["color"], stroke=t["stroke"], sw=1.6))
        # Тіло списку
        F.append(rect(t["x"], 185, t["w"], 380, fill=BG, stroke=LINE, sw=1, rx=6))
        cy = 210
        for it in t["items"]:
            if it.startswith("Призначення:"):
                cy += 10
                F.append(fitbox(t["x"] + 10, cy, t["w"] - 20, 65, it, size=11, bold=True,
                                fill=FILL, stroke=MUTED, sw=1))
                cy += 75
            else:
                F.append(text(t["x"] + 14, cy, it, size=11, color=INK, anchor="start"))
                cy += 30

    # Підсумок внизу
    F.append(fitbox(60, 590, 1195, 55,
                    "Ключове правило системного програміста: звичайна пам'ять (RAM) ЗАВЖДИ вимагає Write-Back,\n"
                    "потокові графічні буфери — Write-Combining, а регістри апаратних пристроїв (MMIO) — Uncacheable / Device.",
                    size=12, bold=True, fill=FILL, stroke=MUTED, sw=1.2))

    return render(os.path.join(IMG, "memory-types-spectrum.svg"), W, H, *F,
                  title="Спектр типів пам'яті: порівняння характеристик і призначень")


# ── 3. Небезпека аліасингу типів пам'яті ─────────────────────────────────────
def fig_aliasing_conflict_hazard():
    W, H = 1320, 780
    F = []

    F.append(text(660, 45, "Конфлікт аліасингу: дві віртуальні адреси з різними типами пам'яті на один кадр",
                  size=15, bold=True))

    # Лівий бік: Віртуальне відображення ядра (WB)
    F.append(fitbox(60, 80, 420, 90, "Віртуальна адреса 1: Ядро (Direct Map)\nТип пам'яті: Write-Back (WB)\n(кешоване читання й запис)",
                    size=13, bold=True, fill=GRN_F, stroke=FIELD, sw=1.5))

    # Правий бік: Віртуальне відображення драйвера (UC / WC)
    F.append(fitbox(840, 80, 420, 90, "Віртуальна адреса 2: Драйвер (ioremap)\nТип пам'яті: Uncacheable (UC) / WC\n(прямий некешований доступ)",
                    size=13, bold=True, fill=RED_F, stroke=POS, sw=1.5))

    # Стрілки вниз
    F.append(arrow(270, 170, 270, 240, color=FIELD))
    F.append(arrow(1050, 170, 1050, 420, color=POS))

    # Кеш процесора (L1/L2/L3)
    F.append(fitbox(100, 240, 340, 110, "Кеш процесора L1/L2\nРядок кешу в стані Modified (брудний)\nДані змінено в кеші, але НЕ на шині!",
                    size=12, bold=True, fill=YEL_F, stroke=POS, sw=1.5))

    F.append(arrow(270, 350, 270, 420, color=POS, sw=2))
    F.append(text(285, 390, "Пізніше витіснення (Eviction)\nскидає старі дані на шину!", size=11, bold=True, color=POS, anchor="start"))

    # Центральна шина / Системна пам'ять і пристрій
    F.append(fitbox(200, 430, 920, 110,
                    "Фізичний кадр пам'яті (PCIe BAR / MMIO регістри контролера / Буфер DMA)\n"
                    "Фізична адреса: 0xFD000000",
                    size=14, bold=True, fill=FILL, stroke=LINE, sw=1.8))

    # Небезпеки (3 червоні картки)
    F.append(text(660, 570, "Апаратні катастрофи внаслідок неузгодженості типів пам'яті (Memory Type Mismatch):",
                  size=14, bold=True, color=POS))

    hazards = [
        (60, "1. Перезапис регістрів пристрою",
         "Скидання брудного рядка кешу з WB-відображення перезаписує регістри керування або пошкоджує вхідний пакет DMA."),
        (470, "2. Втрата подій і переривань",
         "Спекулятивне читання через WB-псевдонім зчитує регістр FIFO зі скиданням при читанні (clear-on-read). Апаратне переривання втрачається!"),
        (880, "3. Апаратний збій MCE / шини",
         "Одночасне перебування даних у кеші та некешовані транзакції на шині порушують протокол когерентності (PCIe Completion Error, MCE)."),
    ]

    for hx, htitle, hdesc in hazards:
        F.append(rect(hx, 595, 380, 140, fill=RED_F, stroke=POS, sw=1.3, rx=6))
        F.append(text(hx + 190, 620, htitle, size=12, bold=True, color=POS))
        F.append(fitbox(hx + 10, 635, 360, 90, hdesc, size=11, fill=BG, stroke=MUTED, sw=0.8))

    return render(os.path.join(IMG, "aliasing-conflict-hazard.svg"), W, H, *F,
                  title="Конфлікт аліасингу типів пам'яті")


if __name__ == "__main__":
    fig_pat_index_resolution()
    fig_memory_types_spectrum()
    fig_aliasing_conflict_hazard()
    print("All figures generated successfully.")
