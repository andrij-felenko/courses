# -*- coding: utf-8 -*-
"""Фігури до теми «Фізика комірок» та її вставок (hist-, math-).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

import math

# Локальні відтінки понад палітру svgkit (Flash/затвор — тепле золото)
GOLD = "#b9770e"      # плавучий затвор, заряд у пастці
GOLDF = "#fff8e8"     # тла Flash-карток


# ── helpers ──────────────────────────────────────────────────────────────────
def cap(W, lines, y0=None, size=10.5):
    """Один-два рядки сірого курсивного підпису внизу полотна."""
    if isinstance(lines, str):
        lines = [lines]
    out = []
    y = (y0 if y0 is not None else 0)
    for i, ln in enumerate(lines):
        out.append(text(W / 2, y + i * (size + 4), ln, size=size, color=MUTED, italic=True))
    return out


def cap_transistor(f, cx, top, col):
    """Маленький símbol-ключ (транзистор як вентиль) із виводом затвора вгору."""
    f.append(rect(cx - 20, top, 40, 26, fill="#f4f7f4", stroke=col, sw=1.8))
    f.append(line(cx, top - 16, cx, top, color=col, sw=2.2))
    f.append(line(cx - 11, top - 16, cx + 11, top - 16, color=col, sw=3))
    f.append(line(cx - 20, top + 26, cx - 20, top + 38, color=col, sw=2))
    f.append(line(cx + 20, top + 26, cx + 20, top + 38, color=col, sw=2))


# ════════════════════════════════════════════════════════════════════════════
#  СТАТТЯ «Фізика комірок» — 6 фігур
# ════════════════════════════════════════════════════════════════════════════

# ── 1. overview: три способи зберегти біт ────────────────────────────────────
def fig_overview():
    W, H = 820, 360
    f = [text(W / 2, 30, "Три способи фізично зберегти один біт", size=17, bold=True)]

    cards = [
        ("SRAM", "6 транзисторів",
         ["біт тримає петля", "з двох інверторів —", "той самий тригер"],
         "летка · найшвидша · велика", NEG, "#f3f5fd"),
        ("DRAM", "1 транзистор + 1 конденсатор",
         ["біт — заряд на", "конденсаторі; заряд", "стікає, треба освіжати"],
         "летка · щільна · «тече»", FIELD, "#eef7ee"),
        ("Flash", "1 транзистор, плавучий затвор",
         ["біт — заряд, замкнений", "в ізоляторі; тримається", "роками без живлення"],
         "нелетка · запис зі зносом", GOLD, GOLDF),
    ]
    x = 30
    cw, cy0, ch = 246, 60, 230
    for name, sub, body, foot, col, fill in cards:
        f.append(rect(x, cy0, cw, ch, fill=fill, stroke=col, sw=2))
        f.append(text(x + cw / 2, cy0 + 30, name, size=16, color=col, bold=True))
        f.append(fitbox(x + 10, cy0 + 42, cw - 20, 22, sub, size=11, color=INK, bold=True,
                        fill=fill, stroke="none", sw=0))
        f.append(line(x + 16, cy0 + 72, x + cw - 16, cy0 + 72, color=col, sw=1.1))
        for i, ln in enumerate(body):
            f.append(text(x + cw / 2, cy0 + 96 + i * 18, ln, size=10.5, color=INK))
        f.append(fitbox(x + 10, cy0 + ch - 34, cw - 20, 24, foot, size=10.5, color=col, bold=True,
                        fill=fill, stroke="none", sw=0))
        x += cw + 21

    f.extend(cap(W, ["Дві ідеї: тримати біт ЖИВИМ (струмом у петлі чи зарядом-що-стікає) — це летко;",
                     "або ЗАМКНУТИ його фізично в ізоляторі — це нелетко."], y0=H - 30))
    render(os.path.join(IMG, "overview.svg"), W, H, *f)


# ── 2. SRAM: петля двох інверторів ───────────────────────────────────────────
def fig_sram_6t():
    W, H = 820, 400
    f = [text(W / 2, 30, "SRAM: біт тримає петля з двох інверторів", size=17, bold=True)]

    # два інвертори-трикутники, замкнені в кільце
    f.append('<path d="M 320 150 L 320 200 L 372 175 Z" fill="%s" stroke="%s" stroke-width="2"/>'
             % (BG, NEG))
    f.append(circle(377, 175, 4, fill=BG, stroke=NEG, sw=1.6))
    f.append('<path d="M 500 150 L 500 200 L 448 175 Z" fill="%s" stroke="%s" stroke-width="2"/>'
             % (BG, POS))
    f.append(circle(443, 175, 4, fill=BG, stroke=POS, sw=1.6))
    f.append(text(340, 138, "інвертор 1", size=10, color=NEG, bold=True))
    f.append(text(480, 224, "інвертор 2", size=10, color=POS, bold=True))
    # перехресні зв'язки
    f.append(line(381, 168, 446, 152, color=INK, sw=2))
    f.append('<polyline points="446,152 446,152" fill="none"/>')
    f.append(arrow(381, 168, 444, 153, color=INK, sw=2))
    f.append(arrow(439, 182, 376, 198, color=INK, sw=2))
    f.append(text(412, 142, "вихід одного → вхід іншого", size=9.5, color=MUTED, italic=True))
    f.append(text(298, 180, "Q=1", size=12, color=NEG, bold=True))
    f.append(text(522, 180, "Q̄=0", size=12, color=POS, bold=True))

    # лінія слова + транзистори доступу
    f.append(line(300, 120, 520, 120, color=GOLD, sw=2.4))
    f.append(text(410, 113, "лінія слова (вибір комірки)", size=10, color=GOLD, bold=True))
    cap_transistor(f, 300, 240, FIELD)
    cap_transistor(f, 520, 240, FIELD)
    f.append(line(300, 224, 300, 200, color=FIELD, sw=2))
    f.append(line(520, 224, 520, 200, color=FIELD, sw=2))
    f.append(line(300, 224, 300, 120, color=FIELD, sw=1.4, dash="3 3"))
    f.append(line(520, 224, 520, 120, color=FIELD, sw=1.4, dash="3 3"))
    f.append(line(250, 253, 280, 253, color=FIELD, sw=2))
    f.append(line(540, 253, 570, 253, color=FIELD, sw=2))
    f.append(text(210, 257, "біт-лінія", size=9.5, color=FIELD, bold=True))
    f.append(text(610, 257, "біт-лінія", size=9.5, color=FIELD, bold=True))
    f.append(text(410, 290, "2 транзистори доступу пускають читання/запис лише обраної комірки",
                  size=9.5, color=MUTED, italic=True))

    # бічні пояснення
    body1, _, _ = textbox(120, 175, "Лише два стійкі\nстани: Q=1,Q̄=0\nабо Q=0,Q̄=1.\nКожен інвертор\nпідживлює інший —\nбіт тримає сам себе,\nдоки є живлення.",
                          size=10, fill="#f3f5fd", stroke=NEG, color=INK)
    f.append(body1)
    body2, _, _ = textbox(700, 175, "Ціна — 6 транзисторів:\n4 на петлю + 2 доступ.\nКомірка велика → SRAM\nдорога й місткості мало.\nЗате блискавична\n(читати — лише глянути)\nй без освіження.",
                          size=10, fill="#eef7ee", stroke=FIELD, color=INK)
    f.append(body2)

    f.extend(cap(W, ["«Статична» — бо стан тримається сам, без періодичного відновлення.",
                     "Місце SRAM: кеші процесора й мала швидка робоча пам'ять мікроконтролера."],
                 y0=H - 30))
    render(os.path.join(IMG, "sram-6t.svg"), W, H, *f)


# ── 3. DRAM: один транзистор + конденсатор ───────────────────────────────────
def fig_dram_1t1c():
    W, H = 820, 410
    f = [text(W / 2, 30, "DRAM: біт — це заряд на одному конденсаторі", size=17, bold=True)]

    # комірка ліворуч
    cap_transistor(f, 170, 95, FIELD)
    f.append(line(190, 95, 240, 95, color=GOLD, sw=2.4))
    f.append(text(170, 80, "лінія слова", size=9.5, color=GOLD, bold=True))
    f.append(line(150, 121, 110, 121, color=FIELD, sw=2))
    f.append(text(95, 125, "біт-лінія", size=9.5, color=FIELD, bold=True, anchor="end"))
    # конденсатор під транзистором
    f.append(line(170, 133, 170, 165, color=INK, sw=2))
    f.append(line(150, 165, 190, 165, color=NEG, sw=3))
    f.append(line(150, 174, 190, 174, color=NEG, sw=3))
    f.append(line(170, 174, 170, 196, color=INK, sw=2))
    # земля
    f.append(line(156, 196, 184, 196, color=INK, sw=2.4))
    f.append(line(161, 201, 179, 201, color=INK, sw=2))
    f.append(line(166, 206, 174, 206, color=INK, sw=2))
    f.append(text(232, 168, "конденсатор:", size=11, color=NEG, bold=True, anchor="start"))
    f.append(text(232, 184, "тут «живе» біт (заряд = 1)", size=10, color=MUTED, italic=True, anchor="start"))

    # права картка: щільність
    f.append(fitbox(440, 70, 350, 130, "", fill="#eef7ee", stroke=FIELD, sw=1.6))
    f.append(text(615, 92, "Крихітна — звідси щільність", size=12, color=FIELD, bold=True))
    for i, ln in enumerate(["лише 2 елементи проти 6 транзисторів SRAM",
                            "→ у рази більше біт на тому самому кристалі",
                            "→ дешевша на біт; тому DRAM — велика пам'ять ПК,",
                            "а SRAM лишають для малого й швидкого"]):
        f.append(text(456, 116 + i * 19, ln, size=10, color=INK, anchor="start"))

    # графік стікання заряду
    f.append(text(105, 240, "Підступ: заряд СТІКАЄ", size=12, color=POS, bold=True, anchor="start"))
    gx, gy, gw, gh = 120, 260, 290, 110
    f.append(line(gx, gy, gx, gy + gh, color=MUTED, sw=1.4))
    f.append(line(gx, gy + gh, gx + gw, gy + gh, color=MUTED, sw=1.4))
    f.append(text(gx - 6, gy + 6, "заряд", size=9, color=MUTED, anchor="end"))
    f.append(text(gx + gw + 6, gy + gh, "час", size=9, color=MUTED, anchor="start"))
    pts = [(gx + gw * t, gy + 10 + (gh - 24) * (1 - math.exp(-3.0 * t))) for t in
           [i / 40 for i in range(41)]]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join("%.1f,%.1f" % p for p in pts), NEG))
    thr = gy + gh - 26
    f.append(line(gx, thr, gx + gw, thr, color=POS, sw=1.4, dash="5 3"))
    f.append(text(gx + 6, gy + 6, "повний (1)", size=9, color=NEG, anchor="start"))
    f.append(text(gx + gw, thr - 4, "поріг: нижче — «1» втрачено", size=9, color=POS, anchor="end"))
    f.append(text(gx + gw / 2, gy + gh + 18,
                  "мілісекунди — і заряд протік крізь неідеальний ізолятор", size=9,
                  color=MUTED, italic=True))

    # розв'язок: refresh
    f.append(fitbox(440, 250, 350, 120, "", fill=GOLDF, stroke=GOLD, sw=1.6))
    f.append(text(615, 272, "Розв'язок: ОСВІЖЕННЯ", size=12, color=GOLD, bold=True))
    for i, ln in enumerate(["кожні кілька мс комірку перечитують",
                            "і записують назад — поки біт ще цілий.",
                            "Звідси «динамічна»: стан не стоїть сам.",
                            "Читання теж РУЙНІВНЕ (ключ відкрив —",
                            "заряд витік), тож одразу пишуть назад."]):
        f.append(text(456, 294 + i * 16, ln, size=9.6, color=INK, anchor="start"))

    f.extend(cap(W, "Тут лише фізика комірки; коли освіжати й з якими таймінгами — це вже зовнішній контролер пам'яті.",
                 y0=H - 16))
    render(os.path.join(IMG, "dram-1t1c.svg"), W, H, *f)


# ── 4. floating gate: транзистор, що пам'ятає ────────────────────────────────
def fig_floating_gate():
    W, H = 820, 420
    f = [text(W / 2, 30, "Плавучий затвор: транзистор, що пам'ятає заряд", size=17, bold=True)]

    # стек шарів (вид збоку)
    cx0, w = 150, 240
    # підкладка
    f.append(rect(cx0, 250, w, 36, fill="#eef0f4", stroke=MUTED, sw=1.4))
    f.append(text(cx0 + w / 2, 272, "кремнієва підкладка (канал)", size=9.5, color=MUTED))
    # витік/стік
    f.append(rect(cx0, 230, 52, 20, fill="#dfe6f5", stroke=NEG, sw=1.3))
    f.append(text(cx0 + 26, 244, "витік", size=9, color=NEG, bold=True))
    f.append(rect(cx0 + w - 52, 230, 52, 20, fill="#dfe6f5", stroke=NEG, sw=1.3))
    f.append(text(cx0 + w - 26, 244, "стік", size=9, color=NEG, bold=True))
    # тунельний оксид
    f.append(rect(cx0 + 30, 218, w - 60, 12, fill="#f3f5fd", stroke=MUTED, sw=1))
    f.append(text(cx0 + w + 8, 228, "тонкий «тунельний» оксид", size=9, color=MUTED, anchor="start"))
    # плавучий затвор із зарядом
    f.append(rect(cx0 + 30, 188, w - 60, 28, fill="#fff2cc", stroke=GOLD, sw=2))
    f.append(text(cx0 + w / 2, 206, "ПЛАВУЧИЙ затвор (заряд замкнено)", size=9.5, color=GOLD, bold=True))
    for i in range(7):
        f.append(text(cx0 + 52 + i * 24, 184, "−", size=13, color=POS, bold=True))
    # верхній ізолятор
    f.append(rect(cx0 + 30, 176, w - 60, 12, fill="#f3f5fd", stroke=MUTED, sw=1))
    f.append(text(cx0 + w + 8, 186, "ізолятор (з усіх боків!)", size=9, color=MUTED, anchor="start"))
    # керівний затвор
    f.append(rect(cx0 + 30, 148, w - 60, 28, fill="#dfe6f5", stroke=INK, sw=1.8))
    f.append(text(cx0 + w / 2, 166, "керівний затвор", size=10, color=INK, bold=True))
    f.append(line(cx0 + w / 2, 132, cx0 + w / 2, 148, color=INK, sw=2))
    f.append(text(cx0 + w / 2, 126, "вивід", size=9, color=INK))

    # права картка: як заряд кодує біт
    f.append(fitbox(450, 120, 340, 170, "", fill=GOLDF, stroke=GOLD, sw=1.6))
    f.append(text(620, 144, "Як заряд кодує біт", size=12, color=GOLD, bold=True))
    rows = [("Заряд на плавучому затворі зсуває", INK, False),
            ("поріг, за яким транзистор вмикається:", INK, False),
            ("є замкнений заряд → високий поріг → «0»", POS, True),
            ("нема заряду → низький поріг → «1»", NEG, True),
            ("Читаємо просто: пробуємо ввімкнути —", INK, False),
            ("відкрився чи ні і каже, який біт усередині.", INK, False)]
    for i, (ln, col, b) in enumerate(rows):
        f.append(text(466, 168 + i * 19, ln, size=9.8, color=col, bold=b, anchor="start"))

    body, _, _ = textbox(W / 2, 330,
                         "Ось де НЕЛЕТКІСТЬ: затвор оточений ізолятором, заряд нікуди не дінеться —\n"
                         "тримається роками без живлення. «Роками», а не «вічно»: заряд — лічені тисячі\n"
                         "електронів, із часом чи від нагріву помалу губиться (скінченний строк зберігання).",
                         size=10.5, fill="#f4f7f4", stroke=GOLD, color=INK)
    f.append(body)
    render(os.path.join(IMG, "floating-gate.svg"), W, H, *f)


# ── 5. program/erase: заряд крізь ізолятор ───────────────────────────────────
def fig_fg_program_erase():
    W, H = 820, 400
    f = [text(W / 2, 30, "Запис і стирання: заряд мусить пройти крізь ізолятор", size=16.5, bold=True)]

    # ── запис (ліворуч) ──
    f.append(rect(50, 56, 350, 150, fill="#eef7ee", stroke=FIELD, sw=1.8))
    f.append(text(225, 80, "ЗАПИС: загнати заряд усередину", size=11.5, color=FIELD, bold=True))
    f.append(rect(90, 96, 270, 22, fill="#dfe6f5", stroke=INK, sw=1.4))
    f.append(text(225, 112, "керівний затвор (висока напруга)", size=9, color=INK))
    f.append(rect(90, 124, 270, 14, fill="#f3f5fd", stroke=MUTED, sw=1))
    f.append(rect(90, 142, 270, 22, fill="#fff2cc", stroke=GOLD, sw=1.8))
    f.append(text(225, 158, "плавучий затвор", size=9, color=GOLD, bold=True))
    for i in range(5):
        f.append(arrow(130 + i * 50, 138, 130 + i * 50, 124, color=POS, sw=1.8))
    f.append(text(225, 188, "сильне поле проштовхує електрони КРІЗЬ оксид усередину",
                  size=9.2, color=MUTED, italic=True))

    # ── стирання (праворуч) ──
    f.append(rect(420, 56, 350, 150, fill="#fdf6f6", stroke=POS, sw=1.8))
    f.append(text(595, 80, "СТИРАННЯ: витягти заряд назад", size=11.5, color=POS, bold=True))
    f.append(rect(460, 96, 270, 22, fill="#fff2cc", stroke=GOLD, sw=1.8))
    f.append(text(595, 112, "плавучий затвор", size=9, color=GOLD, bold=True))
    f.append(rect(460, 124, 270, 14, fill="#f3f5fd", stroke=MUTED, sw=1))
    f.append(rect(460, 142, 270, 22, fill="#dfe6f5", stroke=INK, sw=1.4))
    f.append(text(595, 158, "підкладка (висока напруга)", size=9, color=INK))
    for i in range(5):
        f.append(arrow(500 + i * 50, 124, 500 + i * 50, 110, color=NEG, sw=1.8))
    f.append(text(595, 188, "поле зворотного знаку витягує електрони геть",
                  size=9.2, color=MUTED, italic=True))

    # ── три наслідки ──
    f.append(rect(50, 224, 720, 132, fill=GOLDF, stroke=GOLD, sw=1.7))
    f.append(text(410, 248, "Звідси — увесь характер запису Flash:", size=12, color=INK, bold=True))
    items = [("ПОВІЛЬНО:", GOLD,
              "проштовхати заряд крізь ізолятор — мікро- й мілісекунди (проти тактів RAM), і робиться це блоками."),
             ("ЗНОС:", POS,
              "кожен прохід крізь оксид потроху його псує; після ~10⁴–10⁵ циклів комірка не тримає заряд."),
             ("ЧИТАННЯ:", FIELD,
              "навпаки, легке й швидке — заряду не чіпає, лише дивиться на поріг; тому код виконують прямо з Flash.")]
    y = 274
    for tag, col, txt in items:
        f.append(text(70, y, tag, size=10.5, color=col, bold=True, anchor="start"))
        f.append(text(168, y, txt, size=9.6, color=INK, anchor="start"))
        y += 26

    f.extend(cap(W, "Сам квантовий механізм проходу електрона крізь ізолятор (тунелювання) і чому він руйнує оксид — окрема, тонша історія.",
                 y0=H - 16))
    render(os.path.join(IMG, "fg-program-erase.svg"), W, H, *f)


# ── 6. tradeoffs: три комірки поряд (таблиця) ────────────────────────────────
def fig_tradeoffs():
    W, H = 840, 360
    f = [text(W / 2, 30, "Три комірки поряд: будова комірки вирішує все", size=17, bold=True)]

    cols = [("комірка", 70), ("тримає біт", 210), ("летка?", 360),
            ("розмір", 470), ("запис", 575), ("де вживають", 700)]
    f.append(rect(50, 52, 740, 26, fill="#eef0f4", stroke=INK, sw=1.2))
    for name, x in cols:
        f.append(text(x, 70, name, size=10.5, color=INK, bold=True, anchor="start"))

    rows = [
        ("SRAM", NEG, "#f3f5fd",
         ["петля 2 інверторів", "(тригер)"], ["летка"], ["велика", "(6 транз.)"],
         ["швидкий,", "необмежений"], ["кеші, мала", "RAM МК"]),
        ("DRAM", FIELD, "#fafafa",
         ["заряд на", "конденсаторі"], ["летка", "(+освіження)"], ["крихітна", "(1Т+1С)"],
         ["швидкий,", "читання руйнівне"], ["велика", "пам'ять ПК"]),
        ("Flash", GOLD, "#fafafa",
         ["заряд у плавучому", "затворі"], ["НЕлетка"], ["мала", "(1 транз.)"],
         ["повільний,", "блоками, знос"], ["програма МК,", "SSD, флешки"]),
    ]
    y = 82
    for name, col, fill, c2, c3, c4, c5, c6 in rows:
        f.append(rect(50, y, 740, 70, fill=fill, stroke=col, sw=1.6))
        f.append(text(70, y + 30, name, size=14, color=col, bold=True, anchor="start"))
        for cells, x in ((c2, 210), (c3, 360), (c4, 470), (c5, 575), (c6, 700)):
            for i, ln in enumerate(cells):
                f.append(text(x, y + 28 + i * 16, ln, size=9.6, color=INK, anchor="start"))
        y += 76

    f.extend(cap(W, ["Один біт — три зовсім різні фізики: дві леткі (струм / заряд-що-стікає) і одна нелетка (замкнений заряд).",
                     "Біт зрештою — завжди якийсь фізичний стан, а «0» і «1» — лише імена, що йому дають."],
                 y0=H - 30))
    render(os.path.join(IMG, "tradeoffs.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
#  Вставка hist-frohman-eprom — 4 фігури
# ════════════════════════════════════════════════════════════════════════════

# ── h1. FAMOS: плавучий затвор і лавинна інжекція ────────────────────────────
def fig_famos():
    W, H = 820, 380
    f = [text(W / 2, 30, "Комірка FAMOS: плавучий затвор і лавинна інжекція", size=16.5, bold=True)]

    def stack(x0, charged, title, col, fill):
        w = 250
        ff = [rect(x0, 96, w + 70, 200, fill=fill, stroke=col, sw=1.7)]
        bx = x0 + 35
        ff.append(text(x0 + (w + 70) / 2, 120, title, size=12, color=col, bold=True))
        # підкладка
        ff.append(rect(bx, 250, w, 30, fill="#eef0f4", stroke=MUTED, sw=1.3))
        ff.append(text(bx + w / 2, 270, "підкладка (канал)", size=9, color=MUTED))
        ff.append(rect(bx, 232, w, 10, fill="#f3f5fd", stroke=MUTED, sw=1))      # товстий оксид
        # плавучий затвор
        ff.append(rect(bx, 204, w, 26, fill="#fff2cc", stroke=GOLD, sw=1.8))
        ff.append(text(bx + w / 2, 221, "плавучий затвор", size=9, color=GOLD, bold=True))
        if charged:
            for i in range(6):
                ff.append(text(bx + 30 + i * 36, 200, "−", size=12, color=POS, bold=True))
            ff.append(text(bx + w / 2, 192, "заряд є → поріг високий → «0»", size=9, color=POS, bold=True))
            # лавина електронів знизу вгору
            for i in range(5):
                ff.append(arrow(bx + 40 + i * 44, 250, bx + 40 + i * 44, 228, color=POS, sw=1.7))
            ff.append(text(bx + w / 2, 296 - 6, "сильне поле: «гарячі» електрони лавиною крізь оксид",
                           size=9, color=MUTED, italic=True))
        else:
            ff.append(text(bx + w / 2, 192, "заряду нема → поріг низький → «1»", size=9, color=NEG, bold=True))
            ff.append(text(bx + w / 2, 290, "транзистор вмикається — читаємо «1»",
                           size=9, color=MUTED, italic=True))
        ff.append(rect(bx, 158, w, 10, fill="#f3f5fd", stroke=MUTED, sw=1))      # верхній ізолятор
        ff.append(rect(bx, 130, w, 28, fill="#dfe6f5", stroke=INK, sw=1.6))      # керівний затвор
        ff.append(text(bx + w / 2, 148, "керівний затвор", size=9, color=INK, bold=True))
        return ff

    f.extend(stack(40, True, "ЗАПИС (лавинна інжекція)", POS, "#fdf6f6"))
    f.extend(stack(420, False, "Стерта комірка", NEG, "#f3f5fd"))

    f.extend(cap(W, "FAMOS = floating-gate avalanche-injection MOS. Читання заряду не чіпає, тому біт тримається роками.",
                 y0=H - 16))
    render(os.path.join(IMG, "famos.svg"), W, H, *f)


# ── h2. cycle: запис струмом, стирання ультрафіолетом ────────────────────────
def fig_cycle():
    W, H = 820, 320
    f = [text(W / 2, 30, "Цикл життя біта EPROM: запис струмом, стирання ультрафіолетом", size=15.5, bold=True)]

    def chip(cx, bits, label, col):
        ff = [rect(cx - 70, 70, 140, 90, fill="#1b1b1b", stroke=INK, sw=1.5, rx=8)]
        # «віконце»
        ff.append(rect(cx - 46, 86, 92, 40, fill="#dfe6f5", stroke="#9fb6e8", sw=1.4, rx=3))
        bx = cx - 38
        for i, b in enumerate(bits):
            c = POS if b == "0" else NEG
            ff.append(text(bx + (i % 4) * 22, 102 + (i // 4) * 18, b, size=12, color=c, bold=True))
        ff.append(text(cx, 150, "EPROM", size=9, color="#cccccc"))
        ff.append(text(cx, 178, label, size=10.5, color=col, bold=True))
        return ff

    f.extend(chip(140, "11111111", "чистий: усі біти = 1", MUTED))
    f.extend(chip(410, "10110010", "записано: 0 і 1 (програма)", INK))
    f.extend(chip(680, "11111111", "стерто: знову чистий", FIELD))

    f.append(arrow(216, 115, 336, 115, color=POS, sw=2.2))
    f.append(text(276, 104, "ЗАПИС", size=10, color=POS, bold=True))
    f.append(text(276, 130, "висока напруга", size=9, color=MUTED, italic=True))
    f.append(arrow(486, 115, 606, 115, color=GOLD, sw=2.2))
    f.append(text(546, 104, "СТИРАННЯ", size=10, color=GOLD, bold=True))
    f.append(text(546, 130, "УФ крізь віконце ~20 хв", size=9, color=MUTED, italic=True))

    body, _, _ = textbox(W / 2, 232,
                         "Вічна АСИМЕТРІЯ: записати можна окремі біти й електрикою,\n"
                         "а стерти — лише ВЕСЬ чип і оптично (спалах ультрафіолету). Цей слід дожив до Flash.",
                         size=10.5, fill=GOLDF, stroke=GOLD, color=INK)
    f.append(body)
    f.extend(cap(W, "Програма тримається роками без живлення (нелетка); кварц — бо звичайне скло ультрафіолет не пропускає.",
                 y0=H - 14))
    render(os.path.join(IMG, "cycle.svg"), W, H, *f)


# ── h3. flow: маскова ROM проти EPROM ────────────────────────────────────────
def fig_flow():
    W, H = 820, 320
    f = [text(W / 2, 30, "Маскова ROM проти EPROM: один постріл проти ітерації", size=16, bold=True)]

    # ліва колонка — mask ROM
    f.append(rect(40, 56, 360, 230, fill="#fdf6f6", stroke=POS, sw=1.7))
    f.append(text(220, 80, "Маскова ROM: один постріл", size=12, color=POS, bold=True))
    steps = ["написав код", "замовив фотомаски", "чекаєш тижні, платиш дорого",
             "отримав чипи з «вкарбованим» кодом", "знайшов баг → усе на смітник"]
    for i, s in enumerate(steps):
        col = POS if i == len(steps) - 1 else INK
        f.append(rect(64, 96 + i * 36, 312, 28, fill=BG, stroke=col, sw=1.3))
        f.append(text(220, 114 + i * 36, s, size=9.8, color=col, bold=(i == len(steps) - 1)))
        if i < len(steps) - 1:
            f.append(arrow(220, 124 + i * 36, 220, 132 + i * 36, color=MUTED, sw=1.5))

    # права колонка — EPROM
    f.append(rect(420, 56, 360, 230, fill="#eef7ee", stroke=FIELD, sw=1.7))
    f.append(text(600, 80, "EPROM: дешева петля на столі", size=12, color=FIELD, bold=True))
    loop = ["прошив сам", "спробував у схемі", "стер ультрафіолетом", "прошив той самий чип знову"]
    cy = 110
    for i, s in enumerate(loop):
        f.append(rect(470, cy + i * 40, 260, 28, fill=BG, stroke=FIELD, sw=1.3))
        f.append(text(600, cy + 18 + i * 40, s, size=9.8, color=INK))
    # стрілка-петля назад
    f.append(arrow(730, cy + 14, 752, cy + 14, color=FIELD, sw=1.6))
    f.append(line(752, cy + 14, 752, cy + 3 * 40 + 14, color=FIELD, sw=1.6))
    f.append(arrow(752, cy + 3 * 40 + 14, 732, cy + 3 * 40 + 14, color=FIELD, sw=1.6))
    for i in range(3):
        f.append(arrow(600, cy + 28 + i * 40, 600, cy + 36 + i * 40, color=MUTED, sw=1.5))

    f.extend(cap(W, "«Дорого й повільно помилятися» змінилося на «дешево й швидко» — а отже, швидше вчитися.",
                 y0=H - 16))
    render(os.path.join(IMG, "flow.svg"), W, H, *f)


# ── h4. lineage: родовід плавучого затвора ───────────────────────────────────
def fig_lineage():
    W, H = 860, 300
    f = [text(W / 2, 30, "Родовід плавучого затвора: ідея, перший чип, спадкоємці", size=16, bold=True)]

    nodes = [
        ("1967", "Канг і Це (Bell Labs):\nідея плавучого затвора\nна папері, без чипа", NEG, "#f3f5fd"),
        ("1971", "Фроман (Intel):\nкомірка FAMOS і чип 1702 —\nперша EPROM, стирання УФ", GOLD, GOLDF),
        ("кінець 1970-х", "EEPROM:\nстирання ЕЛЕКТРИКОЮ,\nвіконце зникає", FIELD, "#eef7ee"),
        ("1980-ті й далі", "Flash:\nдешевше й щільніше,\nстирання блоками", INK, "#fafafa"),
    ]
    x = 30
    bw = 196
    for tag, body, col, fill in nodes:
        f.append(rect(x, 72, bw, 150, fill=fill, stroke=col, sw=1.7))
        f.append(text(x + bw / 2, 96, tag, size=12, color=col, bold=True))
        f.append(line(x + 18, 106, x + bw - 18, 106, color=col, sw=1))
        for i, ln in enumerate(body.split("\n")):
            f.append(text(x + bw / 2, 128 + i * 18, ln, size=9.6, color=INK))
        if x > 30:
            f.append(arrow(x - 16, 147, x - 2, 147, color=MUTED, sw=2))
        x += bw + 14

    f.extend(cap(W, "Кожен крок додав своє; жоден не зробив усього сам. Підручник любить одне ім'я там, де працював цілий ланцюг.",
                 y0=H - 16))
    render(os.path.join(IMG, "lineage.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
#  Вставка math-tunneling — 3 фігури
# ════════════════════════════════════════════════════════════════════════════

# ── m1. barrier: бар'єр оксиду й тунелювання ─────────────────────────────────
def fig_barrier():
    W, H = 820, 360
    f = [text(W / 2, 30, "Енергетичний бар'єр оксиду й тунелювання крізь нього", size=16, bold=True)]

    def panel(x0, tilted, title, col):
        ff = [rect(x0, 60, 360, 240, fill="#fcfcfd", stroke="#e6e6ea", sw=1.4)]
        ff.append(text(x0 + 180, 84, title, size=12, color=col, bold=True))
        bx, by, bw, bh = x0 + 60, 110, 240, 150
        # осі
        ff.append(line(bx, by, bx, by + bh, color=MUTED, sw=1.3))
        ff.append(line(bx, by + bh, bx + bw + 16, by + bh, color=MUTED, sw=1.3))
        ff.append(text(bx - 6, by + 4, "енергія", size=9, color=MUTED, anchor="end"))
        # рівень електрона
        elv = by + bh - 46
        ff.append(line(bx, elv, bx + bw + 10, elv, color=NEG, sw=1.6, dash="5 3"))
        ff.append(text(bx + bw + 12, elv, "рівень e⁻", size=9, color=NEG, anchor="start"))
        # бар'єр
        top = by + 20
        if not tilted:
            ff.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#eef0f4" stroke="%s" stroke-width="1.8"/>'
                      % (bx + 90, top, 60, (by + bh) - top, GOLD))
            ff.append(text(bx + 120, top - 6, "товста стіна", size=9, color=GOLD, bold=True))
            ff.append(text(bx + 120, by + bh + 18, "поле відсутнє: e⁻ відскакує", size=9, color=MUTED, italic=True))
        else:
            # трикутний бар'єр (нахилений полем)
            ff.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="#eef0f4" stroke="%s" stroke-width="1.8"/>'
                      % (bx + 90, by + bh, bx + 90, top, bx + 150, by + bh, GOLD))
            # тонкий кінчик на рівні електрона
            ff.append(circle(bx + 112, elv, 4, fill=POS, stroke=POS, sw=1))
            ff.append(arrow(bx + 100, elv, bx + 140, elv, color=POS, sw=1.8))
            ff.append(text(bx + 120, top - 6, "тонкий кінчик", size=9, color=POS, bold=True))
            ff.append(text(bx + 130, by + bh + 18, "сильне поле нахиляє стіну → e⁻ тунелює", size=9, color=MUTED, italic=True))
        return ff

    f.extend(panel(30, False, "оксид без поля", MUTED))
    f.extend(panel(430, True, "оксид під сильним полем", POS))

    f.extend(cap(W, "Уся хитрість запису й стирання — зробити кінчик бар'єра достатньо тонким, щоб струм електронів потік.",
                 y0=H - 16))
    render(os.path.join(IMG, "barrier.svg"), W, H, *f)


# ── m2. program/erase: електрони крізь той самий оксид ───────────────────────
def fig_m_program_erase():
    W, H = 820, 360
    f = [text(W / 2, 30, "Запис і стирання: електрони крізь той самий оксид", size=16, bold=True)]

    def cell(x0, write, title, col, fill):
        ff = [rect(x0, 60, 360, 200, fill=fill, stroke=col, sw=1.7)]
        ff.append(text(x0 + 180, 84, title, size=12, color=col, bold=True))
        bx = x0 + 50
        w = 260
        ff.append(rect(bx, 220, w, 26, fill="#dfe6f5", stroke=INK, sw=1.4))   # канал/підкладка
        ff.append(text(bx + w / 2, 238, "канал / підкладка", size=9, color=INK))
        ff.append(rect(bx, 206, w, 12, fill="#f3f5fd", stroke=MUTED, sw=1))   # тунельний оксид
        ff.append(text(bx + w + 6, 215, "тунельний оксид", size=9, color=MUTED, anchor="start"))
        ff.append(rect(bx, 176, w, 28, fill="#fff2cc", stroke=GOLD, sw=1.8))  # плавучий затвор
        ff.append(text(bx + w / 2, 194, "плавучий затвор", size=9, color=GOLD, bold=True))
        if write:
            for i in range(5):
                ff.append(arrow(bx + 40 + i * 50, 218, bx + 40 + i * 50, 204, color=POS, sw=1.8))
            ff.append(text(bx + w / 2, 130, "поле заганяє електрони В пастку", size=9.5, color=POS, italic=True))
            ff.append(text(bx + w / 2, 150, "заряд замкнено → поріг високий («0»)", size=9, color=INK))
        else:
            for i in range(5):
                ff.append(arrow(bx + 40 + i * 50, 204, bx + 40 + i * 50, 218, color=NEG, sw=1.8))
            ff.append(text(bx + w / 2, 130, "поле витягує електрони З пастки", size=9.5, color=NEG, italic=True))
            ff.append(text(bx + w / 2, 150, "пастка порожня → поріг низький («1»)", size=9, color=INK))
        return ff

    f.extend(cell(30, True, "ЗАПИС («0»)", POS, "#fdf6f6"))
    f.extend(cell(430, False, "СТИРАННЯ («1»)", NEG, "#f3f5fd"))

    f.extend(cap(W, ["Читання заряду не торкається — лише дивиться, відкривається транзистор чи ні; тому швидке й безмежне.",
                     "А запис і стирання щоразу ПРОТЯГУЮТЬ заряд крізь оксид — і цей прохід не безкоштовний."],
                 y0=H - 30))
    render(os.path.join(IMG, "m-program-erase.svg"), W, H, *f)


# ── m3. wear: пастки в оксиді й звуження вікна ───────────────────────────────
def fig_wear():
    W, H = 820, 380
    f = [text(W / 2, 30, "Знос: пастки в оксиді й звуження вікна читання", size=16, bold=True)]

    # ліворуч: свіжий vs зношений оксид
    def oxide(x0, worn, label, col):
        ff = [rect(x0, 70, 170, 120, fill="#fcfcfd", stroke=col, sw=1.6)]
        ff.append(text(x0 + 85, 90, label, size=10.5, color=col, bold=True))
        import random
        random.seed(1 if not worn else 7)
        n = 4 if not worn else 26
        for _ in range(n):
            rx = x0 + 20 + random.random() * 130
            ry = 104 + random.random() * 74
            if worn and random.random() < 0.4:
                ff.append(text(rx, ry, "−", size=10, color=POS, bold=True))   # застряглий заряд
            else:
                ff.append(circle(rx, ry, 2.4, fill="none", stroke=MUTED, sw=1.1))  # пастка-дефект
        return ff

    f.extend(oxide(40, False, "свіжий оксид", FIELD))
    f.extend(oxide(225, True, "зношений: дефекти + заряд", POS))

    # праворуч: графік звуження вікна
    gx, gy, gw, gh = 470, 80, 300, 200
    f.append(rect(gx - 20, 70, 330, 220, fill="#fcfcfd", stroke="#e6e6ea", sw=1.4))
    f.append(text(gx + gw / 2 - 20, 90, "вікно читання звужується з циклами", size=10.5, color=INK, bold=True))
    f.append(line(gx, gy + 20, gx, gy + gh, color=MUTED, sw=1.3))
    f.append(line(gx, gy + gh, gx + gw, gy + gh, color=MUTED, sw=1.3))
    f.append(text(gx + gw, gy + gh + 14, "цикли", size=9, color=MUTED, anchor="end"))
    f.append(text(gx - 6, gy + 26, "поріг", size=9, color=MUTED, anchor="end"))
    # поріг «0» (заряд є) повзе вниз
    p0 = [(gx + gw * t, gy + 36 + 60 * t) for t in [i / 30 for i in range(31)]]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join("%.1f,%.1f" % p for p in p0), POS))
    f.append(text(gx + gw - 4, gy + 34, "«0» (заряд є)", size=9, color=POS, anchor="end"))
    # поріг «1» (заряду нема) повзе вгору
    p1 = [(gx + gw * t, gy + gh - 36 - 56 * t) for t in [i / 30 for i in range(31)]]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join("%.1f,%.1f" % p for p in p1), NEG))
    f.append(text(gx + gw - 4, gy + gh - 30, "«1» (заряду нема)", size=9, color=NEG, anchor="end"))
    # стрілка-вікно
    f.append(line(gx + 40, gy + 48, gx + 40, gy + gh - 48, color=FIELD, sw=1.4, dash="4 3"))
    f.append(text(gx + 70, (gy + gh) / 2 + 10, "вікно", size=9, color=FIELD, bold=True, anchor="start"))

    f.extend(cap(W, "Межа ~10⁴–10⁵ циклів — точка, де пороги «0» і «1» зближуються так, що датчик їх плутає. Читання зносу не дає.",
                 y0=H - 16))
    render(os.path.join(IMG, "wear.svg"), W, H, *f)


if __name__ == "__main__":
    # стаття
    fig_overview(); fig_sram_6t(); fig_dram_1t1c()
    fig_floating_gate(); fig_fg_program_erase(); fig_tradeoffs()
    # hist-
    fig_famos(); fig_cycle(); fig_flow(); fig_lineage()
    # math-
    fig_barrier(); fig_m_program_erase(); fig_wear()
    print("OK: 13 figures ->", IMG)
