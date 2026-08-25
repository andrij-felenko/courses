# -*- coding: utf-8 -*-
"""Фігури до теми «Логіка 74».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Ім'я чипа = чотири незалежні поля ──────────────────────────────────────
# Ідея: розкласти SN74HCT04N на поля й показати, що вони НЕЗАЛЕЖНІ:
# функцію читаєш окремо від сімейства, сімейство — окремо від корпусу.
def fig_name_fields():
    W, H = 780, 360
    f = []

    # Саме ім'я великими літерами по центру вгорі, з підсвіченими полями.
    parts = [
        ("SN",  MUTED, "виробник"),
        ("74",  INK,   "серія\n(темп. діапазон)"),
        ("HCT", POS,   "СІМЕЙСТВО\nрівні · швидкість"),
        ("04",  FIELD, "функція\n(6 інверторів)"),
        ("N",   NEG,   "корпус\n(форма)"),
    ]
    # ширини під кожен фрагмент — пропорційні довжині
    widths = [70, 70, 120, 80, 60]
    gap = 8
    total = sum(widths) + gap * (len(widths) - 1)
    x = (W - total) / 2
    top = 70
    boxh = 56
    centers = []
    for (txt, col, _), w in zip(parts, widths):
        f.append(rect(x, top, w, boxh, fill="#fbfbfb", stroke=col, sw=2.2, rx=8))
        fs = fit_font(txt, w - 12, 26, bold=True)
        f.append(text(x + w / 2, top + boxh / 2 + fs * 0.35, txt, size=fs, color=col, bold=True))
        centers.append(x + w / 2)
        x += w + gap

    # підписи-виноски під кожним полем
    lab_y = top + boxh + 30
    for (txt, col, note), cx in zip(parts, centers):
        f.append(line(cx, top + boxh + 2, cx, lab_y - 22, color=col, sw=1.3, dash="3,3"))
        lines = note.split("\n")
        for i, ln in enumerate(lines):
            f.append(text(cx, lab_y + i * 15, ln, size=10.5, color=col,
                          bold=(col in (POS,))))

    # стрілка «як читає досвідчений»: одразу стрибок на сімейство
    y2 = 250
    f.append(text(W / 2, y2,
                  "Досвідчений читає не зліва направо, а стрибає на СІМЕЙСТВО:",
                  size=12, color=INK, bold=True))
    b1 = fitbox(60, y2 + 20, 320, 70,
                "Функція «04» = шість інверторів\nхоч у 74HC04, хоч у 74LVC04.\n"
                "Літери НЕ міняють логіки.",
                size=11, fill="#eef6ef", stroke=FIELD, sw=1.4)
    f.append(b1)
    b2 = fitbox(400, y2 + 20, 320, 70,
                "Літери «HCT» = напруга, пороги,\nшвидкодія, з ким стикується.\n"
                "Саме тут відповідь «порозуміються?».",
                size=11, fill="#fdecea", stroke=POS, sw=1.4)
    f.append(b2)

    render(os.path.join(IMG, "name-fields.svg"), W, H, *f,
           title="Ім'я 74xx — чотири незалежні відповіді в одному рядку")


# ── 2. Одна функція, багато сімейств: спільна мова коду ───────────────────────
# Ідея: код функції — стовпчик; сімейства — стовпці; той самий «04» існує в
# кожному сімействі, лише електричний світ навколо міняється.
def fig_families_grid():
    W, H = 780, 380
    f = []

    fams = [
        ("74HC",  "CMOS 2–6 В", "5 В, пороги\nсиметричні"),
        ("74HCT", "HC + TTL-вхід", "5 В, читає\nстарий TTL"),
        ("74LVC", "низька напруга", "1.65–3.6 В,\nвхід терпить 5 В"),
        ("74LS",  "біполярний TTL", "5 В, давні\nсхеми"),
    ]
    funcs = [("00", "×4  І-НЕ"), ("04", "×6  НЕ"), ("08", "×4  І"), ("595", "зсув. рег.")]

    x0, y0 = 150, 90
    cw, rh = 150, 52
    # заголовки-сімейства
    for j, (fam, sub, _) in enumerate(fams):
        cx = x0 + j * cw + cw / 2
        f.append(rect(x0 + j * cw + 4, y0 - 46, cw - 8, 40, fill="#eef2f7", stroke=LINE, sw=1.6, rx=7))
        f.append(text(cx, y0 - 28, fam, size=13, color=POS, bold=True))
        f.append(text(cx, y0 - 12, sub, size=9.5, color=MUTED))

    # рядки-функції
    for i, (code, fn) in enumerate(funcs):
        cy = y0 + i * rh + rh / 2
        f.append(rect(10, y0 + i * rh + 4, 130, rh - 8, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=7))
        f.append(text(24, cy - 2, code, size=15, color=FIELD, bold=True, anchor="start"))
        f.append(text(24, cy + 15, fn, size=9.5, color=INK, anchor="start"))
        for j in range(len(fams)):
            cxx = x0 + j * cw
            f.append(rect(cxx + 4, y0 + i * rh + 4, cw - 8, rh - 8,
                          fill="#fbfbfb", stroke=MUTED, sw=1.1, rx=6))
            f.append(text(cxx + cw / 2, cy + 5, "74" + fams[j][0][2:] + code,
                          size=11, color=INK))

    # підпис знизу
    b = fitbox(90, y0 + len(funcs) * rh + 22, 600, 34,
               "Уздовж рядка — та сама функція в різних сімействах (міняються рівні); "
               "уздовж стовпця — різні функції одного сімейства.",
               size=11, fill="#fbfbfb", stroke=MUTED, sw=1.3)
    f.append(b)

    render(os.path.join(IMG, "families-grid.svg"), W, H, *f,
           title="Код функції — спільна мова; сімейство — вибір електричного світу")


# ── 3. DIP-14 гекс-інвертор 74×04: розводка на макеті ─────────────────────────
# Ідея: показати три закони серії — живлення по діагоналі, конденсатор розв'язки,
# невжиті входи на шину. Один інвертор у роботі: 1A → 1Y = NOT(1A).
def fig_dip_wiring():
    W, H = 780, 430
    f = []

    # корпус DIP-14
    bx, by, bw, bh = 300, 70, 180, 300
    f.append(rect(bx, by, bw, bh, fill="#eceff3", stroke=INK, sw=2.4, rx=10))
    # мітка-ключ (виїмка) зверху
    f.append(circle(bx + bw / 2, by, 10, fill=BG, stroke=INK, sw=2))
    f.append(text(bx + bw / 2, by + 34, "74×04", size=16, bold=True, color=INK))
    f.append(text(bx + bw / 2, by + 52, "6 × НЕ (інвертор)", size=10.5, color=MUTED))

    # 14 ніжок: 1..7 ліворуч зверху вниз, 8..14 праворуч знизу вгору
    pin_y = [by + 40 + i * 36 for i in range(7)]
    left_pins = {}
    right_pins = {}
    for i in range(7):
        n = i + 1
        y = pin_y[i]
        f.append(line(bx - 26, y, bx, y, color=INK, sw=2))
        f.append(text(bx - 32, y + 4, str(n), size=10, color=MUTED, anchor="end"))
        left_pins[n] = (bx - 26, y)
    for i in range(7):
        n = 14 - i
        y = pin_y[i]
        f.append(line(bx + bw, y, bx + bw + 26, y, color=INK, sw=2))
        f.append(text(bx + bw + 32, y + 4, str(n), size=10, color=MUTED, anchor="start"))
        right_pins[n] = (bx + bw + 26, y)

    # живлення по діагоналі: Vcc=14 (правий верхній), GND=7 (лівий нижній)
    vx, vy = right_pins[14]
    gx, gy = left_pins[7]
    f.append(line(vx, vy, vx + 90, vy, color=POS, sw=2.4))
    f.append(text(vx + 96, vy + 4, "Vcc (пін 14)", size=11, color=POS, bold=True, anchor="start"))
    f.append(line(gx, gy, gx - 90, gy, color=NEG, sw=2.4))
    f.append(text(gx - 96, gy + 4, "GND (пін 7)", size=11, color=NEG, bold=True, anchor="end"))
    # позначка діагоналі
    f.append(line(vx + 70, vy, vx + 70, 392, color=POS, sw=1.2, dash="4,4"))
    f.append(line(gx - 70, gy, gx - 70, 392, color=NEG, sw=1.2, dash="4,4"))
    f.append(text(W / 2, 404, "живлення — по діагоналі корпусу", size=11, color=INK, italic=True))

    # конденсатор розв'язки 0.1 мкФ між Vcc(14) і GND(7) — упритул
    cap_x = vx + 44
    f.append(line(cap_x, vy, cap_x, 190, color=POS, sw=1.6))
    f.append(line(cap_x - 14, 190, cap_x + 14, 190, color=INK, sw=2.6))   # пластина +
    f.append(line(cap_x - 14, 200, cap_x + 14, 200, color=INK, sw=2.6))   # пластина −
    f.append(line(cap_x, 200, cap_x, 250, color=NEG, sw=1.6))
    f.append(line(cap_x, 250, gx - 70, 250, color=NEG, sw=1.6))
    f.append(text(cap_x + 20, 196, "0.1 мкФ", size=10, color=INK, anchor="start"))
    f.append(text(cap_x + 20, 210, "розв'язка", size=9.5, color=MUTED, anchor="start"))

    # один інвертор у роботі: 1A (пін1) → 1Y (пін2)
    ax, ay = left_pins[1]
    yx, yy = left_pins[2]
    f.append(line(ax - 60, ay, ax, ay, color=FIELD, sw=2))
    f.append(text(ax - 66, ay + 4, "1A вхід", size=10.5, color=FIELD, bold=True, anchor="end"))
    f.append(line(yx - 60, yy, yx, yy, color=FIELD, sw=2))
    f.append(text(yx - 66, yy + 4, "1Y = NOT(1A)", size=10.5, color=FIELD, bold=True, anchor="end"))

    # невжиті входи — на шину
    b = fitbox(300, 388, 180, 34,
               "Невжиті входи\n2A…6A → GND чи Vcc",
               size=10, fill="#eef6ef", stroke=FIELD, sw=1.4)
    f.append(b)

    render(os.path.join(IMG, "dip14-wiring.svg"), W, H, *f)


# ── 4. Розсип деталей → один корпус: чому TTL-в-кристалі перемогла ────────────
# Ідея (для вставки hist): показати, що коштувало зібрати вентиль «з розсипу»
# (DTL: 7 деталей на ОДИН вентиль) проти одного чипа 7400 (4 вентилі в корпусі).
def fig_gate_collapse():
    W, H = 760, 300
    f = []

    # Ліворуч: DTL-вентиль із розсипу — 7 деталей на 1 вентиль
    lx, ly, lw, lh = 40, 66, 300, 176
    f.append(rect(lx, ly, lw, lh, fill="#fdf3f2", stroke=POS, sw=1.8, rx=10))
    f.append(text(lx + lw / 2, ly + 24, "«Розсип»: DTL-вентиль", size=14, color=POS, bold=True))
    f.append(text(lx + lw / 2, ly + 42, "1 вентиль І-НЕ = 7 деталей", size=11, color=INK))
    # 7 дискретних деталей значками: 3 діоди, 1 резистор, 1 транзистор, дротики
    parts_lbl = ["діод", "діод", "діод", "резистор", "транзистор", "+ пайка", "+ плата"]
    px = lx + 26
    py = ly + 74
    for i, lb in enumerate(parts_lbl):
        cx = px + (i % 4) * 68
        cy = py + (i // 4) * 46
        f.append(circle(cx, cy, 8, fill="#fff", stroke=POS, sw=1.6))
        f.append(text(cx, cy + 3, str(i + 1), size=9, color=POS, bold=True))
        f.append(text(cx, cy + 22, lb, size=9, color=MUTED))
    f.append(text(lx + lw / 2, ly + lh - 10,
                  "×4 вентилі = 28 деталей + 28 стиків", size=9.5, color=POS, italic=True))

    # Стрілка «в кристал»
    f.append(arrow(lx + lw + 12, H / 2, lx + lw + 74, H / 2, color=INK, sw=2.4))
    f.append(text(lx + lw + 43, H / 2 - 12, "у кристал", size=10.5, color=INK, bold=True))

    # Праворуч: один корпус 7400 — 4 вентилі всередині
    rx2, ry2, rw2, rh2 = lx + lw + 90, 66, 300, 176
    f.append(rect(rx2, ry2, rw2, rh2, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(rx2 + rw2 / 2, ry2 + 24, "Один чип: 7400", size=14, color=FIELD, bold=True))
    f.append(text(rx2 + rw2 / 2, ry2 + 42, "×4 вентилі І-НЕ у корпусі", size=11, color=INK))
    # маленький DIP із 4 значками вентилів
    dip_x = rx2 + 60
    dip_y = ry2 + 60
    f.append(rect(dip_x, dip_y, rw2 - 120, 70, fill="#eceff3", stroke=INK, sw=2, rx=8))
    for i in range(4):
        gx = dip_x + 26 + i * ((rw2 - 120 - 40) / 3)
        gy = dip_y + 35
        f.append(circle(gx, gy, 11, fill="#fff", stroke=FIELD, sw=1.8))
        f.append(text(gx, gy + 4, "&", size=12, color=FIELD, bold=True))
    f.append(text(rx2 + rw2 / 2, ry2 + rh2 - 10,
                  "1 деталь · 1 пайка · взаємозамінний у 10 фірм", size=9.5, color=FIELD, italic=True))

    render(os.path.join(IMG, "gate-collapse.svg"), W, H, *f,
           title="Чому логіка переселилася в кристал: 7 деталей на вентиль → 1 корпус")


# ── 5. Геологічні шари: ідея → патент → перша родина → масовий стандарт ───────
# Ідея (для вставки hist): показати ЧОТИРИ різні внески як шари, і що в літерах
# сучасних імен (LS→HC→HCT→LVC) закам'янілі покоління технологій.
def fig_strata():
    W, H = 760, 430
    f = []

    # Верхня стрічка: чотири різні ролі в народженні стандарту
    roles = [
        ("ІДЕЯ / НАЗВА", "Бісон, Fairchild\nбл. 9.03.1961\nназвав «TTL»", POS),
        ("ПАТЕНТ", "Б'юї, TRW\nподав 8.09.1961\nUS 3,283,170 (1966)", "#8e44ad"),
        ("ПЕРША РОДИНА", "Лонго, Sylvania\nSUHL, 1963\n→ ракета Phoenix", NEG),
        ("МАСОВИЙ СТАНДАРТ", "TI: 5400 (1964)\n7400 (1966)\n>50% ринку", FIELD),
    ]
    bx0, by0 = 20, 58
    bw = (W - 40 - 3 * 10) / 4
    bh = 92
    cx_list = []
    for i, (head, body, col) in enumerate(roles):
        x = bx0 + i * (bw + 10)
        f.append(rect(x, by0, bw, bh, fill="#fbfbfb", stroke=col, sw=2, rx=9))
        f.append(text(x + bw / 2, by0 + 20, head, size=11.5, color=col, bold=True))
        for j, ln in enumerate(body.split("\n")):
            f.append(text(x + bw / 2, by0 + 40 + j * 15, ln, size=9.5, color=INK))
        cx_list.append(x + bw / 2)
        if i < 3:
            f.append(arrow(x + bw + 1, by0 + bh / 2, x + bw + 9, by0 + bh / 2, color=MUTED, sw=1.8))

    # Підпис-міст: піонер ≠ переможець
    f.append(fitbox(90, by0 + bh + 16, W - 180, 30,
                    "Піонер (ідея й перша родина) ≠ переможець ринку (масовий, дешевий стандарт) — це РІЗНІ внески.",
                    size=11, fill="#fdf6e3", stroke=MUTED, sw=1.3))

    # Нижня частина: геологічні шари технологій, закам'янілі в літерах імені
    strata_y = by0 + bh + 66
    layers = [
        ("74  (1966)", "біполярний TTL — вихідний шар", "#a04000"),
        ("74LS (1971)", "TTL із діодами Шоткі — швидше, менше струму", "#b9770e"),
        ("74HC (1980-ті)", "CMOS: майже нуль струму в спокої", FIELD),
        ("74HCT (1980-ті)", "CMOS зі старим TTL-порогом на вході", NEG),
        ("74LVC (1990-ті)", "низька напруга 3.3 В, вхід терпить 5 В", "#8e44ad"),
    ]
    lh2 = 40
    lx2, lw2 = 60, W - 120
    f.append(text(W / 2, strata_y - 12,
                  "…а в літерах сучасного імені закам'яніли покоління технологій:",
                  size=11.5, color=INK, bold=True))
    for i, (tag, desc, col) in enumerate(layers):
        y = strata_y + i * lh2
        f.append(rect(lx2, y, lw2, lh2 - 6, fill="#fbfbfb", stroke=col, sw=1.6, rx=6))
        f.append(text(lx2 + 14, y + (lh2 - 6) / 2 + 5, tag, size=12.5, color=col, bold=True, anchor="start"))
        f.append(text(lx2 + 160, y + (lh2 - 6) / 2 + 5, desc, size=10.5, color=INK, anchor="start"))

    render(os.path.join(IMG, "strata.svg"), W, H, *f,
           title="Народження стандарту 74: чотири внески — і шари технологій у назві")


if __name__ == "__main__":
    fig_name_fields()
    fig_families_grid()
    fig_dip_wiring()
    fig_gate_collapse()
    fig_strata()
    print("OK: 5 figures ->", IMG)
