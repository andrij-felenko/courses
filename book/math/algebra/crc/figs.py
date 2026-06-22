# -*- coding: utf-8 -*-
"""Фігури для статті math/algebra/crc «Циклічна надмірність».
svgkit імпортуємо зі scripts/, не переписуємо (§5 AUTHORING). Вивід — у ./img/.
Запуск:  python figs.py   →  python ../../../../scripts/svgcheck.py img
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

MONO = "'Consolas', 'DejaVu Sans Mono', 'Courier New', monospace"
GOLD = "#caa24a"          # «межовий» акцент (нейтральний третій колір)
POSF = "#fdecea"          # світла заливка під POS
NEGF = "#eaf0fd"          # світла заливка під NEG
FLDF = "#eef7f0"          # світла заливка під FIELD


def mono(x, y, s, size=16, color=INK, anchor="middle", bold=True):
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%g" fill="%s" '
            'text-anchor="%s"%s>%s</text>' % (x, y, MONO, size, color, anchor, w, esc(s)))


def cell(cx, cy, s, sz=56, fill=FILL, stroke=LINE, color=INK, mono_font=True, fsize=17):
    """Квадратна клітинка таблиці з символом по центру."""
    out = rect(cx - sz / 2, cy - sz / 2, sz, sz, fill=fill, stroke=stroke, sw=1.5, rx=6)
    if mono_font:
        out += mono(cx, cy + fsize * 0.34, s, size=fsize, color=color)
    else:
        out += text(cx, cy + fsize * 0.34, s, size=fsize, color=color, bold=True)
    return out


# ── 1. Таблиці дій у GF(2): + (=XOR), · (=AND), − (= те саме, що +) ───────────
def fig_gf2_tables():
    W, H = 940, 540
    P = []
    P.append(text(W / 2, 32, "Поле GF(2): уся арифметика — на двох числах {0, 1}", size=19, bold=True))
    P.append(text(W / 2, 53, "додавання — це XOR, множення — це AND; віднімання окремо не існує — воно збігається з додаванням",
                  size=12, color=MUTED, italic=True))

    sz = 56

    def table(ox, oy, op, vals, hot, hotcolor, hotfill):
        """ox,oy — лівий верхній кут клітинки-кутка; vals[i][j] — результат; hot — список (i,j) виділених."""
        frag = []
        # кутова клітинка зі знаком дії
        frag.append(cell(ox + sz / 2, oy + sz / 2, op, sz, fill="#faf3e0", stroke=GOLD, fsize=18))
        # шапка зверху (b) і ліворуч (a): значення 0,1
        for j, b in enumerate((0, 1)):
            cx = ox + sz / 2 + (j + 1) * sz
            frag.append(cell(cx, oy + sz / 2, str(b), sz, fill=NEGF, stroke=NEG, color=NEG, fsize=16))
        for i, a in enumerate((0, 1)):
            cy = oy + sz / 2 + (i + 1) * sz
            frag.append(cell(ox + sz / 2, cy, str(a), sz, fill=NEGF, stroke=NEG, color=NEG, fsize=16))
        # тіло
        for i in range(2):
            for j in range(2):
                cx = ox + sz / 2 + (j + 1) * sz
                cy = oy + sz / 2 + (i + 1) * sz
                v = vals[i][j]
                if (i, j) in hot:
                    frag.append(cell(cx, cy, str(v), sz, fill=hotfill, stroke=hotcolor, color=hotcolor))
                else:
                    frag.append(cell(cx, cy, str(v), sz, fill=BG, stroke="#e4e4e4"))
        return "".join(frag)

    oy = 54
    # Додавання = XOR
    P.append(text(166, 98, "Додавання   a + b   (= XOR)", size=14, color=POS, bold=True))
    P.append(table(54, oy, "+", [[0, 1], [1, 0]], [(0, 1), (1, 0)], POS, POSF))
    # Множення = AND
    P.append(text(466, 98, "Множення   a · b   (= AND)", size=14, color=FIELD, bold=True))
    P.append(table(354, oy, "·", [[0, 0], [0, 1]], [(1, 1)], FIELD, FLDF))
    # Віднімання = те саме, що додавання
    P.append(text(766, 98, "Віднімання   a − b   (те саме!)", size=14, color=POS, bold=True))
    P.append(table(654, oy, "−", [[0, 1], [1, 0]], [(0, 1), (1, 0)], POS, POSF))

    P.append(text(166, 250, "↑ та сама таблиця, що й «−» праворуч", size=12, color=GOLD, bold=True))
    P.append(text(766, 250, "↑ поклітинно збігається з «+» ліворуч", size=12, color=GOLD, bold=True))

    # пояснення внизу
    P.append(rect(60, 300, 820, 100, fill=BG, stroke=INK, sw=1.6, rx=12))
    P.append(text(470, 328, "Чому віднімання не потрібне окремо", size=15, bold=True))
    P.append(text(90, 356, "У звичайних числах a − b = a + (−b), і знак мінус указує «протилежне» число. У GF(2) протилежного шукати",
                  size=12, anchor="start"))
    P.append(text(90, 376, "не доводиться: з таблиці «+» видно, що 1 + 1 = 0, тобто кожне число САМЕ СОБІ протилежне (−1 = 1, −0 = 0).",
                  size=12, anchor="start"))

    P.append(rect(60, 432, 820, 64, fill=POSF, stroke=POS, sw=1.6, rx=12))
    P.append(mono(470, 458, "a + a = 0      ⇒      −a = a      ⇒      a − b  =  a + b  =  a ⊕ b", size=17, color=POS))
    P.append(text(470, 482, "Один знак ⊕ виконує і плюс, і мінус — звідси вся простота арифметики CRC.", size=12, bold=True))

    render(os.path.join(OUT, "gf2-tables.svg"), W, H, *P)


# ── 2. Біти як коефіцієнти многочлена (байт 0xD3) ────────────────────────────
def fig_bits_as_poly():
    W, H = 940, 470
    P = []
    P.append(text(W / 2, 32, "Біти — це коефіцієнти многочлена над GF(2)", size=19, bold=True))
    P.append(text(W / 2, 53, "позиція біта = степінь x; одиниця означає «доданок є», нуль — «доданка немає»",
                  size=12, color=MUTED, italic=True))

    bits = [1, 1, 0, 1, 0, 0, 1, 1]                       # 0xD3
    powers = ["x⁷", "x⁶", "x⁵", "x⁴", "x³", "x²", "x", "1"]
    degs = [7, 6, 5, 4, 3, 2, 1, 0]
    cw, gap = 70, 8
    x0 = 158
    P.append(text(144, 142, "байт:", size=13, color=NEG, anchor="end", bold=True))
    for k, b in enumerate(bits):
        cx = x0 + k * (cw + gap) + cw / 2
        P.append(text(cx, 96, powers[k], size=14, color=MUTED, bold=True))
        if b:
            P.append(rect(cx - cw / 2, 110, cw, 50, fill=POSF, stroke=POS, sw=1.8, rx=7))
            P.append(mono(cx, 142, "1", size=22, color=POS))
        else:
            P.append(rect(cx - cw / 2, 110, cw, 50, fill=BG, stroke="#e4e4e4", sw=1.8, rx=7))
            P.append(mono(cx, 142, "0", size=22, color=MUTED))
        P.append(text(cx, 178, "степінь %d" % degs[k], size=10, color=MUTED))

    P.append(mono(470, 206, "= 0b1101 0011 = 0xD3", size=13, color=NEG))

    P.append(rect(60, 250, 820, 58, fill=NEGF, stroke=NEG, sw=1.6, rx=12))
    P.append(text(470, 274, "цьому байту відповідає многочлен", size=12, bold=True))
    P.append(mono(470, 296, "M(x) = x⁷ + x⁶ + x⁴ + x + 1", size=18, color=NEG))

    P.append(rect(60, 332, 820, 110, fill="#faf3e0", stroke=GOLD, sw=1.6, rx=12))
    P.append(text(470, 358, "Поліном-дільник (generator polynomial) CRC задають так само — рядком бітів", size=13, bold=True))
    P.append(mono(470, 386, "приклад: CRC-8 з поліномом 0x07  →  G(x) = x⁸ + x² + x + 1", size=16, color=POS))
    P.append(text(470, 414, "Степінь G(x) = 8 (старший біт x⁸ домовлено не пишуть у байті 0x07) ⇒ лишок займає 8 біт = CRC-8.",
                  size=11))
    P.append(text(470, 432, "Саме степінь дільника задає ширину контрольної суми: степінь 16 → CRC-16, степінь 32 → CRC-32.",
                  size=11))

    render(os.path.join(OUT, "bits-as-poly.svg"), W, H, *P)


# ── 3. Ділення многочленів «стовпчиком» = обчислення CRC ──────────────────────
def fig_long_division():
    W, H = 940, 620
    P = []
    P.append(text(W / 2, 32, "Ділення многочленів над GF(2) «стовпчиком» — це і є обчислення CRC", size=18, bold=True))
    P.append(text(W / 2, 53, "на кожному кроці віднімаємо (XOR) зсунутий дільник; жодних переносів і позик — кожен стовпчик сам по собі",
                  size=12, color=MUTED, italic=True))

    P.append(mono(232, 110, "G = 1011", size=16, color=GOLD, anchor="end"))
    P.append(text(232, 128, "(x³+x+1)", size=11, color=MUTED, anchor="end"))

    # рядки ділення: (текст, колір, підпис, лінія_під)
    rows = [
        ("1010000", INK,  "ділене: повідомлення 1010 + три нулі під майбутній лишок", False),
        ("1011000", POS,  "⊕ G, підведений під старшу 1 (позиція x⁶)", True),
        ("0001000", INK,  "= проміжок (старша 1 згасла)", False),
        ("0001000", MUTED, "старший біт = 0 ⇒ G не віднімаємо, зсуваємось далі", False),
        ("0001000", MUTED, "знову 0 ⇒ пропуск", False),
        ("0001011", POS,  "⊕ G, підведений під наступну 1 (позиція x³)", True),
        ("0000011", FIELD, "= лишок: коротший за G, ділити більше нічим", False),
    ]
    y = 96
    for txt, col, cap, underline in rows:
        P.append(mono(250, y, txt, size=19, color=col, anchor="start"))
        if underline:
            P.append(line(248, y + 6, 330, y + 6, color=col, sw=1.4))
        P.append(text(440, y, cap, size=11, color=col, anchor="start",
                      bold=(col in (POS, FIELD))))
        y += 30
    P.append(mono(250, 316, "CRC-3 = 011", size=19, color=FIELD, anchor="start"))
    P.append(text(440, 316, "лишок коротший за дільник — це і є контрольна сума повідомлення 1010",
                  size=12, color=FIELD, anchor="start", bold=True))

    # бічна панель
    P.append(rect(600, 88, 312, 360, fill=NEGF, stroke=NEG, sw=1.6, rx=12))
    P.append(text(756, 116, "Що тут відбувається", size=14, bold=True))
    steps = [
        ("1. До повідомлення дописуємо стільки", True),
        ("   нулів, який степінь у дільника G", False),
        ("   (тут 3) — це місце під майбутній CRC.", False),
        ("", False),
        ("2. Ділимо стовпчиком: де старший біт", True),
        ("   проміжку = 1 — віднімаємо (XOR) G,", False),
        ("   зсунутий під цю одиницю; де 0 —", False),
        ("   просто йдемо до наступного біта.", False),
        ("", False),
        ("3. Що лишилось коротше за G — і є", True),
        ("   лишок R(x). Це й є контрольна сума.", False),
    ]
    sy = 142
    for s, b in steps:
        P.append(text(618, sy, s, size=11, anchor="start", bold=b))
        sy += 21
    P.append(rect(618, 374, 276, 60, fill=FLDF, stroke=FIELD, sw=1.6, rx=10))
    P.append(mono(756, 396, "Передаємо: 1010 011", size=13, color=FIELD))
    P.append(text(756, 416, "(повідомлення + лишок замість дописаних нулів)", size=10))

    # нижня рамка
    P.append(rect(60, 470, 820, 120, fill=POSF, stroke=POS, sw=1.6, rx=12))
    P.append(text(470, 496, "Ключ до всього: «віднімання» тут — це XOR біт-у-біт", size=15, color=POS, bold=True))
    P.append(text(90, 524, "У звичайному стовпчику віднімання тягне позики між розрядами. Над GF(2) позик немає: кожен стовпчик —",
                  size=12, anchor="start"))
    P.append(text(90, 544, "окреме 1−1=0, 1−0=1, 0−1=1 — тобто рівно XOR. Тому весь поділ зводиться до зсувів і XOR, і його легко",
                  size=12, anchor="start"))
    P.append(text(90, 564, "робить як кілька вентилів у залізі, так і кілька рядків коду на МК (бітовий цикл — це буквально ці кроки).",
                  size=12, anchor="start"))

    render(os.path.join(OUT, "long-division.svg"), W, H, *P)


# ── 4. Многочлен помилки E(x): що CRC гарантовано ловить ──────────────────────
def fig_error_polynomial():
    W, H = 940, 514
    P = []
    P.append(text(W / 2, 32, "Мова многочленів пояснює, ЯКІ помилки CRC гарантовано ловить", size=18, bold=True))
    P.append(text(W / 2, 53, "перешкода додає до кадру свій многочлен помилки E(x); CRC пропустить її лише тоді, коли G(x) ділить E(x)",
                  size=12, color=MUTED, italic=True))

    # T(x) + E(x) = R(x)
    P.append(rect(70, 96, 250, 56, fill=FLDF, stroke=FIELD, sw=1.6, rx=10))
    P.append(text(195, 118, "передано T(x)", size=12, bold=True))
    P.append(text(195, 140, "ділиться на G(x) націло", size=11, color=FIELD, bold=True))
    P.append(text(360, 130, "+", size=24, color=POS, bold=True))
    P.append(rect(400, 96, 250, 56, fill=POSF, stroke=POS, sw=1.6, rx=10))
    P.append(text(525, 118, "помилка E(x)", size=12, bold=True))
    P.append(text(525, 140, "одиниці там, де біти злетіли", size=11, color=POS, bold=True))
    P.append(text(690, 130, "=", size=24, color=INK, bold=True))
    P.append(rect(720, 96, 190, 56, fill=NEGF, stroke=NEG, sw=1.6, rx=10))
    P.append(text(815, 118, "прийнято R(x)", size=12, bold=True))
    P.append(mono(815, 140, "= T(x) + E(x)", size=11, color=NEG))

    P.append(rect(60, 178, 820, 70, fill=BG, stroke=INK, sw=1.6, rx=12))
    P.append(text(470, 204, "Приймач ділить R(x) на G(x). Оскільки T(x) ділиться без лишку, лишок дає сама лише E(x):",
                  size=12, bold=True))
    P.append(mono(470, 230, "R(x) mod G(x) = E(x) mod G(x)   →   помилка непомітна  ⇔  G(x) ділить E(x)",
                  size=15, color=POS))

    # таблиця класів помилок
    head = [(70, 360, "Клас помилки E(x)", "start", 82), (430, 250, "Чому G(x) її не ділить", "middle", None),
            (680, 190, "Гарантія", "middle", None)]
    for hx, hw, lbl, anc, tx in head:
        P.append(rect(hx, 282, hw, 34, fill="#faf3e0", stroke=GOLD, sw=1.4, rx=6))
        P.append(text(tx if tx else hx + hw / 2, 305, lbl, size=13, anchor=anc, bold=True))

    rows = [
        ("Будь-який 1 перевернутий біт", "E(x) = xⁱ, а дільник має ≥ 2 доданки", "завжди"),
        ("Будь-які 2 перевернуті біти", "беруть примітивний G(x) із ≥ 3 доданками", "у межах кадру"),
        ("Непарне число помилок", "беруть G(x), кратний (x + 1)", "завжди"),
        ("Серія (burst) завдовжки ≤ степінь G", "коротша за G ⇒ не ділиться на G націло", "завжди"),
    ]
    ry = 316
    for left, mid, guar in rows:
        P.append(rect(70, ry, 360, 40, fill="#fafafa", stroke="#e4e4e4", sw=1.2, rx=6))
        P.append(text(82, ry + 24.8, left, size=12, anchor="start", bold=True))
        P.append(rect(430, ry, 250, 40, fill=BG, stroke="#e4e4e4", sw=1.2, rx=6))
        P.append(text(555, ry + 24.8, mid, size=11))
        P.append(rect(680, ry, 190, 40, fill=FLDF, stroke=FIELD, sw=1.4, rx=6))
        P.append(text(775, ry + 24.8, guar, size=12, color=FIELD, bold=True))
        ry += 40

    P.append(text(470, 502, "Саме тому поліноми CRC (CRC-8/16/32) не випадкові: їх добирають так, щоб E(x) найчастіших помилок не ділилось на G(x).",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "error-polynomial.svg"), W, H, *P)


if __name__ == "__main__":
    fig_gf2_tables()
    fig_bits_as_poly()
    fig_long_division()
    fig_error_polynomial()
    print("OK: 4 figures -> img/")
