# -*- coding: utf-8 -*-
"""Фігури до теми «Wear leveling» (зношування комірок і вирівнювання зносу).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).

Шість фігур теми + дві фігури math-вставки (math-endurance.md, префікс end-)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

WARN = "#caa24a"          # осторога / «потерте»
CELL = "#e4e4e4"          # межа незайманої комірки
GREY_BG = "#f0f0f0"


def _grid(f, x0, y0, cols, rows, cell, gap, fill, stroke, sw=1.2,
          hot=None, hot_fill="#fdecea", hot_stroke=POS):
    """Сітка секторів cols×rows; hot=(c,r) — підсвітити одну клітинку."""
    for r in range(rows):
        for c in range(cols):
            x = x0 + c * (cell + gap)
            y = y0 + r * (cell + gap)
            if hot is not None and (c, r) == hot:
                f.append(rect(x, y, cell, cell, fill=hot_fill, stroke=hot_stroke, sw=1.4, rx=3))
            else:
                f.append(rect(x, y, cell, cell, fill=fill, stroke=stroke, sw=sw, rx=3))


# ── 1. Чому комірка зношується: свіжа → потерта → вичерпана ───────────────────
def fig_why_wear():
    W, H = 920, 400
    f = [text(W / 2, 30, "Чому комірки Flash зношуються", size=18, bold=True),
         text(W / 2, 52, "кожне стирання прогонить електрони крізь ізолятор — і потроху псує його",
              size=11, color=MUTED, italic=True)]

    stages = [
        (170, FIELD, "#eef6ef", "Свіжа комірка", "ізолятор цілий,", "заряд тримається роками", 0),
        (460, WARN,  "#fff6e0", "Після тисяч циклів", "ізолятор потертий,", "заряд починає текти", 5),
        (750, POS,   "#fdecea", "Вичерпана", "заряд не тримається —", "біт ненадійний", 12),
    ]
    import math as _m
    for cx, col, fill, head, l1, l2, leaks in stages:
        f.append(circle(cx, 176, 46, fill=fill, stroke=col, sw=2.4))
        # «застряглі» заряди в ізоляторі — що більше циклів, то більше
        for i in range(leaks):
            a = i * 2.39996
            r = 6 + (i % 5) * 7
            f.append(circle(cx + r * _m.cos(a), 176 + r * _m.sin(a), 2.2, fill=col, stroke=col, sw=0))
        f.append(text(cx, 256, head, size=12, color=col, bold=True))
        f.append(text(cx, 276, l1, size=9.5, color=INK))
        f.append(text(cx, 292, l2, size=9.5, color=MUTED))

    f.append(arrow(228, 176, 402, 176, color=INK, sw=2))
    f.append(text(315, 166, "тунелювання", size=9, color=MUTED))
    f.append(arrow(518, 176, 692, 176, color=INK, sw=2))
    f.append(text(605, 166, "× тисячі циклів", size=9, color=MUTED))

    f.append(fitbox(150, 326, 620, 52,
                    "Кожен цикл «стерти-записати» трохи руйнує ізоляцію затвора.\n"
                    "Звідси — скінченна кількість циклів, яку звуть endurance.",
                    size=10, bold=True, fill="#fff6e0", stroke=WARN, sw=1.4))
    render(os.path.join(IMG, "why-wear.svg"), W, H, *f)


# ── 2. Ресурс різних пам'ятей у циклах стирання (на сектор) ───────────────────
def fig_endurance():
    W, H = 900, 360
    f = [text(W / 2, 30, "Скільки циклів витримує комірка (endurance)", size=18, bold=True),
         text(W / 2, 52, "орієнтовно, на один СЕКТОР (одиницю стирання) — і число це скінченне",
              size=11, color=MUTED, italic=True)]

    rows = [
        ("NOR-Flash (код у чипі)",        "~100 000 циклів", "багато, та не безкінечно",   "#eef6ef", FIELD),
        ("NAND (картки, SSD)",            "~10 000 – 100 000", "менше, бо щільніша",        "#e9eefb", NEG),
        ("Багатобітові комірки (MLC/TLC)", "одиниці тисяч",   "ще менше: біт у бік щільності", "#fff6e0", WARN),
        ("FRAM (для лічильників)",        "~10¹² і більше",  "практично без зносу",        "#fdecea", POS),
    ]
    y, rh = 92, 50
    for label, num, note, fill, col in rows:
        f.append(rect(60, y, 780, rh, fill=fill, stroke=col, sw=1.6, rx=10))
        f.append(text(80, y + 30, label, size=11.5, color=col, anchor="start", bold=True))
        f.append(text(470, y + 30, num, size=12, color=INK, bold=True))
        f.append(text(700, y + 30, note, size=9, color=MUTED))
        y += rh + 10

    f.append(text(W / 2, 348, "Число — на сектор: стер сектор 100 000 разів — і він починає збоїти.",
                  size=9.6, color=INK, bold=True))
    render(os.path.join(IMG, "endurance.svg"), W, H, *f)


# ── 3. Пастка гарячої точки: довбають один сектор, решта незаймана ────────────
def fig_hotspot():
    W, H = 900, 400
    f = [text(W / 2, 30, "Пастка: завжди писати в той самий сектор", size=18, bold=True),
         text(W / 2, 52, "оновлюєш дані «на місці» — і вбиваєш ОДИН сектор, поки решта чипа незаймана",
              size=11, color=MUTED, italic=True)]

    _grid(f, 120, 110, 8, 5, 30, 4, BG, CELL, hot=(7, 1))
    # стрілка «сюди щоразу» в гарячу клітинку (8-ма колонка, 2-й рядок)
    hx = 120 + 7 * 34 + 15
    f.append(arrow(hx, 96, hx, 108, color=POS, sw=2))
    f.append(text(hx, 90, "сюди щоразу", size=9, color=POS, bold=True))

    f.append(rect(560, 130, 300, 170, fill="#fffafa", stroke=POS, sw=1.8, rx=12))
    f.append(text(710, 158, "Що стається:", size=11.5, color=POS, bold=True))
    for i, ln in enumerate([
        "• цей сектор стерто 100 000 разів",
        "• він почав збоїти — дані гинуть",
        "• а 39 сусідів — як нові",
        "• чіп «помер» на 1/40 ресурсу"]):
        f.append(text(580, 188 + i * 26, ln, size=10, color=INK, anchor="start"))

    f.append(text(W / 2, 380, "Класичний приклад — лічильник, що його оновлюють у тому самому місці.",
                  size=9.6, color=INK, bold=True))
    render(os.path.join(IMG, "hotspot.svg"), W, H, *f)


# ── 4. Wear leveling: рівномірний знос замість гарячої точки ──────────────────
def fig_wear_leveling():
    W, H = 900, 400
    f = [text(W / 2, 30, "Wear leveling: розкласти знос рівно по всіх секторах", size=18, bold=True),
         text(W / 2, 52, "не довбати один сектор, а писати по черзі в усі — тоді чіп служить у рази довше",
              size=11, color=MUTED, italic=True)]

    f.append(text(240, 96, "Без вирівнювання", size=11, color=POS, bold=True))
    _grid(f, 110, 110, 8, 4, 30, 4, BG, CELL, hot=(7, 1))
    f.append(text(240, 270, "один зношений, решта марнує", size=9, color=MUTED))

    f.append(text(670, 96, "З вирівнюванням", size=11, color=FIELD, bold=True))
    # усі — рівномірно «потроху зношені» (зелена заливка)
    for r in range(4):
        for c in range(8):
            x = 540 + c * 34
            y = 110 + r * 34
            f.append(rect(x, y, 30, 30, fill="#eef6ef", stroke=FIELD, sw=1.2, rx=3))
    f.append(text(670, 270, "усі зношені рівномірно й потроху", size=9, color=MUTED))

    f.append(fitbox(150, 300, 600, 76,
                    "Замість переписувати той самий сектор — пишемо в наступний вільний,\n"
                    "а старий лишаємо «застарілим». Знос лягає на всі сектори порівну —\n"
                    "і ресурс чипа множиться на їхню кількість.",
                    size=10, bold=True, fill="#eef6ef", stroke=FIELD, sw=1.6))
    render(os.path.join(IMG, "wear-leveling.svg"), W, H, *f)


# ── 5. Арифметика строку служби ──────────────────────────────────────────────
def fig_lifetime():
    W, H = 900, 360
    f = [text(W / 2, 30, "Порахуймо строк служби", size=18, bold=True),
         text(W / 2, 52, "вирівнювання зносу множить ресурс на кількість секторів — і це величезна різниця",
              size=11, color=MUTED, italic=True)]

    f.append(fitbox(180, 86, 540, 46, "строк = endurance × сектори ÷ записів за добу",
                    size=13, bold=True, fill="#fff6e0", stroke=WARN, sw=1.4))

    rows = [
        ("Без вирівнювання (1 сектор)", "100 000 ÷ (10/добу)", "≈ 27 років… для 1 байта", "#fff6e0", WARN),
        ("…але всі записи в нього:",     "при 10 записах/хв",   "≈ кілька місяців — і смерть", "#fdecea", POS),
        ("З вирівнюванням (×256 секторів)", "100 000 × 256 ÷ записи", "роки навіть під шквалом", "#eef6ef", FIELD),
    ]
    y = 156
    for label, mid, res, fill, col in rows:
        f.append(rect(80, y, 740, 46, fill=fill, stroke=col, sw=1.4, rx=8))
        f.append(text(100, y + 28, label, size=10.5, color=col, anchor="start", bold=True))
        f.append(text(430, y + 28, mid, size=10, color=INK))
        f.append(text(700, y + 28, res, size=9.5, color=col, bold=True))
        y += 56

    f.append(text(W / 2, 348,
                  "Висновок: частота записів вирішує все. Рідше пишеш — довше живе, хоч скільки секторів.",
                  size=9.6, color=INK, bold=True))
    render(os.path.join(IMG, "lifetime.svg"), W, H, *f)


# ── 6. Як не вбити Flash: дві колонки звичок ─────────────────────────────────
def fig_practical():
    W, H = 900, 360
    f = [text(W / 2, 30, "Як не вбити Flash: правила на щодень", size=18, bold=True),
         text(W / 2, 52, "знос — тиха смерть; кілька звичок рятують пам'ять на роки",
              size=11, color=MUTED, italic=True)]

    f.append(rect(60, 90, 380, 240, fill="#fffafa", stroke=POS, sw=2, rx=12))
    f.append(text(250, 116, "НЕ роби", size=12.5, color=POS, bold=True))
    for i, ln in enumerate([
        "✗ оновлювати дані «на місці»",
        "✗ писати у Flash щосекунди",
        "✗ вести лічильник у тому ж байті",
        "✗ лити логи без обмежень",
        "✗ ігнорувати endurance"]):
        f.append(text(82, 148 + i * 34, ln, size=10.5, color=INK, anchor="start"))

    f.append(rect(460, 90, 380, 240, fill="#fbfdfb", stroke=FIELD, sw=2, rx=12))
    f.append(text(650, 116, "Роби", size=12.5, color=FIELD, bold=True))
    for i, ln in enumerate([
        "✓ довір NVS / ФС вирівнювання",
        "✓ тримай гаряче в RAM, скидай зрідка",
        "✓ групуй і відкладай записи",
        "✓ обмеж лог кільцем",
        "✓ для лічильників — FRAM"]):
        f.append(text(482, 148 + i * 34, ln, size=10.5, color=INK, anchor="start"))
    render(os.path.join(IMG, "practical.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
#  Фігури до math-вставки math-endurance.md (префікс end-)
# ════════════════════════════════════════════════════════════════════════════

# ── Три важелі формули T = E·N / u ───────────────────────────────────────────
def fig_end_levers():
    W, H = 880, 320
    f = [text(W / 2, 30, "Скільки протягне Flash: три важелі", size=18, bold=True),
         text(W / 2, 52, "строк служби росте з ресурсом, із вирівнюванням — і падає з частотою записів",
              size=10.3, color=MUTED, italic=True)]

    f.append(rect(250, 92, 380, 70, fill="#fbfbff", stroke=INK, sw=1.8, rx=12))
    f.append(text(310, 138, "T", size=26, color=INK, bold=True))
    f.append(text(345, 138, "=", size=22, color=MUTED))
    f.append(text(430, 122, "E · N", size=20, color=FIELD, bold=True))
    f.append(line(390, 132, 470, 132, color=INK, sw=1.6))
    f.append(text(430, 154, "u", size=20, color=POS, bold=True))
    f.append(text(560, 138, "(днів)", size=12, color=MUTED))

    legend = [
        ("E", FIELD, "— ресурс: циклів стирання на сектор (напр. 100 000)"),
        ("N", FIELD, "— вирівнювання: скільки секторів ділять знос"),
        ("u", POS,   "— частота: стирань на день (більша — гірше)"),
        ("T", INK,   "— строк служби, що з цього виходить"),
    ]
    for i, (sym, col, desc) in enumerate(legend):
        y = 196 + i * 28
        f.append(text(120, y, sym, size=14, color=col, bold=True))
        f.append(text(150, y, desc, size=11, color=INK, anchor="start"))

    f.append(text(W / 2, 312, "Побільшити E чи N — або поменшити u — і строк служби росте.",
                  size=10.5, color=INK, bold=True))
    render(os.path.join(IMG, "end-levers.svg"), W, H, *f)


# ── Той самий лічильник, три долі (12 днів / 230 днів / 200+ років) ───────────
def fig_end_example():
    W, H = 880, 320
    f = [text(W / 2, 30, "Той самий лічильник, три долі", size=18, bold=True),
         text(W / 2, 52, "E = 100 000 циклів; міняємо лише вирівнювання й частоту",
              size=11, color=MUTED, italic=True)]

    # три смужки-«терміни»: довжина пропорційна (log) строку, у межах полотна
    bars = [
        ("1 сектор · кожні 10 с",   90,  "≈ 12 днів",    "✗ помирає за два тижні", "#fdecea", POS),
        ("20 секторів · кожні 10 с", 300, "≈ 230 днів",  "вирівнювання × 20",      "#fff6e0", WARN),
        ("20 секторів · щогодини",   560, "≈ 200+ років", "✓ рідше + вирівнювання", "#eef6ef", FIELD),
    ]
    x0, y = 70, 100
    for label, bw, res, note, fill, col in bars:
        f.append(text(x0, y + 18, label, size=11, color=INK, anchor="start", bold=True))
        f.append(rect(x0, y + 26, bw, 28, fill=fill, stroke=col, sw=1.6, rx=5))
        f.append(text(x0 + bw / 2, y + 45, res, size=12, color=col, bold=True))
        f.append(text(x0, y + 70, note, size=9, color=MUTED, anchor="start"))
        y += 66

    f.append(text(W / 2, 308, "Два головні важелі: вирівнювання (× секторів) і рідші записи (÷ частоту).",
                  size=10.5, color=INK, bold=True))
    render(os.path.join(IMG, "end-example.svg"), W, H, *f)


if __name__ == "__main__":
    # тема
    fig_why_wear()
    fig_endurance()
    fig_hotspot()
    fig_wear_leveling()
    fig_lifetime()
    fig_practical()
    # вставка math-endurance.md
    fig_end_levers()
    fig_end_example()
    print("OK: why-wear, endurance, hotspot, wear-leveling, lifetime, practical, "
          "end-levers, end-example")
