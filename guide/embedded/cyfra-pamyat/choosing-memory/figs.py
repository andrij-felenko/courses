# -*- coding: utf-8 -*-
"""Фігури до теми «Вибір пам'яті».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки понад палітру svgkit
VOL  = NEG          # летка (робоча) пам'ять — холодне синє
NONV = FIELD        # нелетка (сховище) — зелене
GOLD = "#b9770e"    # рішення-вузли (тепле, читабельне)


# ── 1. Дерево вибору: спершу призначення даних ───────────────────────────────
def fig_decision_tree():
    W, H = 780, 470
    f = [text(W / 2, 26, "Спершу призначення даних, тоді чіп", size=15, bold=True)]

    # корінь
    f.append(rect(310, 44, 160, 52, fill=FILL, stroke=INK, sw=2.2))
    f.append(text(390, 67, "що це за дані?", size=12.5, bold=True))
    f.append(text(390, 84, "робочі чи сховище", size=10, color=MUTED, italic=True))

    # дві великі гілки
    f.append(rect(60, 132, 240, 50, fill="#eef2fb", stroke=VOL, sw=2))
    f.append(text(180, 153, "робочі, швидкі,", size=11.5, color=VOL, bold=True))
    f.append(text(180, 170, "зникають із живленням", size=11.5, color=VOL, bold=True))
    f.append(line(350, 96, 200, 132, color=INK, sw=1.8, dash="4 3"))
    f.append(text(258, 118, "робота", size=10, color=VOL, italic=True))

    f.append(rect(480, 132, 240, 50, fill="#eef6ef", stroke=NONV, sw=2))
    f.append(text(600, 153, "сховище: мусить", size=11.5, color=NONV, bold=True))
    f.append(text(600, 170, "пережити вимкнення", size=11.5, color=NONV, bold=True))
    f.append(line(430, 96, 600, 132, color=INK, sw=1.8, dash="4 3"))
    f.append(text(540, 118, "зберегти", size=10, color=NONV, italic=True))

    # летка гілка: два листки
    leaves_v = [
        (60, "до сотень КБ", "вбудована SRAM", VOL),
        (210, "мегабайти (кадри)", "SDRAM/DDR + контролер", VOL),
    ]
    for x, q, ans, col in leaves_v:
        f.append(line(x + 45, 182, x + 45, 224, color=MUTED, sw=1.4))
        f.append(rect(x, 224, 130, 60, fill=BG, stroke=col, sw=1.6))
        f.append(text(x + 65, 244, q, size=9.5, color=MUTED, italic=True))
        f.append(text(x + 65, 266, ans, size=10.5, color=col, bold=True))

    # нелетка гілка: три листки
    leaves_n = [
        (480, "виконувати код (XIP)", "NOR-флеш", NONV),
        (600, "гори файлів, медіа", "NAND / SD / eMMC", NONV),
        (720, "дрібні часті уставки", "EEPROM / FRAM", NONV),
    ]
    f.append(line(600, 182, 600, 206, color=MUTED, sw=1.4))
    f.append(line(490, 206, 720, 206, color=MUTED, sw=1.4))
    for cx, q, ans, col in leaves_n:
        f.append(line(cx, 206, cx, 224, color=MUTED, sw=1.4))
        f.append(rect(cx - 65, 224, 116, 60, fill=BG, stroke=col, sw=1.6))
        f.append(text(cx - 7, 244, q, size=9, color=MUTED, italic=True))
        f.append(text(cx - 7, 266, ans, size=10.5, color=col, bold=True))

    # підсумкова смуга
    f.append(rect(60, 330, 660, 96, fill=FILL, stroke="#e0e0e4", sw=1.4))
    f.append(text(390, 354, "перше питання ділить вибір надвоє", size=12, bold=True, color=GOLD))
    f.append(text(390, 378,
                  "РОБОЧІ → летка RAM (зникає з живленням, зате швидка)",
                  size=11, color=VOL))
    f.append(text(390, 400,
                  "СХОВИЩЕ → нелетка (переживе вимкнення); далі — код / обсяг / ресурс",
                  size=11, color=NONV))

    f.append(text(W / 2, 452,
                  "діагноз даних економить більше, ніж будь-яке порівняння чіпів",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "decision-tree.svg"), W, H, *f)


# ── 2. Карта компромісів: швидкість ↔ ємність ────────────────────────────────
def fig_tradeoff_map():
    W, H = 720, 470
    f = [text(W / 2, 26, "Карта компромісів: швидкість проти ємності", size=15, bold=True)]

    # осі
    ox, oy = 90, 400          # початок координат (низ-ліво)
    ax, ay = 660, 70          # кінці осей
    f.append(arrow(ox, oy, ax, oy, color=INK, sw=1.8))   # X: ємність →
    f.append(arrow(ox, oy, ox, ay, color=INK, sw=1.8))   # Y: швидкість ↑
    f.append(text(ax - 6, oy + 26, "ємність →", size=11, color=MUTED, anchor="end", italic=True))
    f.append(text(ox - 16, ay + 6, "швидкість ↑", size=11, color=MUTED, anchor="start", italic=True))

    # пунктир компромісу (швидке = дрібне; ємне = повільне)
    f.append(line(150, 110, 600, 360, color="#c9c9cf", sw=1.6, dash="5 4"))
    f.append(text(440, 250, "що швидше — те дрібніше й дорожче",
                  size=9.5, color=MUTED, italic=True))

    # точки: (x, y, назва, нелетка?)
    pts = [
        (140, 100, "SRAM",        False),
        (250, 150, "DRAM",        False),
        (300, 235, "NOR",         True),
        (470, 300, "NAND",        True),
        (540, 340, "SD",          True),
        (610, 350, "eMMC / SSD",  True),
    ]
    for x, y, name, nv in pts:
        col = NONV if nv else VOL
        f.append(circle(x, y, 7, fill=col, stroke=col, sw=1))
        f.append(text(x + 12, y + 4, name, size=11, color=col, bold=True, anchor="start"))

    # легенда
    f.append(circle(420, 430, 7, fill=VOL, stroke=VOL, sw=1))
    f.append(text(434, 434, "летка (робоча RAM)", size=10.5, color=VOL, anchor="start"))
    f.append(circle(560, 430, 7, fill=NONV, stroke=NONV, sw=1))
    f.append(text(574, 434, "нелетка (сховище)", size=10.5, color=NONV, anchor="start"))

    f.append(text(220, 434,
                  "фізика не дає водночас\nі швидкість, і дешеву ємність",
                  size=9.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "tradeoff-map.svg"), W, H, *f)


# ── 3. Комплект пам'яті реального пристрою ────────────────────────────────────
def fig_budget_example():
    W, H = 720, 330
    f = [text(W / 2, 26, "Реєстратор з екраном: чотири пам'яті, чотири потреби", size=15, bold=True)]

    # центр — мікроконтролер
    cx, cy = 360, 180
    f.append(rect(cx - 70, cy - 34, 140, 68, fill=FILL, stroke=INK, sw=2.2))
    f.append(text(cx, cy - 6, "мікроконтролер", size=12, bold=True))
    f.append(text(cx, cy + 14, "збирає чотири чіпи", size=9.5, color=MUTED, italic=True))

    # чотири периферійні пам'яті
    mems = [
        (150, 80,  "кадри екрана",  "SDRAM",          VOL,  "швидко, об'ємно; летко байдуже"),
        (570, 80,  "прошивка (код)", "NOR (XIP)",     NONV, "виконати на місці, без копії"),
        (150, 280, "журнал вимірів", "SD-картка",     NONV, "мегабайти, дешево, знімно"),
        (570, 280, "калібрування",  "FRAM",           NONV, "часті дрібні записи — ресурс!"),
    ]
    for bx, by, need, chip, col, note in mems:
        anchor_dx = -1 if bx < cx else 1
        f.append(line(cx + anchor_dx * 70, cy + (by - cy) * 0.18,
                      bx - anchor_dx * 78, by, color=col, sw=1.8))
        f.append(rect(bx - 84, by - 33, 168, 66, fill=BG, stroke=col, sw=1.8))
        f.append(text(bx, by - 13, need, size=10, color=MUTED, italic=True))
        f.append(text(bx, by + 7, chip, size=12.5, color=col, bold=True))
        f.append(text(bx, by + 25, note, size=9, color=MUTED, italic=True))

    f.append(text(W / 2, 318,
                  "жодна окрема пам'ять не закрила б усі чотири потреби — звідси й кілька",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "budget-example.svg"), W, H, *f)


# ── 4. Драбина ресурсу (лог-шкала циклів перезапису) ─────────────────────────
def fig_endurance_ladder():
    W, H = 760, 470
    f = [text(W / 2, 26, "Ресурс перезапису: різниця на порядки (лог-шкала)", size=15, bold=True)]

    # горизонтальна лог-вісь від 10^2 до 10^16
    ox, oy = 250, 70          # ліва межа смуг, верх
    x0, x1 = ox, 700          # діапазон осі X
    lo, hi = 2, 16            # степені десятки
    def xof(exp):
        return x0 + (x1 - x0) * (exp - lo) / (hi - lo)

    # сітка десяткових поділок
    for e in range(lo, hi + 1, 2):
        gx = xof(e)
        f.append(line(gx, oy - 6, gx, oy + 330, color="#e4e4e8", sw=1))
        f.append(text(gx, oy + 348, "10" + "".join("⁰¹²³⁴⁵⁶⁷⁸⁹"[int(d)] for d in str(e)),
                      size=10, color=MUTED))
    f.append(text((x0 + x1) / 2, oy + 366, "циклів перезапису на комірку (більше — краще)",
                  size=10.5, color=MUTED, italic=True))

    # рядки: (назва, степінь-від, степінь-до, нелетка?, підпис)
    rows = [
        ("QLC NAND",   2.0, 3.0, True,  "~10²–10³"),
        ("TLC NAND",   3.0, 3.5, True,  "~10³"),
        ("MLC NAND",   3.5, 4.0, True,  "~10³–10⁴"),
        ("SLC NAND",   4.7, 5.0, True,  "~10⁵"),
        ("NOR-флеш",   4.0, 5.0, True,  "~10⁴–10⁵"),
        ("EEPROM",     5.0, 6.0, True,  "~10⁵–10⁶"),
        ("FRAM",      12.0, 14.0, True, "~10¹²–10¹⁴"),
        ("DRAM/SRAM", 15.0, 16.0, False, "практично ∞"),
    ]
    bh, gap = 30, 8
    for i, (name, ea, eb, nv, lab) in enumerate(rows):
        y = oy + i * (bh + gap)
        col = NONV if nv else VOL
        bx0, bx1 = xof(ea), xof(eb)
        f.append(text(ox - 14, y + bh * 0.62, name, size=11, color=col,
                      bold=True, anchor="end"))
        f.append(rect(bx0, y, max(bx1 - bx0, 6), bh, fill=col, stroke=col, sw=1, rx=4))
        f.append(text(bx1 + 8, y + bh * 0.62, lab, size=9.5, color=MUTED, anchor="start"))

    f.append(text(W / 2, 458,
                  "від сотні циклів (QLC) до практично безмежних (FRAM, RAM) — 12 порядків різниці",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "endurance-ladder.svg"), W, H, *f)


# ── 5. Строк служби: рівномірний знос і формула ──────────────────────────────
def fig_lifetime_wear():
    W, H = 740, 440
    f = [text(W / 2, 26, "Строк служби флеша: знос розмазують по всіх блоках", size=15, bold=True)]

    # ЗЛІВА: без вирівнювання — один блок б'ють, він гине
    lx = 70
    f.append(text(lx + 90, 60, "без вирівнювання", size=12, bold=True, color=POS))
    for i in range(8):
        bx = lx + (i % 4) * 46
        by = 76 + (i // 4) * 46
        worn = (i == 1)   # один блок затиканий
        f.append(rect(bx, by, 40, 40,
                      fill="#fdecea" if worn else BG,
                      stroke=POS if worn else "#d0d0d4", sw=2 if worn else 1.4))
        if worn:
            f.append(text(bx + 20, by + 26, "✗", size=18, color=POS, bold=True))
    f.append(text(lx + 90, 188, "усі записи в один блок —", size=9.5, color=MUTED, italic=True))
    f.append(text(lx + 90, 202, "він зношується за місяці", size=9.5, color=MUTED, italic=True))

    # СТРІЛКА
    f.append(arrow(300, 130, 360, 130, color=INK, sw=2))
    f.append(text(330, 118, "wear", size=9, color=MUTED, italic=True))
    f.append(text(330, 148, "leveling", size=9, color=MUTED, italic=True))

    # СПРАВА: з вирівнюванням — знос розподілено
    rx = 400
    f.append(text(rx + 90, 60, "з вирівнюванням", size=12, bold=True, color=FIELD))
    for i in range(8):
        bx = rx + (i % 4) * 46
        by = 76 + (i // 4) * 46
        f.append(rect(bx, by, 40, 40, fill="#eef6ef", stroke=FIELD, sw=1.6))
        f.append(text(bx + 20, by + 25, "▪", size=13, color=FIELD))
    f.append(text(rx + 90, 188, "записи розкладено рівно —", size=9.5, color=MUTED, italic=True))
    f.append(text(rx + 90, 202, "гинуть усі разом, багато пізніше", size=9.5, color=MUTED, italic=True))

    # ФОРМУЛА строку служби
    fb, fw, fh = 70, 600, 120
    f.append(rect(fb, 250, fw, fh, fill=FILL, stroke="#e0e0e4", sw=1.4))
    f.append(text(W / 2, 276, "звідси — строк служби у роках", size=12, bold=True, color=GOLD))
    f.append(text(W / 2, 308,
                  "строк =  ресурс(циклів) × ємність(байт)  /  ( WAF × запис(байт/добу) × 365 )",
                  size=12))
    f.append(text(W / 2, 336,
                  "WAF — коефіцієнт підсилення запису (фізичних байтів на один логічний)",
                  size=10, color=MUTED, italic=True))

    f.append(text(W / 2, 428,
                  "рівний знос множить ресурс на КІЛЬКІСТЬ блоків — ось чому SD переживає роки",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "lifetime-wear.svg"), W, H, *f)


# ── 6. XIP проти копіювання в RAM: шлях інструкції ────────────────────────────
def fig_xip_path():
    W, H = 740, 380
    f = [text(W / 2, 26, "Дві дороги інструкції до процесора", size=15, bold=True)]

    # ВЕРХ: XIP — процесор бере інструкцію прямо з NOR
    f.append(text(120, 66, "XIP: виконання на місці", size=12, bold=True, color=NONV))
    f.append(rect(60, 78, 120, 56, fill="#eef6ef", stroke=NONV, sw=1.8))
    f.append(text(120, 100, "NOR-флеш", size=11.5, color=NONV, bold=True))
    f.append(text(120, 118, "байт-адресовна", size=9, color=MUTED, italic=True))
    f.append(arrow(180, 106, 470, 106, color=NONV, sw=2))
    f.append(text(325, 96, "інструкції читаються прямо", size=9.5, color=MUTED, italic=True))
    f.append(text(325, 132, "лише кілька тактів очікування (wait-states)", size=9, color=MUTED, italic=True))
    f.append(rect(470, 78, 120, 56, fill=FILL, stroke=INK, sw=2))
    f.append(text(530, 100, "процесор", size=11.5, bold=True))
    f.append(text(530, 118, "виконує", size=9, color=MUTED, italic=True))
    f.append(text(650, 106, "RAM\nвільна", size=10, color=VOL, italic=True))

    # роздільник
    f.append(line(40, 165, 700, 165, color="#e0e0e4", sw=1.2, dash="4 3"))

    # НИЗ: копіювання — NAND → RAM → процесор
    f.append(text(120, 200, "копіювання: NAND через RAM", size=12, bold=True, color=POS))
    f.append(rect(60, 212, 116, 56, fill=BG, stroke=NONV, sw=1.8))
    f.append(text(118, 234, "NAND", size=11.5, color=NONV, bold=True))
    f.append(text(118, 252, "лише сторінками", size=8.5, color=MUTED, italic=True))
    f.append(arrow(176, 240, 300, 240, color=POS, sw=2))
    f.append(text(238, 228, "копія цілком", size=9, color=POS, italic=True))
    f.append(rect(300, 212, 116, 56, fill="#eef2fb", stroke=VOL, sw=1.8))
    f.append(text(358, 234, "RAM", size=11.5, color=VOL, bold=True))
    f.append(text(358, 252, "з'їдена копією коду", size=8.5, color=MUTED, italic=True))
    f.append(arrow(416, 240, 520, 240, color=INK, sw=2))
    f.append(text(468, 228, "виконує", size=9, color=MUTED, italic=True))
    f.append(rect(520, 212, 116, 56, fill=FILL, stroke=INK, sw=2))
    f.append(text(578, 240, "процесор", size=11.5, bold=True))

    f.append(text(W / 2, 316,
                  "NOR дає будь-яку адресу миттєво → код можна лишити у флеші;",
                  size=10.5, color=MUTED, italic=True))
    f.append(text(W / 2, 336,
                  "NAND віддає лише сторінки → перш ніж виконати, її вміст копіюють у RAM",
                  size=10.5, color=MUTED, italic=True))
    f.append(text(W / 2, 366,
                  "різниця в способі доступу, а не в «швидкості» — ось справжня причина розколу",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "xip-path.svg"), W, H, *f)


if __name__ == "__main__":
    fig_decision_tree()
    fig_tradeoff_map()
    fig_budget_example()
    fig_endurance_ladder()
    fig_lifetime_wear()
    fig_xip_path()
    print("OK: 6 figures ->", IMG)
