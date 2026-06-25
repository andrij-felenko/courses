# -*- coding: utf-8 -*-
"""Фігури до теми «Вибір МК» (ландшафт сімейств і стратегія).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки понад палітру svgkit (під розрядність/сімейства)
BLUE = "#2980b9"
PURP = "#8e44ad"
ORNG = "#e67e22"
TEAL = "#16a085"
GRN2 = "#1a6b3a"


# ── 1. Розрядність як три щаблі: 8 → 16 → 32 ────────────────────────────────
def fig_bit_width():
    W, H = 780, 430
    f = [text(W / 2, 28, "Три щаблі розрядності — і де між ними межа", size=16, bold=True)]

    cols = [
        (60, "8-біт", "AVR · PIC", ORNG,
         ["копійки за чіп", "простий, без ОС", "мкА сну легко", "малий код-простір"],
         "просте й дешеве масово"),
        (300, "16-біт", "MSP430 · PIC24", MUTED,
         ["вузька ніша", "колись — енергоощадні", "тиснуть з двох боків",
          "8-біт знизу, 32 згори"],
         "залишок, що тане"),
        (540, "32-біт", "ARM Cortex-M · RISC-V", BLUE,
         ["вибір за замовчанням", "FPU/DSP, багато пам'яті", "ціна впала до 8-біт",
          "екосистема й переносність"],
         "усе серйозне сьогодні"),
    ]
    for x0, title, fam, accent, rows, foot in cols:
        f.append(rect(x0, 56, 200, 300, fill=BG, stroke=accent, sw=2))
        f.append(text(x0 + 100, 84, title, size=18, bold=True, color=accent))
        f.append(text(x0 + 100, 104, fam, size=10.5, color=MUTED, italic=True))
        y = 138
        for r in rows:
            f.append(circle(x0 + 22, y - 4, 2.6, fill=accent, stroke=accent, sw=1))
            f.append(text(x0 + 34, y, r, size=10.5, anchor="start"))
            y += 30
        f.append(line(x0 + 18, 300, x0 + 182, 300, color="#e5e7eb", sw=1))
        f.append(text(x0 + 100, 326, foot, size=10.5, color=accent, italic=True, bold=True))

    # стрілки «тиск» на 16-біт із двох боків
    f.append(arrow(264, 206, 300, 206, color=ORNG, sw=1.6))
    f.append(arrow(540, 230, 504, 230, color=BLUE, sw=1.6))
    f.append(text(W / 2, 392, "16-біт стискають знизу дешеві 8-біт і згори здешевілі 32-біт",
                  size=10.5, color=MUTED, italic=True))
    f.append(text(W / 2, 412, "розрядність — не «більше краще», а грубий поділ ринку на ніші",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "bit-width.svg"), W, H, *f)


# ── 2. Щаблі Cortex-M: M0+ → M4F → M7 ───────────────────────────────────────
def fig_cortex_ladder():
    W, H = 760, 420
    f = [text(W / 2, 28, "Один набір команд — три щаблі продуктивності", size=16, bold=True)]

    # сходинки, що ростуть угору-вправо
    steps = [
        (70,  290, "Cortex-M0+", "ощадливий",
         ["2 такти на конвеєр", "без FPU, без DSP", "найменший струм і ціна"],
         "RP2040 · дешеві STM32", FIELD),
        (290, 220, "Cortex-M4F", "робоча конячка",
         ["DSP-команди (MAC)", "FPU одинарної точності", "баланс ціни й сили"],
         "nRF52 · STM32F4", BLUE),
        (510, 150, "Cortex-M7", "продуктивний",
         ["конвеєр на 2 інструкції", "FPU подвійної точності", "кеш, найвищі такти"],
         "STM32H7 · i.MX RT", PURP),
    ]
    bw, bh = 190, 96
    for x0, y0, name, role, rows, who, accent in steps:
        f.append(rect(x0, y0, bw, bh, fill=BG, stroke=accent, sw=2))
        f.append(text(x0 + bw / 2, y0 + 24, name, size=15, bold=True, color=accent))
        f.append(text(x0 + bw / 2, y0 + 42, role, size=10.5, color=MUTED, italic=True))
        yy = y0 + 60
        for r in rows:
            f.append(text(x0 + bw / 2, yy, r, size=9.5, color=INK))
            yy += 14
        f.append(text(x0 + bw / 2, y0 + bh + 18, who, size=10, color=accent, italic=True, bold=True))

    # стрілка зростання вздовж сходів
    f.append(arrow(110, 286, 690, 150, color=MUTED, sw=1.4))
    f.append(text(648, 130, "більше DMIPS,", size=10, color=MUTED, italic=True))
    f.append(text(648, 144, "ціни, струму", size=10, color=MUTED, italic=True))
    f.append(text(W / 2, 404,
                  "та сама ISA: код для нижчого щабля піде на вищому — росте чіп, не переписується код",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "cortex-ladder.svg"), W, H, *f)


# ── 3. Карта сімейств за «коронною» рисою ───────────────────────────────────
def fig_family_map():
    W, H = 840, 430
    f = [text(W / 2, 28, "Кожне сімейство — за своєю коронною рисою", size=16, bold=True)]

    # центральна вісь рішення
    box, bw, bh = textbox(W / 2, 64, "що головне\nдля виробу?", size=12, bold=True,
                          fill=FILL, stroke=INK, sw=2, min_w=140)
    f.append(box)

    # п'ять сімейств навколо, кожне зі своєю «короною»
    fam = [
        (90,  150, "AVR / PIC", "8-біт", "простота й копійка", ORNG,
         "масовий простий виріб"),
        (320, 150, "STM32", "Cortex-M, широта", "повний спектр периферії", BLUE,
         "від M0+ до M7 під будь-що"),
        (550, 150, "ESP32", "Wi-Fi + Bluetooth", "вбудоване радіо й SDK", FIELD,
         "хмарний підключений вузол"),
        (90,  300, "RP2040", "PIO", "програмований ввід-вивід", PURP,
         "нестандартний протокол"),
        (320, 300, "nRF52/53", "BLE + мкА сну", "роки від батарейки-таблетки", TEAL,
         "носимий датчик на BLE"),
        (550, 300, "RISC-V", "відкрита ISA", "без роялті, висхідний", "#c0392b",
         "ESP32-C · CH32V ~$0.10"),
    ]
    for x0, y0, name, crown, desc, accent, who in fam:
        f.append(rect(x0, y0, 200, 96, fill=BG, stroke=accent, sw=2))
        f.append(text(x0 + 100, y0 + 24, name, size=14.5, bold=True, color=accent))
        f.append(text(x0 + 100, y0 + 43, crown, size=11, color=INK, bold=True))
        f.append(text(x0 + 100, y0 + 60, desc, size=9.5, color=MUTED, italic=True))
        f.append(line(x0 + 16, y0 + 70, x0 + 184, y0 + 70, color="#e5e7eb", sw=1))
        f.append(text(x0 + 100, y0 + 86, who, size=9.5, color=accent, italic=True))

    f.append(text(W / 2, 416,
                  "вибираєш не «найкращий чіп», а сімейство, чия корона збігається з головною вимогою",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "family-map.svg"), W, H, *f)


# ── 4. (📜 hist-arm) Чому Acorn зробила власний процесор ─────────────────────
def fig_why_own_cpu():
    W, H = 820, 340
    f = [text(W / 2, 28, "Чому Acorn вирішила зробити власний процесор", size=15, bold=True)]

    # глухий кут
    f.append(rect(60, 55, 220, 240, fill="#fef2f2", stroke=POS, sw=2, rx=10))
    f.append(text(170, 77, "Глухий кут", size=13, bold=True, color=POS))
    f.append(rect(125.4, 87.3, 89.2, 39.3, fill="#fff0f0", stroke=POS, sw=1))
    f.append(mtext(170, 103.7, ["6502 (8-біт)", "BBC Micro"], size=11))
    f.append(text(170, 140.7, "→ стеля продуктивності", size=10, color=MUTED))
    f.append(rect(119.1, 152.7, 101.8, 39.3, fill="#fff0f0", stroke=POS, sw=1))
    f.append(mtext(170, 169.0, ["Motorola 68000", "16-біт CISC"], size=11))
    f.append(text(170, 206.0, "✗ повільна реакція", size=10, color=MUTED))
    f.append(rect(119.1, 218.0, 101.8, 39.3, fill="#fff0f0", stroke=POS, sw=1))
    f.append(mtext(170, 234.3, ["National 32016", "16-біт CISC"], size=11))
    f.append(text(170, 271.2, "✗ висока латентність", size=10, color=MUTED))

    f.append(arrow(284, 175, 316, 175, color=LINE, sw=2))

    # поворот
    f.append(rect(320, 55, 220, 240, fill="#fffbea", stroke="#d97706", sw=2, rx=10))
    f.append(text(430, 77, "Поворот", size=13, bold=True, color="#d97706"))
    f.append(mtext(430, 107, [
        "Візит у Western", "Design Center,", "Фенікс (1983)", "",
        "Очікували:", "корпорацію-гіганта", "",
        "Побачили:", "кімнату + жменю", "інженерів зі", "студентами", "",
        "→ «якщо ВОНИ", "можуть — і ми»"], size=11, lh=1.28))

    f.append(arrow(544, 175, 576, 175, color=LINE, sw=2))

    # рішення
    f.append(rect(580, 55, 220, 240, fill="#f0fdf4", stroke=FIELD, sw=2, rx=10))
    f.append(text(690, 77, "Рішення", size=13, bold=True, color=FIELD))
    f.append(mtext(690, 107, [
        "Спроєктувати", "ВЛАСНЕ RISC-ядро", "",
        "Ключові ролі:", "Sophie Wilson", "→ система команд", "(ISA)", "",
        "Steve Furber", "→ мікроархітек-", "тура й логіка", "",
        "Команда Acorn", "→ кремній і тести"], size=11, lh=1.28))

    f.append(text(W / 2, 328,
                  "Технічний тупик + знятий психологічний бар'єр = народження ARM",
                  size=10, color=MUTED))
    render(os.path.join(IMG, "why-own-cpu.svg"), W, H, *f)


# ── 5. (📜 hist-arm) RISC проти CISC ────────────────────────────────────────
def fig_risc_vs_cisc():
    W, H = 720, 360
    f = [text(W / 2, 28, "Дві філософії системи команд", size=15, bold=True)]

    rows = ["Регістрів:", "Команд:", "Довжина команди:", "Декодер:", "Конвеєр:"]
    cisc = ["мало (8–16)", "багато (сотні)", "різна (1–15 байт)", "складний", "важко заповнити"]
    risc = ["багато (16–32)", "мало (~70)", "фіксована (4 байт)", "простий", "рівний, швидкий"]
    ys = [116, 152, 188, 224, 260]

    # CISC
    f.append(rect(50, 48, 280, 270, fill="#fef2f2", stroke=POS, sw=2.5, rx=12))
    f.append(text(190, 74, "CISC", size=16, bold=True, color=POS))
    f.append(text(190, 90, "(x86, 68000, VAX)", size=10, color=MUTED))
    for r, v, yy in zip(rows, cisc, ys):
        f.append(text(64, yy, r, size=11, color=MUTED, anchor="start"))
        f.append(text(316, yy, v, size=11, bold=True, anchor="end"))
        f.append(line(60, yy + 8, 320, yy + 8, color="#e5e7eb", sw=1))

    # RISC
    f.append(rect(390, 48, 280, 270, fill="#f0fdf4", stroke=FIELD, sw=2.5, rx=12))
    f.append(text(530, 74, "RISC (ARM)", size=16, bold=True, color=FIELD))
    f.append(text(530, 90, "(Acorn RISC Machine)", size=10, color=MUTED))
    for r, v, yy in zip(rows, risc, ys):
        f.append(text(404, yy, r, size=11, color=MUTED, anchor="start"))
        f.append(text(656, yy, v, size=11, bold=True, color=FIELD, anchor="end"))
        f.append(line(400, yy + 8, 660, yy + 8, color="#d1fae5", sw=1))

    f.append(circle(360, 183, 20, fill=FILL, stroke=LINE, sw=1.5))
    f.append(text(360, 188, "VS", size=12, bold=True))
    f.append(text(W / 2, 346,
                  "Проста архітектура RISC — і та, що під силу крихітній команді Acorn",
                  size=10, color=MUTED))
    render(os.path.join(IMG, "risc-vs-cisc.svg"), W, H, *f)


# ── 6. (📜 hist-arm) Ліцензійна модель: одне ядро в усіх ─────────────────────
def fig_arm_licensing():
    W, H = 820, 400
    f = [text(W / 2, 28, "Бізнес-модель ARM: продавати дизайн ядра, а не чипи",
              size=15, bold=True)]

    # центр — ARM Ltd
    f.append(rect(320, 165, 180, 90, fill="#eff6ff", stroke=NEG, sw=2.5, rx=12))
    f.append(mtext(410, 202, ["ARM Ltd", "дизайн ядра Cortex-M",
                              "(без власних фабрик)"], size=12))

    makers = [
        (35, 50, "STMicroelectronics", "STM32",
         (325, 170, 230, 85), (220, 95, 315, 180)),
        (595, 50, "Raspberry Pi", "RP2040",
         (505, 180, 600, 95), (590, 85, 495, 170)),
        (35, 310, "Nordic Semiconductor", "nRF-серія",
         (315, 240, 220, 345), (230, 355, 325, 250)),
        (595, 310, "NXP Semiconductors", "LPC / Kinetis",
         (495, 250, 590, 355), (600, 345, 505, 240)),
    ]
    for x0, y0, name, chip, lic, roy in makers:
        f.append(rect(x0, y0, 190, 80, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=9))
        f.append(text(x0 + 95, y0 + 16, name, size=10, bold=True, color=FIELD))
        f.append(mtext(x0 + 95, y0 + 44, [chip, "(Cortex-M + СВОЯ", "периферія)"], size=10, lh=1.3))
        f.append(arrow(lic[0], lic[1], lic[2], lic[3], color=NEG, sw=1.8))   # ліцензія ARM→виробник
        f.append(arrow(roy[0], roy[1], roy[2], roy[3], color=FIELD, sw=1.5)) # роялті виробник→ARM

    # легенда
    f.append(arrow(20, 364, 50, 364, color=NEG, sw=1.8))
    f.append(text(58, 368, "ліцензія (ARM → виробник)", size=10, anchor="start"))
    f.append(arrow(20, 384, 50, 384, color=FIELD, sw=1.5))
    f.append(text(58, 388, "роялті з кожного чипа (виробник → ARM)", size=10, anchor="start"))
    render(os.path.join(IMG, "arm-licensing.svg"), W, H, *f)


if __name__ == "__main__":
    fig_bit_width()
    fig_cortex_ladder()
    fig_family_map()
    fig_why_own_cpu()
    fig_risc_vs_cisc()
    fig_arm_licensing()
    print("OK: 6 SVG -> ./img/")
