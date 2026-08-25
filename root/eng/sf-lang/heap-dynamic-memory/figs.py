# -*- coding: utf-8 -*-
"""Фігури до теми «Купа» (динамічна пам'ять) та її вставок.
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# Кольори ролей (поверх палітри svgkit)
USED = NEG          # зайнятий блок
FREE = FIELD        # вільний блок / безпечно
BAD  = POS          # біда / відмова
WARN = "#caa24a"    # рамка-висновок


def boxlabel(f, x, y, w, h, s, fill=FILL, stroke=LINE, tcol=INK, size=12, sw=1.6):
    """Прямокутник із підписом по центру; багаторядковий через \\n (fitbox масштабує)."""
    if "\n" in s:
        f.append(fitbox(x, y, w, h, s.split("\n"), size=size, fill=fill,
                        stroke=stroke, sw=sw, color=tcol, bold=True, pad=6))
        return
    f.append(rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=6))
    fs = fit_font(s, w - 12, size, bold=True)
    f.append(text(x + w / 2, y + h / 2 + fs * 0.35, s, size=fs, color=tcol, bold=True))


def note(f, cx, y, w, lines, fill="#fff6e0", stroke=WARN, size=11):
    """Рамка-висновок знизу фігури."""
    f.append(fitbox(cx - w / 2, y, w, 16 + size * 1.45 * len(lines), lines,
                    size=size, fill=fill, stroke=stroke))


# ════════════════════════════════════════════════════════════════════════════
#  СТАТТЯ «Купа»
# ════════════════════════════════════════════════════════════════════════════

# ── 1. Навіщо купа: два випадки, з якими стек не впорається ──────────────────
def fig_why():
    W, H = 880, 380
    f = [text(W / 2, 30, "Навіщо купа: два випадки, з якими стек не впорається",
              size=17, bold=True)]
    f.append(text(W / 2, 52, "локальне зникає при поверненні, а його розмір фіксований — та інколи треба не так",
                  size=11, color=MUTED, italic=True))

    # випадок 1 — пережити функцію
    boxlabel(f, 70, 82, 350, 130,
             "1. Дані мусять ПЕРЕЖИТИ функцію\n\n"
             "функція створила результат і завершилась,\n"
             "а він потрібен далі\n"
             "стек: кадр знято → дані зникли",
             fill="#fdf6f6", stroke=BAD, size=11, tcol=INK)
    # випадок 2 — невідомий розмір
    boxlabel(f, 460, 82, 350, 130,
             "2. Розмір невідомий НАПЕРЕД\n\n"
             "скільки даних — вирішується під час роботи\n"
             "(прочитати N вимірів, N — на льоту)\n"
             "стек: локальний масив фіксований",
             fill="#fff8ec", stroke=WARN, size=11, tcol=INK)

    note(f, W / 2, 236, 760,
         ["Для обох є КУПА: велика область, з якої беруть блок будь-якого розміру під час роботи,",
          "тримають скільки треба (він переживає функції) і повертають, коли вже не потрібен.",
          "«Динамічна» — бо розмір і час життя вирішуються на льоту, а не наперед."],
         fill="#eef6ef", stroke=FREE)
    render(os.path.join(IMG, "why.svg"), W, H, *f)


# ── 2. Взяти й повернути (allocate / free) ──────────────────────────────────
def fig_alloc_free():
    W, H = 880, 360
    f = [text(W / 2, 30, "Дві дії над купою: взяти блок і повернути його",
              size=17, bold=True)]

    # арена-купа
    ax, aw = 70, 740
    f.append(text(ax, 78, "купа (спільний запас вільної пам'яті)", size=11, bold=True, anchor="start"))
    f.append(rect(ax, 88, aw, 40, fill="#eef6ef", stroke=FREE, sw=1.5))
    # виданий блок усередині
    f.append(rect(330, 88, 150, 40, fill="#e9eefb", stroke=USED, sw=1.8))
    f.append(text(405, 113, "виданий блок", size=11, bold=True, color=USED))

    # allocate
    boxlabel(f, 70, 175, 340, 50, "взяти:  p = malloc(100)", fill="#e9eefb", stroke=USED, size=13, tcol=USED)
    f.append(text(240, 240, "купа знаходить вільне місце,", size=10.5, color=MUTED, italic=True))
    f.append(text(240, 256, "повертає ПОКАЖЧИК на нього", size=10.5, color=MUTED, italic=True))
    f.append(arrow(240, 168, 405, 130, color=USED))

    # free
    boxlabel(f, 470, 175, 340, 50, "повернути:  free(p)", fill="#eef6ef", stroke=FREE, size=13, tcol=FREE)
    f.append(text(640, 240, "блок іде назад у спільний запас,", size=10.5, color=MUTED, italic=True))
    f.append(text(640, 256, "звідки його видадуть комусь іншому", size=10.5, color=MUTED, italic=True))
    f.append(arrow(640, 168, 470, 130, color=FREE))

    note(f, W / 2, 286, 760,
         ["Купа РУЧНА: ти сам береш і сам мусиш повернути, причому в будь-якому порядку (не LIFO).",
          "Покажчик — твоя ЄДИНА ниточка до блоку: дані на купі не мають імені, лише адресу."])
    render(os.path.join(IMG, "alloc-free.svg"), W, H, *f)


# ── 3. Стек проти купи ──────────────────────────────────────────────────────
def fig_stack_vs_heap():
    W, H = 900, 472
    f = [text(W / 2, 30, "Стек проти купи: дві області — два характери", size=17, bold=True)]

    cx0, cx1, cx2 = 70, 350, 630
    cw = 250
    # шапки колонок
    boxlabel(f, cx1, 64, cw, 30, "СТЕК", fill="#fdf4f4", stroke=USED, size=13, tcol=USED)
    boxlabel(f, cx2, 64, cw, 30, "КУПА", fill="#fff8ec", stroke=WARN, size=13, tcol="#9a7322")

    rows = [
        ("керування", "автоматичне (вхід/вихід)", "РУЧНЕ (взяв — поверни)"),
        ("порядок", "суворий LIFO", "будь-який"),
        ("швидкість", "дуже швидко (рух SP)", "повільніше (пошук блоку)"),
        ("розмір", "відомий наперед, малий", "гнучкий, до межі купи"),
        ("час життя", "поки триває функція", "поки сам не звільниш"),
        ("головна біда", "переповнення", "фрагментація, витоки"),
    ]
    y = 104
    rh = 44
    for name, a, b in rows:
        boxlabel(f, cx0, y, cw, rh, name, fill="#fafafa", stroke=MUTED, size=12)
        boxlabel(f, cx1, y, cw, rh, a, fill="#fdf4f4", stroke=USED, size=10.5, tcol=INK, sw=1.2)
        boxlabel(f, cx2, y, cw, rh, b, fill="#fff8ec", stroke=WARN, size=10.5, tcol=INK, sw=1.2)
        y += rh + 6

    note(f, W / 2, y + 2, 820,
         ["Стек — для тимчасового, що живе з викликом: швидко й безтурботно, але жорстко.",
          "Купа — для довговічного чи невідомого наперед розміру: гнучко, та повільніше й вручну."])
    render(os.path.join(IMG, "stack-vs-heap.svg"), W, H, *f)


# ── 4. Фрагментація ─────────────────────────────────────────────────────────
def fig_fragmentation():
    W, H = 900, 380
    f = [text(W / 2, 30, "Зовнішня фрагментація: вільного вистачає, та немає суцільного шматка",
              size=16, bold=True)]

    ax, aw = 70, 760
    # спочатку — суцільне
    f.append(text(ax, 74, "спочатку — суцільний вільний простір:", size=10.5, bold=True, anchor="start"))
    f.append(rect(ax, 82, aw, 28, fill="#eef6ef", stroke=FREE, sw=1.4))
    f.append(text(ax + aw / 2, 101, "вільно", size=10, bold=True, color=FREE))

    # після alloc/free — дірки (зайняті/вільні чергуються)
    f.append(text(ax, 150, "після багатьох alloc/free — дірки між зайнятими блоками:", size=10.5, bold=True, anchor="start"))
    segs = [("u", 120), ("f", 70), ("u", 90), ("f", 60), ("u", 110), ("f", 80), ("u", 100), ("f", 90)]
    x = ax
    for kind, w in segs:
        if kind == "u":
            f.append(rect(x, 160, w, 28, fill="#e9eefb", stroke=USED, sw=1.3, rx=2))
        else:
            f.append(rect(x, 160, w, 28, fill="#eef6ef", stroke=FREE, sw=1.3, rx=2))
            f.append(text(x + w / 2, 179, str(w), size=9, color=FREE, bold=True))
        x += w

    # запит на 200
    boxlabel(f, ax, 224, 300, 30, "запит: блок на 200 байтів", fill="#fff8ec", stroke=WARN, size=11, tcol="#9a7322")
    f.append(text(ax + 320, 245, "не влазить — немає суцільних 200", size=13, color=BAD, bold=True, anchor="start"))

    note(f, W / 2, 278, 800,
         ["Вільного загалом ВИСТАЧАЄ (70+60+80+90 = 300), та суцільного шматка на 200 поспіль немає.",
          "Як паркінг із проміжками, у який не влазить автобус, хоч вільних місць сумарно й багато.",
          "Наростає поступово й непомітно, аж велике виділення раптом провалюється."])
    render(os.path.join(IMG, "fragmentation.svg"), W, H, *f)


# ── 5. Біди купи ────────────────────────────────────────────────────────────
def fig_heap_bugs():
    W, H = 900, 360
    f = [text(W / 2, 30, "Три біди ручного керування пам'яттю", size=17, bold=True)]

    cards = [
        (70, "Витік (leak)", BAD,
         "узяв блок і не повернув\n(чи загубив покажчик)\n→ пам'ять помалу\nзаповнюється до краху"),
        (330, "Використання після free", BAD,
         "звільнив блок, та далі\nним користуєшся\n→ висячий покажчик:\nсміття або аварія"),
        (590, "Подвійне free", BAD,
         "звільнив той самий блок\nдвічі\n→ псує бухгалтерію\nрозпорядника купи"),
    ]
    for x, title, col, body in cards:
        f.append(rect(x, 70, 240, 180, fill="#fdf6f6", stroke=col, sw=1.7, rx=8))
        f.append(text(x + 120, 96, title, size=12.5, bold=True, color=col))
        f.append(line(x + 20, 108, x + 220, 108, color="#f0d6d4", sw=1))
        f.append(fitbox(x + 16, 118, 208, 120, body.split("\n"), size=11, fill="#fdf6f6",
                        stroke="#fdf6f6", color=INK, sw=0))

    note(f, W / 2, 268, 800,
         ["Усі три ростуть із того самого кореня, що й біди покажчиків: пам'яттю керуєш ти.",
          "Звідси золоте правило: кожному «взяти» — рівно одне «повернути», і не чіпай блок після free."])
    render(os.path.join(IMG, "heap-bugs.svg"), W, H, *f)


# ── 6. Купа на мікроконтролері ──────────────────────────────────────────────
def fig_heap_on_mcu():
    W, H = 900, 380
    f = [text(W / 2, 30, "Чому на мікроконтролері купу беруть обережно", size=17, bold=True)]

    cards = [
        (70, "Мізерна RAM", "кілобайти всього —\nфрагментація вичерпує\nїх швидко й фатально"),
        (310, "Витік = крах", "пристрій працює тижнями\nбез перезапуску, тож\nнавіть крихітний витік уб'є"),
        (550, "Недетермінований час", "malloc триває то довше,\nто коротше (пошук блоку)\n— зле для реального часу"),
    ]
    for x, title, body in cards:
        f.append(rect(x, 66, 280, 120, fill="#fdf6f6", stroke=BAD, sw=1.6, rx=8))
        f.append(text(x + 140, 90, title, size=12, bold=True, color=BAD))
        f.append(fitbox(x + 14, 100, 252, 78, body.split("\n"), size=10.5, fill="#fdf6f6",
                        stroke="#fdf6f6", color=INK, sw=0))

    # типові підходи
    f.append(text(W / 2, 218, "Типові вбудовані підходи:", size=12, bold=True))
    ways = ["уникати динаміки\nзовсім",
            "виділити все раз\nна старті",
            "пули блоків\nоднакового розміру",
            "статика і стек\nзамість купи"]
    wx = 70
    for w in ways:
        boxlabel(f, wx, 232, 195, 46, w, fill="#eef6ef", stroke=FREE, size=11, tcol=INK)
        wx += 205

    note(f, W / 2, 296, 800,
         ["Це не означає, що «купа погана» — на ПК і серверах вона незамінна.",
          "На крихітному залізі реального часу для постійних чи критичних даних — статика й стек."])
    render(os.path.join(IMG, "heap-on-mcu.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
#  ВСТАВКА math-fragmentation
# ════════════════════════════════════════════════════════════════════════════

# ── дві фрагментації поряд ──────────────────────────────────────────────────
def fig_frag_two_kinds():
    W, H = 900, 380
    f = [text(W / 2, 30, "Та сама втрата пам'яті, два різні механізми", size=17, bold=True)]

    # ── зліва: зовнішня ──
    f.append(text(225, 64, "зовнішня: між блоками", size=12.5, bold=True, color=BAD))
    ax = 60
    segs = [("u", 70), ("f", 18), ("u", 60), ("f", 14), ("u", 60), ("f", 12), ("u", 50), ("f", 16)]
    x = ax
    for kind, w in segs:
        if kind == "u":
            f.append(rect(x, 86, w, 30, fill="#e9eefb", stroke=USED, sw=1.2, rx=2))
        else:
            f.append(rect(x, 86, w, 30, fill="#eef6ef", stroke=FREE, sw=1.2, rx=2))
            f.append(text(x + w / 2, 105, str(w), size=9, color=FREE, bold=True))
        x += w
    f.append(text(ax, 138, "вільно: 18+14+12+16 = 60 Б", size=10, anchor="start"))
    f.append(text(ax, 156, "найбільший суцільний: лише 18 Б", size=10, anchor="start"))
    boxlabel(f, ax, 172, 320, 30, "malloc(40) → відмова", fill="#fdf4f4", stroke=BAD, size=11, tcol=BAD)

    f.append(line(W / 2, 56, W / 2, 230, color="#dde2ea", sw=1.5, dash="2,4"))

    # ── справа: внутрішня ──
    f.append(text(675, 64, "внутрішня: всередині блока", size=12.5, bold=True, color=WARN))
    bx = 520
    f.append(rect(bx, 86, 320, 40, fill="#e9eefb", stroke=USED, sw=1.5))
    # просили 30
    f.append(rect(bx + 6, 91, 200, 30, fill="#eef6ef", stroke=FREE, sw=1.2, rx=2))
    f.append(text(bx + 106, 110, "дані: 30 Б", size=10, color=FREE, bold=True))
    # хвіст у нікуди
    f.append(rect(bx + 210, 91, 104, 30, fill="#fdecea", stroke=BAD, sw=1.2, rx=2))
    f.append(text(bx + 262, 110, "+18 Б", size=10, color=BAD, bold=True))
    f.append(text(bx, 146, "заголовок 8 Б + округлення до 48 Б", size=10, anchor="start"))
    boxlabel(f, bx, 172, 320, 30, "18 з 48 Б у нікуди ≈ 38 %", fill="#fff8ec", stroke=WARN, size=11, tcol="#9a7322")

    note(f, W / 2, 232, 800,
         ["Зовнішня губить пам'ять МІЖ блоками: вільне роздроблене, великий запит не влазить.",
          "Внутрішня губить пам'ять ВСЕРЕДИНІ блока: видали більше, ніж просили, лишок марний."])
    render(os.path.join(IMG, "frag-two-kinds.svg"), W, H, *f)


# ── скільки коштує один malloc (таблиця) ────────────────────────────────────
def fig_frag_internal_cost():
    W, H = 880, 400
    f = [text(W / 2, 30, "Скільки коштує один malloc: заголовок H = 8 Б, класи-степені двійки",
              size=15.5, bold=True)]

    cols = ["запит", "видане (клас)", "втрата", "частка марна"]
    cx = [70, 280, 510, 690]
    cw = [210, 230, 180, 170]
    y = 64
    for i, c in enumerate(cols):
        boxlabel(f, cx[i], y, cw[i], 32, c, fill="#eef0f4", stroke=MUTED, size=11.5)

    rows = [
        ("1 Б", "16 Б", "15 Б", "94 %", BAD),
        ("17 Б", "32 Б", "15 Б", "47 %", BAD),
        ("33 Б", "64 Б", "31 Б", "48 %", BAD),
        ("100 Б", "128 Б", "28 Б", "22 %", FREE),
    ]
    y = 100
    rh = 42
    for req, got, lost, frac, col in rows:
        boxlabel(f, cx[0], y, cw[0], rh, req, fill="#fafafa", stroke=MUTED, size=12)
        boxlabel(f, cx[1], y, cw[1], rh, got, fill="#e9eefb", stroke=USED, size=12, sw=1.2)
        boxlabel(f, cx[2], y, cw[2], rh, lost, fill="#fff8ec", stroke=WARN, size=12, sw=1.2)
        boxlabel(f, cx[3], y, cw[3], rh, frac, fill="#fdf4f4" if col is BAD else "#eef6ef",
                 stroke=col, size=13, tcol=col, sw=1.4)
        y += rh + 6

    note(f, W / 2, y + 2, 800,
         ["Трохи переступив межу класу (17→32, 33→64) — і платиш за весь наступний клас.",
          "Для великих блоків (100→128) фіксований заголовок розчиняється. Дрібні часті виділення — найгірші."])
    render(os.path.join(IMG, "frag-internal-cost.svg"), W, H, *f)


# ── три стратегії в часі ────────────────────────────────────────────────────
def fig_frag_strategies():
    W, H = 900, 400
    f = [text(W / 2, 30, "Найбільший суцільний вільний шматок у часі: три стратегії",
              size=16, bold=True)]

    # три міні-графіки: вісь часу X, «найбільший вільний» Y
    panels = [
        (70, "(а) malloc/free врозкид", BAD, "тане 100 % → 8 %", "spike"),
        (370, "(б) усе раз на старті", FREE, "не змінюється ніколи", "flat"),
        (670, "(в) пул однакових слотів", FREE, "сталий, O(1)", "flat"),
    ]
    gx0, gw, gy0, gh = 0, 220, 110, 150
    for px, title, col, sub, shape in panels:
        f.append(text(px + gw / 2, 64, title, size=12, bold=True, color=col))
        # рамка-графік
        f.append(rect(px + 20, gy0, 180, gh, fill="#fbfcff", stroke=MUTED, sw=1.2))
        ox, oy = px + 30, gy0 + gh - 14
        f.append(line(ox, gy0 + 8, ox, oy, color=MUTED, sw=1))            # вісь Y
        f.append(line(ox, oy, px + 190, oy, color=MUTED, sw=1))           # вісь X
        f.append(text(px + 24, gy0 + 4, "макс", size=9, color=MUTED, anchor="start"))
        f.append(text(px + 188, oy + 11, "час", size=9, color=MUTED, anchor="end"))
        if shape == "spike":
            # спадна пилка з обривом
            pts = "%d,%d %d,%d %d,%d %d,%d %d,%d %d,%d" % (
                ox, gy0 + 18, ox + 40, gy0 + 40, ox + 70, gy0 + 30,
                ox + 110, gy0 + 70, ox + 130, gy0 + 60, ox + 155, oy - 6)
            f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (pts, col))
            f.append(text(ox + 155, oy - 14, "✘", size=13, color=BAD, bold=True))
        else:
            f.append(line(ox, gy0 + 24, px + 190, gy0 + 24, color=col, sw=2.4))
        f.append(text(px + gw / 2, oy + 30, sub, size=10, color=MUTED, italic=True))

    note(f, W / 2, 296, 820,
         ["(а) врозкид: суцільний вільний тане, аж великий запит провалюється — пристрій падає в полі.",
          "(б) усе на старті: картина заморожена, найгірший випадок відомий ще при компіляції.",
          "(в) пул: зовнішньої фрагментації нема за визначенням, alloc/free стають O(1)."])
    render(os.path.join(IMG, "frag-strategies.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
#  ВСТАВКА proj-toy-allocator
# ════════════════════════════════════════════════════════════════════════════

# ── анатомія купи: масив байтів і free list ─────────────────────────────────
def fig_alloc_anatomy():
    W, H = 900, 360
    f = [text(W / 2, 30, "Купа зсередини: масив байтів і список вільних блоків",
              size=16, bold=True)]

    # ряд блоків з заголовками; вільні зшито у free list
    ax = 60
    blocks = [("free", 150, "вільний"), ("used", 130, "зайнятий"),
              ("free", 170, "вільний"), ("used", 120, "зайнятий"), ("free", 150, "вільний")]
    y = 110
    bh = 56
    centers = []
    x = ax
    for kind, w, lab in blocks:
        col = FREE if kind == "free" else USED
        fill = "#eef6ef" if kind == "free" else "#e9eefb"
        # заголовок (вузька смужка зліва)
        f.append(rect(x, y, 22, bh, fill="#eceff3", stroke=col, sw=1.4, rx=0))
        f.append(text(x + 11, y + bh / 2 + 3, "H", size=10, color=MUTED, bold=True))
        # тіло
        f.append(rect(x + 22, y, w - 22, bh, fill=fill, stroke=col, sw=1.5, rx=0))
        f.append(text(x + 22 + (w - 22) / 2, y + bh / 2 + 4, lab, size=10.5, color=col, bold=True))
        centers.append((kind, x + 22 + (w - 22) / 2))
        x += w

    # free list поверх: дуги між вільними (next)
    free_x = [c for k, c in centers if k == "free"]
    f.append(text(ax, y - 30, "free_list →", size=11, bold=True, color=FREE, anchor="start"))
    for i in range(len(free_x) - 1):
        x1, x2 = free_x[i], free_x[i + 1]
        mx = (x1 + x2) / 2
        f.append('<path d="M%.0f,%.0f Q%.0f,%.0f %.0f,%.0f" fill="none" stroke="%s" '
                 'stroke-width="1.8" marker-end="url(#arrow)"/>' % (x1, y - 6, mx, y - 40, x2, y - 6, FREE))
    f.append(text(free_x[-1] + 16, y - 6, "→ NULL", size=10, color=FREE, anchor="start"))

    note(f, W / 2, 210, 800,
         ["Перед кожним блоком — заголовок H (розмір, «вільний?», а у вільних — next).",
          "Зайняті в списку НЕ присутні: free list зшиває лише вільні.",
          "Сусідство за АДРЕСОЮ (фізично впритул) — не те саме, що сусідство за СПИСКОМ (next)."])
    render(os.path.join(IMG, "alloc-anatomy.svg"), W, H, *f)


# ── виділення first-fit і split ─────────────────────────────────────────────
def fig_alloc_firstfit():
    W, H = 900, 360
    f = [text(W / 2, 30, "Виділення first-fit: перший, що влазить, і відрізання хвоста",
              size=16, bold=True)]

    # ряд: malloc(40) пробігає 16, 24, 96
    ax = 60
    y = 92
    bh = 46
    f.append(text(ax, y - 14, "malloc(40) пробігає список:", size=11, bold=True, anchor="start"))
    items = [("16", 120, False), ("24", 150, False), ("96", 260, True)]
    x = ax
    for sz, w, ok in items:
        col = FREE if ok else MUTED
        fill = "#eef6ef" if ok else "#f3f4f6"
        f.append(rect(x, y, w, bh, fill=fill, stroke=col, sw=1.5))
        f.append(text(x + w / 2, y + bh / 2 - 2, sz + " Б", size=11, color=col, bold=True))
        tag = "підходить ✓" if ok else "мале ✗"
        f.append(text(x + w / 2, y + bh / 2 + 14, tag, size=9, color=col))
        x += w

    # унизу: split блока 96 на 40 + 56
    y2 = 200
    f.append(text(ax, y2 - 14, "блок 96 Б ділимо (split):", size=11, bold=True, anchor="start"))
    f.append(rect(ax, y2, 110, bh, fill="#e9eefb", stroke=USED, sw=1.7))
    f.append(text(ax + 55, y2 + bh / 2 + 4, "40 Б віддано", size=10, color=USED, bold=True))
    f.append(rect(ax + 110, y2, 150, bh, fill="#eef6ef", stroke=FREE, sw=1.5))
    f.append(text(ax + 110 + 75, y2 + bh / 2 + 4, "≈56 Б лишок (вільний)", size=10, color=FREE, bold=True))
    f.append(arrow(ax + 320, y2 + bh / 2, ax + 360, y2 + bh / 2, color=INK))
    f.append(text(ax + 370, y2 + bh / 2 + 4, "якщо лишок < поріг — блок віддають цілим", size=10, color=MUTED, anchor="start", italic=True))

    note(f, W / 2, 274, 800,
         ["First-fit бере НАЙПЕРШИЙ придатний блок: не оптимально, зате швидко (best-fit — найтісніший).",
          "Знайдений майже завжди більший за запит: перші n байтів зайняті, хвіст лишається вільним.",
          "Повертають покажчик на ТІЛО — одразу за заголовком."])
    render(os.path.join(IMG, "alloc-firstfit.svg"), W, H, *f)


# ── повернення і злиття сусідів (coalescing) ────────────────────────────────
def fig_alloc_coalesce():
    W, H = 900, 380
    f = [text(W / 2, 30, "Повернення блоку і злиття вільних сусідів (coalescing)",
              size=16, bold=True)]

    ax = 90
    bw = 200
    bh = 40

    def triple(y, mid_free, merged, lab):
        x = ax
        if merged:
            f.append(rect(x, y, bw * 3 + 4, bh, fill="#eef6ef", stroke=FREE, sw=1.8))
            f.append(text(x + (bw * 3) / 2, y + bh / 2 + 4, "один великий вільний блок (96 Б)", size=11, color=FREE, bold=True))
        else:
            for i, (free, sz) in enumerate([(True, "24"), (mid_free, "32"), (True, "40")]):
                col = FREE if free else USED
                fill = "#eef6ef" if free else "#e9eefb"
                f.append(rect(x, y, bw, bh, fill=fill, stroke=col, sw=1.5, rx=2))
                txt = (sz + " Б вільн.") if free else (sz + " Б — звільняємо")
                f.append(text(x + bw / 2, y + bh / 2 + 4, txt, size=10, color=col, bold=True))
                x += bw + 2
        f.append(text(ax - 14, y + bh / 2 + 4, lab, size=11, bold=True, anchor="end"))

    triple(80, False, False, "(а)")
    f.append(text(ax + bw * 1.5, 142, "наївний free лишив би ТРИ уламки (24+32+40), порізано натроє", size=10, color=BAD, italic=True))
    triple(160, True, False, "(б)")
    triple(240, True, True, "(в)")

    note(f, W / 2, 300, 820,
         ["Звільнив блок поряд із вільними — наївний free дає три дрібні уламки: великий запит не влізе.",
          "Лік: злити блок із вільними сусідами за АДРЕСОЮ в один суцільний.",
          "Наступного сусіда дає «адреса + розмір»; попереднього — граничні мітки (розмір у кінці блока)."])
    render(os.path.join(IMG, "alloc-coalesce.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
#  ВСТАВКА proj-block-pools
# ════════════════════════════════════════════════════════════════════════════

# ── анатомія пулу: однакові слоти й free list усередині них ──────────────────
def fig_pool_anatomy():
    W, H = 900, 360
    f = [text(W / 2, 30, "Анатомія пулу: однакові слоти, free list усередині вільних",
              size=16, bold=True)]

    ax = 70
    n = 8
    sw_ = 95
    y = 110
    sh = 60
    # слоти: деякі зайняті, деякі вільні; вільні зшито
    occ = [False, True, False, False, True, False, True, False]  # False = вільний
    centers = []
    x = ax
    for i in range(n):
        used = occ[i]
        col = USED if used else FREE
        fill = "#e9eefb" if used else "#eef6ef"
        f.append(rect(x, y, sw_, sh, fill=fill, stroke=col, sw=1.5))
        f.append(text(x + sw_ / 2, y + 18, "слот %d" % i, size=9.5, color=MUTED))
        if used:
            f.append(text(x + sw_ / 2, y + sh / 2 + 10, "дані", size=10.5, color=USED, bold=True))
        else:
            f.append(text(x + sw_ / 2, y + sh / 2 + 10, "next", size=10.5, color=FREE, bold=True))
        centers.append((used, x + sw_ / 2))
        x += sw_ + 2

    # free_head → ланцюг вільних
    free_c = [c for u, c in centers if not u]
    f.append(text(ax, y - 28, "free_head →", size=11, bold=True, color=FREE, anchor="start"))
    f.append(arrow(ax + 70, y - 24, free_c[0], y - 4, color=FREE))
    for i in range(len(free_c) - 1):
        x1, x2 = free_c[i], free_c[i + 1]
        mx = (x1 + x2) / 2
        f.append('<path d="M%.0f,%.0f Q%.0f,%.0f %.0f,%.0f" fill="none" stroke="%s" '
                 'stroke-width="1.8" marker-end="url(#arrow)"/>' % (x1, y + sh + 4, mx, y + sh + 40, x2, y + sh + 4, FREE))
    f.append(text(free_c[-1] + 8, y + sh + 16, "→ NULL", size=10, color=FREE, anchor="start"))

    note(f, W / 2, 232, 820,
         ["Арену поділено на однакові слоти. Зайняті віддають усі байти даним; вільні зшито у список.",
          "Ключове: next живе ВСЕРЕДИНІ порожнього тіла вільного слота — службового заголовка не треба зовсім.",
          "free_head — вершина стека вільних; порядок у списку не зобов'язаний збігатися з порядком адрес."])
    render(os.path.join(IMG, "pool-anatomy.svg"), W, H, *f)


# ── виділення/звільнення за O(1) ────────────────────────────────────────────
def fig_pool_o1():
    W, H = 900, 380
    f = [text(W / 2, 30, "Пул: alloc і free за сталий час; загальний malloc мусить шукати",
              size=15.5, bold=True)]

    # верх: пул — pop / push
    f.append(text(225, 66, "пул — pop / push вершини", size=12.5, bold=True, color=FREE))
    boxlabel(f, 60, 86, 150, 44, "pool_alloc()\n= pop", fill="#eef6ef", stroke=FREE, size=11)
    f.append(arrow(215, 108, 255, 108, color=INK))
    boxlabel(f, 260, 86, 130, 44, "free_head", fill="#fbfcff", stroke=INK, size=11)
    f.append(arrow(395, 108, 435, 108, color=INK))
    boxlabel(f, 440, 86, 150, 44, "pool_free(p)\n= push", fill="#eef6ef", stroke=FREE, size=11)
    f.append(text(225, 150, "кілька інструкцій, без жодного перебору", size=10, color=MUTED, italic=True))

    f.append(line(60, 176, 840, 176, color="#dde2ea", sw=1.2, dash="2,4"))

    # низ: загальний malloc — пробіг списку
    f.append(text(225, 200, "загальний malloc — пробіг різнорозмірних блоків", size=12, bold=True, color=BAD))
    ax = 60
    y = 220
    for i, (sz, ok) in enumerate([("16", False), ("24", False), ("8", False), ("96", True)]):
        col = FREE if ok else MUTED
        fill = "#eef6ef" if ok else "#f3f4f6"
        x = ax + i * 150
        f.append(rect(x, y, 130, 40, fill=fill, stroke=col, sw=1.4))
        f.append(text(x + 65, y + 24, sz + " Б", size=10.5, color=col, bold=True))
        if i < 3:
            f.append(text(x + 65, y - 6, "«чи влізе?»", size=9, color=MUTED, italic=True))
            f.append(arrow(x + 130, y + 20, x + 150, y + 20, color=MUTED))
    f.append(text(ax + 3 * 150 + 65, y - 6, "нарешті ділимо", size=9, color=FREE, italic=True))

    note(f, W / 2, 286, 820,
         ["Пул шукати не мусить — усі слоти однакові, тож вершину видно одразу: і alloc, і free — O(1).",
          "Загальний malloc проходить список, на кожному перевіряючи «чи влізе?», і ще ділить знайдений.",
          "Сталий час — саме те, що потрібно в керуванні реального часу."])
    render(os.path.join(IMG, "pool-o1.svg"), W, H, *f)


# ── чим пул платить: tradeoff ───────────────────────────────────────────────
def fig_pool_tradeoff():
    W, H = 900, 380
    f = [text(W / 2, 30, "Чим пул платить за свою простоту", size=17, bold=True)]

    # ліворуч: зовнішньої нема
    f.append(text(225, 66, "зовнішньої фрагментації НЕМА", size=12.5, bold=True, color=FREE))
    ax = 60
    y = 86
    for i in range(6):
        x = ax + i * 62
        free = i % 2 == 0
        col = FREE if free else USED
        fill = "#eef6ef" if free else "#e9eefb"
        f.append(rect(x, y, 58, 40, fill=fill, stroke=col, sw=1.4))
    f.append(text(225, 148, "будь-який вільний слот пасує будь-якому запиту", size=10, color=MUTED, italic=True))

    f.append(line(W / 2, 60, W / 2, 230, color="#dde2ea", sw=1.5, dash="2,4"))

    # праворуч: внутрішня
    f.append(text(675, 66, "натомість — ВНУТРІШНЯ фрагментація", size=11.5, bold=True, color=WARN))
    bx = 520
    f.append(rect(bx, 86, 320, 44, fill="#e9eefb", stroke=USED, sw=1.6))
    f.append(rect(bx + 6, 91, 200, 34, fill="#eef6ef", stroke=FREE, sw=1.2, rx=2))
    f.append(text(bx + 106, 112, "об'єкт 40 Б", size=10, color=FREE, bold=True))
    f.append(rect(bx + 206, 91, 108, 34, fill="#fdecea", stroke=BAD, sw=1.2, rx=2))
    f.append(text(bx + 260, 112, "24 Б марно", size=10, color=BAD, bold=True))
    f.append(text(675, 148, "слот на 64 Б, об'єкт 40 Б → хвіст лежить без діла", size=10, color=MUTED, italic=True))

    # дві тверді межі
    boxlabel(f, 150, 196, 280, 40, "запит > слота → відмова\n(хай би скільки слотів вільних)",
             fill="#fdf4f4", stroke=BAD, size=10.5, tcol=BAD)
    boxlabel(f, 470, 196, 280, 40, "усі N слотів роздані →\npool_alloc повертає NULL",
             fill="#fdf4f4", stroke=BAD, size=10.5, tcol=BAD)

    note(f, W / 2, 256, 820,
         ["Розмір слота беруть під найбільший очікуваний об'єкт класу; різні класи — окремі пули.",
          "N рахують під пік одночасно живих об'єктів, ще й із запасом.",
          "І звільняйте лише власні слоти пулу й рівно раз — інакше вільний список псується тихцем."])
    render(os.path.join(IMG, "pool-tradeoff.svg"), W, H, *f)


if __name__ == "__main__":
    # стаття «Купа»
    fig_why()
    fig_alloc_free()
    fig_stack_vs_heap()
    fig_fragmentation()
    fig_heap_bugs()
    fig_heap_on_mcu()
    # math-fragmentation
    fig_frag_two_kinds()
    fig_frag_internal_cost()
    fig_frag_strategies()
    # proj-toy-allocator
    fig_alloc_anatomy()
    fig_alloc_firstfit()
    fig_alloc_coalesce()
    # proj-block-pools
    fig_pool_anatomy()
    fig_pool_o1()
    fig_pool_tradeoff()
    print("Готово: 15 SVG у", IMG)
