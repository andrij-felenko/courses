# -*- coding: utf-8 -*-
# Фігури теми «Складові МК». svgkit імпортуємо (не копіюємо) — §5 AUTHORING.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Узгоджені з палітрою svgkit відтінки рамок
RED_F, RED   = "#fdf4f4", POS        # ядро (CPU)
BLU_F, BLU   = "#eef3ff", NEG        # Flash (код)
GRN_F, GRN   = "#eef6ef", FIELD      # SRAM (дані)


# ── block-diagram: уся будова МК на одній шині ────────────────────────────────
# Ідея: ядро в центрі, дві пам'яті ліворуч, гроно периферії праворуч — усе
# нанизане на спільну внутрішню шину, від якої вниз ідуть ніжки у світ.

def fig_block_diagram():
    W, H = 760, 440
    p = []
    # межа чипа
    p.append(rect(40, 56, W - 80, H - 96, fill="#fbfcff", stroke=INK, sw=2.4, rx=14))
    p.append(text(58, 78, "Мікроконтролер — один кристал", size=12, color=MUTED,
                  anchor="start", bold=True))

    # ядро
    core, cw, ch = textbox(W / 2, 120, "Ядро (CPU)\nвибірка–декод–виконання",
                           size=12, bold=True, color=RED, fill=RED_F, stroke=RED, sw=1.8)
    p.append(core)

    # спільна шина
    busy = 196
    p.append(line(96, busy, W - 56, busy, color=GRN, sw=6))
    p.append(text(W - 60, busy - 10, "внутрішня шина — спільна карта адрес",
                  size=11, color=GRN, anchor="end", bold=True))
    p.append(line(W / 2, 120 + ch / 2, W / 2, busy, color=GRN, sw=3))

    # дві пам'яті ліворуч
    fl = fitbox(96, 232, 130, 92, "Flash\nпрограма (код)\nенергонезалежна",
                size=11, bold=True, color=BLU, fill=BLU_F, stroke=BLU, sw=1.8)
    sr = fitbox(238, 232, 130, 92, "SRAM\nдані (змінні)\nенергозалежна",
                size=11, bold=True, color=GRN, fill=GRN_F, stroke=GRN, sw=1.8)
    p.append(line(161, busy, 161, 232, color=GRN, sw=3))
    p.append(line(303, busy, 303, 232, color=GRN, sw=3))
    p.append(fl); p.append(sr)

    # периферія праворуч
    p.append(rect(396, 224, 300, 150, fill="#fafafa", stroke=INK, sw=1.8, rx=10))
    p.append(text(546, 244, "Периферія", size=13, color=INK, bold=True))
    p.append(line(546, busy, 546, 224, color=GRN, sw=3))
    cells = [
        (410, 256, 132, 34, "GPIO"),
        (552, 256, 132, 34, "Таймери · ШІМ"),
        (410, 298, 132, 34, "АЦП · ЦАП"),
        (552, 298, 132, 34, "UART · I2C · SPI"),
    ]
    for cx, cy, cwid, chei, lab in cells:
        p.append(fitbox(cx, cy, cwid, chei, lab, size=12, bold=True,
                        fill=BG, stroke=INK, sw=1.6))
    p.append(fitbox(410, 336, 274, 30, "перерив. · DMA · RTC · сторожовий таймер",
                    size=11, bold=True, fill=BG, stroke=INK, sw=1.6))

    # ніжки у світ
    for i in range(12):
        x = 110 + i * 52
        p.append(rect(x, H - 40, 8, 14, fill="#9a9aa0", stroke="#666666", sw=0.8, rx=0))
    p.append(text(W / 2, H - 12, "ніжки (pins) — у світ", size=11, color=MUTED, bold=True))

    render(os.path.join(OUT, "block-diagram.svg"), W, H, *p,
           title="Будова МК: ядро, дві пам'яті, периферія на спільній шині")


# ── core: що всередині ядра й що таке розрядність ─────────────────────────────
# Ідея: лічильник команд бере інструкцію з Flash, декодер розпізнає, АЛП діє над
# регістрами; ширина «шматка» = розрядність.

def fig_core():
    W, H = 720, 320
    p = []
    p.append(rect(40, 56, W - 80, H - 96, fill="#fbfcff", stroke=RED, sw=2.0, rx=12))
    p.append(text(58, 78, "Ядро (CPU)", size=12, color=RED, anchor="start", bold=True))

    y = 150
    pc  = fitbox(70,  y - 26, 96, 52, "PC\nлічильник\nкоманд", size=10, bold=True,
                 fill=FILL, stroke=INK, sw=1.6)
    dec = fitbox(200, y - 26, 96, 52, "декодер\nрозпізнає", size=10, bold=True,
                 fill=FILL, stroke=INK, sw=1.6)
    alu = fitbox(330, y - 26, 96, 52, "АЛП\nарифметика\nй логіка", size=10, bold=True,
                 fill=RED_F, stroke=RED, sw=1.6, color=RED)
    reg = fitbox(460, y - 26, 110, 52, "регістри\nпроміжні\nзначення", size=10, bold=True,
                 fill=GRN_F, stroke=GRN, sw=1.6, color=GRN)
    for b in (pc, dec, alu, reg):
        p.append(b)
    p.append(arrow(166, y, 200, y, color=INK, sw=1.7))
    p.append(arrow(296, y, 330, y, color=INK, sw=1.7))
    p.append(line(426, y, 460, y, color=INK, sw=1.7))
    # АЛП ↔ регістри в обидва боки
    p.append(arrow(460, y + 12, 426, y + 12, color=INK, sw=1.4))

    # такт під рядком
    p.append(text(W / 2, y + 64, "усе крокує в ритмі такту", size=11, color=MUTED, italic=True))

    # розрядність — ширина шматка
    by = 252
    p.append(text(70, by - 8, "розрядність — ширина «шматка» за один прийом:",
                  size=11, color=INK, anchor="start", bold=True))
    p.append(rect(70, by, 40, 22, fill=BLU_F, stroke=NEG, sw=1.4, rx=3))
    p.append(text(90, by + 16, "8", size=11, color=NEG, bold=True))
    p.append(rect(120, by, 80, 22, fill=BLU_F, stroke=NEG, sw=1.4, rx=3))
    p.append(text(160, by + 16, "16", size=11, color=NEG, bold=True))
    p.append(rect(210, by, 160, 22, fill=BLU_F, stroke=NEG, sw=1.4, rx=3))
    p.append(text(290, by + 16, "32 біт", size=11, color=NEG, bold=True))
    p.append(text(390, by + 16, "→ більші числа й більше пам'яті за крок",
                  size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "core.svg"), W, H, *p,
           title="Усередині ядра: PC, декодер, АЛП, регістри")


# ── memory: дві пам'яті й хто в них живе ──────────────────────────────────────
# Ідея: Flash — постійна, код/константи, пишеться рідко; SRAM — тимчасова,
# змінні/стек/купа, стирається без живлення.

def fig_memory():
    W, H = 720, 320
    p = []
    # Flash
    p.append(rect(50, 70, 300, 210, fill=BLU_F, stroke=NEG, sw=2.0, rx=10))
    p.append(text(200, 96, "Flash — програмна пам'ять", size=13, color=NEG, bold=True))
    p.append(text(200, 116, "енергонезалежна · пишеться рідко, читається весь час",
                  size=10, color=MUTED))
    for i, lab in enumerate(["код (інструкції)", "константи", "текстові рядки", "таблиці"]):
        p.append(text(72, 146 + i * 26, "• " + lab, size=12, color=INK, anchor="start"))
    p.append(text(200, 262, "переживає вимкнення живлення", size=11, color=NEG, italic=True))

    # SRAM
    p.append(rect(370, 70, 300, 210, fill=GRN_F, stroke=FIELD, sw=2.0, rx=10))
    p.append(text(520, 96, "SRAM — пам'ять даних", size=13, color=FIELD, bold=True))
    p.append(text(520, 116, "енергозалежна · швидка, вільно перезаписується",
                  size=10, color=MUTED))
    for i, lab in enumerate(["змінні", "стек викликів", "динамічна пам'ять (купа)"]):
        p.append(text(392, 146 + i * 26, "• " + lab, size=12, color=INK, anchor="start"))
    p.append(text(520, 262, "стирається без живлення", size=11, color=POS, italic=True))

    p.append(text(W / 2, H - 14,
                  "програма «живе» у Flash, а «думає» у SRAM",
                  size=12, color=INK, bold=True))

    render(os.path.join(OUT, "memory.svg"), W, H, *p,
           title="Дві пам'яті МК: Flash для коду, SRAM для даних")


# ── peripheral-catalog: периферія, згрупована за призначенням ─────────────────
# Ідея: п'ять груп вузлів (цифрова, час, аналог, зв'язок, системне); кожен
# вузол — окреме залізо, що працює само.

def fig_peripheral_catalog():
    W, H = 900, 470
    p = []

    def group(x, y, w, h, title, color, rows):
        out = [rect(x, y, w, h, fill="#fbfbfb", stroke=color, sw=2.0, rx=8)]
        out.append(text(x + 12, y + 22, title, size=12, color=color, anchor="start", bold=True))
        out.append(line(x + 12, y + 30, x + w - 12, y + 30, color=color, sw=1.4))
        yy = y + 52
        for name, sub in rows:
            out.append(text(x + 12, yy, "• " + name, size=11, color=INK, anchor="start", bold=True))
            out.append(text(x + 24, yy + 14, sub, size=9, color=MUTED, anchor="start"))
            yy += 36
        return out

    p += group(40, 70, 270, 170, "Цифровий ввід-вивід", NEG, [
        ("GPIO", "універсальні ніжки: 0 або 1"),
        ("читання / запис", "кнопки, світлодіоди, лінії"),
    ])
    p += group(320, 70, 270, 170, "Час", FIELD, [
        ("таймери / лічильники", "міряють і задають інтервали"),
        ("ШІМ (PWM)", "«аналог» цифровою ніжкою"),
    ])
    p += group(600, 70, 260, 170, "Аналог", POS, [
        ("АЦП", "напруга → число"),
        ("ЦАП", "число → напруга"),
    ])
    p += group(40, 256, 405, 180, "Зв'язок із іншими чипами", INK, [
        ("UART", "асинхронний послідовний потік"),
        ("I2C", "дві лінії — багато пристроїв"),
        ("SPI", "швидка повнодуплексна шина"),
    ])
    p += group(455, 256, 405, 180, "Системне", "#6a6a6a", [
        ("контролер переривань", "реагувати на подію вмить"),
        ("DMA", "перекидати дані без ядра"),
        ("RTC · сторожовий таймер", "годинник реального часу · захист від зависань"),
    ])

    render(os.path.join(OUT, "peripheral-catalog.svg"), W, H, *p,
           title="Периферія за призначенням: кожен вузол — окреме залізо")


# ── offload: програмою (ядро застрягло) проти периферії (ядро вільне) ──────────
# Ідея: та сама задача — рівний сигнал — двома способами; смикання вручну тримає
# ядро на 100 % і все одно тремтить, таймер видає рівний сигнал сам.

def fig_offload():
    W, H = 720, 320
    p = []

    # зверху: програмою
    p.append(text(60, 76, "Програмою (bit-banging):", size=12, color=POS,
                  anchor="start", bold=True))
    cpu1 = fitbox(60, 92, 150, 46, "ядро в циклі\nувімк–вимк", size=10, bold=True,
                  fill=RED_F, stroke=POS, sw=1.6, color=POS)
    p.append(cpu1)
    p.append(text(222, 108, "зайняте на 100 %", size=10, color=POS, anchor="start"))
    # тремтливий сигнал
    ox, oy = 420, 116
    jit = [0, 18, 18, 40, 40, 52, 52, 78, 78, 96, 96, 120]
    seq = "0,1,1,0,0,1,1,0,0,1,1,0".split(",")
    pts = []
    x = ox
    hi, lo = oy - 18, oy
    for i, v in enumerate(seq):
        yv = hi if v == "1" else lo
        pts.append("%.0f,%.0f" % (x, yv))
        x = ox + jit[i] * 2.2 if i < len(jit) else x + 16
        pts.append("%.0f,%.0f" % (x, yv))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (" ".join(pts), POS))
    p.append(text(ox, oy + 22, "імпульси тремтять", size=9, color=POS, anchor="start"))

    # знизу: периферією
    p.append(text(60, 196, "Периферією (таймер):", size=12, color=FIELD,
                  anchor="start", bold=True))
    cpu2 = fitbox(60, 212, 150, 46, "ядро лише\nналаштувало", size=10, bold=True,
                  fill=GRN_F, stroke=FIELD, sw=1.6, color=FIELD)
    p.append(cpu2)
    p.append(text(222, 228, "звільнилося", size=10, color=FIELD, anchor="start"))
    # рівний сигнал
    oy2 = 236
    hi2, lo2 = oy2 - 18, oy2
    pts2 = []
    x = 420
    for i in range(6):
        pts2.append("%.0f,%.0f" % (x, hi2)); x += 22
        pts2.append("%.0f,%.0f" % (x, hi2))
        pts2.append("%.0f,%.0f" % (x, lo2)); x += 22
        pts2.append("%.0f,%.0f" % (x, lo2))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join(pts2), FIELD))
    p.append(text(420, oy2 + 22, "сигнал рівний", size=9, color=FIELD, anchor="start"))

    p.append(text(W / 2, H - 14,
                  "перекладай на периферію — точна робота в реальному часі",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "offload.svg"), W, H, *p,
           title="Та сама задача: ядро застрягло проти ядро вільне")


# ── datasheet: рядок специфікації, розкладений на складові ────────────────────
# Ідея: сухий рядок даташита = ядро + Flash + SRAM + перелік периферії; кожне
# число — одна зі складових.

def fig_datasheet():
    W, H = 760, 300
    p = []
    # рядок даташита
    p.append(rect(40, 70, W - 80, 46, fill="#f6f4ec", stroke=INK, sw=1.8, rx=6))
    p.append(text(W / 2, 98,
                  "32-біт @ 160 МГц · Flash 4 МБ · SRAM 320 КБ · 34×GPIO · 8×АЦП · UART/I2C/SPI",
                  size=12, color=INK, bold=True))

    items = [
        (110, "32-біт @ 160 МГц", "ядро\n(розрядність, частота)", RED, RED_F),
        (300, "Flash 4 МБ", "програма\n(код)", NEG, BLU_F),
        (450, "SRAM 320 КБ", "дані\n(змінні)", FIELD, GRN_F),
        (630, "GPIO · АЦП ·\nUART/I2C/SPI", "периферія\n(числом)", INK, "#fafafa"),
    ]
    y = 150
    for cx, top, bot, col, fill in items:
        b, bw, bh = textbox(cx, y + 36, bot, size=10, bold=True, color=col,
                            fill=fill, stroke=col, sw=1.6)
        # лінія від рядка вниз до картки
        p.append(line(cx, 116, cx, y + 36 - bh / 2, color=col, sw=1.4, dash="4 3"))
        p.append(b)

    p.append(text(W / 2, H - 16,
                  "читай даташит як список складових — число до потреби задачі",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "datasheet.svg"), W, H, *p,
           title="Рядок даташита, розкладений на складові")


if __name__ == "__main__":
    fig_block_diagram()
    fig_core()
    fig_memory()
    fig_peripheral_catalog()
    fig_offload()
    fig_datasheet()
    print("OK: figures written to", OUT)
