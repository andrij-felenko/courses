# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def box_at(cx, cy, s, **kw):
    """textbox at center, returns (svg, half_w, half_h)."""
    body, w, h = textbox(cx, cy, s, **kw)
    return body, w / 2, h / 2


# ── Фігура 1: прямий виклик проти шини подій ────────────────────────────────
def direct_vs_events():
    W, H = 940, 470
    parts = []
    parts.append(text(W / 2, 30, "Прямий виклик проти шини подій", size=18, bold=True))

    # роздільна вертикаль
    parts.append(line(W / 2, 60, W / 2, H - 20, color=MUTED, sw=1, dash="6 6"))
    parts.append(text(W / 4, 58, "ПРЯМИЙ ВИКЛИК", size=13, bold=True, color=MUTED))
    parts.append(text(W * 3 / 4, 58, "ШИНА ПОДІЙ", size=13, bold=True, color=FIELD))

    # ---- ліва половина: placeOrder тримає стрілки до трьох слухачів ----
    lx = W / 4
    src, shw, shh = box_at(lx, 110, "placeOrder", size=14, bold=True,
                           fill="#fdecea", stroke=POS)
    parts.append(src)

    targets = ["пошта", "доставка", "аналітика"]
    ty = 360
    tspacing = 150
    tx0 = lx - tspacing
    for i, name in enumerate(targets):
        tx = tx0 + i * tspacing
        b, bw, bh = box_at(tx, ty, name, size=13, min_w=110)
        parts.append(b)
        # стрілка від джерела до кожного слухача
        parts.append(arrow(lx, 110 + shh, tx, ty - bh, color=POS, sw=1.8))
    parts.append(text(lx, ty + 55, "знає кожного особисто",
                      size=12, italic=True, color=POS))

    # ---- права половина: publish -> шина -> підписники ----
    rx = W * 3 / 4
    rsrc, rshw, rshh = box_at(rx, 110, "placeOrder", size=14, bold=True,
                              fill="#eaf7ef", stroke=FIELD)
    parts.append(rsrc)

    # шина посередині
    busy = 225
    bus, buw, buh = box_at(rx, busy, "шина подій", size=14, bold=True,
                           fill=FILL, stroke=FIELD, min_w=200)
    parts.append(bus)
    # одна стрілка вниз: publish
    parts.append(arrow(rx, 110 + rshh, rx, busy - buh, color=FIELD, sw=2))
    parts.append(text(rx + 78, (110 + rshh + busy - buh) / 2 + 4, "publish",
                      size=12, italic=True, color=FIELD, anchor="start"))

    rtargets = ["пошта", "доставка", "аналітика"]
    for i, name in enumerate(rtargets):
        tx = tx0 + i * tspacing + (W / 2)
        b, bw, bh = box_at(tx, ty, name, size=13, min_w=110)
        parts.append(b)
        # стрілка від шини до підписника
        parts.append(arrow(rx, busy + buh, tx, ty - bh, color=FIELD, sw=1.8))
    parts.append(text(rx, ty + 55, "знають лише шину",
                      size=12, italic=True, color=FIELD))

    render(os.path.join(IMG, "direct-vs-events.svg"), W, H, *parts)


# ── Фігура 2: тонка проти товстої події ─────────────────────────────────────
def thin_vs_fat():
    W, H = 940, 480
    parts = []
    parts.append(text(W / 2, 30, "Тонка подія проти товстої", size=18, bold=True))
    parts.append(line(W / 2, 60, W / 2, H - 20, color=MUTED, sw=1, dash="6 6"))
    parts.append(text(W / 4, 58, "ТОНКА", size=13, bold=True, color=NEG))
    parts.append(text(W * 3 / 4, 58, "ТОВСТА", size=13, bold=True, color=POS))

    # ---- ліва: тонка подія {orderId}, обробники йдуть у базу ----
    lx = W / 4
    ev, evw, evh = box_at(lx, 105, ["подія", "{ orderId: 42 }"], size=13, bold=False,
                          fill="#eaf0fd", stroke=NEG)
    parts.append(ev)

    hy = 245
    hspacing = 175
    hx0 = lx - hspacing / 2
    hnames = ["обробник\nбонусів", "обробник\nлиста"]
    hcenters = []
    for i, name in enumerate(hnames):
        hx = hx0 + i * hspacing
        hcenters.append(hx)
        b, bw, bh = box_at(hx, hy, name, size=12, min_w=130)
        parts.append(b)
        parts.append(arrow(lx, 105 + evh, hx, hy - bh, color=NEG, sw=1.6))

    # база даних під обробниками, обидва лізуть у неї
    dby = 390
    db, dbw, dbh = box_at(lx, dby, "база даних", size=13, bold=True, min_w=150)
    parts.append(db)
    for hx in hcenters:
        parts.append(arrow(hx, hy + 32, lx, dby - dbh, color=NEG, sw=1.4, ))
    parts.append(text(lx, dby + 48, "кожен дочитує деталі сам",
                      size=12, italic=True, color=NEG))

    # ---- права: товста подія з повним знімком, обробники самодостатні ----
    rx = W * 3 / 4
    rev, revw, revh = box_at(
        rx, 118,
        ["подія (знімок)", "{ orderId, сума,", "  кошик, покупець,", "  адреса }"],
        size=12, fill="#fdecea", stroke=POS)
    parts.append(rev)

    rhx0 = rx - hspacing / 2
    for i, name in enumerate(hnames):
        hx = rhx0 + i * hspacing
        b, bw, bh = box_at(hx, hy + 20, name, size=12, min_w=130)
        parts.append(b)
        parts.append(arrow(rx, 118 + revh, hx, hy + 20 - bh, color=POS, sw=1.6))
    parts.append(text(rx, dby + 8, "самодостатні — у базу не йдуть",
                      size=12, italic=True, color=POS))

    render(os.path.join(IMG, "thin-vs-fat.svg"), W, H, *parts)


# ── Фігура 3: родовід подієвого стилю (для вставки hist-) ────────────────────
def eda_lineage():
    W, H = 1000, 620
    parts = []
    parts.append(text(W / 2, 30, "Родовід: чотири внески сходяться в одну назву",
                      size=18, bold=True))

    # три верхні віхи-механізми (окремі струмки), кожна широка, з роком і суттю
    milestones = [
        (170, "1963 · Sketchpad", "машина вперше\nчекає на людину\n(цикл подій)", NEG),
        (500, "1979 · MVC (PARC)", "модель оголошує\nзміну — залежні\nслухають", NEG),
        (830, "1994 · «Спостерігач»", "механізм названо\nяк патерн\n(GoF)", NEG),
    ]
    my = 120
    top_boxes = []
    for cx, head, body, col in milestones:
        hb, hw, hh = box_at(cx, my, head, size=13, bold=True,
                            fill="#eaf0fd", stroke=col, min_w=230)
        parts.append(hb)
        bb, bw, bh = box_at(cx, my + 72, body, size=12, min_w=230)
        parts.append(bb)
        top_boxes.append((cx, my + 72 + bh))  # низ нижньої коробки струмка

    # вузол назви посередині-внизу (nhw/nhh — ПІВширина/піввисота від box_at)
    node_y = 400
    node, nhw, nhh = box_at(W / 2, node_y,
                            ["event-driven architecture", "Рой Шульте · Gartner · ~2003"],
                            size=14, bold=True, fill="#eaf7ef", stroke=FIELD, min_w=430)
    parts.append(node)

    # стрілки від кожного струмка ДО ВЕРХНЬОГО КРАЮ вузла (торкаються, не входять)
    for cx, ybottom in top_boxes:
        parts.append(arrow(cx, ybottom, W / 2 + (cx - W / 2) * 0.18,
                           node_y - nhh - 3, color=NEG, sw=1.7))

    # гілка доменних подій — окремо збоку, входить у ЛІВИЙ край вузла іншим кольором.
    # центр зсунуто вліво, щоб між правим краєм коробки й лівим краєм вузла був зазор.
    dcx, dy = 128, 400
    deb, dehw, dehh = box_at(dcx, dy,
                             ["доменні події", "Фаулер 2005 · Еванс 2014", "(зміст факту)"],
                             size=12, fill="#fdf3e0", stroke=POS, min_w=205)
    parts.append(deb)
    parts.append(arrow(dcx + dehw + 4, dy, W / 2 - nhw - 4, node_y, color=POS, sw=1.7))

    # підпис-висновок унизу, з запасом від вузла
    parts.append(text(W / 2, 500,
                      "річ старша за назву — механізм визрівав десятиліттями,",
                      size=13, italic=True, color=MUTED))
    parts.append(text(W / 2, 522,
                      "ім'я «архітектура» дав аналітик, а не винахідник",
                      size=13, italic=True, color=MUTED))
    parts.append(text(W / 2, 566,
                      "дата біля вузла — коли з'явилося ІМ'Я, а не РІЧ",
                      size=12, bold=True, color=FIELD))

    render(os.path.join(IMG, "eda-lineage.svg"), W, H, *parts)


# ── Фігура 4: драбина рефакторингу (для вставки proj-order-events-refactor) ───
def refactor_ladder():
    W, H = 1000, 720
    parts = []
    parts.append(text(W / 2, 34, "Драбина рефакторингу: що кожен крок купує й чим платить",
                      size=18, bold=True))

    # Чотири щаблі знизу вгору. Ліворуч — коробка кроку; праворуч від переходу —
    # «купує» (зелене) над лінією-переходом і «платить» (червоне) під нею.
    step_x = 250            # центр колонки коробок кроку
    box_w = 300
    ys = [640, 490, 340, 190]   # крок 0 внизу … крок 3 вгорі
    steps = [
        ("Крок 0 · прямі виклики", "placeOrder кличе всіх поіменно", MUTED),
        ("Крок 1 · синхронна шина", "publish у тому ж потоці", NEG),
        ("Крок 2 · асинхронна шина", "queueMicrotask, повертається одразу", FIELD),
        ("Крок 3 · ідемпотентність", "eventId + дедуплікація, форма події", POS),
    ]
    tops = []
    bottoms = []
    for (head, body, col), y in zip(steps, ys):
        b, bw, bh = box_at(step_x, y, [head, body], size=13, bold=True,
                           fill=FILL, stroke=col, min_w=box_w)
        parts.append(b)
        tops.append(y - bh)
        bottoms.append(y + bh)

    # Вертикальні стрілки-переходи між сусідніми кроками (по спині драбини).
    spine_x = step_x - box_w / 2 - 26
    trans = [
        ("+ розв'язка в коді", "− видимість потоку"),
        ("+ розв'язка в часі", "− гарантія «все або нічого»"),
        ("+ стійкість до повторів", "− стан, що переживе рестарт"),
    ]
    for i, (buys, costs) in enumerate(trans):
        y_lo = tops[i]           # низ = верх нижчої коробки
        y_hi = bottoms[i + 1]    # верх = низ вищої коробки
        parts.append(arrow(spine_x, y_lo, spine_x, y_hi, color=INK, sw=2.2))
        mid = (y_lo + y_hi) / 2
        # написи праворуч від коробок, із запасом, кожен на своєму рядку
        lx = step_x + box_w / 2 + 34
        parts.append(text(lx, mid - 12, buys, size=13, bold=True,
                          color=FIELD, anchor="start"))
        parts.append(text(lx, mid + 14, costs, size=13, bold=True,
                          color=POS, anchor="start"))

    # Права колонка: чого не розв'язати в пам'яті взагалі.
    panel_x = 830
    pb, pbw, pbh = box_at(
        panel_x, 200,
        ["ЗА МЕЖЕЮ ПАМ'ЯТІ", "надійна доставка:", "намір — у ту саму", "транзакцію, черга —", "поза процесом"],
        size=12, bold=False, fill="#fdecea", stroke=POS, min_w=250)
    parts.append(pb)
    parts.append(text(panel_x, 200 + pbh / 2 + 34,
                      "жоден щабель у пам'яті",
                      size=12, italic=True, color=MUTED))
    parts.append(text(panel_x, 200 + pbh / 2 + 54,
                      "сюди не дотягується",
                      size=12, italic=True, color=MUTED))

    # Підпис-орієнтир унизу праворуч, подалі від драбини.
    parts.append(text(panel_x, 520, "читати не як «вище — краще»,",
                      size=12, bold=True, color=INK))
    parts.append(text(panel_x, 542, "а як вибір під конкретний наслідок:",
                      size=12, bold=True, color=INK))
    parts.append(text(panel_x, 574, "єдиний → крок 0",
                      size=12, color=MUTED))
    parts.append(text(panel_x, 596, "невіддільний → крок 1",
                      size=12, color=MUTED))
    parts.append(text(panel_x, 618, "самостійний → крок 2",
                      size=12, color=MUTED))
    parts.append(text(panel_x, 640, "надійний повтор → крок 3",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "refactor-ladder.svg"), W, H, *parts)


if __name__ == "__main__":
    direct_vs_events()
    thin_vs_fat()
    eda_lineage()
    refactor_ladder()
    print("figures written to", IMG)
