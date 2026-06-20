# -*- coding: utf-8 -*-
"""Фігури до теми «Що таке давач».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Давач як перекладач: фізична величина → електричний сигнал ─────────────
def fig_translator():
    W, H = 680, 320
    f = []
    # центральна рамка «ДАВАЧ»
    f.append(rect(268, 92, 150, 152, fill="#eef6ef", stroke=FIELD, sw=2, rx=10))
    f.append(text(343, 162, "ДАВАЧ", size=19, color=FIELD, bold=True))
    f.append(text(343, 186, "перетворювач", size=12, italic=True))
    # лівий бік — фізичний світ
    f.append(text(118, 78, "ФІЗИЧНИЙ СВІТ", size=12, color=MUTED, bold=True))
    rows = [("температура", "ефект Зеебека", 122),
            ("світло", "фотоефект", 158),
            ("сила / тиск", "п'єзоефект", 194),
            ("відстань", "час відлуння", 230)]
    for name, eff, y in rows:
        f.append(text(52, y, name, size=13, anchor="start", bold=True))
        f.append(text(52, y + 15, eff, size=10, color=MUTED, anchor="start", italic=True))
        f.append(arrow(206, y - 4, 262, y - 4, color=INK, sw=2))
    # правий бік — електрика
    f.append(text(585, 78, "ЕЛЕКТРИКА", size=12, color=MUTED, bold=True))
    f.append(arrow(424, 168, 558, 168, color=FIELD, sw=2.5))
    # маленька синусоїда на виході
    import math
    pts = []
    for i in range(49):
        x = 470 + i * 1.8
        y = 134 - 12 * math.sin(i / 49.0 * 4 * math.pi)
        pts.append("%.1f,%.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" '
             'stroke-linejoin="round" stroke-linecap="round"/>' % (" ".join(pts), FIELD))
    f.append(text(588, 166, "напруга", size=14, color=FIELD, bold=True))
    f.append(text(588, 186, "→ число", size=11, italic=True))
    render(os.path.join(IMG, "translator.svg"), W, H, *f,
           title="Давач — перекладач: фізична величина → електричний сигнал")


# ── 2. Вимірювальний ланцюг: від величини до числа (без нумерації) ────────────
def fig_chain():
    W, H = 720, 210
    f = []
    boxes = [("величина", "T, світло…", MUTED),
             ("чутл. елемент", "давач", FIELD),
             ("нормування", "підсилювач", NEG),
             ("АЦП", "напруга → код", POS),
             ("число в МК", "зміст", INK)]
    x, y, bw, bh, gap = 30, 70, 116, 72, 20
    for i, (top, sub, col) in enumerate(boxes):
        bx = x + i * (bw + gap)
        f.append(rect(bx, y, bw, bh, fill=BG, stroke=col, sw=2, rx=8))
        f.append(text(bx + bw / 2, y + 30, top, size=12, bold=True))
        f.append(text(bx + bw / 2, y + 50, sub, size=10, color=col, italic=True))
        if i:
            f.append(arrow(bx - gap + 1, y + bh / 2, bx - 2, y + bh / 2, color=INK, sw=2))
    f.append(text(W / 2, 172, "сирий мкВ-сигнал → підсилений → відфільтрований → оцифрований → зміст",
                  size=12.5, italic=True))
    render(os.path.join(IMG, "chain.svg"), W, H, *f,
           title="Вимірювальний ланцюг: від величини до числа")


# ── 3. Дві сім'ї давачів ──────────────────────────────────────────────────────
def fig_families():
    W, H = 700, 320
    f = []
    # ліва панель — самогенерувальний
    f.append(rect(30, 50, 310, 246, fill="#fff0e2", stroke=POS, sw=1.6, rx=10))
    f.append(text(185, 74, "САМОГЕНЕРУВАЛЬНИЙ", size=13.5, color=POS, bold=True))
    f.append(text(185, 92, "сам джерело ЕРС — живлення не треба", size=11, italic=True))
    f.append(text(70, 138, "тепло/світло", size=10.5, color="#e8702a"))
    f.append(arrow(70, 150, 120, 150, color="#e8702a", sw=2.4))
    f.append(circle(150, 150, 22, fill=BG, stroke=INK, sw=2))
    f.append(text(150, 145, "+", size=15, color=POS, bold=True))
    f.append(line(143, 160, 157, 160, color=NEG, sw=2.4))
    f.append(line(150, 172, 150, 210, color=INK, sw=2))
    f.append(line(172, 150, 250, 150, color=INK, sw=2))
    f.append(line(250, 150, 250, 210, color=INK, sw=2))
    f.append(line(150, 210, 224, 210, color=INK, sw=2))
    f.append(circle(250, 210, 20, fill=BG, stroke=INK, sw=2))
    f.append(text(250, 216, "V", size=16, color=FIELD, bold=True))
    f.append(text(150, 250, "термопара · фотодіод · п'єзо", size=11, bold=True))
    f.append(text(185, 282, "сигнал малий, але автономний", size=11, color=MUTED, italic=True))
    # права панель — параметричний
    f.append(rect(360, 50, 310, 246, fill="#e8f1fb", stroke=NEG, sw=1.6, rx=10))
    f.append(text(515, 74, "ПАРАМЕТРИЧНИЙ", size=13.5, color=NEG, bold=True))
    f.append(text(515, 92, "змінний R/C/L — його треба живити", size=11, italic=True))
    f.append(circle(412, 187, 18, fill=BG, stroke=INK, sw=2))
    f.append(text(412, 182, "+", size=15, color=POS, bold=True))
    f.append(line(405, 195, 419, 195, color=NEG, sw=2.4))
    f.append(text(412, 158, "V_оп", size=11, bold=True))
    f.append(line(412, 169, 412, 118, color=INK, sw=2))
    f.append(line(412, 118, 560, 118, color=INK, sw=2))
    f.append(line(412, 205, 412, 256, color=INK, sw=2))
    f.append(line(412, 256, 560, 256, color=INK, sw=2))
    # верхній фіксований резистор (зигзаг)
    f.append('<polyline points="560,118 552,122.2 568,130.5 552,138.8 568,147.2 552,155.5 568,163.8 560,168" '
             'fill="none" stroke="%s" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>' % INK)
    f.append(text(576, 146, "R", size=12, anchor="start", bold=True))
    f.append(circle(560, 176, 4, fill=INK, stroke=INK, sw=1))
    f.append(line(560, 168, 560, 184, color=INK, sw=2))
    f.append(line(560, 176, 632, 176, color=FIELD, sw=2))
    f.append(text(636, 180, "→ АЦП", size=11, color=FIELD, anchor="start", bold=True))
    # нижній змінний резистор (зигзаг)
    f.append('<polyline points="560,184 552,188.2 568,196.5 552,204.8 568,213.2 552,221.5 568,229.8 560,234" '
             'fill="none" stroke="%s" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/>' % FIELD)
    f.append(line(560, 234, 560, 256, color=INK, sw=2))
    f.append(arrow(600, 210, 572, 208, color=FIELD, sw=1.8))
    f.append(text(604, 214, "R(вимір.)", size=10.5, color=FIELD, anchor="start", bold=True))
    f.append(text(515, 282, "терморезистор · фоторезистор · ємнісний", size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "families.svg"), W, H, *f,
           title="Дві сім'ї давачів за джерелом енергії сигналу")


# ── 4. Оборотність: давач ↔ виконавчий пристрій ───────────────────────────────
def fig_duality():
    W, H = 680, 300
    PUR = "#6a4ea8"
    f = []
    f.append(rect(285, 78, 110, 80, fill="#f2f0fb", stroke=PUR, sw=2, rx=8))
    f.append(text(340, 112, "перетво-", size=12.5, color=PUR, bold=True))
    f.append(text(340, 130, "рювач", size=12.5, color=PUR, bold=True))
    f.append(text(120, 98, "ФІЗИЧНЕ", size=12.5, color=MUTED, bold=True))
    f.append(text(560, 98, "ЕЛЕКТРИЧНЕ", size=12.5, color=MUTED, bold=True))
    # давач: фізичне → електричне (зелені стрілки)
    f.append(text(340, 72, "давач:  фізичне → електричне", size=12, color=FIELD, bold=True))
    f.append(arrow(150, 118, 279, 118, color=FIELD, sw=2.4))
    f.append(arrow(401, 118, 540, 118, color=FIELD, sw=2.4))
    # виконавчий пристрій: електричне → фізичне (червоні стрілки)
    f.append(text(340, 196, "та сама фізика — два застосування:", size=12, italic=True))
    f.append(arrow(540, 194, 401, 194, color=POS, sw=2.4))
    f.append(arrow(279, 194, 150, 194, color=POS, sw=2.4))
    f.append(text(340, 216, "виконавчий пристрій:  електричне → фізичне", size=12, color=POS, bold=True))
    # пари
    pairs = [(147, "динамік", "мікрофон"), (287, "мотор", "генератор"),
             (427, "п'єзо-пищалка", "давач удару"), (567, "Пельтьє", "термопара")]
    for cx, a, b in pairs:
        f.append(rect(cx - 65, 230, 130, 36, fill="#fafafa", stroke=MUTED, sw=1, rx=6))
        f.append(text(cx, 247, a, size=11, color=POS, bold=True))
        f.append(text(cx, 261, b, size=11, color=FIELD, bold=True))
    render(os.path.join(IMG, "duality.svg"), W, H, *f,
           title="Перетворювач читається у два боки: давач ↔ виконавчий пристрій")


# ── 5. Форми вихідного сигналу ────────────────────────────────────────────────
def fig_output_forms():
    W, H = 700, 350
    PUR = "#6a4ea8"
    f = []
    rows = [("напруга", "просто на АЦП; боїться завад і падіння на дротах", 64),
            ("струм 4–20 мА", "однаковий уздовж кола → стійкий на відстані", 118),
            ("зміна R / C", "потребує дільника чи моста, далі АЦП", 172),
            ("частота / період", "рахує таймер — точно, без аналогу", 226),
            ("цифрове число", "давач уже містить АЦП; читаємо готове", 280)]
    for name, desc, y in rows:
        f.append(rect(28, y, 644, 46, fill="#fbfbfb", stroke="#e4e4e4", sw=1, rx=6))
        f.append(text(46, y + 28, name, size=13, anchor="start", bold=True))
        f.append(text(326, y + 28, desc, size=11.5, anchor="start"))
    # піктограми по центру кожного рядка (210..300)
    f.append(line(210, 97, 300, 77, color=FIELD, sw=2.2))                       # напруга — нахил
    f.append(rect(210, 132, 90, 22, fill="none", stroke=POS, sw=1.6, rx=4))     # струм — петля
    f.append(arrow(218, 143, 288, 143, color=POS, sw=1.8))
    f.append('<polyline points="210,196 217.5,188 232.5,204 247.5,188 262.5,204 277.5,188 292.5,204 300,196" '
             'fill="none" stroke="%s" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>' % INK)  # R/C — пила
    f.append('<polyline points="210,262 210,240 225,240 225,262 240,262 240,240 255,240 255,262 270,262 '
             '270,240 285,240 285,262 300,262" fill="none" stroke="%s" stroke-width="2" '
             'stroke-linejoin="round" stroke-linecap="round"/>' % NEG)          # частота — меандр
    f.append(text(255, 310, "0 1 0 1 1 0", size=14, color=PUR, bold=True))      # цифра — біти
    render(os.path.join(IMG, "output-forms.svg"), W, H, *f,
           title="Форми вихідного сигналу давача — і чим читати кожну")


# ── 6. Кожна ланка щось спотворює (джерела похибок; без нумерації) ─────────────
def fig_imperfect_chain():
    W, H = 720, 250
    f = []
    boxes = [("величина", "істина", MUTED),
             ("чутл. елемент", "давач", FIELD),
             ("підсилювач", "тракт", NEG),
             ("АЦП", "крок", POS),
             ("число", "оцінка", INK)]
    x, y, bw, bh, gap = 30, 96, 116, 72, 20
    cx_list = []
    for i, (top, sub, col) in enumerate(boxes):
        bx = x + i * (bw + gap)
        cx_list.append(bx + bw / 2)
        f.append(rect(bx, y, bw, bh, fill=BG, stroke=col, sw=2, rx=8))
        f.append(text(bx + bw / 2, y + 30, top, size=12, bold=True))
        f.append(text(bx + bw / 2, y + 50, sub, size=10, color=col, italic=True))
        if i:
            f.append(arrow(bx - gap + 1, y + bh / 2, bx - 2, y + bh / 2, color=INK, sw=2))
    # підписи похибок над ланками (без номерів)
    errs = [(cx_list[1], "нелінійність / дрейф / шум"),
            (cx_list[2], "зсув, смуга"),
            (cx_list[3], "квантування")]
    for cx, lbl in errs:
        f.append(text(cx, 62, lbl, size=10.5, color=POS, bold=True))
        f.append(arrow(cx, 70, cx, y - 4, color=POS, sw=1.8))
    f.append(text(W / 2, 214, "давач дає не істину, а підказку — її треба грамотно витлумачити",
                  size=13, italic=True))
    render(os.path.join(IMG, "imperfect-chain.svg"), W, H, *f,
           title="Кожна ланка щось спотворює")


if __name__ == "__main__":
    fig_translator()
    fig_chain()
    fig_families()
    fig_duality()
    fig_output_forms()
    fig_imperfect_chain()
    print("Готово: 6 SVG у", IMG)
