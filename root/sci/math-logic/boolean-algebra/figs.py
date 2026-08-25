# -*- coding: utf-8 -*-
"""Фігури до math-вставки «Аксіоми булевої алгебри й доведення тотожностей».
Запуск:  python figs.py   → пише SVG у ./img/  (axioms, proof, demorgan, karnaugh)
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

ROW = "#f4f6f8"   # світла смуга парного рядка


# ── 1. Аксіоми у дуальних парах ──────────────────────────────────────────────
def fig_axioms():
    W, H = 880, 470
    f = [text(W / 2, 30, "Аксіоми булевої алгебри (постулати Гантінґтона, 1904)",
              size=18, bold=True),
         text(W / 2, 52, "усього кілька правил, узятих за дане; решта законів — це вже ТЕОРЕМИ, доведені з них",
              size=12, color=MUTED, italic=True)]

    # шапка колонок
    f.append(text(118, 92, "аксіома", size=12, color=MUTED, bold=True))
    f.append(text(250, 92, "для « + » (АБО)", size=14, bold=True))
    f.append(text(620, 92, "для « · » (І)", size=14, bold=True))

    rows = [
        ("Замкненість",      "a + b ∈ B",            "a · b ∈ B",          False),
        ("Нейтральний",      "a + 0 = a",            "a · 1 = a",          False),
        ("Комутативність",   "a + b = b + a",        "a · b = b · a",      False),
        ("Дистрибутивність", "a + (b·c) = (a+b)·(a+c)", "a · (b+c) = a·b + a·c", False),
        ("Доповнення",       "a + ā = 1",            "a · ā = 0",          False),
        ("Два елементи",     "у B є 0 ≠ 1",          "(не той самий)",     True),
    ]
    top, rh = 110, 46
    box_h = len(rows) * rh
    f.append(rect(60, top, 760, box_h, fill="none", stroke=MUTED, sw=1.2))
    # роздільник колонок
    f.append(line(625, top, 625, top + box_h, color="#e4e4e4", sw=1.4))
    for i, (name, left, right, muted) in enumerate(rows):
        y = top + i * rh
        if i % 2 == 0:
            f.append(rect(60, y, 760, rh, fill=ROW, stroke="none", sw=0, rx=0))
        f.append(text(74, y + 30, name, size=12.5, color=INK, anchor="start", bold=True))
        col = MUTED if muted else INK
        bold = not muted
        f.append(text(250, y + 30, left, size=14.5, color=col, bold=bold))
        f.append(text(620, y + 30, right, size=14.5, color=col, bold=bold))

    # підсумок-плашка
    by = top + box_h + 12
    f.append(rect(60, by, 760, 44, fill="#f1f8f3", stroke=FIELD, sw=1.6, rx=10))
    f.append(text(W / 2, by + 28,
                  "Кожна аксіома ліворуч має ДВІЙНИКА праворуч: міняємо + ↔ · та 0 ↔ 1 — і одне правило стає іншим.",
                  size=12.5, bold=True))
    render(os.path.join(IMG, "axioms.svg"), W, H, *f)


# ── 2. Доведення тотожності a + a = a ────────────────────────────────────────
def fig_proof():
    W, H = 880, 430
    f = [text(W / 2, 30, "Доведення тотожності: a + a = a — лише з аксіом", size=18, bold=True),
         text(W / 2, 52, "ідемпотентність не приймаємо як «очевидну» — її ВИВОДИМО; праворуч — аксіома, що дозволяє крок",
              size=12, color=MUTED, italic=True)]

    steps = [
        ("a + a", "= (a + a) · 1",        "[ нейтральний (·1) ]",     False),
        ("",      "= (a + a) · (a + ā)",  "[ доповнення (a+ā=1) ]",   False),
        ("",      "= a + (a · ā)",        "[ дистрибутивність ]",     False),
        ("",      "= a + 0",              "[ доповнення (a·ā=0) ]",    False),
        ("",      "= a",                  "[ нейтральний (+0) ]",     True),
    ]
    top, rh = 100, 46
    f.append(line(234, top - 14, 234, top + len(steps) * rh - rh + 8, color="#e4e4e4", sw=2))
    for i, (lhs, rhs, why, last) in enumerate(steps):
        y = top + i * rh
        if lhs:
            f.append(text(150, y, lhs, size=18, color=INK, anchor="end", bold=True))
        col = FIELD if last else INK
        f.append(text(250, y, rhs, size=17, color=col, anchor="start", bold=last))
        f.append(text(600, y, why, size=12.5, color=MUTED, anchor="start", italic=True))

    by = 360
    f.append(rect(60, by, 760, 50, fill="#f1f8f3", stroke=FIELD, sw=1.6, rx=10))
    f.append(text(W / 2, by + 22,
                  "За дуальністю одразу маємо й двійника: a · a = a (міняємо + ↔ · та 0 ↔ 1 у кожному рядку).",
                  size=12.5, bold=True))
    f.append(text(W / 2, by + 41,
                  "Так само з аксіом доводять поглинання, Де Моргана й решту «шпаргалки» — нічого не беручи на віру.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "proof.svg"), W, H, *f)


# ── 3. Де Морган через єдиність доповнення ───────────────────────────────────
def fig_demorgan():
    W, H = 880, 470
    f = [text(W / 2, 30, "Закон Де Моргана як теорема: ‾(a+b) = ā·b̄", size=18, bold=True),
         text(W / 2, 52, "доповнення ЄДИНЕ — отже досить показати, що x = ā·b̄ грає роль доповнення до (a+b)",
              size=12, color=MUTED, italic=True)]

    # ключ зверху
    f.append(rect(60, 72, 760, 40, fill=ROW, stroke=MUTED, sw=1.2, rx=8))
    f.append(text(W / 2, 97,
                  "Ключ: якщо для якогось x водночас  (a+b)+x = 1  і  (a+b)·x = 0,  то цей x — і є ‾(a+b).",
                  size=13, bold=True))

    # дві колонки перевірок
    colL, colR = 250, 630
    f.append(text(colL, 142, "Перевірка « = 1 »", size=13.5, bold=True, color=POS))
    f.append(text(colR, 142, "Перевірка « = 0 »", size=13.5, bold=True, color=NEG))
    f.append(line(440, 130, 440, 392, color="#e4e4e4", sw=1.4))

    left = [
        "(a+b) + ā·b̄",
        "= (a+b+ā)·(a+b+b̄)",
        "    [дистрибутивність]",
        "= (1+b)·(a+1)",
        "    [a+ā=1, b+b̄=1]",
        "= 1 · 1  =  1  ✓",
    ]
    right = [
        "(a+b) · ā·b̄",
        "= a·ā·b̄ + b·ā·b̄",
        "    [дистрибутивність]",
        "= 0·b̄ + 0·ā",
        "    [a·ā=0, b·b̄=0]",
        "= 0 + 0  =  0  ✓",
    ]
    y = 172
    for i in range(len(left)):
        hint = left[i].strip().startswith("[")
        f.append(text(colL, y, left[i], size=14 if not hint else 11.5,
                      color=MUTED if hint else INK, italic=hint,
                      bold=left[i].strip().endswith("✓")))
        f.append(text(colR, y, right[i], size=14 if not hint else 11.5,
                      color=MUTED if hint else INK, italic=hint,
                      bold=right[i].strip().endswith("✓")))
        y += 36

    by = 408
    f.append(rect(60, by, 760, 46, fill="#f1f8f3", stroke=FIELD, sw=1.6, rx=10))
    f.append(text(W / 2, by + 28,
                  "Обидві рівності справдились → ā·b̄ і є ‾(a+b). Другий закон ‾(a·b)=ā+b̄ — задарма, двійником.",
                  size=12.5, bold=True))
    render(os.path.join(IMG, "demorgan.svg"), W, H, *f)


# ── 4. Карта Карно: спрощення видно оком ─────────────────────────────────────
def fig_karnaugh():
    W, H = 880, 440
    f = [text(W / 2, 30, "Карта Карно: те саме спрощення, але видно оком", size=18, bold=True),
         text(W / 2, 52, "сусідні одиниці, що складаються у прямокутник, склеюються — змінна, що в ньому міняється, зникає",
              size=12, color=MUTED, italic=True)]

    # Сітка 4×4. Беремо F(a,b,c,d) = 1 рівно у чотирьох клітинках, де b=0 і d=0.
    # У коді Грея b — старший біт пари ab → b=0 для рядків ab ∈ {00, 01}.
    #             d — молодший біт пари cd → d=0 для стовпців cd ∈ {00, 10}.
    ox, oy, cw, ch = 220, 112, 86, 58
    cols = ["00", "01", "11", "10"]   # cd за кодом Грея (b… власне d — молодший)
    rows = ["00", "01", "11", "10"]   # ab за кодом Грея

    def b_of(ab):  return ab[0]       # старший біт пари ab = b
    def d_of(cd):  return cd[1]       # молодший біт пари cd = d

    def is_one(ab, cd):
        return b_of(ab) == "0" and d_of(cd) == "0"

    # підписи осей
    f.append(text(ox - 30, oy - 16, "ab \\ cd", size=12, color=MUTED, anchor="middle"))
    for j, c in enumerate(cols):
        f.append(text(ox + j * cw + cw / 2, oy - 16, c, size=13, bold=True))
    for i, r in enumerate(rows):
        f.append(text(ox - 14, oy + i * ch + ch / 2 + 5, r, size=13, bold=True, anchor="end"))

    one_cells = []
    for i, r in enumerate(rows):
        for j, c in enumerate(cols):
            x, y = ox + j * cw, oy + i * ch
            one = is_one(r, c)
            if one:
                one_cells.append((i, j))
            f.append(rect(x, y, cw, ch, fill=("#fdecea" if one else BG),
                          stroke=MUTED, sw=1.2, rx=0))
            f.append(text(x + cw / 2, y + ch / 2 + 6, "1" if one else "0",
                          size=16, bold=one, color=(POS if one else MUTED)))

    # Чотири одиниці лежать у кутах рядків {00,01} × стовпців {00,10}: суміжні «по тору».
    # Обводимо обидва стовпці-кандидати у двох верхніх рядках двома рамками (карта згортається по краях).
    rs = sorted({i for i, _ in one_cells}); cs = sorted({j for _, j in one_cells})
    y0 = oy + rs[0] * ch; yh = (rs[-1] - rs[0] + 1) * ch
    for j in cs:
        x0 = ox + j * cw
        f.append(rect(x0 - 4, y0 - 4, cw + 8, yh + 8, fill="none", stroke=POS, sw=2.6, rx=8))

    # правий стовпчик пояснень
    px = 600
    f.append(text(px, 132, "F = (терми, де b=0, d=0)", size=13.5, bold=True, anchor="start"))
    f.append(text(px, 160, "оком: усі чотири одиниці", size=12.5, color=MUTED, anchor="start"))
    f.append(text(px, 178, "стоять там, де b=0 і d=0", size=12.5, color=MUTED, anchor="start"))
    f.append(text(px, 212, "усередині блоку a й c", size=12.5, color=MUTED, anchor="start"))
    f.append(text(px, 230, "пробігають усі значення", size=12.5, color=MUTED, anchor="start"))
    f.append(text(px, 248, "→ обидві зайві", size=12.5, color=MUTED, anchor="start"))
    f.append(text(px, 290, "F = b̄·d̄", size=20, bold=True, color=FIELD, anchor="start"))

    by = 384
    f.append(rect(60, by, 760, 44, fill="#f1f8f3", stroke=FIELD, sw=1.6, rx=10))
    f.append(text(W / 2, by + 28,
                  "Карта — це та сама алгебра, лише геометрично: більший блок = коротший добуток.",
                  size=12.5, bold=True))
    render(os.path.join(IMG, "karnaugh.svg"), W, H, *f)


if __name__ == "__main__":
    fig_axioms()
    fig_proof()
    fig_demorgan()
    fig_karnaugh()
    print("OK: 4 figures ->", IMG)
