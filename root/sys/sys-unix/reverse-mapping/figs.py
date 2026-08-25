# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT = "#fbfcff"
WARM = "#fdecea"
COOL = "#eaf0fd"
GREENF = "#eafaf0"
PALE = "#f4f6f8"


# ── 1. Три способи мати обернене відображення ────────────────────────────────
def fig_three_designs():
    W, H = 1220, 620
    p = []

    cols = [
        (80, "Перебрати все", MUTED, PALE,
         "жодної службової\nструктури не треба",
         "переглянути записи\nусіх таблиць усіх\nпроцесів",
         "0", "десятки мільйонів\nзаписів на одну\nсторінку"),
        (460, "Список на кадрі", POS, WARM,
         "кожен кадр носить\nсписок записів, які\nна нього вказують",
         "пройти готовий\nсписок",
         "структура на кожен\nкадр системи + правка\nна кожному відображенні",
         "довжина списку,\nале суцільні\nпромахи кеша"),
        (840, "Шлях через об'єкт", FIELD, GREENF,
         "сторінка знає свій\nоб'єкт, об'єкт знає\nсвої ділянки",
         "спитати об'єкт про\nділянки й порахувати\nадресу для кожної",
         "нуль на кадр: усе\nпотрібне вже є для\nінших цілей",
         "кількість ділянок,\nщо справді накривають\nце місце об'єкта"),
    ]

    for x, name, accent, fillc, keeps, how, price_mem, price_time in cols:
        p.append(fitbox(x, 62, 300, 46, name, size=15,
                        fill=fillc, stroke=accent, sw=1.8, color=accent, bold=True))
        p.append(fitbox(x, 132, 300, 88, keeps, size=12,
                        fill=SOFT, stroke=MUTED, sw=1.2, color=INK))
        p.append(fitbox(x, 244, 300, 88, how, size=12,
                        fill=SOFT, stroke=accent, sw=1.5, color=INK))
        p.append(fitbox(x, 356, 300, 84, price_mem, size=12,
                        fill="#fff", stroke=MUTED, sw=1.2, color=MUTED))
        p.append(fitbox(x, 464, 300, 84, price_time, size=12,
                        fill="#fff", stroke=accent, sw=1.4, color=INK))

    p.append(text(70, 170, "що зберігаємо", size=12, color=MUTED, anchor="end"))
    p.append(text(70, 282, "як відповідаємо", size=12, color=MUTED, anchor="end"))
    p.append(text(70, 392, "плата пам'яттю", size=12, color=MUTED, anchor="end"))
    p.append(text(70, 500, "плата часом", size=12, color=MUTED, anchor="end"))

    return render(os.path.join(OUT, "three-designs.svg"), W, H, *p,
                  title="Хто вказує на цей кадр: три способи відповісти")


# ── 2. Два шляхи від сторінки до записів таблиць ─────────────────────────────
def fig_two_paths():
    W, H = 1180, 800
    p = []

    lanes = [
        (70, "Сторінка з файловою підкладкою", NEG, COOL,
         "mapping → опис відображуваного\nвмісту інода (address_space)",
         "index = зміщення в ФАЙЛІ,\nу сторінках",
         "дерево інтервалів усіх ділянок,\nщо відображають цей файл",
         "запит: які ділянки накривають\nзміщення index"),
        (630, "Анонімна сторінка", POS, WARM,
         "mapping → anon_vma\n(молодший біт вказівника = 1)",
         "index = зміщення в ДІЛЯНЦІ,\nзафіксоване при першому збої",
         "дерево ребер «ділянка ↔ об'єкт»,\nзаведених при кожному fork",
         "запит: які ділянки приписані\nдо цього об'єкта"),
    ]

    for x, name, accent, fillc, f_map, f_index, tree, query in lanes:
        p.append(fitbox(x, 64, 480, 46, name, size=15,
                        fill=fillc, stroke=accent, sw=1.8, color=accent, bold=True))
        p.append(fitbox(x, 132, 480, 62, f_map, size=12.5,
                        fill=SOFT, stroke=accent, sw=1.4, color=INK))
        p.append(fitbox(x, 206, 480, 62, f_index, size=12.5,
                        fill=SOFT, stroke=MUTED, sw=1.2, color=INK))
        p.append(arrow(x + 240, 274, x + 240, 302, color=accent))
        p.append(fitbox(x, 310, 480, 62, tree, size=12.5,
                        fill="#fff", stroke=accent, sw=1.4, color=INK))
        p.append(fitbox(x, 384, 480, 56, query, size=12.5,
                        fill=PALE, stroke=MUTED, sw=1.2, color=MUTED))
        p.append(arrow(x + 240, 446, x + 240, 486, color=accent))

    p.append(fitbox(70, 494, 1040, 96,
                    "спільна арифметика: для кожної знайденої ділянки\n"
                    "address = vm_start + (index − vm_pgoff) · PAGE_SIZE",
                    size=15, fill=GREENF, stroke=FIELD, sw=1.8, color=INK, bold=True))
    p.append(arrow(590, 596, 590, 630, color=FIELD))
    p.append(fitbox(70, 638, 1040, 60,
                    "один спуск таблицями цього процесу до ОДНІЄЇ адреси — і потрібний запис у руках",
                    size=13.5, fill=SOFT, stroke=FIELD, sw=1.4, color=INK))
    p.append(fitbox(70, 714, 1040, 56,
                    "інваріант, без якого формули не існує: сусідні сторінки об'єкта видно за сусідніми адресами",
                    size=13, fill="#fff", stroke=MUTED, sw=1.2, color=MUTED))

    return render(os.path.join(OUT, "two-paths.svg"), W, H, *p,
                  title="Від сторінки до всіх її записів: два входи, одна дорога")


# ── 3. anon_vma до і після розділення ────────────────────────────────────────
def fig_anon_vma_fork():
    W, H = 1300, 700
    p = []

    # ── ліва панель: один спільний об'єкт ───────────────────────────────────
    p.append(fitbox(60, 62, 540, 44, "Спільний об'єкт на все дерево розгалужень",
                    size=14.5, fill=WARM, stroke=POS, sw=1.8, color=POS, bold=True))
    p.append(fitbox(190, 128, 280, 52, "один anon_vma", size=14,
                    fill=SOFT, stroke=POS, sw=1.6, color=INK, bold=True))

    kids = ["ділянка\nбатька", "ділянка\nдитини 1", "ділянка\nдитини 2", "ділянка\nдитини N"]
    for i, lbl in enumerate(kids):
        x = 66 + i * 136
        p.append(arrow(330, 182, x + 56, 232, color=POS, sw=1.2))
        p.append(fitbox(x, 240, 112, 64, lbl, size=11.5,
                        fill="#fff", stroke=MUTED, sw=1.2, color=INK))

    p.append(fitbox(60, 330, 540, 76,
                    "сторінка дитини 2, яку після копіювання при записі\n"
                    "більше ніхто не бачить, помічена ЦИМ ЖЕ об'єктом",
                    size=12.5, fill=SOFT, stroke=MUTED, sw=1.2, color=INK))
    p.append(fitbox(60, 420, 540, 66,
                    "обхід перебирає всі N ділянок, і N−1 з них марні",
                    size=13.5, fill=WARM, stroke=POS, sw=1.6, color=POS, bold=True))

    # ── права панель: власний об'єкт + ребра до предків ─────────────────────
    p.append(fitbox(700, 62, 540, 44, "Власний об'єкт у кожної ділянки",
                    size=14.5, fill=GREENF, stroke=FIELD, sw=1.8, color=FIELD, bold=True))

    p.append(fitbox(700, 122, 168, 40, "глибина", size=12,
                    fill=PALE, stroke=MUTED, sw=1.2, color=MUTED))
    p.append(fitbox(880, 122, 168, 40, "свій об'єкт", size=12,
                    fill=PALE, stroke=MUTED, sw=1.2, color=MUTED))
    p.append(fitbox(1060, 122, 180, 40, "приписана ще до", size=12,
                    fill=PALE, stroke=MUTED, sw=1.2, color=MUTED))

    rows = [
        ("0 — батько", "av₀", "—"),
        ("1 — дитина", "av₁", "av₀"),
        ("2 — онук", "av₂", "av₀, av₁"),
    ]
    for i, (who, own, extra) in enumerate(rows):
        y = 176 + i * 62
        p.append(fitbox(700, y, 168, 50, who, size=12,
                        fill=SOFT, stroke=MUTED, sw=1.2, color=INK))
        p.append(fitbox(880, y, 168, 50, own, size=13,
                        fill="#fff", stroke=FIELD, sw=1.5, color=INK, bold=True))
        p.append(fitbox(1060, y, 180, 50, extra, size=12,
                        fill="#fff", stroke=MUTED, sw=1.2, color=MUTED))

    p.append(fitbox(700, 372, 540, 76,
                    "сторінка, доторкана вже в онука, помічена av₂,\n"
                    "а в дереві av₂ стоїть рівно одна ділянка",
                    size=12.5, fill=SOFT, stroke=MUTED, sw=1.2, color=INK))
    p.append(fitbox(700, 462, 540, 66,
                    "обхід закінчується за один крок",
                    size=13.5, fill=GREENF, stroke=FIELD, sw=1.6, color=FIELD, bold=True))

    p.append(fitbox(60, 556, 1180, 96,
                    "сторінка, доторкана ДО розгалуження, помічена об'єктом предка — і його дерево досі містить усіх нащадків,\n"
                    "тож жоден глядач не загубився; платою за розділення є ребра «ділянка ↔ об'єкт», по одному на предка",
                    size=13, fill="#fff", stroke=FIELD, sw=1.4, color=INK))

    return render(os.path.join(OUT, "anon-vma-fork.svg"), W, H, *p,
                  title="Що робить fork зі зворотним відображенням анонімної сторінки")


# ── 4. Дві конкурентні прив'язки анонімної сторінки (2004) ───────────────────
def fig_anonmm_vs_anonvma():
    W, H = 1240, 700
    p = []

    p.append(fitbox(60, 40, 540, 52, "anonmm — прив'язка до адресного простору",
                    size=15.5, fill=COOL, stroke=NEG, sw=1.8, color=NEG, bold=True))
    p.append(fitbox(640, 40, 540, 52, "anon_vma — прив'язка до ділянок",
                    size=15.5, fill=GREENF, stroke=FIELD, sw=1.8, color=FIELD, bold=True))

    # ліва колонка
    p.append(fitbox(230, 128, 200, 54, "анонімна сторінка", size=13,
                    fill=SOFT, stroke=MUTED, sw=1.4, color=INK))
    p.append(arrow(330, 182, 330, 226, NEG, 1.8))
    p.append(fitbox(230, 226, 200, 54, "struct anonmm", size=13,
                    fill=COOL, stroke=NEG, sw=1.8, color=NEG, bold=True))
    p.append(arrow(330, 280, 330, 324, NEG, 1.8))
    p.append(fitbox(80, 324, 200, 58, "mm процесу A", size=12.5,
                    fill="#fff", stroke=MUTED, sw=1.3, color=INK))
    p.append(fitbox(380, 324, 200, 58, "mm процесу B", size=12.5,
                    fill="#fff", stroke=MUTED, sw=1.3, color=INK))
    p.append(line(330, 300, 180, 324, NEG, 1.4))
    p.append(line(330, 300, 480, 324, NEG, 1.4))
    p.append(fitbox(80, 404, 500, 76,
                    "адресу в просторі беремо з поля index самої сторінки:\n"
                    "вона однакова в усіх, хто цю сторінку успадкував",
                    size=12.5, fill=SOFT, stroke=MUTED, sw=1.2, color=INK))
    p.append(fitbox(80, 500, 500, 96,
                    "ЛАМАЄТЬСЯ на mremap: ділянку пересунули —\n"
                    "збережена адреса стала брехнею.\n"
                    "Лікування: скопіювати зачеплені сторінки",
                    size=12.5, fill=WARM, stroke=POS, sw=1.6, color=INK))

    # права колонка
    p.append(fitbox(810, 128, 200, 54, "анонімна сторінка", size=13,
                    fill=SOFT, stroke=MUTED, sw=1.4, color=INK))
    p.append(arrow(910, 182, 910, 226, FIELD, 1.8))
    p.append(fitbox(810, 226, 200, 54, "struct anon_vma", size=13,
                    fill=GREENF, stroke=FIELD, sw=1.8, color=FIELD, bold=True))
    p.append(arrow(910, 280, 910, 324, FIELD, 1.8))
    p.append(fitbox(660, 324, 200, 58, "ділянка в A", size=12.5,
                    fill="#fff", stroke=MUTED, sw=1.3, color=INK))
    p.append(fitbox(960, 324, 200, 58, "ділянка в B", size=12.5,
                    fill="#fff", stroke=MUTED, sw=1.3, color=INK))
    p.append(line(910, 300, 760, 324, FIELD, 1.4))
    p.append(line(910, 300, 1060, 324, FIELD, 1.4))
    p.append(fitbox(660, 404, 500, 76,
                    "адресу рахуємо з полів самої ділянки:\n"
                    "де ділянка тепер, там і сторінка",
                    size=12.5, fill=SOFT, stroke=MUTED, sw=1.2, color=INK))
    p.append(fitbox(660, 500, 500, 96,
                    "mremap не страшний; обхід не мусить шукати ділянку\n"
                    "в дереві простору.\n"
                    "Ціна: більша структура ділянки й гірше злиття сусідніх",
                    size=12.5, fill=GREENF, stroke=FIELD, sw=1.6, color=INK))

    p.append(fitbox(60, 618, 1120, 62,
                    "виміри показали приблизно рівну швидкодію — вибирали не за нею",
                    size=13, fill="#fff", stroke=MUTED, sw=1.3, color=MUTED))

    return render(os.path.join(OUT, "anonmm-vs-anonvma.svg"), W, H, *p,
                  title="Дві конкурентні прив'язки анонімної сторінки")


# ── 5. Один запис pagemap: 64 біти ───────────────────────────────────────────
def fig_pagemap_entry():
    W, H = 1180, 580
    p = []

    p.append(text(590, 44,
                  "один 64-бітний запис /proc/<pid>/pagemap — одна віртуальна сторінка",
                  size=15, color=INK, bold=True))

    segs = [
        (80,  "63",    POS,   WARM),
        (80,  "62",    NEG,   COOL),
        (80,  "61",    MUTED, PALE),
        (80,  "60–59", MUTED, PALE),
        (80,  "58",    MUTED, PALE),
        (80,  "57",    MUTED, PALE),
        (80,  "56",    MUTED, PALE),
        (80,  "55",    MUTED, PALE),
        (360, "54 … 0", FIELD, GREENF),
    ]
    x = 90
    for w, nm, accent, fillc in segs:
        p.append(fitbox(x, 76, w, 62, nm, size=15,
                        fill=fillc, stroke=accent, sw=1.8, color=accent, bold=True))
        x += w

    left = [
        ("63 — сторінка присутня у фізичній пам'яті", POS, WARM),
        ("62 — сторінка витіснена у своп", NEG, COOL),
        ("61 — файлова або спільна анонімна (з 3.5)", MUTED, SOFT),
        ("60–59 — нуль", MUTED, SOFT),
        ("58 — сторінка-сторож (з 6.15)", MUTED, SOFT),
    ]
    right = [
        ("57 — під захистом запису userfaultfd (з 5.13)", MUTED, SOFT),
        ("56 — відображена рівно один раз (з 4.2)", MUTED, SOFT),
        ("55 — soft-dirty: писали після скидання (з 3.11)", MUTED, SOFT),
        ("54–0 — номер кадру (PFN), коли біт 63 = 1", FIELD, GREENF),
        ("54–5 і 4–0 — зміщення й тип свопу, коли біт 62 = 1", NEG, COOL),
    ]
    for i, (s, accent, fillc) in enumerate(left):
        p.append(fitbox(90, 186 + i * 58, 480, 46, s, size=13,
                        fill=fillc, stroke=accent, sw=1.3, color=INK))
    for i, (s, accent, fillc) in enumerate(right):
        p.append(fitbox(610, 186 + i * 58, 480, 46, s, size=13,
                        fill=fillc, stroke=accent, sw=1.3, color=INK))

    p.append(fitbox(90, 488, 1000, 58,
                    "без CAP_SYS_ADMIN поле PFN читається як нуль — решта бітів лишається чинною",
                    size=13, fill="#fff", stroke=MUTED, sw=1.4, color=MUTED))

    return render(os.path.join(OUT, "pagemap-entry.svg"), W, H, *p,
                  title="Запис pagemap: 64 біти на одну віртуальну сторінку")


if __name__ == "__main__":
    print(fig_three_designs())
    print(fig_two_paths())
    print(fig_anon_vma_fork())
    print(fig_anonmm_vs_anonvma())
    print(fig_pagemap_entry())
