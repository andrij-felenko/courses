# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: ціна на ціннику проти повної вартості володіння (айсберг) ──────
def fig_iceberg():
    W, H = 1000, 560
    els = []
    els.append(text(W/2, 30, "Ціна купівлі — верхівка; вартість живе під водою", size=16, bold=True))

    # лінія води
    water_y = 150
    els.append(line(60, water_y, W-60, water_y, color=NEG, sw=2, dash="7,5"))
    els.append(text(W-64, water_y-9, "видно при купівлі", size=12, anchor="end", color=NEG, italic=True))
    els.append(text(64, water_y+17, "прихована вартість володіння", size=12, anchor="start", color=MUTED, italic=True))

    # верхівка — над водою (ліцензія / розробка)
    tip, tw, th = textbox(W/2, 102, "ціна купівлі / ліцензія\n(те, що в рахунку)", size=13, bold=True,
                          min_w=280, fill="#eef4ff", stroke=NEG)
    els.append(tip)

    # чотири підводні відра — окремими коробками, з великими проміжками
    by = 258
    buckets = [
        (185, "ПОБУДУВАТИ", "розробка, інтеграція,\nміграція, навчання"),
        (415, "ЕКСПЛУАТУВАТИ", "сервери, трафік,\nчергування, підтримка"),
        (630, "МІНЯТИ", "правки, зчеплення,\nтехнічний борг"),
        (835, "ВИЙТИ", "переписати, вивезти\nдані, розірвати замок"),
    ]
    for bx, cap, body in buckets:
        b, bw, bh = textbox(bx, by, cap, size=13, bold=True, min_w=175,
                            fill="#f7f7f7", stroke=FIELD, color=FIELD)
        els.append(b)
        b2, bw2, bh2 = textbox(bx, by + 74, body, size=12, min_w=180, fill=FILL)
        els.append(b2)

    els.append(text(W/2, H-18, "рішення порівнюють за сумою всіх чотирьох за весь строк життя, а не за верхівкою",
                    size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, 'iceberg.svg'), W, H, *els)


# ── Фігура 2: вартість — атрибут, що воює з рештою ───────────────────────────
def fig_tension():
    W, H = 820, 470
    els = []
    els.append(text(W/2, 30, "Вартість — не окрема графа, а атрибут у спільному натягу", size=16, bold=True))

    # центр — «вартість»
    cx, cy = W/2, 250
    c, cw, ch = textbox(cx, cy, "ВАРТІСТЬ", size=17, bold=True, min_w=170,
                        fill="#eafaf0", stroke=FIELD, color=FIELD)
    els.append(c)

    # чотири атрибути навколо, кожен тягне вартість угору
    spokes = [
        (cx, 95,  "доступність", "резерв, репліки,\nчергування 24/7"),
        (W-140, cy, "продуктивність", "більше ядер,\nкеш, ширший канал"),
        (cx, 405, "безпека", "шифрування, аудит,\nключі, перевірки"),
        (140, cy, "змінюваність", "абстракції, шари,\nточки розширення"),
    ]
    for sx, sy, name, body in spokes:
        b, bw, bh = textbox(sx, sy, name, size=13, bold=True, min_w=150, fill="#eef4ff", stroke=NEG)
        els.append(b)
        # маленький підпис ціни — зміщений НАЗОВНІ, щоб не накрити лінію
        if sy < cy:      ty = sy - 32
        elif sy > cy:    ty = sy + 34
        else:            ty = sy + 40
        els.append(text(sx, ty, body.replace("\n", "  "), size=10.5, color=MUTED, italic=True))
        # двобічна стрілка «тягне вартість» (від краю коробки до краю центру)
        els.append(arrow(sx, sy, cx, cy, color=POS, sw=1.6))

    els.append(text(W/2, H-16, "кожен «покращ мене» тягне вартість угору — тому її ставлять у той самий натяг, що й решту",
                    size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, 'tension.svg'), W, H, *els)


# ── Фігура 3: вартість як сценарій із числом і порогом (бюджет) ──────────────
def fig_budget_scenario():
    W, H = 940, 320
    els = []
    els.append(text(W/2, 30, "Вартість стає вимогою лише як сценарій із числом і порогом", size=16, bold=True))

    # ланцюг зліва направо: турбота → число на місяць → поріг → вирок
    y = 150
    b1, w1, h1 = textbox(150, y, "турбота власника:\n«щоб не розорило»", size=13,
                         min_w=230, fill="#f7f7f7")
    els.append(b1)

    b2, w2, h2 = textbox(410, y, "сценарій із числом:\n≤ 0.002 $ на активного\nкористувача на місяць", size=13,
                         bold=True, min_w=280, fill="#eef4ff", stroke=NEG)
    els.append(b2)
    els.append(arrow(150 + w1/2, y, 410 - w2/2, y))

    b3, w3, h3 = textbox(720, y - 46, "поріг бюджету:\n2000 $ / міс на 1 млн", size=12,
                         bold=True, min_w=230, fill="#fff8e1", stroke="#b8860b")
    els.append(b3)
    b4, w4, h4 = textbox(720, y + 52, "прикидка: 1800 $ →\nВЛАЗИТЬ (запас ×1.1)", size=12,
                         bold=True, min_w=230, fill="#eafaf0", stroke=FIELD, color=FIELD)
    els.append(b4)
    els.append(arrow(410 + w2/2, y, 720 - w3/2, y - 40))
    els.append(arrow(410 + w2/2, y, 720 - w4/2, y + 46))

    els.append(text(W/2, H-16, "без числа «дешево» не перевіриш і не автоматизуєш; з числом — його стереже машина, а не пам'ять",
                    size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, 'budget-scenario.svg'), W, H, *els)


if __name__ == '__main__':
    fig_iceberg()
    fig_tension()
    fig_budget_scenario()
    print("figs done")
