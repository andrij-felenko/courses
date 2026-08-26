# -*- coding: utf-8 -*-
"""Фігури до теми «Документація чипа: даташит, reference manual, errata, приклади».
Запуск: python figs.py -> генерує SVG у ./img/
Стиль і компоненти — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

RED, GRN, BLU, YEL, PUR = POS, FIELD, NEG, "#b8860b", "#7d5ba6"


# ── 1. Чотирикутник документації мікроконтролера ─────────────────────────────
def fig_doc_quadrant():
    W, H = 760, 390
    f = [text(W / 2, 26, "Чотири стовпи інженерної документації мікроконтролера", size=15.5, bold=True)]

    # 4 блоки у сітці 2x2
    cards = [
        # (x, y, w, h, title, sub, desc, question, bg, border)
        (40, 50, 325, 145,
         "Datasheet (DS)", "Паспорт чипа від виробника кристала",
         "• Фізичні корпуси та розпіновка (Pinout)\n• Граничні напруги й струми (Absolute Max)\n• Споживання живлення у режимах сну/роботи\n• Часові діаграми шин (Setup/Hold timing)",
         "Питання: чи витримає схема і як розпаяти?",
         "#eaf0fd", BLU),

        (395, 50, 325, 145,
         "Reference Manual (RM / TRM)", "Технічний довідник периферії МК",
         "• Блок-схеми та тактування кожного блоку\n• Карта регістрів пам'яті (Base + Offset)\n• Призначення бітових полів (R/W, RO, W1C)\n• Покроковий алгоритм ініціалізації периферії",
         "Питання: як запрограмувати кожен блок?",
         "#eafaf1", GRN),

        (40, 210, 325, 145,
         "Programming Manual (PM / Core)", "Архітектурний опис ядра процесора",
         "• Архітектура системи команд (ARM / RISC-V)\n• Контролер переривань (NVIC / CLIC / PLIC)\n• Системний таймер SysTick та блок MPU\n• Регістри ядра (R0-R15, PSR, PRIMASK)",
         "Питання: як керувати ядром та винятками?",
         "#f3e9f3", PUR),

        (395, 210, 325, 145,
         "Errata Sheet (ES)", "Бюлетень відомих апаратних вад кремнію",
         "• Апаратні баги конкретних ревізій кристала\n• Граничні умови, де периферія збоїть\n• Опис програмних обходів (Workarounds)\n• Недокументовані обмеження функціоналу",
         "Питання: чому зависає залізо і як це обійти?",
         "#fdecea", RED)
    ]

    for x, y, bw, bh, title, sub, desc, question, bg, col in cards:
        f.append(rect(x, y, bw, bh, fill=bg, stroke=col, sw=1.6, rx=8))
        f.append(text(x + 14, y + 20, title, size=12.5, color=col, bold=True, anchor="start"))
        f.append(text(x + 14, y + 36, sub, size=10, color=MUTED, anchor="start"))

        lines = desc.split("\n")
        for idx, l in enumerate(lines):
            f.append(text(x + 14, y + 54 + idx * 16, l, size=9.8, color=INK, anchor="start"))

        f.append(line(x + 10, y + 120, x + bw - 10, y + 120, color=col, sw=0.8, dash="3 3"))
        f.append(text(x + 14, y + 134, question, size=9.8, color=col, bold=True, italic=True, anchor="start"))

    f.append(text(W / 2, H - 10,
                  "Помилка у виборі документа коштує днів налагодження: жоден документ не замінює інші три",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "doc-quadrant.svg"), W, H, *f)


# ── 2. Анатомія адресації та бітової карти регістра ───────────────────────────
def fig_register_map_anatomy():
    W, H = 760, 350
    f = [text(W / 2, 26, "Анатомія регістра: відображення у пам'ять (MMIO) та бітова карта", size=15.5, bold=True)]

    # Верхній рівень: Базова адреса + Зміщення
    f.append(rect(40, 48, 680, 52, fill=FILL, stroke="#9bb0c2", sw=1.4, rx=6))
    f.append(text(54, 70, "Базова адреса периферійного блоку (Base Address)", size=11, color=INK, bold=True, anchor="start"))
    f.append(text(54, 88, "USART1 Base: 0x4001 3800  (відображено на шину APB2)", size=10, color=MUTED, anchor="start"))

    f.append(text(380, 78, "+", size=16, color=INK, bold=True))

    f.append(text(410, 70, "Зміщення регістра (Offset)", size=11, color=INK, bold=True, anchor="start"))
    f.append(text(410, 88, "USART_ISR Offset: +0x1C  ->  Фізична адреса: 0x4001 381C", size=10, color=BLU, bold=True, anchor="start"))

    # Нижня частина: 32-бітна розбивка регістра
    f.append(text(40, 126, "Бітова карта регістра стану USART_ISR (32 біти, 4 байти):", size=11.5, color=INK, bold=True, anchor="start"))

    # Таблиця бітів
    # Колонки бітових груп: [31:12] Reserved, [11:8] ERR_FLAGS, [7] TXE, [6] TC, [5] RXNE, [4:0] STATUS
    cols = [
        (40, 190, "31:12 (20 біт)", "Reserved", "Резерв", "Писати 0", "#f5f5f5", MUTED),
        (235, 115, "11:8 (4 біти)", "ERR_FLAGS", "W1C / rc_w1", "PE, FE, NE, ORE", "#fdecea", RED),
        (355, 85, "7 (1 біт)", "TXE", "RO", "Tx порожній", "#eaf0fd", BLU),
        (445, 85, "6 (1 біт)", "TC", "W1C / rc_w1", "Tx завершено", "#fdecea", RED),
        (535, 85, "5 (1 біт)", "RXNE", "RO", "Rx повний", "#eafaf1", GRN),
        (625, 95, "4:0 (5 біт)", "CFG_STAT", "R/W", "IDLE, CTS", "#fdf1dc", YEL)
    ]

    table_y = 138
    for x, w, bits, name, acc, desc, bg, col in cols:
        f.append(rect(x, table_y, w, 82, fill=bg, stroke=col, sw=1.3, rx=4))
        f.append(text(x + w / 2, table_y + 16, bits, size=9.8, color=MUTED, bold=True))
        f.append(text(x + w / 2, table_y + 34, name, size=11, color=col, bold=True))
        f.append(text(x + w / 2, table_y + 52, f"[{acc}]", size=9.8, color=col, bold=True))
        f.append(text(x + w / 2, table_y + 70, desc, size=9.5, color=INK))

    # Пояснення типів доступу
    legend_y = 236
    f.append(rect(40, legend_y, 680, 78, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=6))
    f.append(text(54, legend_y + 18, "Критичні типи доступу до бітів у Reference Manual:", size=11, color=INK, bold=True, anchor="start"))

    f.append(text(54, legend_y + 36, "• R/W (Read/Write) — читання поточного значення, запис конфігурації", size=9.8, color=INK, anchor="start"))
    f.append(text(54, legend_y + 52, "• RO (Read Only) — апаратний прапорець стану, запис із ЦП ігнорується або генерує помилку", size=9.8, color=BLU, anchor="start"))
    f.append(text(54, legend_y + 68, "• W1C (Write 1 to Clear) — запис «1» очищає прапорець; запис «0» НЕ впливає на біт (захист від збою)", size=9.8, color=RED, bold=True, anchor="start"))

    f.append(text(W / 2, H - 10,
                  "Зсув адреси (Offset) визначає розташування у пам'яті, а тип доступу (R/W vs W1C) — поведінку шини при записі",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "register-map-anatomy.svg"), W, H, *f)


# ── 3. W1C проти Read-Modify-Write: захист від Race Condition ────────────────
def fig_w1c_vs_rmw():
    W, H = 760, 360
    f = [text(W / 2, 26, "Чому прапорці скидають через W1C, а не Read-Modify-Write", size=15.5, bold=True)]

    # Ліва колонка: Проблема RMW (Read-Modify-Write)
    lx, ly, lw, lh = 40, 48, 325, 270
    f.append(rect(lx, ly, lw, lh, fill="#fdecea", stroke=RED, sw=1.5, rx=8))
    f.append(text(lx + lw / 2, ly + 20, "Небезпека: Read-Modify-Write (RMW)", size=12, color=RED, bold=True))

    steps_rmw = [
        ("1. Читання регістра:", "ISR = 0b00000011 (активні біти 0 і 1)", MUTED),
        ("2. Подія під час обробки:", "Апаратний блок встановлює біт 2!", RED),
        ("3. Модифікація в ЦП:", "Маска скидає біт 0: val &= ~(1 << 0)", MUTED),
        ("4. Запис старого стану:", "ЦП записує 0b00000010 назад у регістр", MUTED),
        ("КАТАСТРОФА:", "Біт 2 випадково СТЕРТО! Подію втрачено назавжди", RED)
    ]

    for i, (st, desc, col) in enumerate(steps_rmw):
        yy = ly + 46 + i * 44
        f.append(rect(lx + 12, yy, lw - 24, 38, fill="#ffffff", stroke=col if col == RED else "#d0d7de", sw=1.1, rx=4))
        f.append(text(lx + 20, yy + 15, st, size=10, color=col, bold=(col == RED), anchor="start"))
        f.append(text(lx + 20, yy + 30, desc, size=9.8, color=INK, anchor="start"))

    # Права колонка: Безпека W1C (Write 1 to Clear)
    rx, ry, rw, rh = 395, 48, 325, 270
    f.append(rect(rx, ry, rw, rh, fill="#eafaf1", stroke=GRN, sw=1.5, rx=8))
    f.append(text(rx + rw / 2, ry + 20, "Атомарний порятунок: W1C (Write 1 to Clear)", size=12, color=GRN, bold=True))

    steps_w1c = [
        ("1. Читання регістра:", "ISR = 0b00000011 (бачимо подію 0)", MUTED),
        ("2. Подія під час обробки:", "Апаратний блок встановлює біт 2!", GRN),
        ("3. Прямий запис маски:", "ЦП пише 1 ТІЛЬКИ в біт 0: ICR = (1 << 0)", MUTED),
        ("4. Апаратне скидання:", "Кремній очищає лише біт 0. Біт 2 НЕ зачіпається", MUTED),
        ("РЕЗУЛЬТАТ:", "Біт 2 цілий! Переривання надійно спрацює знову", GRN)
    ]

    for i, (st, desc, col) in enumerate(steps_w1c):
        yy = ry + 46 + i * 44
        f.append(rect(rx + 12, yy, rw - 24, 38, fill="#ffffff", stroke=col if col == GRN else "#d0d7de", sw=1.1, rx=4))
        f.append(text(rx + 20, yy + 15, st, size=10, color=col, bold=(col == GRN), anchor="start"))
        f.append(text(rx + 20, yy + 30, desc, size=9.8, color=INK, anchor="start"))

    f.append(text(W / 2, H - 10,
                  "W1C дозволяє безпечно скидати прапорці стану в перериваннях без блокування ядра та без гонок",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "w1c-vs-rmw.svg"), W, H, *f)


# ── 4. Життєвий цикл налаштування периферійного блоку ────────────────────────
def fig_peripheral_lifecycle():
    W, H = 760, 330
    f = [text(W / 2, 26, "Послідовність запуску периферійного блоку за Reference Manual", size=15.5, bold=True)]

    steps = [
        ("1. Подача тактування", "Clock Gating & Reset",
         "Увімкнути тактування шини в блоці RCC / SYSCON.\nБез цього доступ до регістрів дає Bus Fault!",
         "#eaf0fd", BLU),
        ("2. Конфігурація GPIO", "Pin Muxing / AF",
         "Перевести піни в режим альтернативної функції.\nНалаштувати Pull-up/Down, швидкість та вихід.",
         "#fdf1dc", YEL),
        ("3. Налаштування блоку", "Control Registers (CR)",
         "Задати дільники (Baud Rate), режими та переривання.\nУсі параметри задаються ДО увімкнення блоку!",
         "#f3e9f3", PUR),
        ("4. Активація (Enable)", "Enable Bit & Loop",
         "Встановити біт ENABLE (напр. UE у CR1).\nОчікувати прапорець готовності та запустити обмін.",
         "#eafaf1", GRN)
    ]

    bx, by, bw, bh = 40, 56, 155, 215
    for i, (title, sub, desc, bg, col) in enumerate(steps):
        x = bx + i * (bw + 20)
        f.append(rect(x, by, bw, bh, fill=bg, stroke=col, sw=1.5, rx=8))
        f.append(text(x + bw / 2, by + 22, title, size=11, color=col, bold=True))
        f.append(text(x + bw / 2, by + 38, sub, size=9.8, color=MUTED, bold=True))

        lines = desc.split("\n")
        for idx, l in enumerate(lines):
            f.append(text(x + 10, by + 68 + idx * 16, l, size=9.6, color=INK, anchor="start"))

        # Стрілка між кроками
        if i < len(steps) - 1:
            ax = x + bw + 3
            ay = by + bh / 2
            f.append(arrow(ax, ay, ax + 14, ay, color=INK, sw=1.8))

    f.append(text(W / 2, H - 12,
                  "Порушення порядку (наприклад запис параметрів після увімкнення) — головна причина «мовчання» периферії",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "peripheral-lifecycle.svg"), W, H, *f)


if __name__ == "__main__":
    fig_doc_quadrant()
    fig_register_map_anatomy()
    fig_w1c_vs_rmw()
    fig_peripheral_lifecycle()
    print("OK: 4 figures generated ->", IMG)
