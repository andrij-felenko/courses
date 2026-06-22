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


if __name__ == "__main__":
    fig_decision_tree()
    fig_tradeoff_map()
    fig_budget_example()
    print("OK: 3 figures ->", IMG)
