# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

GRN = "#eafaf0"   # заливка «власника» / об'єкта
RED = "#fdecea"   # заливка копії-правила


# ── 1. Дві осі організації логіки: за дією проти за річчю ────────────────────
def fig_logic_organization():
    W, H = 1140, 580
    f = []
    f.append(text(W / 2, 34, "Дві осі організації логіки: за дією проти за річчю", size=17, bold=True))

    DIV = 566
    f.append(line(DIV, 58, DIV, 524, color=MUTED, sw=1.2, dash="5 5"))

    # ══ ЛІВОРУЧ: сценарій транзакції — за дією ══
    f.append(text(285, 76, "СЦЕНАРІЙ ТРАНЗАКЦІЇ", size=14, color=FIELD, bold=True))
    f.append(text(285, 98, "логіка за дією — дієслово", size=11.5, color=MUTED, italic=True))

    scripts = [
        (52, "placeOrder", ["SELECT товар", "перевір склад", "INSERT замовлення", "UPDATE залишок"]),
        (192, "cancelOrder", ["SELECT замовлення", "перевір статус", "UPDATE «cancelled»", "поверни залишок"]),
        (332, "applyInterest", ["SELECT рахунок", "нарахуй відсоток", "UPDATE баланс"]),
    ]
    BW, BY, BH = 130, 122, 200
    for bx, name, steps in scripts:
        f.append(rect(bx, BY, BW, BH, fill=BG, stroke=FIELD, sw=1.8, rx=8))
        f.append(rect(bx, BY, BW, 30, fill=GRN, stroke=FIELD, sw=1.4, rx=8))
        f.append(text(bx + BW / 2, BY + 20, name, size=11.5, color=INK, bold=True))
        for i, s in enumerate(steps):
            f.append(text(bx + 12, BY + 54 + i * 24, s, size=11, color=INK, anchor="start"))

    # спільна база під трьома сценаріями
    DBX, DBW, DBY = 52, 410, 442
    f.append(rect(DBX, DBY, DBW, 46, fill=FILL, stroke=LINE, sw=1.6, rx=10))
    f.append(text(DBX + DBW / 2, DBY + 29, "база даних", size=13, color=INK, bold=True))
    for bx, _, _ in scripts:
        cx = bx + BW / 2
        f.append(arrow(cx, BY + BH + 4, cx, DBY - 4, color=MUTED, sw=1.7))
    f.append(text(285, 518, "кожен сценарій пірнає до бази сам — SQL напряму або крізь тонкий шлюз",
                  size=11.5, color=MUTED))

    # ══ ПРАВОРУЧ: предметна модель — за річчю ══
    f.append(text(852, 76, "ПРЕДМЕТНА МОДЕЛЬ", size=14, color=NEG, bold=True))
    f.append(text(852, 98, "логіка за річчю — іменник", size=11.5, color=MUTED, italic=True))

    def obj(cx, cy, name):
        w, h = 138, 62
        f.append(rect(cx - w / 2, cy - h / 2, w, h, fill=GRN, stroke=NEG, sw=1.9, rx=9))
        f.append(text(cx, cy - 6, name, size=13, color=INK, bold=True))
        f.append(text(cx, cy + 15, "дані + правила", size=10.5, color=MUTED))
        return (cx, cy, w, h)

    O = obj(852, 158, "Order")
    C = obj(688, 262, "Customer")
    P = obj(1016, 262, "Product")

    # зв'язки в мережу (лінії між об'єктами, повз написи)
    f.append(line(O[0] - 40, O[1] + 31, C[0] + 20, C[1] - 31, color=MUTED, sw=1.5))
    f.append(line(O[0] + 40, O[1] + 31, P[0] - 20, P[1] - 31, color=MUTED, sw=1.5))
    f.append(line(C[0] + 69, C[1], P[0] - 69, P[1], color=MUTED, sw=1.5))

    # збіжність до мапера
    f.append(line(C[0], C[1] + 31, 852, 336, color=MUTED, sw=1.3))
    f.append(line(P[0], P[1] + 31, 852, 336, color=MUTED, sw=1.3))
    f.append(arrow(852, 336, 852, 356, color=MUTED, sw=1.7))

    f.append(rect(742, 358, 220, 44, fill=FILL, stroke=MUTED, sw=1.5, rx=8))
    f.append(text(852, 378, "мапер даних", size=12.5, color=INK, bold=True))
    f.append(text(852, 395, "об'єкти ↔ таблиці", size=10.5, color=MUTED))

    f.append(arrow(852, 402, 852, 440, color=MUTED, sw=1.7))
    f.append(rect(762, 442, 180, 46, fill=FILL, stroke=LINE, sw=1.6, rx=10))
    f.append(text(852, 471, "база даних", size=13, color=INK, bold=True))
    f.append(text(852, 518, "правило живе в об'єкті-власнику — одна дорога до бази",
                  size=11.5, color=MUTED))

    render(os.path.join(OUT, 'logic-organization.svg'), W, H, *f)


# ── 2. Правило без власника розповзається копіями ───────────────────────────
def fig_duplication_smear():
    W, H = 1140, 560
    f = []
    f.append(text(W / 2, 34, "Правило без власника розповзається копіями", size=17, bold=True))

    DIV = 560
    f.append(line(DIV, 58, DIV, 520, color=MUTED, sw=1.2, dash="5 5"))

    # ══ ЛІВОРУЧ: три сценарії, у кожному — копія того самого правила ══
    f.append(text(282, 78, "СЦЕНАРІЙ ТРАНЗАКЦІЇ", size=14, color=FIELD, bold=True))
    f.append(text(282, 100, "те саме правило — три копії", size=11.5, color=MUTED, italic=True))

    names = ["placeOrder", "changeQty", "reorder"]
    BX, BW, BH = 46, 468, 108
    for i, nm in enumerate(names):
        by = 122 + i * 122
        f.append(rect(BX, by, BW, BH, fill=BG, stroke=FIELD, sw=1.7, rx=8))
        f.append(text(BX + 16, by + 24, nm + "( ):", size=11.5, color=INK, anchor="start", bold=True))
        # виділена копія правила
        f.append(rect(BX + 28, by + 38, BW - 56, 56, fill=RED, stroke=POS, sw=1.7, rx=6))
        f.append(text(BX + 44, by + 60, "discount = loyalty(customer)", size=11, color=INK, anchor="start"))
        f.append(text(BX + 44, by + 82, "total = price·qty·(1 − discount) + tax", size=11, color=INK, anchor="start"))

    f.append(text(282, 512, "зміна правила → правити в КОЖНОМУ сценарії", size=12.5, color=POS, bold=True))

    # ══ ПРАВОРУЧ: один власник, три однакові виклики ══
    f.append(text(838, 78, "ПРЕДМЕТНА МОДЕЛЬ", size=14, color=NEG, bold=True))
    f.append(text(838, 100, "те саме правило — один власник", size=11.5, color=MUTED, italic=True))

    # об'єкт-власник
    OX, OW, OY, OH = 706, 268, 138, 108
    f.append(rect(OX, OY, OW, OH, fill=GRN, stroke=FIELD, sw=2, rx=10))
    f.append(text(OX + OW / 2, OY + 26, "Order", size=13.5, color=INK, bold=True))
    f.append(rect(OX + 18, OY + 40, OW - 36, 52, fill=BG, stroke=FIELD, sw=1.4, rx=6))
    f.append(text(OX + OW / 2, OY + 62, "знижка · податок · склад", size=11.5, color=INK, bold=True))
    f.append(text(OX + OW / 2, OY + 82, "правило тут — один раз", size=11, color=MUTED))

    # три виклики знизу
    callers = [(640, "placeOrder"), (838, "changeQty"), (1036, "reorder")]
    CY, CBW = 402, 150
    for cx, nm in callers:
        f.append(rect(cx - CBW / 2, CY, CBW, 44, fill=FILL, stroke=MUTED, sw=1.5, rx=8))
        f.append(text(cx, CY + 27, nm, size=11.5, color=INK, bold=True))
        # стрілка вгору до власника
        tx0 = OX + OW / 2 + (cx - 838) * 0.42
        f.append(arrow(cx, CY - 4, tx0, OY + OH + 4, color=MUTED, sw=1.6))

    f.append(text(838, 512, "зміна правила → одне місце", size=12.5, color=FIELD, bold=True))

    render(os.path.join(OUT, 'duplication-smear.svg'), W, H, *f)


# ── 3. Практика на сорок років старша за назву (стрічка часу) ────────────────
def fig_practice_before_name():
    W, H = 1180, 384
    f = []
    AX_Y = 250

    # вісь часу
    f.append(line(120, AX_Y, 1050, AX_Y, color=INK, sw=2))
    f.append(arrow(1050, AX_Y, 1074, AX_Y, color=INK, sw=2))
    f.append(text(1066, AX_Y - 12, "час", size=12, color=MUTED, anchor="end", italic=True))

    # віхи: (x, рік, рядок1, рядок2, ярус)
    ms = [
        (185,  "1959",    "COBOL і RPG",           "пакет: читати · рахувати · писати", 1),
        (545,  "1982",    "клієнт-серверні 4GL",   "«4GL» — термін Дж. Мартіна",        2),
        (765,  "1991–92", "PL/SQL",                "збережені процедури (Oracle)",      1),
        (1000, "2002",    "«Сценарій транзакції»", "Фаулер, PoEAA",                     2),
    ]
    for x, yr, l1, l2, tier in ms:
        cy = 98 if tier == 1 else 176
        green = (yr == "2002")
        frag, w, h = textbox(x, cy, l1 + "\n" + l2, size=11, pad=9,
                             fill=("#eafaf0" if green else BG),
                             stroke=(FIELD if green else MUTED),
                             sw=(1.9 if green else 1.4),
                             color=INK, bold=green)
        f.append(frag)
        f.append(line(x, cy + h / 2, x, AX_Y - 6, color=MUTED, sw=1.2))
        f.append(circle(x, AX_Y, 7 if green else 5,
                        fill=(FIELD if green else INK), stroke=(FIELD if green else INK)))
        f.append(text(x, AX_Y + 22, yr, size=11.5,
                      color=(FIELD if green else MUTED), bold=green))

    # дужка «розрив у сорок з гаком років»
    bx0, bx1, by = 185, 1000, 300
    f.append(line(bx0, by, bx1, by, color=MUTED, sw=1.4))
    f.append(line(bx0, by, bx0, by - 8, color=MUTED, sw=1.4))
    f.append(line(bx1, by, bx1, by - 8, color=MUTED, sw=1.4))
    f.append(text((bx0 + bx1) / 2, by + 20,
                  "≈ 43 роки: сценарій транзакції — беззаперечна звичка, ще без назви",
                  size=12.5, color=MUTED, italic=True))

    f.append(text(W / 2, 352,
                  "Назва не створила практику — вона зробила її видимою і свідомим вибором поряд із предметною моделлю.",
                  size=12, color=INK))

    render(os.path.join(OUT, 'practice-before-name.svg'), W, H, *f,
           title="Практика — на сорок років старша за свою назву")


# ── 4. Три стадії однієї логіки: копії → функція → власник ───────────────────
def fig_rescue_ladder():
    W, H = 1200, 560
    f = []
    f.append(text(W / 2, 34, "Три стадії однієї логіки ціни", size=17, bold=True))
    for dx in (400, 800):
        f.append(line(dx, 172, dx, 470, color=MUTED, sw=1.1, dash="5 5"))

    names = ["placeOrder", "changeQty", "reorder"]

    # ══ СТАДІЯ 0 · КОПІЇ (центр 200) ══
    f.append(text(200, 80, "СТАДІЯ 0 · КОПІЇ", size=13, color=POS, bold=True))
    f.append(text(200, 99, "копії правила розійшлися", size=10.5, color=MUTED, italic=True))
    chips0 = ["знижка · податок · поріг", "знижка · податок", "знижка"]
    for i, (nm, ch) in enumerate(zip(names, chips0)):
        by = 118 + i * 72
        f.append(rect(92, by, 216, 58, fill=BG, stroke=FIELD, sw=1.5, rx=8))
        f.append(text(104, by + 20, nm, size=11, color=INK, anchor="start", bold=True))
        f.append(fitbox(104, by + 28, 192, 22, ch, size=10, pad=6,
                        fill=RED, stroke=POS, sw=1.2, rx=4))
    f.append(fitbox(58, 402, 284, 46, "1 правка правила → 3 місця, одне забуто",
                    size=11, pad=8, fill=RED, stroke=POS, sw=1.4, bold=True, color=POS, rx=8))

    # перехід 0→1
    f.append(arrow(370, 232, 428, 232, color=INK, sw=2))
    f.append(mtext(400, 150, ["копії", "розходяться"], size=10.5, color=MUTED))

    # ══ СТАДІЯ 1 · СПІЛЬНА ФУНКЦІЯ (центр 600) ══
    f.append(text(600, 80, "СТАДІЯ 1 · СПІЛЬНА ФУНКЦІЯ", size=13, color=NEG, bold=True))
    f.append(text(600, 99, "копії зійшлися в одну функцію", size=10.5, color=MUTED, italic=True))
    for i, nm in enumerate(names):
        cy = 150 + i * 60
        f.append(rect(446, cy - 19, 132, 38, fill=BG, stroke=MUTED, sw=1.3, rx=7))
        f.append(text(512, cy + 4, nm, size=10.5, color=INK, bold=True))
        f.append(arrow(580, cy, 636, 210, color=MUTED, sw=1.5))
    f.append(rect(638, 150, 134, 120, fill=FILL, stroke=NEG, sw=1.9, rx=9))
    f.append(text(705, 200, "priceOrder()", size=12, color=INK, bold=True))
    f.append(text(705, 224, "правило", size=10.5, color=MUTED))
    f.append(text(705, 242, "1 копія", size=10.5, color=MUTED))
    f.append(fitbox(464, 402, 280, 46, "хвіст параметрів росте; правило можна оминути",
                    size=10.5, pad=8, fill=FILL, stroke=MUTED, sw=1.3, color=INK, rx=8))

    # перехід 1→2
    f.append(arrow(776, 232, 830, 232, color=INK, sw=2))
    f.append(mtext(800, 150, ["функція", "обростає"], size=10.5, color=MUTED))

    # ══ СТАДІЯ 2 · ВЛАСНИК (центр 1000) ══
    f.append(text(1000, 80, "СТАДІЯ 2 · ВЛАСНИК", size=13, color=FIELD, bold=True))
    f.append(text(1000, 99, "правило й дані зрослися в об'єкт", size=10.5, color=MUTED, italic=True))
    for i, nm in enumerate(names):
        cy = 150 + i * 60
        f.append(rect(846, cy - 19, 132, 38, fill=BG, stroke=MUTED, sw=1.3, rx=7))
        f.append(text(912, cy + 4, nm, size=10.5, color=INK, bold=True))
        f.append(arrow(980, cy, 1036, 210, color=MUTED, sw=1.5))
    f.append(rect(1038, 150, 130, 120, fill=GRN, stroke=FIELD, sw=2, rx=9))
    f.append(text(1103, 196, "Order", size=12.5, color=INK, bold=True))
    f.append(text(1103, 220, "правило", size=10.5, color=MUTED))
    f.append(text(1103, 240, "інваріант ✓", size=10.5, color=FIELD, bold=True))
    f.append(fitbox(864, 402, 280, 46, "інваріант — у конструкторі, оминути нічим",
                    size=10.5, pad=8, fill=GRN, stroke=FIELD, sw=1.4, color=INK, rx=8))

    render(os.path.join(OUT, 'rescue-ladder.svg'), W, H, *f)


if __name__ == '__main__':
    fig_logic_organization()
    fig_duplication_smear()
    fig_practice_before_name()
    fig_rescue_ladder()
    print("figures written to", OUT)
