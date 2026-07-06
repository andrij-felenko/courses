# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: доступність = частка часу вгору; MTBF vs MTTR ──────────────────
def fig_mtbf():
    W, H = 900, 300
    frags = []
    y = 150            # рівень «вгору»
    down = 210         # рівень «лежить»
    x0, x1 = 70, W - 40

    # смуга життя системи: довгі відрізки «вгору» і короткі провали «лежить»
    segs = [
        (70, 300, "up"),
        (300, 350, "down"),
        (350, 620, "up"),
        (620, 655, "down"),
        (655, 860, "up"),
    ]
    for a, b, st in segs:
        yy = y if st == "up" else down
        col = FIELD if st == "up" else POS
        frags.append(line(a, yy, b, yy, color=col, sw=5))
        # вертикальні переходи між рівнями
    for a, b, st in segs:
        # з'єднати кінець одного з початком наступного вертикаллю
        pass
    # вертикалі падінь/підйомів
    frags.append(line(300, y, 300, down, color=MUTED, sw=1.4, dash="3,3"))
    frags.append(line(350, down, 350, y, color=MUTED, sw=1.4, dash="3,3"))
    frags.append(line(620, y, 620, down, color=MUTED, sw=1.4, dash="3,3"))
    frags.append(line(655, down, 655, y, color=MUTED, sw=1.4, dash="3,3"))

    # підписи рівнів ліворуч (поза лініями)
    frags.append(text(x0 - 6, y + 5, "вгору", size=12, bold=True, color=FIELD, anchor="end"))
    frags.append(text(x0 - 6, down + 5, "лежить", size=12, bold=True, color=POS, anchor="end"))

    # MTBF: дужка над довгим «вгору» відрізком (655→860 задовгий, беремо 350→620)
    frags.append(line(350, 108, 620, 108, color=NEG, sw=1.6))
    frags.append(line(350, 108, 350, 128, color=NEG, sw=1.6))
    frags.append(line(620, 108, 620, 128, color=NEG, sw=1.6))
    mb, mbw, mbh = textbox(485, 92, "MTBF — довго працює до відмови", size=12, bold=True,
                           fill="#eef4ff", stroke=NEG, sw=1.6, pad=7)
    frags.append(mb)

    # MTTR: дужка під коротким провалом 620→655
    frags.append(line(620, 250, 655, 250, color=POS, sw=1.6))
    frags.append(line(620, 232, 620, 250, color=POS, sw=1.6))
    frags.append(line(655, 232, 655, 250, color=POS, sw=1.6))
    rb, rbw, rbh = textbox(637, 278, "MTTR — швидко підняли", size=12, bold=True,
                           fill="#fdecea", stroke=POS, sw=1.6, pad=7)
    frags.append(rb)

    render(os.path.join(IMG, 'mtbf-mttr.svg'), W, H, *frags,
           title="Доступність = MTBF / (MTBF + MTTR)")


# ── Фігура 2: канонічне дерево тактик доступності ───────────────────────────
def fig_tree():
    W, H = 960, 470
    frags = []
    root, rw, rh = textbox(W / 2, 66, "Утримати доступність попри збій", size=16, bold=True,
                           fill="#eef4ff", stroke=NEG, sw=2, pad=14)
    frags.append(root)

    cols = [
        ("Виявити\nзбій", ["ping / echo", "серцебиття (heartbeat)", "таймаут", "виняток", "самоперевірка"], NEG),
        ("Оговтатись:\nпідготовка й ремонт",
         ["резерв гарячий / теплий / холодний", "перемкнутись (failover)", "повтор (retry)", "відкат (rollback)", "деградація"], FIELD),
        ("Оговтатись:\nповернення в лад", ["ресинхронізація стану", "тіньовий режим (shadow)", "східчастий рестарт"], "#5aa469"),
        ("Не допустити\nзбою", ["зняти вузол із ротації", "транзакція", "монітор процесу"], POS),
    ]
    n = len(cols)
    colw = W / n
    top_y = 172
    for i, (head, items, col) in enumerate(cols):
        cx = colw * i + colw / 2
        frags.append(line(W / 2, 66 + rh / 2, cx, top_y - 28, color=MUTED, sw=1.4))
        hb, hw, hh = textbox(cx, top_y, head, size=13.5, bold=True, fill="#fbfbfb",
                             stroke=col, sw=2, pad=9, min_w=colw - 30)
        frags.append(hb)
        yy = top_y + hh / 2 + 24
        for it in items:
            ib = fitbox(cx - (colw - 30) / 2, yy, colw - 30, 34, it, size=11.5,
                        fill=FILL, stroke=col, sw=1.3)
            frags.append(ib)
            yy += 42
    render(os.path.join(IMG, 'tactic-tree.svg'), W, H, *frags,
           title="Три родини тактик доступності")


# ── Фігура 3: драбина резерву — ціна проти часу відновлення ──────────────────
def fig_redundancy():
    W, H = 900, 380
    frags = []
    # три рядки: гарячий / теплий / холодний
    rows = [
        ("Гарячий резерв", "запасний працює й рахує те саме в реальному часі",
         "мілісекунди", "найдорожче: подвійне залізо весь час", POS, 250),
        ("Теплий резерв", "запасний увімкнений, але лише отримує стан, не рахує",
         "секунди", "дешевше: залізо є, але простоює", MUTED, 175),
        ("Холодний резерв", "запасний вимкнений; вмикають і піднімають стан після збою",
         "хвилини", "найдешевше: залізо чекає вимкненим", FIELD, 100),
    ]
    box_x, box_w = 40, 470
    row_h = 78
    for i, (nm, desc, trec, cost, col, barlen) in enumerate(rows):
        yy = 70 + i * (row_h + 18)
        frags.append(rect(box_x, yy, box_w, row_h, fill=FILL, stroke=col, sw=1.7, rx=8))
        frags.append(text(box_x + 16, yy + 26, nm, size=14, bold=True, color=INK, anchor="start"))
        frags.append(text(box_x + 16, yy + 48, desc, size=11, color=MUTED, anchor="start"))
        frags.append(text(box_x + 16, yy + 66, cost, size=10.5, color=col, anchor="start", italic=True))
        # стовпчик «час відновлення» праворуч
        bx = box_x + box_w + 40
        frags.append(rect(bx, yy + row_h / 2 - 13, barlen, 26, fill=col, stroke=col, sw=1, rx=5))
        frags.append(text(bx + barlen + 10, yy + row_h / 2 + 5, trec, size=12, bold=True,
                          color=INK, anchor="start"))

    # осьовий підпис праворуч
    frags.append(text(box_x + box_w + 40, 52, "час на відновлення →", size=12, bold=True,
                      color=MUTED, anchor="start"))
    render(os.path.join(IMG, 'redundancy-ladder.svg'), W, H, *frags,
           title="Резерв: що тепліший, то швидше відновлення — і дорожче")


# ── Фігура 4: скінченний автомат перемикання (для вставки proj) ──────────────
def fig_failover_fsm():
    W, H = 1060, 540
    frags = []

    # чотири стани по колу; координати центрів рознесені з ЗАПАСОМ
    states = {
        "ACTIVE":   (215, 150, "ГОЛОВНИЙ\n(працює, пише)", FIELD),
        "PROBATION":(785, 150, "НА ПІДОЗРІ\nпропуски ростуть", POS),
        "PROMOTE":  (785, 400, "ПІДНЯВСЯ\nрезерв — новий головний", NEG),
        "REJOIN":   (215, 400, "ПОВЕРНЕННЯ\nстарий доганяє стан", MUTED),
    }
    boxes = {}
    for k, (cx, cy, label, col) in states.items():
        b, w, h = textbox(cx, cy, label, size=13.5, bold=True, fill="#fbfbfb",
                          stroke=col, sw=2.2, pad=13, min_w=220)
        boxes[k] = (cx, cy, w, h, col)
        frags.append(b)

    # ребро: лінію ведемо від краю до краю, а підпис ставимо ЗБОКУ (ox,oy)
    # від середини — щоб напис НЕ лежав на лінії.
    def edge(a, bkey, label, col, ox=0, oy=0):
        import math
        ax, ay, aw, ah, _ = boxes[a]
        bx, by, bw, bh, _ = boxes[bkey]
        dx, dy = bx - ax, by - ay
        d = math.hypot(dx, dy) or 1
        x1 = ax + dx / d * (aw / 2 + 6)
        y1 = ay + dy / d * (ah / 2 + 6)
        x2 = bx - dx / d * (bw / 2 + 10)
        y2 = by - dy / d * (bh / 2 + 10)
        frags.append(arrow(x1, y1, x2, y2, color=col, sw=2))
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        lb, lw, lh = textbox(mx + ox, my + oy, label, size=11, fill="#ffffff",
                             stroke=col, sw=1.3, pad=6, color=INK)
        frags.append(lb)

    # два горизонтальні ребра між ГОЛОВНИЙ і НА ПІДОЗРІ — підписи вгору/вниз
    edge("ACTIVE", "PROBATION", "пропущено удар", POS, oy=-30)
    edge("PROBATION", "ACTIVE", "удар повернувся\n(лічильник у нуль)", FIELD, oy=40)
    # вертикальне ребро праворуч: підпис відсунуто ПРАВОРУЧ від лінії (x=785)
    edge("PROBATION", "PROMOTE", "MISS_LIMIT досягнуто\nТА взяв оренду / кворум", NEG, ox=150)
    # нижнє горизонтальне ребро: підпис під лінією
    edge("PROMOTE", "REJOIN", "старий ожив,\nпобачив свіжий токен", MUTED, oy=42)
    # вертикальне ребро ліворуч: підпис відсунуто ЛІВОРУЧ від лінії (x=215)
    edge("REJOIN", "ACTIVE", "стан догнав +\nвитримав RETURN_DELAY", FIELD, ox=-135)

    # підпис-легенда внизу двома рядками (щоб рамка не вилізла за полотно)
    note = ("Гістерезис живе на ребрі НА ПІДОЗРІ → ПІДНЯВСЯ (поріг пропусків);\n"
            "затримка повернення — на ребрі ПОВЕРНЕННЯ → ГОЛОВНИЙ.")
    nb, nw, nh = textbox(W / 2, 505, note, size=11, fill="#f4f6f8",
                         stroke=MUTED, sw=1.2, pad=9, color=MUTED)
    frags.append(nb)

    render(os.path.join(IMG, 'failover-fsm.svg'), W, H, *frags,
           title="Перемикання як скінченний автомат: де сидять гістерезис і затримка")


# ── Фігура 5: розкол мозку й огорожа токеном (для вставки proj) ──────────────
def fig_fencing():
    W, H = 980, 440
    frags = []

    # два «головні» ліворуч
    a, aw, ah = textbox(175, 135, "Вузол A (завис і ожив)\nдумає: я головний\nтокен = 33 (старий)",
                        size=12.5, bold=True, fill="#fdecea", stroke=POS, sw=2.2, pad=12, min_w=250)
    frags.append(a)
    b, bw, bh = textbox(175, 300, "Вузол B (підняли)\nдумає: я головний\nтокен = 34 (новий)",
                        size=12.5, bold=True, fill="#eaf7ee", stroke=FIELD, sw=2.2, pad=12, min_w=250)
    frags.append(b)

    # сховище-воротар праворуч
    g, gw, gh = textbox(800, 217, "СХОВИЩЕ\nпам'ятає найбільший\nбачений токен = 34",
                        size=13, bold=True, fill="#eef4ff", stroke=NEG, sw=2.4, pad=14, min_w=230)
    frags.append(g)

    # стрілки записів — до лівого краю сховища
    gx_left = 800 - gw / 2
    frags.append(arrow(175 + aw / 2 + 4, 150, gx_left - 8, 190, color=POS, sw=2))
    frags.append(arrow(175 + bw / 2 + 4, 300, gx_left - 8, 250, color=FIELD, sw=2))

    # вироки біля воріт: над/під стрілками, посунуті так, щоб не лежати на лініях
    rej, rw, rh = textbox(500, 108, "запис токеном 33\nВІДКИНУТО (менший)",
                          size=11.5, bold=True, fill="#ffffff", stroke=POS, sw=1.5, pad=8)
    frags.append(rej)
    acc, cw2, ch2 = textbox(485, 340, "запис токеном 34\nПРИЙНЯТО (найбільший)",
                            size=11.5, bold=True, fill="#ffffff", stroke=FIELD, sw=1.5, pad=8)
    frags.append(acc)

    # легенда двома рядками, з полем — рамка гарантовано в межах
    note = ("Огорожа (fencing) не заважає двом вважати себе головними —\n"
            "вона робить це БЕЗПЕЧНИМ: воротар пропускає лише монотонно старший токен.")
    nb, nw, nh = textbox(W / 2, 410, note, size=11, fill="#f4f6f8",
                         stroke=MUTED, sw=1.2, pad=9, color=MUTED)
    frags.append(nb)

    render(os.path.join(IMG, 'fencing-token.svg'), W, H, *frags,
           title="Огорожа токеном: як гасять розкол мозку на боці сховища")


# ── Фігура 6 (вставка hist): чому три слова, а не одне ──────────────────────
# Пропагація дефект→похибка→відмова: дрімає → спрацьовує → повзе → перетинає межу.
def fig_chain():
    W, H = 980, 430
    frags = []

    # межа системи — вертикальна риса, за якою «видно ззовні»
    boundary_x = 760
    frags.append(line(boundary_x, 70, boundary_x, 330, color=MUTED, sw=2, dash="7,5"))
    frags.append(text(boundary_x + 12, 62, "межа системи", size=12, bold=True,
                      color=MUTED, anchor="start"))
    frags.append(text(boundary_x + 12, 350, "усе, що правіше, —\nбачить користувач", size=11,
                      color=MUTED, anchor="start"))

    yc = 175  # спільний рівень ланцюга

    # 1) ДЕФЕКТ — дрімає всередині
    d1, w1, h1 = textbox(150, yc, "ДЕФЕКТ (fault)\nхибний рядок коду,\nтранзистор на грані",
                         size=12.5, bold=True, fill=FILL, stroke=MUTED, sw=2, pad=12, min_w=230)
    frags.append(d1)
    frags.append(text(150, yc - h1 / 2 - 14, "дрімає — роками нічого", size=11,
                      italic=True, color=MUTED))

    # 2) ПОХИБКА — спрацював, зіпсував стан
    d2, w2, h2 = textbox(430, yc, "ПОХИБКА (error)\nзіпсоване значення\nв пам'яті / стані",
                         size=12.5, bold=True, fill="#eef4ff", stroke=NEG, sw=2.2, pad=12, min_w=230)
    frags.append(d2)
    frags.append(text(430, yc - h2 / 2 - 14, "спрацював → активний", size=11,
                      italic=True, color=NEG))

    # 3) ВІДМОВА — прорвалася за межу
    d3, w3, h3 = textbox(870, yc, "ВІДМОВА (failure)\nсервіс не той,\nщо обіцяли",
                         size=12.5, bold=True, fill="#fdecea", stroke=POS, sw=2.2, pad=12, min_w=190)
    frags.append(d3)

    # стрілки переходів із підписами-механізмом (поза лініями)
    frags.append(arrow(150 + w1 / 2 + 6, yc, 430 - w2 / 2 - 8, yc, color=INK, sw=2.2))
    ax, aw, ah = textbox((150 + w1 / 2 + 430 - w2 / 2) / 2, yc - 40,
                         "спрацював\n(активація)", size=11, fill="#ffffff",
                         stroke=INK, sw=1.3, pad=7)
    frags.append(ax)

    frags.append(arrow(430 + w2 / 2 + 6, yc, 870 - w3 / 2 - 8, yc, color=INK, sw=2.2))
    bx, bw, bh = textbox((430 + w2 / 2 + 870 - w3 / 2) / 2, yc - 40,
                         "прорвалася\nза межу", size=11, fill="#ffffff",
                         stroke=INK, sw=1.3, pad=7)
    frags.append(bx)

    # три місця важеля — знизу, кожне під своїм переходом, добре відсунуті
    lever_y = 300
    l1 = fitbox(60, lever_y, 200, 46, "прибрати, поки дрімає\n→ відмови не буде",
                size=11, fill="#eaf7ee", stroke=FIELD, sw=1.5, bold=True)
    frags.append(l1)
    l2 = fitbox(330, lever_y, 200, 46, "перехопити всередині\n→ не дати вирватись",
                size=11, fill="#eaf7ee", stroke=FIELD, sw=1.5, bold=True)
    frags.append(l2)
    l3 = fitbox(600, lever_y, 150, 46, "оговтатись швидко\n→ скоротити простій",
                size=11, fill="#eaf7ee", stroke=FIELD, sw=1.5, bold=True)
    frags.append(l3)

    render(os.path.join(IMG, 'fault-error-failure.svg'), W, H, *frags,
           title="Три слова — бо втручатися можна у трьох різних місцях")


if __name__ == "__main__":
    fig_mtbf()
    fig_tree()
    fig_redundancy()
    fig_failover_fsm()
    fig_fencing()
    fig_chain()
    print("figures written to", IMG)
