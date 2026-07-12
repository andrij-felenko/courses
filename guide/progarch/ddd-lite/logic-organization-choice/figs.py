# -*- coding: utf-8 -*-
"""Фігури до кроку «Вибір: як організувати логіку домену»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_where_logic_lives():
    """Три способи поруч: де стоїть правило відносно даних."""
    W, H = 1040, 470
    frags = []

    # вертикальні розділювачі між панелями
    for sx in (348, 692):
        frags.append(line(sx, 50, sx, 452, color=MUTED, sw=1, dash="4,5"))

    cxL, cxM, cxR = 174, 520, 866

    # заголовки панелей
    frags.append(text(cxL, 70, "Сценарій-транзакція", size=15, bold=True))
    frags.append(text(cxM, 70, "Анемічна модель", size=15, bold=True))
    frags.append(text(cxR, 70, "Багата модель", size=15, bold=True))

    # ── Ліва: правило в процедурі (окремо, відверто) ──
    b, _, _ = textbox(cxL, 150, "commission_device()\nправило переходу — тут",
                      size=13, fill="#fdecea", stroke=POS, min_w=190)
    frags.append(b)
    frags.append(arrow(cxL, 188, cxL, 300, color=LINE, sw=2))
    frags.append(text(cxL + 16, 248, "читає / пише", size=11, color=MUTED, anchor="start"))
    b, _, _ = textbox(cxL, 332, "рядок у базі\nпласкі поля", size=13, fill="#eef2f6", min_w=190)
    frags.append(b)
    frags.append(text(cxL, 420, "правило й дані — нарізно (відверто)", size=11, color=MUTED))

    # ── Середня: правило в сервісі (окремо, за спиною мішка) ──
    b, _, _ = textbox(cxM, 150, "Device\nstatus, home — навстіж",
                      size=13, fill=FILL, stroke=MUTED, min_w=200)
    frags.append(b)
    frags.append(arrow(cxM, 300, cxM, 190, color=POS, sw=2))
    frags.append(text(cxM + 18, 248, "порпає поля", size=11, color=MUTED, anchor="start"))
    b, _, _ = textbox(cxM, 332, "DeviceService\nправило переходу",
                      size=13, fill="#fdecea", stroke=POS, min_w=200)
    frags.append(b)
    frags.append(text(cxM, 420, "правило й дані — теж нарізно (за спиною мішка)", size=11, color=MUTED))

    # ── Права: дані + правило за однією зеленою стіною ──
    frags.append(text(cxR, 118, "ззовні лише наказ", size=11, color=MUTED))
    frags.append(text(cxR, 134, "commission()", size=12, color=NEG, bold=True))
    frags.append(arrow(cxR, 146, cxR, 214, color=NEG, sw=2.2))
    b, _, _ = textbox(cxR, 274, "Device\nдані: status, home (закриті)\nправило: вартовий переходу",
                      size=13, fill="#eafaf0", stroke=FIELD, sw=2.6, min_w=230)
    frags.append(b)
    frags.append(text(cxR, 392, "дані + правило за однією стіною", size=11, color=MUTED))
    frags.append(text(cxR, 410, "неможливий стан нема звідки взяти", size=11, color=FIELD))

    render(os.path.join(IMG, "where-logic-lives.svg"), W, H, *frags,
           title="Де живе правило — при даних чи окремо")


def fig_invariants_axis():
    """Вісь «скільки інваріантів над даними»: поріг ділить зони способів."""
    W, H = 1020, 430
    frags = []

    thr = 520          # поріг
    band_top, band_bot = 108, 356
    axis_y = 244

    # зони-смуги
    frags.append(rect(78, band_top, thr - 78, band_bot - band_top,
                      fill="#eef2fb", stroke="none", sw=0, rx=10))
    frags.append(rect(thr, band_top, 942 - thr, band_bot - band_top,
                      fill="#eef7f0", stroke="none", sw=0, rx=10))

    # поріг
    frags.append(line(thr, 96, thr, 368, color=MUTED, sw=1.6, dash="5,5"))
    frags.append(text(thr, 90, "поріг", size=12, color=MUTED, bold=True))

    # вісь
    frags.append(arrow(108, axis_y, 906, axis_y, color=LINE, sw=1.8))

    # заголовки зон
    frags.append(mtext(292, 150, ["мало правил над даними", "проста процедура чесна"],
                       size=13, color=INK, bold=True, lh=1.35))
    frags.append(mtext(726, 150, ["багато правил, ще й ростуть", "правило шукає дім в об'єкті"],
                       size=13, color=INK, bold=True, lh=1.35))

    # маркери-контексти DH ліворуч
    for cx, label in [(178, "довідник\nпристроїв"), (312, "версії\nпрошивок"), (438, "звіти")]:
        b, _, h = textbox(cx, 312, label, size=12, fill="#ffffff", min_w=96)
        frags.append(line(cx, 262, cx, 312 - h / 2, color=MUTED, sw=1.3))
        frags.append(circle(cx, axis_y, 5, fill="#ffffff", stroke=NEG, sw=2))
        frags.append(b)

    # маркер-контекст DH праворуч (переможець зони)
    b, _, h = textbox(712, 312, "життєвий цикл пристрою\n(автомат станів)",
                      size=12, fill="#eafaf0", stroke=FIELD, sw=2, min_w=200)
    frags.append(line(712, 262, 712, 312 - h / 2, color=MUTED, sw=1.3))
    frags.append(circle(712, axis_y, 5, fill="#eafaf0", stroke=FIELD, sw=2.4))
    frags.append(b)

    # підпис осі та межі
    frags.append(text(500, 392, "вісь: скільки інваріантів (правил) мусять тримати ці дані  →",
                      size=12, color=MUTED))
    frags.append(text(500, 412, "де саме проходить поріг — вирішує стратегічний розкрій",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "invariants-axis.svg"), W, H, *frags,
           title="Переможця в порожнечі нема — є поріг за кількістю правил")


def fig_naming_map():
    """Історія назв: трійка Фаулера (2002) → трійка сьогодні; TM випадає, анемічна входить."""
    W, H = 1200, 566
    frags = []

    xL, xR = 250, 830
    ys = [152, 288, 418]

    # заголовки колонок
    frags.append(mtext(xL, 66, ["Що назвав Фаулер", "PoEAA · листопад 2002"],
                       size=14, color=NEG, bold=True, lh=1.3))
    frags.append(text(xR, 70, "Трійка, якою вчать сьогодні", size=14, color=FIELD, bold=True))

    # ── ліва колонка: трійка Фаулера ──
    bTS, _, _ = textbox(xL, ys[0], "Transaction Script\n(логіка — процедура)",
                        size=13, fill=FILL, stroke=NEG, min_w=224)
    bDM, _, _ = textbox(xL, ys[1], "Domain Model\n(дані + поведінка разом)",
                        size=13, fill=FILL, stroke=NEG, min_w=224)
    bTM, _, hTM = textbox(xL, ys[2], "Table Module\n(об'єкт на всю таблицю)",
                          size=13, fill="#eef0f2", stroke=MUTED, color=MUTED, min_w=224)
    frags += [bTS, bDM, bTM]

    # ── права колонка: трійка сьогодні ──
    rST, _, _ = textbox(xR, ys[0], "Сценарій-транзакція", size=13, fill=FILL, stroke=NEG, min_w=244)
    rRM, _, _ = textbox(xR, ys[1], "Багата модель\n(Еванс, DDD · серпень 2003)",
                        size=13, fill="#eafaf0", stroke=FIELD, min_w=244)
    rAM, _, hAM = textbox(xR, ys[2], "Анемічна модель\n(есей · 25 листопада 2003)",
                          size=13, fill="#fdecea", stroke=POS, min_w=244)
    frags += [rST, rRM, rAM]

    xLe, xRe = xL + 112, xR - 122     # праві/ліві краї колонок
    mid = (xL + xR) / 2

    # рядок 1: та сама
    frags.append(arrow(xLe, ys[0], xRe, ys[0], color=LINE, sw=1.8))
    frags.append(text(mid, ys[0] - 14, "та сама — просто укр. назва", size=12, color=MUTED))

    # рядок 2: Еванс поглибив
    frags.append(arrow(xLe, ys[1], xRe, ys[1], color=FIELD, sw=2.3))
    frags.append(text(mid, ys[1] - 30, "Еванс дав їй глибину:", size=12, color=FIELD, bold=True))
    frags.append(text(mid, ys[1] - 14, "мова, сутності, агрегати", size=12, color=MUTED))

    # рядок 3: без відповідника — TM випадає, анемічна посіла місце
    frags.append(mtext(mid, ys[2] - 16, ["(без відповідника:", "місце звільнилось, зайняла інша)"],
                       size=12, color=MUTED, lh=1.3))
    # TM тьмяніє й випадає вниз
    frags.append(arrow(xL, ys[2] + hTM / 2 + 8, xL, ys[2] + hTM / 2 + 52, color=MUTED, sw=1.6))
    frags.append(mtext(xL, ys[2] + hTM / 2 + 72, ["тьмяніє й випадає з трійки",
                       "(артефакт ери .NET DataSet)"], size=11, color=MUTED, lh=1.3))
    # анемічна — новоприбула
    frags.append(text(xR, ys[2] + hAM / 2 + 20, "новий патерн-засторога", size=11, color=POS))

    # ── дужка тотожності: Сценарій-транзакція ≡ Анемічна (Фаулер сам зв'язав) ──
    xb = 986
    frags.append(line(xR + 122, ys[0], xb, ys[0], color=INK, sw=1.4))
    frags.append(line(xR + 122, ys[2], xb, ys[2], color=INK, sw=1.4))
    frags.append(line(xb, ys[0], xb, ys[2], color=INK, sw=1.4))
    frags.append(circle(xb, ys[1], 4, fill=INK, stroke=INK))
    frags.append(line(xb, ys[1], xb + 12, ys[1], color=INK, sw=1.4))
    frags.append(mtext(xb + 18, ys[1] - 30,
                       ["Той самий «окремо».", "Фаулер сам зв'язав:", "анемічна модель —",
                        "«по суті Transaction", "Script» (лист. 2003)"],
                       size=12, color=INK, anchor="start", lh=1.34))

    render(os.path.join(IMG, "naming-and-swap.svg"), W, H, *frags,
           title="Як народилися назви — і як трійка змінила склад")


if __name__ == "__main__":
    fig_where_logic_lives()
    fig_invariants_axis()
    fig_naming_map()
    print("OK: figures written to", IMG)
