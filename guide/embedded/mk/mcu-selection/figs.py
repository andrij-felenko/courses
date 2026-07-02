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


# ── 7. (детальна) Площа кристала: чому ядро перестало домінувати в ціні ──────
def fig_die_area():
    W, H = 780, 400
    f = [text(W / 2, 28, "Чому 32-бітне ядро подешевшало до ціни 8-бітного", size=16, bold=True)]

    # два «кристали»-стовпчики: старий грубий вузол vs сучасний
    # кожен — стос шарів однакової загальної висоти; змінюється лише частка ЯДРА
    def die(x0, title, core_frac, note, accent):
        top, tot_h, w = 66, 250, 210
        f.append(text(x0 + w / 2, top - 12, title, size=13, bold=True, color=accent))
        # шари знизу вгору: корпус+ніжки, аналог, флеш, ЯДРО (згори)
        base = [
            ("корпус · ніжки", 0.24, "#d1d5db"),
            ("аналог · I/O",   0.22, "#cbd5e1"),
            ("флеш-пам'ять",   0.30, "#e5e7eb"),
        ]
        fixed = sum(fr for _, fr, _ in base)
        # ядро займає рівно core_frac, решту фіксованих шарів масштабуємо у (1-core_frac)
        scale = (1.0 - core_frac) / fixed
        y = top + tot_h
        for label, fr, col in base:
            hh = tot_h * fr * scale
            y -= hh
            f.append(rect(x0, y, w, hh, fill=col, stroke="#9ca3af", sw=1, rx=0))
            if hh >= 20:
                f.append(text(x0 + w / 2, y + hh / 2 + 4, label, size=10, color=MUTED))
        # ядро — згори, кольорове
        hh = tot_h * core_frac
        y -= hh
        f.append(rect(x0, y, w, hh, fill="#dbeafe", stroke=accent, sw=2, rx=0))
        lab = "ЯДРО 32-біт" if hh >= 18 else "ядро"
        f.append(text(x0 + w / 2, y + hh / 2 + 4, lab, size=11 if hh >= 18 else 9,
                      bold=True, color=accent))
        f.append(text(x0 + w / 2, top + tot_h + 22, note, size=10.5, color=accent, italic=True))

    die(90,  "Грубий старий вузол", 0.42, "ядро — велика частка → дорого", "#c0392b")
    die(480, "Сучасний тонкий вузол", 0.06, "ядро — крихта → майже безкоштовно", FIELD)

    f.append(arrow(310, 190, 470, 190, color=MUTED, sw=1.8))
    f.append(text(390, 178, "техпроцес", size=10, color=MUTED, italic=True))
    f.append(text(390, 205, "↓ на порядки", size=10, color=MUTED, italic=True))
    f.append(text(W / 2, 384,
                  "логіка ядра масштабується з вузлом, а флеш, аналог і корпус — майже ні",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "die-area.svg"), W, H, *f)


# ── 8. (детальна) Енергетичний перелом: сон проти активної фази ──────────────
def fig_energy_crossover():
    import math
    W, H = 800, 440
    f = [text(W / 2, 28, "Точка перелому робочого циклу: коли швидкодія починає важити",
              size=15, bold=True)]

    # осі
    ox, oy, aw, ah = 90, 360, 620, 280
    f.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.5))          # X
    f.append(line(ox, oy, ox, oy - ah, color=INK, sw=1.5))          # Y
    f.append(text(ox + aw / 2, oy + 40, "робочий цикл D (лог-шкала) →", size=11, color=MUTED))
    f.append(text(ox - 60, oy - ah / 2, "I_сер", size=11, color=MUTED))

    # лог-вісь D від 1e-5 до 1e-1; дві складові струму
    Iact, Isleep = 80.0, 0.010   # мА (ESP32-клас)
    d_lo, d_hi = 1e-5, 1e-1
    def X(d):
        return ox + aw * (math.log10(d) - math.log10(d_lo)) / (math.log10(d_hi) - math.log10(d_lo))
    Imax = Iact * d_hi + Isleep
    def Y(i):
        return oy - ah * (i / Imax) ** 0.5 * 0.92   # sqrt-стиск для видимості малих

    # крива внеску сну (майже стала) і активної фази (росте) та сума
    N = 80
    ds = [d_lo * (d_hi / d_lo) ** (k / N) for k in range(N + 1)]
    def poly(vals, col, sw, dash=None):
        pts = " ".join("%.1f,%.1f" % (X(d), Y(v)) for d, v in vals)
        dd = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                % (pts, col, sw, dd))

    f.append(poly([(d, Isleep) for d in ds], TEAL, 2.2, "6 4"))            # сон
    f.append(poly([(d, Iact * d) for d in ds], ORNG, 2.2, "6 4"))          # актив
    f.append(poly([(d, Iact * d + Isleep) for d in ds], NEG, 3.0))         # сума

    # точка перелому D_крит = Isleep/(Iact+Isleep)
    Dc = Isleep / (Iact + Isleep)
    f.append(line(X(Dc), oy, X(Dc), Y(Iact * Dc + Isleep), color=POS, sw=1.4, dash="3 3"))
    f.append(circle(X(Dc), Y(Iact * Dc + Isleep), 4, fill=POS, stroke=POS, sw=1))
    f.append(text(X(Dc), oy - ah - 4, "D_крит ≈ 0.0125 %", size=10.5, bold=True, color=POS))

    # робочий цикл датчика D≈3.3e-4
    Dw = 3.3e-4
    f.append(line(X(Dw), oy, X(Dw), oy - 20, color=MUTED, sw=1, dash="2 2"))
    f.append(text(X(Dw), oy + 20, "датчик 20мс/60с", size=9.5, color=MUTED))

    # підписи зон і кривих
    f.append(text(X(3e-5), oy - ah + 22, "домінує СОН", size=11, bold=True, color=TEAL))
    f.append(text(X(3e-5), oy - ah + 38, "швидкодія байдужа", size=9.5, color=TEAL, italic=True))
    f.append(text(X(4e-2), oy - ah + 22, "домінує АКТИВ", size=11, bold=True, color=ORNG, anchor="end"))
    f.append(text(X(4e-2), oy - ah + 38, "race to sleep", size=9.5, color=ORNG, italic=True, anchor="end"))
    f.append(text(X(6e-3), Y(Iact * 6e-3 + Isleep) - 12, "I_сер (сума)", size=10, bold=True, color=NEG))

    f.append(text(W / 2, 424,
                  "ліворуч від порога виграє найглибший сон, праворуч — найшвидше «зробив і заснув»",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "energy-crossover.svg"), W, H, *f)


# ── 9. (детальна) Компроміс щаблів: швидкість проти передбачуваності відгуку ──
def fig_pipeline_latency():
    W, H = 800, 400
    f = [text(W / 2, 28, "Глибший конвеєр: швидше в середньому — але відгук менш передбачуваний",
              size=14.5, bold=True)]

    tiers = [
        (120, "Cortex-M0+", "2–3 щаблі", "0.9 DMIPS/MHz",
         "відгук: малий, сталий", 0.30, FIELD),
        (400, "Cortex-M4F", "3 щаблі + DSP", "1.25 DMIPS/MHz",
         "відгук: сталий, короткий", 0.55, BLUE),
        (680, "Cortex-M7", "6 щаблів, 2 інстр/такт", "2.14 DMIPS/MHz",
         "відгук: довший, «плаває»", 1.00, PURP),
    ]
    baseY = 300
    for cx, name, pipe, dmips, resp, spd, accent in tiers:
        # стовпчик середньої швидкодії
        bh = 150 * spd
        f.append(rect(cx - 42, baseY - bh, 84, bh, fill="#eef2ff", stroke=accent, sw=2))
        f.append(text(cx, baseY - bh - 8, dmips, size=10, bold=True, color=accent))
        f.append(text(cx, baseY + 20, name, size=12.5, bold=True, color=accent))
        f.append(text(cx, baseY + 37, pipe, size=9.5, color=MUTED))
        # «вус» розкиду часу відгуку — росте зі щаблем
        jitter = 8 + 46 * spd
        jy = baseY + 60
        f.append(line(cx - jitter, jy, cx + jitter, jy, color=POS, sw=2.2))
        f.append(line(cx - jitter, jy - 5, cx - jitter, jy + 5, color=POS, sw=2.2))
        f.append(line(cx + jitter, jy - 5, cx + jitter, jy + 5, color=POS, sw=2.2))
        f.append(circle(cx, jy, 3, fill=POS, stroke=POS, sw=1))
        f.append(text(cx, jy + 22, resp, size=9.5, color=POS, italic=True))

    f.append(text(150, baseY - 150, "↑ середня", size=10, color=MUTED, anchor="start"))
    f.append(text(150, baseY - 137, "  швидкодія", size=10, color=MUTED, anchor="start"))
    f.append(text(600, baseY + 60, "↔ розкид часу відгуку (WCET)", size=10, color=POS, italic=True))
    f.append(text(W / 2, 388,
                  "для жорсткого реального часу M4 із коротким конвеєром часто кращий за швидший M7",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "pipeline-latency.svg"), W, H, *f)


# ── 10. (детальна) Бюджет пам'яті: флеш і ОЗП по шарах ───────────────────────
def fig_memory_budget():
    W, H = 800, 440
    f = [text(W / 2, 28, "Бюджет пам'яті МК: рахуй флеш і ОЗП окремо, на найгірший випадок",
              size=14.5, bold=True)]

    top, colh, bw = 66, 300, 150

    # ── ФЛЕШ (ліворуч): стос знизу вгору, фреймворк домінує ──
    fx = 150
    f.append(text(fx + bw / 2, top - 14, "ФЛЕШ (код)", size=13, bold=True, color=NEG))
    flash = [
        ("код застосунку", 0.14, "#dbeafe", INK),
        ("BLE/Wi-Fi стек", 0.40, "#fde2c4", "#b45309"),   # домінує
        ("HAL/драйвери", 0.10, "#e5e7eb", MUTED),
        ("OTA-дубль образу", 0.22, "#fee2e2", POS),
        ("запас +30…50 %", 0.14, "#f0fdf4", FIELD),
    ]
    y = top + colh
    for label, fr, col, tc in flash:
        hh = colh * fr
        y -= hh
        f.append(rect(fx, y, bw, hh, fill=col, stroke="#9ca3af", sw=1, rx=0))
        if hh >= 16:
            f.append(text(fx + bw / 2, y + hh / 2 + 4, label, size=10, color=tc,
                          bold=(fr >= 0.30)))
    f.append(text(fx + bw / 2, top + colh + 22, "домінує стек, а не застосунок",
                  size=10, color="#b45309", italic=True))

    # ── ОЗП (праворуч): статика внизу, купа ↑ і стек ↓ ростуть назустріч ──
    rx = 520
    f.append(text(rx + bw / 2, top - 14, "ОЗП (виконання)", size=13, bold=True, color=FIELD))
    # статичні дані (низ, фіксовані)
    stat_h = colh * 0.20
    f.append(rect(rx, top + colh - stat_h, bw, stat_h, fill="#dbeafe", stroke="#9ca3af", sw=1, rx=0))
    f.append(text(rx + bw / 2, top + colh - stat_h / 2 + 4, "статичні дані", size=10, color=INK))
    # купа (над статикою, росте вгору)
    heap_h = colh * 0.30
    f.append(rect(rx, top + colh - stat_h - heap_h, bw, heap_h, fill="#d1fae5",
                  stroke=FIELD, sw=1.4, rx=0))
    f.append(text(rx + bw / 2, top + colh - stat_h - heap_h / 2, "купа (heap)", size=10,
                  color=FIELD, bold=True))
    f.append(arrow(rx + bw / 2, top + colh - stat_h - heap_h + 14,
                   rx + bw / 2, top + colh - stat_h - heap_h - 6, color=FIELD, sw=1.4))
    # стек (верх, росте вниз)
    stk_h = colh * 0.22
    f.append(rect(rx, top, bw, stk_h, fill="#fee2e2", stroke=POS, sw=1.4, rx=0))
    f.append(text(rx + bw / 2, top + stk_h / 2 + 4, "стек (worst-case)", size=10,
                  color=POS, bold=True))
    f.append(arrow(rx + bw / 2, top + stk_h - 14, rx + bw / 2, top + stk_h + 8, color=POS, sw=1.4))
    # вільний зазор посередині
    gap_top = top + stk_h
    gap_bot = top + colh - stat_h - heap_h
    f.append(text(rx + bw / 2, (gap_top + gap_bot) / 2 + 4, "← вільний зазор →",
                  size=9.5, color=MUTED, italic=True))
    f.append(text(rx + bw / 2, top + colh + 22, "стек і купа стикнулись → тихо псується",
                  size=10, color=POS, italic=True))

    f.append(text(W / 2, 424,
                  "у бюджеті домінує вага фреймворку/стеків, а не сам застосунок; стек рахуй на найгірший випадок",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "memory-budget.svg"), W, H, *f)


if __name__ == "__main__":
    fig_bit_width()
    fig_cortex_ladder()
    fig_family_map()
    fig_why_own_cpu()
    fig_risc_vs_cisc()
    fig_arm_licensing()
    fig_die_area()
    fig_energy_crossover()
    fig_pipeline_latency()
    fig_memory_budget()
    print("OK: 10 SVG -> ./img/")
