# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: три тіла, які реально лежать у наборі, з маркуванням і полярністю ──
def anatomy():
    W, H = 860, 470
    f = []
    # три колонки з великим запасом, щоб підписи не накладались
    cols = [150, 430, 710]
    top = 70
    f.append(text(W/2, 34, "Три види конденсаторів у типовому наборі", size=17, bold=True))

    # --- 1. Керамічний диск (неполярний) ---
    cx = cols[0]
    # корпус — крапля/диск на двох ніжках
    f.append('<ellipse cx="%.1f" cy="%.1f" rx="46" ry="54" fill="#f0d9a8" stroke="%s" stroke-width="1.5"/>' % (cx, top+54, LINE))
    f.append(text(cx, top+44, "104", size=20, bold=True, color=INK))
    f.append(text(cx, top+70, "50V", size=13, color=MUTED))
    # ніжки
    f.append(line(cx-18, top+106, cx-18, top+150, color=LINE, sw=2))
    f.append(line(cx+18, top+106, cx+18, top+150, color=LINE, sw=2))
    f.append(text(cx, top+178, "керамічний диск", size=14, bold=True))
    f.append(mtext(cx, top+200, ["неполярний", "ставиться будь-яким боком"], size=12, color=MUTED, lh=1.35))
    # розшифровка коду
    box = textbox(cx, top+270, "код 104:\n10 · 10⁴ пФ\n= 100 нФ = 0.1 мкФ", size=12.5, pad=9,
                  fill="#eef7f0", stroke=FIELD)
    f.append(box[0])

    # --- 2. Плівковий / коробочка (неполярний) ---
    cx = cols[1]
    f.append(rect(cx-52, top, 104, 88, fill="#cfe3f7", stroke=LINE, sw=1.5, rx=8))
    f.append(text(cx, top+38, "0.1", size=20, bold=True))
    f.append(text(cx, top+62, "J  63", size=13, color=MUTED))
    f.append(line(cx-24, top+88, cx-24, top+150, color=LINE, sw=2))
    f.append(line(cx+24, top+88, cx+24, top+150, color=LINE, sw=2))
    f.append(text(cx, top+178, "плівковий (box)", size=14, bold=True))
    f.append(mtext(cx, top+200, ["неполярний", "точний, для сигналу"], size=12, color=MUTED, lh=1.35))
    box = textbox(cx, top+270, "0.1 = 0.1 мкФ\nJ = ±5 %\n63 = робочі 63 В", size=12.5, pad=9,
                  fill="#eef7f0", stroke=FIELD)
    f.append(box[0])

    # --- 3. Електролітичний циліндр (ПОЛЯРНИЙ) ---
    cx = cols[2]
    # банка
    f.append(rect(cx-42, top-6, 84, 108, fill="#2a2f3a", stroke=LINE, sw=1.5, rx=10))
    # смуга «−» уздовж корпусу
    f.append(rect(cx-42, top-6, 20, 108, fill="#b9c2d0", stroke="none", sw=0, rx=10))
    f.append(text(cx-32, top+54, "−", size=26, bold=True, color=NEG))
    f.append(text(cx+8, top+40, "470", size=19, bold=True, color="#ffffff"))
    f.append(text(cx+8, top+64, "µF", size=14, color="#ffffff"))
    f.append(text(cx+8, top+86, "25V", size=12, color="#dfe6f0"))
    # ніжки: довша = «+»
    f.append(line(cx-22, top+102, cx-22, top+140, color=LINE, sw=2))     # коротка «−»
    f.append(line(cx+16, top+102, cx+16, top+156, color=LINE, sw=2))     # довга «+»
    f.append(plus(cx+16, top+168, r=9))
    f.append(minus(cx-22, top+152, r=9))
    f.append(text(cx, top+198, "електролітичний", size=14, bold=True))
    f.append(text(cx, top+218, "ПОЛЯРНИЙ — бік важить", size=12.5, color=POS, bold=True))
    box = textbox(cx, top+275, "смуга «−» = мінус\nдовша ніжка = плюс\n470 мкФ, макс 25 В", size=12.5, pad=9,
                  fill="#fdecea", stroke=POS)
    f.append(box[0])

    render(os.path.join(IMG, 'anatomy.svg'), W, H, *f)


# ── Фігура 2: що взяти з набору під задачу (мапа вибору) ──
def selection():
    W, H = 820, 430
    f = []
    f.append(text(W/2, 34, "Що дістати з набору під задачу", size=17, bold=True))

    # три доріжки-задачі, кожна веде до типу і номіналу
    rows = [
        ("Заспокоїти живлення\nбіля мікросхеми", "керамічний 100 нФ (104)",
         "малий, швидкий, поруч із ніжкою VCC", "#eef7f0", FIELD),
        ("Задати час / фільтр\n(RC, генератор)", "плівковий або керамічний,\nточний номінал",
         "стабільний, неполярний, ±5 %", "#eaf0fd", NEG),
        ("Згладити просадку,\nзапас енергії", "електролітичний 100–1000 мкФ",
         "полярний! запас напруги ×1.5–2", "#fdecea", POS),
    ]
    y = 78
    rowh = 108
    for title, pick, note, fill, stroke in rows:
        # ліва картка — задача
        b = fitbox(40, y, 230, 78, title, size=14, pad=12, fill="#f4f6f8", stroke=LINE, bold=True)
        f.append(b)
        # стрілка
        f.append(arrow(280, y+39, 340, y+39, color=stroke, sw=2.2))
        # права картка — що взяти
        bb = textbox(555, y+26, pick, size=13.5, pad=11, fill=fill, stroke=stroke, bold=True, min_w=360)
        f.append(bb[0])
        f.append(text(555, y+70, note, size=11.5, color=MUTED))
        y += rowh

    render(os.path.join(IMG, 'selection.svg'), W, H, *f)


# ── Фігура 3 (для вставки proj-decode-code): три гілки розбору → одне число ──
def decode():
    W, H = 900, 470
    f = []
    f.append(text(W/2, 32, "Розбір маркування: три гілки, одне число в пФ", size=17, bold=True))

    # верх: сирий напис із корпусу
    top = textbox(W/2, 74, "напис на корпусі:  104   ·   0.1   ·   4n7   ·   470µF 25V",
                  size=13.5, pad=11, fill="#f4f6f8", stroke=LINE, bold=True, min_w=560)
    f.append(top[0])

    # крок «зняти обгортку»: відрізати напругу й літеру-допуск
    strip = textbox(W/2, 138, "спершу відрізати напругу (…V) і літеру-допуск (J/K/M) — в окремі поля",
                    size=12, pad=9, fill="#eef7f0", stroke=FIELD)
    f.append(strip[0])
    f.append(arrow(W/2, 92, W/2, 122, color=LINE, sw=1.8))

    # три гілки під смугою
    by = 210
    bh = 96
    branches = [
        (170, "ТРИЦИФРОВИЙ КОД", "104  →  10 · 10⁴",
         "дві цифри × 10^третя,\nв пікофарадах", "#eaf0fd", NEG),
        (450, "ПРЯМЕ МАРКУВАННЯ", "0.1  →  0.1 · 10⁶",
         "число × одиниця:\nмкФ=10⁶, нФ=10³, пФ=1", "#eef7f0", FIELD),
        (730, "БУКВА ЗАМІСТЬ КОМИ", "4n7  →  4.7 нФ",
         "цифри до/після літери,\nлітера дає одиницю", "#fdf6e8", "#b8860b"),
    ]
    for cx, head, mid, note, fill, stroke in branches:
        f.append(arrow(W/2, 158, cx, by-6, color=stroke, sw=1.6))
        bb = textbox(cx, by+16, head, size=12.5, pad=8, fill=fill, stroke=stroke, bold=True, min_w=210)
        f.append(bb[0])
        f.append(text(cx, by+52, mid, size=13, bold=True, color=INK))
        f.append(mtext(cx, by+72, note.split("\n"), size=10.5, color=MUTED, lh=1.3))

    # низ: усе стікає в одне число (пФ), тоді показ у зручній одиниці
    fy = by + bh + 40
    for cx, *_ in branches:
        f.append(arrow(cx, by+bh-2, W/2, fy-8, color=LINE, sw=1.4))
    out = textbox(W/2, fy+16, "одне число в пФ  →  показ як пФ / нФ / мкФ",
                  size=13.5, pad=11, fill="#e8f0ff", stroke=NEG, bold=True, min_w=440)
    f.append(out[0])

    # пастка «100» — окремо збоку, щоб не наліз на гілки
    trap = textbox(W/2, fy+72, "пастка:  код 100 = 10 · 10⁰ = 10 пФ  (а НЕ 100 пФ)",
                   size=12.5, pad=9, fill="#fdecea", stroke=POS, bold=True, min_w=440)
    f.append(trap[0])

    render(os.path.join(IMG, 'decode.svg'), W, H, *f)


if __name__ == '__main__':
    anatomy()
    selection()
    decode()
    print("ok")
