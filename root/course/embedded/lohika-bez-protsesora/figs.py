# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE  = NEG
RED   = POS
GREEN = FIELD
AMBER = "#b8860b"
GREY  = "#8a8a8a"
GRID  = "#dfe3e8"


def clk_tri(x, y, size=8, color=INK):
    """Трикутник тактового входу на тілі компонента."""
    return ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="none" '
            'stroke="%s" stroke-width="1.4"/>' % (x, y - size, x + size, y, x, y + size, color))


# ── 1. Загальна структура апаратного автомата ────────────────────────────────
def fig_fsm_structure():
    W, H = 880, 360
    p = []
    p.append(text(W / 2, 28, "Канонічна структура тактованого автомата без процесора", size=16, bold=True))

    # Блок комбінаційної логіки наступного стану (Next-State Logic)
    p.append(rect(140, 90, 190, 140, fill="#f0f4ff", stroke=BLUE, sw=1.8))
    p.append(text(235, 125, "Комбінаційна логіка", size=13, bold=True, color=BLUE))
    p.append(text(235, 145, "наступного стану", size=12, bold=True, color=BLUE))
    p.append(text(235, 175, "Вентилі AND/OR/NAND", size=10.5, color=MUTED))
    p.append(text(235, 192, "або MUX (74HC151)", size=10.5, color=MUTED))

    # Блок регістра стану (State Register - 74HC74)
    p.append(rect(420, 90, 160, 140, fill="#fdf2e9", stroke=AMBER, sw=1.8))
    p.append(text(500, 125, "Регістр стану", size=13, bold=True, color=AMBER))
    p.append(text(500, 145, "(D-тригери)", size=12, bold=True, color=AMBER))
    p.append(text(500, 175, "74HC74", size=11, bold=True, color=INK))
    p.append(text(500, 192, "фіксація по CLK", size=10.5, color=MUTED))
    p.append(clk_tri(420, 195))

    # Блок логіки виходів (Output Logic)
    p.append(rect(660, 90, 170, 140, fill="#eafaf1", stroke=GREEN, sw=1.8))
    p.append(text(745, 125, "Логіка виходів", size=13, bold=True, color=GREEN))
    p.append(text(745, 145, "(дешифратор)", size=12, bold=True, color=GREEN))
    p.append(text(745, 175, "Виходи Мура:", size=10.5, bold=True, color=INK))
    p.append(text(745, 192, "залежать лише від Q", size=10, color=MUTED))

    # Входи: Зовнішні сигнали In -> Логіка наступного стану
    p.append(arrow(40, 140, 140, 140, color=INK))
    p.append(text(90, 130, "Входи (In)", size=11, bold=True, color=INK))
    p.append(text(90, 155, "давачі, кнопки", size=9.5, color=MUTED))

    # З'єднання: Логіка -> D-входи регістра (D)
    p.append(arrow(330, 140, 420, 140, color=BLUE))
    p.append(text(375, 130, "D[1:0]", size=11, bold=True, color=BLUE))
    p.append(text(375, 155, "наступний стан", size=9.5, color=MUTED))

    # З'єднання: Регістр -> Виходи Q
    p.append(line(580, 140, 660, 140, color=AMBER, sw=1.8))
    p.append(arrow(580, 140, 660, 140, color=AMBER))
    p.append(text(620, 130, "Q[1:0]", size=11, bold=True, color=AMBER))
    p.append(text(620, 155, "поточний стан", size=9.5, color=MUTED))

    # Виходи автомата назовні
    p.append(arrow(830, 140, 875, 140, color=GREEN))
    p.append(text(855, 128, "Out", size=11, bold=True, color=GREEN))

    # Зворотний зв'язок: Q повертається в комбінаційну логіку
    p.append(circle(615, 140, 3.5, fill=AMBER, stroke=AMBER))
    p.append(line(615, 140, 615, 275, color=AMBER, sw=1.8))
    p.append(line(615, 275, 100, 275, color=AMBER, sw=1.8))
    p.append(line(100, 275, 100, 180, color=AMBER, sw=1.8))
    p.append(arrow(100, 180, 140, 180, color=AMBER))
    p.append(text(355, 295, "Зворотний зв'язок: поточний стан Q подається назад на вхід логіки", size=11, bold=True, color=AMBER))

    # Тактовий сигнал CLK та скидання RESET
    p.append(arrow(500, 310, 500, 230, color=RED))
    p.append(line(500, 230, 420, 195, color=RED, sw=1.4))
    p.append(text(500, 326, "Тактовий генератор (CLK)", size=11, bold=True, color=RED))
    p.append(text(500, 342, "74HC14 + RC або 555", size=9.5, color=MUTED))

    p.append(arrow(500, 45, 500, 90, color=RED))
    p.append(text(500, 40, "Скидання (RESET / CLR)", size=11, bold=True, color=RED))

    return render(os.path.join(OUT, "fsm-general-structure.svg"), W, H, *p)


# ── 2. Діаграма станів практичного автомата безпеки ──────────────────────────
def fig_state_diagram():
    W, H = 880, 380
    p = []
    p.append(text(W / 2, 28, "Діаграма станів автомата керування продувкою і пальником", size=16, bold=True))

    # 4 стани по колу або по прямокутнику
    # IDLE (200, 130), PURGE (680, 130), IGNITE (680, 280), RUN (200, 280)
    st = [
        (200, 130, "IDLE", "00", "Вентилятор=0\nКлапан=0\nСтатус=ОЧІКУВАННЯ", BLUE),
        (680, 130, "PURGE", "01", "Вентилятор=1\nКлапан=0\nСтатус=ПРОДУВКА", AMBER),
        (680, 290, "IGNITE", "10", "Вентилятор=1\nКлапан=1, Іскра=1\nСтатус=РОЗПАЛ", RED),
        (200, 290, "RUN", "11", "Вентилятор=1\nКлапан=1, Іскра=0\nСтатус=РОБОТА", GREEN),
    ]

    for (cx, cy, name, code, desc, col) in st:
        p.append(circle(cx, cy, 54, fill="#fdfefe", stroke=col, sw=2.4))
        p.append(text(cx, cy - 24, name, size=13, bold=True, color=col))
        p.append(text(cx, cy - 8, "Q1Q0 = " + code, size=11, bold=True, color=INK))
        lines = desc.split("\n")
        for i, ln in enumerate(lines):
            p.append(text(cx, cy + 10 + i * 13, ln, size=9.5, color=MUTED))

    # Перехід IDLE -> IDLE (Start=0)
    p.append('<path d="M 152 110 C 100 80 100 160 148 140" fill="none" stroke="%s" stroke-width="1.6" marker-end="url(#arrow)"/>' % BLUE)
    p.append(text(78, 125, "Start = 0", size=10, color=BLUE, bold=True))

    # Перехід IDLE -> PURGE (Start=1)
    p.append(arrow(254, 130, 626, 130, color=BLUE))
    p.append(text(440, 118, "Start = 1 (команда пуску)", size=11, bold=True, color=BLUE))

    # Перехід PURGE -> PURGE (Done=0 & Abort=0)
    p.append('<path d="M 728 110 C 780 80 780 160 732 140" fill="none" stroke="%s" stroke-width="1.6" marker-end="url(#arrow)"/>' % AMBER)
    p.append(text(810, 125, "Done=0", size=10, color=AMBER, bold=True))

    # Перехід PURGE -> IGNITE (Done=1 & Abort=0)
    p.append(arrow(680, 184, 680, 236, color=AMBER))
    p.append(text(735, 212, "Done = 1", size=11, bold=True, color=AMBER))

    # Перехід IGNITE -> RUN (Flame=1)
    p.append(arrow(626, 290, 254, 290, color=GREEN))
    p.append(text(440, 308, "Flame = 1 (полум'я зафіксовано)", size=11, bold=True, color=GREEN))

    # Перехід RUN -> RUN (Flame=1 & Abort=0)
    p.append('<path d="M 148 280 C 100 260 100 340 152 310" fill="none" stroke="%s" stroke-width="1.6" marker-end="url(#arrow)"/>' % GREEN)
    p.append(text(75, 305, "Flame=1", size=10, color=GREEN, bold=True))

    # Аварійні переходи в IDLE:
    # 1) RUN -> IDLE (Flame=0 або Abort=1)
    p.append(arrow(200, 236, 200, 184, color=RED))
    p.append(text(125, 212, "Flame=0 / Abort", size=10, bold=True, color=RED))

    # 2) IGNITE -> IDLE (Timeout/NoFlame або Abort)
    p.append('<path d="M 640 255 L 245 155" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="4 4" marker-end="url(#arrow)"/>' % RED)
    p.append(text(440, 215, "Аварія / Flame=0 / Abort", size=10.5, bold=True, color=RED))

    return render(os.path.join(OUT, "state-diagram.svg"), W, H, *p)


# ── 3. Карти Карно для синтезу функцій D1 та D0 ──────────────────────────────
def fig_karnaugh_maps():
    W, H = 880, 360
    p = []
    p.append(text(W / 2, 28, "Карти Карно: мінімізація функцій збудження тригерів D1 та D0", size=16, bold=True))

    def draw_kmap(x0, y0, title, var_row, var_col, grid_vals, group_rects, result_eq, col):
        q = []
        # Заголовок карти
        q.append(text(x0 + 150, y0 - 32, title, size=14, bold=True, color=col))

        # Розмітка осей
        q.append(line(x0 - 25, y0 - 25, x0, y0, color=GRID, sw=1.4))
        q.append(text(x0 - 15, y0 - 8, var_row, size=11, bold=True, color=INK))
        q.append(text(x0 + 8, y0 - 15, var_col, size=11, bold=True, color=INK))

        cols = ["00", "01", "11", "10"]
        rows = ["00", "01", "11", "10"]
        cw, ch = 65, 45

        # Підписи стовпчиків
        for j, c in enumerate(cols):
            q.append(text(x0 + j * cw + cw / 2, y0 - 8, c, size=11, bold=True, color=MUTED))
        # Підписи рядків
        for i, r in enumerate(rows):
            q.append(text(x0 - 15, y0 + i * ch + ch / 2 + 4, r, size=11, bold=True, color=MUTED))

        # Сітка комірок
        for i in range(4):
            for j in range(4):
                rx = x0 + j * cw
                ry = y0 + i * ch
                val = grid_vals[i][j]
                bg = "#ffffff" if val == "0" else "#f0fdf4"
                q.append(rect(rx, ry, cw, ch, fill=bg, stroke=GRID, sw=1.2, rx=0))
                txt_col = INK if val == "0" else (col if val == "1" else MUTED)
                q.append(text(rx + cw / 2, ry + ch / 2 + 5, val, size=13, bold=(val == "1"), color=txt_col))

        # Контури петель групування
        for (gj, gi, gw, gh, gcol) in group_rects:
            gx = x0 + gj * cw + 4
            gy = y0 + gi * ch + 4
            g_w = gw * cw - 8
            g_h = gh * ch - 8
            q.append(rect(gx, gy, g_w, g_h, fill="none", stroke=gcol, sw=2.2, rx=8))

        # Підсумкова спрощена формула
        q.append(rect(x0 - 20, y0 + 4 * ch + 15, 300, 36, fill="#f7f9fb", stroke=col, sw=1.6, rx=6))
        q.append(text(x0 + 130, y0 + 4 * ch + 38, result_eq, size=12, bold=True, color=col))
        return q

    # Карта для D1 (залежить від Q1, Q0 та Start, Done, Flame)
    # Згрупована проекція для 4 станів (рядки Q1 Q0, стовпчики Start / Done / Flame)
    # Спрощена матриця 4x4
    vals_d1 = [
        ["0", "0", "0", "0"],  # IDLE (00) -> D1=0
        ["0", "1", "1", "0"],  # PURGE (01) -> D1=1 if Done=1
        ["0", "0", "1", "1"],  # IGNITE (10) -> D1=1 if Flame=1
        ["0", "0", "1", "1"],  # RUN (11) -> D1=1 if Flame=1
    ]
    groups_d1 = [
        (1, 1, 2, 1, BLUE),   # група PURGE*Done
        (2, 2, 2, 2, GREEN),  # група (IGNITE+RUN)*Flame
    ]
    p += draw_kmap(60, 75, "Карта для D1 (старший біт стану)", "Q1 Q0", "In1 In0", vals_d1, groups_d1,
                   "D1 = Q0̄·Q1·Flame + Q0·Q1̄·Done", BLUE)

    # Карта для D0
    vals_d0 = [
        ["0", "1", "1", "0"],  # IDLE (00) -> D0=1 if Start=1
        ["1", "1", "0", "0"],  # PURGE (01) -> D0=1 if Done=0
        ["0", "0", "0", "0"],  # IGNITE (10) -> D0=0 (перехід у RUN 11 дає D0=1)
        ["0", "0", "1", "1"],  # RUN (11) -> D0=1 if Flame=1
    ]
    groups_d0 = [
        (1, 0, 2, 1, RED),    # IDLE*Start
        (0, 1, 2, 1, AMBER),  # PURGE*Donē
        (2, 3, 2, 1, GREEN),  # RUN*Flame
    ]
    p += draw_kmap(500, 75, "Карта для D0 (молодший біт стану)", "Q1 Q0", "In1 In0", vals_d0, groups_d0,
                   "D0 = Q1̄·Q0̄·Start + Q1̄·Q0·Donē + Q1·Q0·Flame", RED)

    return render(os.path.join(OUT, "karnaugh-maps.svg"), W, H, *p)


# ── 4. Принципова схема автомата на мікросхемах 74HC ─────────────────────────
def fig_schematic_74hc():
    W, H = 900, 480
    p = []
    p.append(text(W / 2, 26, "Принципова електрична схема апаратного автомата на логіці 74HC", size=16, bold=True))

    # 1. Блок тактового генератора й антибрязка (74HC14) ліворуч
    p.append(rect(30, 60, 210, 390, fill="#fef9e7", stroke=AMBER, sw=1.8))
    p.append(text(135, 84, "Тактування та входи", size=13, bold=True, color=AMBER))
    p.append(text(135, 102, "74HC14 (тригери Шмітта)", size=10.5, color=MUTED))

    # RC-генератор такту
    p.append(rect(45, 120, 180, 100, fill="#fff", stroke=AMBER, sw=1.4))
    p.append(text(135, 140, "RC Тактовий генератор", size=11, bold=True, color=INK))
    p.append(text(135, 160, "R=100k, C=10uF (~1 Гц)", size=9.5, color=MUTED))
    p.append(arrow(180, 185, 230, 185, color=RED))
    p.append(text(205, 175, "CLK", size=11, bold=True, color=RED))

    # Антибрязкіт кнопки START
    p.append(rect(45, 240, 180, 95, fill="#fff", stroke=BLUE, sw=1.4))
    p.append(text(135, 260, "Антибрязкіт START", size=11, bold=True, color=INK))
    p.append(text(135, 280, "Кнопка + RC (10k/100nF)", size=9.5, color=MUTED))
    p.append(arrow(180, 300, 230, 300, color=BLUE))
    p.append(text(205, 290, "Start_clean", size=10, bold=True, color=BLUE))

    # Вхід FLAME
    p.append(rect(45, 350, 180, 85, fill="#fff", stroke=GREEN, sw=1.4))
    p.append(text(135, 370, "Вхід давача FLAME", size=11, bold=True, color=INK))
    p.append(text(135, 390, "Шмітт-формувач 74HC14", size=9.5, color=MUTED))
    p.append(arrow(180, 405, 230, 405, color=GREEN))
    p.append(text(205, 395, "Flame_clean", size=10, bold=True, color=GREEN))

    # 2. Блок комбінаційної логіки (74HC08 AND, 74HC32 OR, 74HC04 NOT)
    p.append(rect(270, 60, 260, 390, fill="#f0f4ff", stroke=BLUE, sw=1.8))
    p.append(text(400, 84, "Комбінаційна логіка", size=13, bold=True, color=BLUE))
    p.append(text(400, 102, "74HC08 (AND) + 74HC32 (OR) + 74HC04", size=10, color=MUTED))

    # Входи логіки зліва
    p.append(arrow(230, 185, 270, 185, color=RED))   # CLK іде транзитом далі
    p.append(arrow(230, 300, 270, 300, color=BLUE))  # Start
    p.append(arrow(230, 405, 270, 405, color=GREEN)) # Flame

    p.append(text(400, 160, "Обчислення D1 та D0", size=12, bold=True, color=INK))
    p.append(text(400, 185, "D1 = Q1̄·Q0·Done + Q1·Flame", size=10.5, color=BLUE))
    p.append(text(400, 210, "D0 = Q1̄·Q0̄·Start + ...", size=10.5, color=RED))

    p.append(arrow(530, 260, 590, 260, color=BLUE))
    p.append(text(560, 250, "D1", size=12, bold=True, color=BLUE))

    p.append(arrow(530, 320, 590, 320, color=RED))
    p.append(text(560, 310, "D0", size=12, bold=True, color=RED))

    # Лінія CLK транзитом через верх до тригерів
    p.append(line(230, 185, 250, 185, color=RED, sw=1.6))
    p.append(line(250, 185, 250, 40, color=RED, sw=1.6))
    p.append(line(250, 40, 640, 40, color=RED, sw=1.6))
    p.append(line(640, 40, 640, 140, color=RED, sw=1.6))

    # 3. Блок пам'яті станів: 74HC74
    p.append(rect(590, 60, 140, 390, fill="#fdf2e9", stroke=AMBER, sw=1.8))
    p.append(text(660, 84, "Регістр станів", size=13, bold=True, color=AMBER))
    p.append(text(660, 102, "74HC74 Dual D-FF", size=10.5, color=MUTED))

    # FF1 (старший біт Q1)
    p.append(rect(605, 140, 110, 110, fill="#fff", stroke=AMBER, sw=1.4))
    p.append(text(660, 160, "FF1 (Q1)", size=11, bold=True, color=INK))
    p.append(text(620, 190, "D1", size=10, bold=True, color=BLUE))
    p.append(text(700, 190, "Q1", size=10, bold=True, color=AMBER))
    p.append(clk_tri(605, 220))
    p.append(text(625, 224, "CLK", size=9, color=RED))

    # FF0 (молодший біт Q0)
    p.append(rect(605, 280, 110, 110, fill="#fff", stroke=AMBER, sw=1.4))
    p.append(text(660, 300, "FF0 (Q0)", size=11, bold=True, color=INK))
    p.append(text(620, 330, "D0", size=10, bold=True, color=RED))
    p.append(text(700, 330, "Q0", size=10, bold=True, color=AMBER))
    p.append(clk_tri(605, 360))
    p.append(text(625, 364, "CLK", size=9, color=RED))

    # Спільна лінія CLK до обох FF
    p.append(arrow(640, 140, 640, 220, color=RED))
    p.append(arrow(640, 220, 605, 220, color=RED))
    p.append(circle(640, 220, 3, fill=RED, stroke=RED))
    p.append(line(640, 220, 640, 360, color=RED, sw=1.6))
    p.append(arrow(640, 360, 605, 360, color=RED))

    # 4. Блок дешифратора виходів та індикації
    p.append(rect(760, 60, 120, 390, fill="#eafaf1", stroke=GREEN, sw=1.8))
    p.append(text(820, 84, "Виходи Мура", size=13, bold=True, color=GREEN))
    p.append(text(820, 102, "Силове кер.", size=10.5, color=MUTED))

    # Сигнали Q1 і Q0 ідуть на виходи
    p.append(arrow(715, 190, 760, 190, color=AMBER))
    p.append(arrow(715, 330, 760, 330, color=AMBER))

    # Вихідні лінії
    p.append(arrow(880, 150, 895, 150, color=GREEN))
    p.append(text(820, 145, "FAN (Вентилятор)", size=10, bold=True, color=INK))

    p.append(arrow(880, 230, 895, 230, color=GREEN))
    p.append(text(820, 225, "VALVE (Клапан)", size=10, bold=True, color=INK))

    p.append(arrow(880, 310, 895, 310, color=GREEN))
    p.append(text(820, 305, "SPARK (Запал)", size=10, bold=True, color=INK))

    p.append(arrow(880, 390, 895, 390, color=GREEN))
    p.append(text(820, 385, "OK (Статус)", size=10, bold=True, color=GREEN))

    # Зворотний зв'язок Q1, Q0 назад у комбінаційну логіку (по низу)
    p.append(line(735, 190, 735, 465, color=AMBER, sw=1.6))
    p.append(circle(735, 190, 3, fill=AMBER, stroke=AMBER))
    p.append(line(735, 465, 330, 465, color=AMBER, sw=1.6))
    p.append(arrow(330, 465, 330, 450, color=AMBER))
    p.append(text(520, 460, "Зворотний зв'язок Q[1:0] у логіку переходів", size=10, bold=True, color=AMBER))

    return render(os.path.join(OUT, "schematic-74hc.svg"), W, H, *p)


# ── 5. Часова діаграма перехідних процесів та відсутності глічів ──────────────
def fig_timing_glitch():
    W, H = 880, 340
    p = []
    p.append(text(W / 2, 26, "Часова діаграма: синхронізація, затримка поширення та чисті виходи", size=16, bold=True))

    x0, x1 = 140, 820
    period = 110

    # Вертикальні сітки тактових фронтів
    edges = [x0 + period * i for i in range(7)]
    for ex in edges:
        p.append(line(ex, 55, ex, 315, color=GRID, sw=1.2, dash="3 5"))

    def draw_wave(y, label, segs, col=INK):
        p.append(text(130, y + 4, label, size=11, anchor="end", bold=True, color=col))
        px, hi = x0, segs[0][1]
        path = ["M %.1f %.1f" % (x0, y - (14 if hi else 0))]
        for (xend, lvl) in segs:
            path.append("L %.1f %.1f" % (xend, y - (14 if hi else 0)))
            if lvl != hi:
                path.append("L %.1f %.1f" % (xend, y - (14 if lvl else 0)))
            hi = lvl
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (" ".join(path), col))

    # 1. CLK
    clk = []
    for i in range(6):
        clk.append((x0 + period * i + period / 2, True))
        clk.append((x0 + period * (i + 1), False))
    draw_wave(80, "CLK", clk, col=RED)

    # 2. Кнопка START із брязкотом
    b_start = x0 + period * 0.3
    b_end = x0 + period * 0.6
    # брязкіт
    p.append(text(130, 134, "Кнопка (сира)", size=10, anchor="end", color=MUTED))
    p.append(line(x0, 134, b_start, 134, color=GREY, sw=1.6))
    p.append('<path d="M%.1f 134 L%.1f 120 L%.1f 134 L%.1f 120 L%.1f 134 L%.1f 120 L%.1f 120 L%.1f 120" '
             'fill="none" stroke="%s" stroke-width="1.6"/>'
             % (b_start, b_start+8, b_start+16, b_start+24, b_start+30, b_end, b_end+40, x1, GREY))
    p.append(text(b_start + 20, 112, "брязкіт", size=9, color=MUTED))

    # 3. Чистий сигнал після RC + 74HC14
    draw_wave(175, "Start (Шмітт)", [(b_end + 10, False), (x1, True)], col=BLUE)

    # 4. Стан Q0 (переходить в 1 на наступному фронті CLK після Start)
    t_edge1 = edges[1]
    t_prop = 12 # затримка t_pd тригера 74HC74
    draw_wave(225, "Стан Q0", [(t_edge1 + t_prop, False), (edges[3] + t_prop, True), (x1, False)], col=AMBER)
    p.append(arrow(t_edge1, 235, t_edge1 + t_prop, 235, color=AMBER))
    p.append(text(t_edge1 + t_prop + 25, 246, "t_pd ≈ 15 нс", size=9, color=AMBER))

    # 5. Вихід VALVE (Мур: активний у станах IGNITE і RUN, коли Q1=1)
    draw_wave(280, "Вихід VALVE", [(edges[2] + t_prop + 8, False), (edges[5] + t_prop + 8, True), (x1, False)], col=GREEN)
    p.append(text(edges[3], 268, "Чистий сигнал без глічів (Мур)", size=9.5, color=GREEN, bold=True))

    return render(os.path.join(OUT, "timing-glitch-race.svg"), W, H, *p)


if __name__ == "__main__":
    fig_fsm_structure()
    fig_state_diagram()
    fig_karnaugh_maps()
    fig_schematic_74hc()
    fig_timing_glitch()
    print("OK: figures written to", OUT)
