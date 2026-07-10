# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: чотири групи тактик змінюваності ──────────────────────────────
def fig_tree():
    W, H = 900, 470
    frags = []
    # корінь
    root, rw, rh = textbox(W / 2, 70, "Здешевити майбутню зміну", size=16, bold=True,
                           fill="#eef4ff", stroke=NEG, sw=2, pad=14)
    frags.append(root)

    cols = [
        ("Зменшити\nмодуль", ["Розбити модуль"], POS),
        ("Підняти\nзв'язність", ["Одна відповідальність", "Спільна причина зміни"], FIELD),
        ("Послабити\nзчеплення", ["Інкапсуляція", "Посередник", "Обмежити залежності", "Абстрактний сервіс"], NEG),
        ("Відкласти\nзв'язування", ["Параметри / конфіг", "Плагіни", "Поліморфізм"], MUTED),
    ]
    n = len(cols)
    colw = W / n
    top_y = 175
    for i, (head, items, col) in enumerate(cols):
        cx = colw * i + colw / 2
        # лінія від кореня
        frags.append(line(W / 2, 70 + rh / 2, cx, top_y - 26, color=MUTED, sw=1.4))
        hb, hw, hh = textbox(cx, top_y, head, size=14, bold=True, fill="#fbfbfb",
                             stroke=col, sw=2, pad=10, min_w=colw - 34)
        frags.append(hb)
        yy = top_y + hh / 2 + 24
        for it in items:
            ib = fitbox(cx - (colw - 40) / 2, yy, colw - 40, 34, it, size=12,
                        fill=FILL, stroke=col, sw=1.3)
            frags.append(ib)
            yy += 42
    render(os.path.join(IMG, 'tactic-tree.svg'), W, H, *frags,
           title="Чотири родини тактик змінюваності")


# ── Фігура 2: зчеплення → хвиля зміни ───────────────────────────────────────
def fig_ripple():
    W, H = 900, 420
    frags = []

    # ЛІВА панель: пряме зчеплення — правка тече всюди
    lx = 30
    frags.append(text(lx + 200, 62, "Пряме зчеплення: правка тече всюди",
                      size=14, bold=True, anchor="middle"))
    # центральний модуль
    cm, cmw, cmh = textbox(lx + 200, 130, "Формат дати", size=13, bold=True,
                           fill="#fdecea", stroke=POS, sw=2, pad=10)
    frags.append(cm)
    clients = ["Звіт", "Експорт", "UI", "Лог", "API"]
    cxs = [lx + 40, lx + 120, lx + 200, lx + 280, lx + 360]
    bus_y = 250
    # шина від модуля вниз, тоді горизонталь, тоді короткі вертикальні спуски в кожну коробку
    frags.append(line(lx + 200, 130 + cmh / 2, lx + 200, bus_y, color=POS, sw=1.8))
    frags.append(line(cxs[0], bus_y, cxs[-1], bus_y, color=POS, sw=1.8))
    for nm, cxp in zip(clients, cxs):
        frags.append(line(cxp, bus_y, cxp, 300, color=POS, sw=1.8))
        cb = fitbox(cxp - 44, 300, 88, 40, nm, size=12, fill=FILL, stroke=POS, sw=1.6)
        frags.append(cb)
    frags.append(text(lx + 200, 374, "5 клієнтів знають формат → 5 правок",
                      size=12, color=POS, anchor="middle"))

    # роздільник
    frags.append(line(W / 2, 46, W / 2, H - 20, color="#d0d5db", sw=1.2, dash="5,5"))

    # ПРАВА панель: інтерфейс-посередник розриває хвилю
    rx = W / 2 + 30
    frags.append(text(rx + 190, 62, "Інтерфейс-посередник: правка локальна",
                      size=14, bold=True, anchor="middle"))
    ifc, ifw, ifh = textbox(rx + 190, 130, "fmtDate()", size=13, bold=True,
                            fill="#eafaf1", stroke=FIELD, sw=2, pad=10)
    frags.append(ifc)
    impl, iw2, ih2 = textbox(rx + 190, 205, "Формат дати\n(реалізація)", size=12,
                             fill=FILL, stroke=FIELD, sw=1.6, pad=8)
    frags.append(impl)
    frags.append(line(rx + 190, 130 + ifh / 2, rx + 190, 205 - ih2 / 2, color=FIELD, sw=1.8))
    cxs2 = [rx + (c - lx) for c in cxs]
    frags.append(line(rx + 190, 205 + ih2 / 2, rx + 190, bus_y, color=MUTED, sw=1.4, dash="3,3"))
    frags.append(line(cxs2[0], bus_y, cxs2[-1], bus_y, color=MUTED, sw=1.4, dash="3,3"))
    for nm, cxp2 in zip(clients, cxs2):
        frags.append(line(cxp2, bus_y, cxp2, 300, color=MUTED, sw=1.4, dash="3,3"))
        cb = fitbox(cxp2 - 44, 300, 88, 40, nm, size=12, fill=FILL, stroke=MUTED, sw=1.4)
        frags.append(cb)
    frags.append(text(rx + 190, 374, "Клієнти знають лише fmtDate() → 1 правка",
                      size=12, color=FIELD, anchor="middle"))

    render(os.path.join(IMG, 'coupling-ripple.svg'), W, H, *frags,
           title="Зчеплення вирішує, скільки місць чіпає одна зміна")


# ── Фігура 3: вісь моменту зв'язування ──────────────────────────────────────
def fig_binding():
    W, H = 900, 250
    frags = []
    y = 130
    frags.append(line(60, y, W - 60, y, color=INK, sw=2))
    frags.append(text(60, y + 46, "раніше (дешевше рішення, дорожча зміна)",
                      size=12, color=MUTED, anchor="start"))
    frags.append(text(W - 60, y + 46, "пізніше (гнучкіше, складніше)",
                      size=12, color=MUTED, anchor="end"))

    stops = [
        (150, "Компіляція", "#if / шаблон"),
        (330, "Складання", "лінкер / прапори"),
        (510, "Запуск", "конфіг / плагін"),
        (700, "Робота", "гаряча заміна"),
    ]
    for x, top, bot in stops:
        frags.append(circle(x, y, 7, fill=BG, stroke=NEG, sw=2.5))
        tb, tw, th = textbox(x, y - 48, top, size=13, bold=True, fill="#eef4ff",
                             stroke=NEG, sw=1.6, pad=8)
        frags.append(tb)
        frags.append(fitbox(x - 62, y + 18, 124, 26, bot, size=11,
                            fill=FILL, stroke=MUTED, sw=1.2))
    render(os.path.join(IMG, 'binding-axis.svg'), W, H, *frags,
           title="Момент зв'язування: коли рішення «застигає»")


# ── Фігура 4 (hist): часова лінія народження понять ─────────────────────────
def fig_hist_timeline():
    W, H = 940, 330
    frags = []
    y = 165
    frags.append(line(70, y, W - 40, y, color=INK, sw=2))
    frags.append(text(70, y + 62, "інтуїція студента", size=11, color=MUTED, anchor="start"))
    frags.append(text(W - 40, y + 62, "канон, який усі цитують", size=11, color=MUTED, anchor="end"))

    stops = [
        (140, "1943", "Народження\nЛ. Константайна", NEG, "up"),
        (330, "1960-ті", "MIT: перші\nмірки модулів", FIELD, "down"),
        (500, "1968", "Симпозіум:\nдоповідь про\nсегментацію", POS, "up"),
        (690, "1974", "IBM Systems\nJournal:\n«Structured\nDesign»", POS, "down"),
        (860, "1975 / 79", "Книжка\nз Йорданом", MUTED, "up"),
    ]
    for x, yr, lab, col, side in stops:
        frags.append(circle(x, y, 7, fill=BG, stroke=col, sw=2.5))
        yb, yw, yh = textbox(x, y, yr, size=13, bold=True, fill="#ffffff",
                             stroke=col, sw=1.8, pad=6)
        # рік ставимо трохи над/під вузлом як мітку на самій лінії — але щоб не накрити, зсунемо
        if side == "up":
            ty = y - 74
        else:
            ty = y + 96
        lb, lw, lh = textbox(x, ty, lab, size=11.5, fill=FILL, stroke=col, sw=1.4, pad=8, min_w=140)
        frags.append(lb)
        # тонка ніжка від вузла до підпису
        if side == "up":
            frags.append(line(x, y - 9, x, ty + lh / 2, color=col, sw=1.2, dash="3,3"))
        else:
            frags.append(line(x, y + 9, x, ty - lh / 2, color=col, sw=1.2, dash="3,3"))
    # рік-мітки прямо на осі поверх усього
    for x, yr, lab, col, side in stops:
        frags.append(text(x, y - 16 if side == "down" else y + 26, yr,
                          size=12, bold=True, color=col, anchor="middle"))
    render(os.path.join(IMG, 'coupling-timeline.svg'), W, H, *frags,
           title="Народження зчеплення і зв'язності")


# ── Фігура 5 (hist): дві драбини — зв'язність і зчеплення ────────────────────
def fig_hist_ladders():
    W, H = 940, 560
    frags = []
    rung_h = 52
    box_w = 300

    # ЛІВА драбина: зв'язність (знизу найгірша → вгорі найкраща)
    lx = 40
    frags.append(text(lx + box_w / 2, 40, "Зв'язність — тягнути ВГОРУ",
                      size=15, bold=True, anchor="middle"))
    cohesion = [  # згори (найкраща) вниз (найгірша) — так і малюємо зверху вниз
        ("Функційна", "одне чітке завдання", FIELD),
        ("Послідовна", "вихід → вхід наступного", FIELD),
        ("Комунікаційна", "ті самі дані", "#5aa469"),
        ("Процедурна", "спільний порядок кроків", MUTED),
        ("Часова", "робиться в один час", MUTED),
        ("Логічна", "схожі за категорією", POS),
        ("Випадкова", "не пов'язане нічим", POS),
    ]
    top = 70
    for i, (nm, desc, col) in enumerate(cohesion):
        yy = top + i * (rung_h + 8)
        frags.append(rect(lx, yy, box_w, rung_h, fill="#f6faf7" if col == FIELD else FILL,
                          stroke=col, sw=1.6, rx=7))
        frags.append(text(lx + 14, yy + 22, nm, size=13, bold=True, color=INK, anchor="start"))
        frags.append(text(lx + 14, yy + 40, desc, size=11, color=MUTED, anchor="start"))
    # стрілка «вгору = краще» ліворуч від драбини
    ay = top + len(cohesion) * (rung_h + 8)
    frags.append(arrow(lx - 18, ay - 6, lx - 18, top + 6, color=FIELD, sw=2.2))
    frags.append(text(lx - 30, (top + ay) / 2, "краще", size=11, bold=True,
                      color=FIELD, anchor="middle"))

    # роздільник
    frags.append(line(W / 2, 30, W / 2, H - 20, color="#d0d5db", sw=1.2, dash="5,5"))

    # ПРАВА драбина: зчеплення (згори найгірше → внизу найкраще)
    rx = W / 2 + 40
    frags.append(text(rx + box_w / 2, 40, "Зчеплення — тягнути ВНИЗ",
                      size=15, bold=True, anchor="middle"))
    coupling = [  # згори (найгірше) вниз (найкраще)
        ("За вмістом", "лізе в чужі нутрощі", POS),
        ("Спільне", "спільна глобальна змінна", POS),
        ("Зовнішнє", "нав'язаний формат / протокол", MUTED),
        ("Керівне", "прапорець-команда чужій логіці", MUTED),
        ("За зліпком", "ціла структура заради двох полів", "#5aa469"),
        ("За даними", "лише потрібні параметри", FIELD),
    ]
    for i, (nm, desc, col) in enumerate(coupling):
        yy = top + i * (rung_h + 8)
        frags.append(rect(rx, yy, box_w, rung_h, fill="#f6faf7" if col == FIELD else FILL,
                          stroke=col, sw=1.6, rx=7))
        frags.append(text(rx + 14, yy + 22, nm, size=13, bold=True, color=INK, anchor="start"))
        frags.append(text(rx + 14, yy + 40, desc, size=11, color=MUTED, anchor="start"))
    ay2 = top + len(coupling) * (rung_h + 8)
    frags.append(arrow(rx + box_w + 18, top + 6, rx + box_w + 18, ay2 - 6, color=FIELD, sw=2.2))
    frags.append(text(rx + box_w + 30, (top + ay2) / 2, "краще", size=11, bold=True,
                      color=FIELD, anchor="middle"))

    render(os.path.join(IMG, 'coupling-cohesion-ladders.svg'), W, H, *frags,
           title="Дві драбини Константайна")


# ── Фігура 6 (d): дві осі залежності — fan-in і fan-out ──────────────────────
def fig_fanin_fanout():
    W, H = 960, 470
    frags = []
    cx, cy = W / 2, 250
    m, mw, mh = textbox(cx, cy, "Модуль M", size=15, bold=True,
                        fill="#eef4ff", stroke=NEG, sw=2.2, pad=14, min_w=150)
    frags.append(text(200, 72, "Аферентне (Ca): хто залежить від M", size=13, bold=True))
    frags.append(text(W - 200, 72, "Еферентне (Ce): від кого залежить M", size=13, bold=True))
    lys = [130, 200, 270, 340]
    lnames = ["Звіт", "Оплата", "UI", "Пошук"]
    for y, nm in zip(lys, lnames):
        frags.append(fitbox(120, y - 20, 120, 40, nm, size=12, fill=FILL, stroke=POS, sw=1.6))
        frags.append(arrow(242, y, cx - mw / 2 - 6, cy, color=POS, sw=1.8))
    rnames = ["СУБД", "Лог", "Пошта", "Кеш"]
    for y, nm in zip(lys, rnames):
        frags.append(fitbox(W - 240, y - 20, 120, 40, nm, size=12, fill=FILL, stroke=MUTED, sw=1.6))
        frags.append(arrow(cx + mw / 2 + 6, cy, W - 242, y, color=MUTED, sw=1.8))
    frags.append(m)
    frags.append(text(cx, cy + mh / 2 + 32, "I = Ce / (Ca + Ce)", size=13, bold=True))
    frags.append(fitbox(60, 402, 320, 46, "висока Ca → зміна M котиться до всіх них",
                        size=12, fill="#fdecea", stroke=POS, sw=1.4))
    frags.append(fitbox(W - 380, 402, 320, 46, "високий Ce → їхні зміни ламають M",
                        size=12, fill=FILL, stroke=MUTED, sw=1.4))
    render(os.path.join(IMG, 'fanin-fanout.svg'), W, H, *frags,
           title="Дві осі залежності: fan-in і fan-out")


# ── Фігура 7 (d): поріг окупності тактики ───────────────────────────────────
def fig_breakeven():
    W, H = 900, 480
    frags = []
    x0, y0 = 100, 400
    x1, ytop = 830, 90
    frags.append(arrow(x0, y0, x1 + 8, y0, color=INK, sw=1.8))
    frags.append(arrow(x0, y0, x0, ytop - 8, color=INK, sw=1.8))
    frags.append(text(x1, y0 + 30, "очікувані зміни за життя коду →", size=12, color=MUTED, anchor="end"))
    frags.append(text(x0 - 8, ytop - 16, "сукупна вартість", size=12, color=MUTED, anchor="start"))
    ax, ay = x1, 130
    frags.append(line(x0, y0, ax, ay, color=POS, sw=2.4))
    iy, by = 300, 220
    frags.append(line(x0, iy, x1, by, color=FIELD, sw=2.4))
    m1 = (ay - y0) / (ax - x0)
    m2 = (by - iy) / (x1 - x0)
    xc = x0 + (iy - y0) / (m1 - m2)
    yc = y0 + m1 * (xc - x0)
    frags.append(line(xc, y0, xc, ytop, color=MUTED, sw=1.3, dash="5,5"))
    frags.append(circle(xc, yc, 6, fill=BG, stroke=INK, sw=2))
    frags.append(text(xc, ytop - 8, "поріг окупності n*", size=12, bold=True, anchor="middle"))
    frags.append(text(x1 - 6, ay - 18, "без тактики (нахил = хвиля)", size=12, color=POS, anchor="end"))
    frags.append(text(x1 - 6, by + 30, "з тактикою (ціна зараз + локальна правка)",
                      size=12, color=FIELD, anchor="end"))
    frags.append(text(xc - 118, 366, "тут тактика — марно", size=12, color=MUTED, anchor="middle"))
    frags.append(text(xc + 150, 366, "тут тактика окупається", size=12, color=FIELD, anchor="middle"))
    frags.append(text(x0 - 8, iy + 4, "ціна тактики", size=11, color=FIELD, anchor="end"))
    render(os.path.join(IMG, 'breakeven.svg'), W, H, *frags,
           title="Коли тактика окупається: поріг за кількістю змін")


# ── Фігура 8 (d): приховування рятує лише на схованій осі ────────────────────
def fig_wrong_axis():
    W, H = 940, 470
    frags = []
    frags.append(line(W / 2, 50, W / 2, H - 18, color="#d0d5db", sw=1.2, dash="5,5"))

    def panel(ox, ok, deps):
        col = FIELD if ok else POS
        cxs = [ox + 70, ox + 185, ox + 300]
        for i, x in enumerate(cxs):
            frags.append(fitbox(x - 48, 95, 96, 40, "Клієнт " + chr(65 + i), size=12,
                                fill=FILL, stroke=(MUTED if ok else col), sw=1.5))
        frags.append(rect(ox + 40, 185, 300, 44, fill="#eef4ff",
                          stroke=(NEG if ok else col), sw=(2 if ok else 2.6), rx=7))
        frags.append(text(ox + 190, 212, "Інтерфейс fmtDate()", size=13, bold=True))
        frags.append(rect(ox + 100, 286, 180, 44, fill=FILL, stroke=MUTED, sw=1.6, rx=7))
        frags.append(text(ox + 190, 313, "секрет: формат дати", size=12,
                          color=(INK if ok else MUTED)))
        if deps:
            for x in cxs:
                frags.append(line(x, 135, x, 183, color=MUTED, sw=1.3))
        return cxs

    panel(0, True, True)
    frags.append(text(190, 74, "Сховали ту вісь, що змінюється", size=13, bold=True))
    frags.append(text(190, 366, "зміна формату", size=12, color=FIELD, bold=True))
    frags.append(arrow(190, 356, 190, 332, color=FIELD, sw=2))
    frags.append(fitbox(38, 404, 304, 48, "зміна влучає у схований секрет — спиняється на шві",
                        size=12, fill="#eafaf1", stroke=FIELD, sw=1.5))

    ox = W / 2
    cxs = panel(ox, False, False)
    frags.append(text(ox + 190, 74, "Змінюється ІНША вісь — крізь шов", size=13, bold=True))
    frags.append(text(ox + 190, 262, "контракт змінюється: новий параметр",
                      size=11, color=POS, bold=True))
    for x in cxs:
        frags.append(arrow(x, 183, x, 137, color=POS, sw=1.8))
    frags.append(fitbox(ox + 38, 404, 304, 48, "зміна влучає у шов — хвиля крізь інтерфейс до всіх",
                        size=12, fill="#fdecea", stroke=POS, sw=1.5))
    render(os.path.join(IMG, 'wrong-axis.svg'), W, H, *frags,
           title="Приховування рятує лише на схованій осі")


# ── Фігура 9 (math): хвиля = fan_in · fix_site (виведення лічбою) ─────────────
def fig_ripple_count():
    W, H = 900, 470
    frags = []
    dec, dw, dh = textbox(W / 2, 96, "Рішення, що змінюється",
                          size=14, bold=True, fill="#fdecea", stroke=POS, sw=2.2, pad=12,
                          min_w=280)
    frags.append(dec)
    frags.append(text(W / 2, 100 + dh / 2 + 4, "формат дати · local = 5 хв", size=12, color=MUTED))

    xs = [130, 290, 450, 610, 770]
    top = 268
    for i, x in enumerate(xs):
        frags.append(arrow(W / 2, 96 + dh / 2, x, top - 8, color=POS, sw=1.5))
        frags.append(fitbox(x - 68, top, 136, 40, "Залежний " + str(i + 1),
                            size=12, fill=FILL, stroke=POS, sw=1.5))
        frags.append(text(x, top + 60, "+ fix_site = 10 хв", size=11, color=POS))

    res, rw, rh = textbox(W / 2, 402, "ripple = fan_in · fix_site = 5 · 10 = 50 хв",
                          size=14, bold=True, fill="#eef4ff", stroke=NEG, sw=2, pad=11)
    frags.append(res)
    frags.append(text(W / 2, 402 + rh / 2 + 22, "c = local + ripple = 5 + 50 = 55 хв",
                      size=13, bold=True))
    render(os.path.join(IMG, 'ripple-count.svg'), W, H, *frags,
           title="Хвиля — це лічба: fan_in залежних, кожен по fix_site")


# ── Фігура 10 (math): ripple-маса p·ripple — найрідша зміна може важити найбільше
def fig_ripple_mass():
    W, H = 900, 470
    frags = []
    x0, y0 = 150, 372
    ytop = 96
    frags.append(arrow(x0, y0, x0, ytop - 8, color=INK, sw=1.8))
    frags.append(arrow(x0, y0, 830, y0, color=INK, sw=1.8))
    frags.append(text(x0 + 210, ytop - 16, "ripple-маса = p · ripple  (хв за 3 роки)",
                      size=13, bold=True, anchor="middle"))
    frags.append(text(830, y0 + 28, "вид зміни", size=12, color=MUTED, anchor="end"))

    bars = [
        ("Поле форми", 12, 10, 120, MUTED, FILL),
        ("Формат дати", 3, 50, 150, POS, "#fdecea"),
        ("Заміна СУБД", 1, 240, 240, NEG, "#eef4ff"),
    ]
    scale = 250.0 / 240.0
    bw, gap, bx = 128, 84, x0 + 54
    for name, p, rip, mass, col, fillc in bars:
        h = mass * scale
        frags.append(rect(bx, y0 - h, bw, h, fill=fillc, stroke=col, sw=1.9))
        frags.append(text(bx + bw / 2, y0 - h - 12, str(mass) + " хв", size=13, bold=True, color=col))
        frags.append(text(bx + bw / 2, y0 + 24, name, size=12, bold=True))
        frags.append(text(bx + bw / 2, y0 + 44, "p=" + str(p) + " · ripple=" + str(rip),
                          size=11, color=MUTED))
        bx += bw + gap

    frags.append(fitbox(560, 150, 300, 46,
                        "найрідша зміна (p=1) — найбільша хвиля",
                        size=12, fill="#eef4ff", stroke=NEG, sw=1.4))
    render(os.path.join(IMG, 'ripple-mass.svg'), W, H, *frags,
           title="Куди ставити шов: не де часто, а де ripple-маса більша")


# ── Фігура (proj): інверсія залежності — ядро закрите ────────────────────────
def fig_ocp_inversion():
    W, H = 980, 540
    frags = []
    frags.append(line(W / 2, 44, W / 2, H - 20, color="#d0d5db", sw=1.2, dash="5,5"))

    # ЛІВОРУЧ: наївно — ядро знає кожен варіант (стрілки ВНИЗ до конкретних)
    lc = 245
    frags.append(text(lc, 66, "Наївно: ядро знає кожен варіант", size=14, bold=True))
    core, cw, ch = textbox(lc, 132, "ReportEngine\n(ядро)", size=13, bold=True,
                           fill="#fdecea", stroke=POS, sw=2.2, pad=12)
    conc = ["CsvExporter", "JsonExporter", "XmlExporter"]
    cxs = [lc - 130, lc, lc + 130]
    for x in cxs:
        frags.append(arrow(lc, 132 + ch / 2, x, 298, color=POS, sw=1.7))
    for nm, x in zip(conc, cxs):
        frags.append(fitbox(x - 62, 300, 124, 42, nm, size=12, fill=FILL, stroke=POS, sw=1.5))
    frags.append(core)
    frags.append(fitbox(lc - 168, 382, 336, 48,
                        "ядро залежить від варіантів → щоб додати новий, правлять ядро",
                        size=12, fill="#fdecea", stroke=POS, sw=1.4))

    # ПРАВОРУЧ: інверсія — варіанти залежать від контракту (стрілки ВГОРУ)
    rc = W / 2 + 245
    frags.append(text(rc, 66, "Інверсія: варіанти залежать від контракту", size=13, bold=True))
    ox, oy, ow, oh = rc - 178, 100, 356, 96
    frags.append(rect(ox, oy, ow, oh, fill="#eafaf1", stroke=FIELD, sw=2.2, rx=9))
    frags.append(text(rc, 92, "ядро (закрите для зміни)", size=11, color=FIELD, bold=True))
    b1, _, _ = textbox(rc, 130, "Exporter — контракт", size=12, bold=True,
                       fill=BG, stroke=FIELD, sw=1.6, pad=8)
    b2, _, _ = textbox(rc, 168, "register() · реєстр", size=12,
                       fill=BG, stroke=FIELD, sw=1.6, pad=8)
    frags.append(b1)
    frags.append(b2)
    cxs2 = [rc - 130, rc, rc + 130]
    for nm, x in zip(conc, cxs2):
        frags.append(arrow(x, 298, x, oy + oh + 2, color=FIELD, sw=1.7))
        frags.append(fitbox(x - 62, 300, 124, 42, nm, size=12, fill=FILL, stroke=FIELD, sw=1.5))
    frags.append(fitbox(rc - 168, 382, 336, 48,
                        "варіанти залежать від контракту → ядро закрите, ripple = 0",
                        size=12, fill="#eafaf1", stroke=FIELD, sw=1.4))
    render(os.path.join(IMG, 'ocp-inversion.svg'), W, H, *frags,
           title="Інверсія залежності: хто на кого спирається")


# ── Фігура (proj): де сідає «+1 правка» на трьох підходах ────────────────────
def fig_where_edit_lives():
    W, H = 1000, 430
    frags = []
    frags.append(line(333, 44, 333, H - 18, color="#d0d5db", sw=1.2, dash="5,5"))
    frags.append(line(667, 44, 667, H - 18, color="#d0d5db", sw=1.2, dash="5,5"))

    # Колонка 1: switch у ядрі
    frags.append(text(167, 62, "switch у ядрі", size=13, bold=True))
    b, _, _ = textbox(167, 150, "ядро: export()\nswitch(format){…}", size=12,
                      fill="#fdecea", stroke=POS, sw=2, pad=12)
    frags.append(b)
    frags.append(fitbox(107, 206, 120, 32, "+ гілка в ядро", size=11,
                        fill=BG, stroke=POS, sw=1.5, color=POS))
    frags.append(text(167, 300, "правок ядра: 1", size=13, bold=True, color=POS))
    frags.append(text(167, 336, "(ядро відкривають)", size=11, color=MUTED))

    # Колонка 2: рукописна мапа в ядрі
    frags.append(text(500, 62, "рукописна мапа в ядрі", size=13, bold=True))
    b, _, _ = textbox(500, 150, "ядро: get()\ntable[format]", size=12,
                      fill="#fdecea", stroke=POS, sw=2, pad=12)
    frags.append(b)
    frags.append(fitbox(440, 206, 120, 32, "+ рядок у ядро", size=11,
                        fill=BG, stroke=POS, sw=1.5, color=POS))
    frags.append(text(500, 300, "правок ядра: 1", size=13, bold=True, color=POS))
    frags.append(text(500, 336, "(менша, та все ж у ядрі)", size=11, color=MUTED))

    # Колонка 3: самореєстрація — правка виходить із ядра
    frags.append(text(833, 62, "самореєстрація", size=13, bold=True))
    b, _, _ = textbox(833, 142, "ядро: реєстр\nget(format)", size=12,
                      fill="#eafaf1", stroke=FIELD, sw=2, pad=12)
    frags.append(b)
    nb, _, _ = textbox(833, 224, "новий файл xml:\nregister('xml', …)", size=11,
                       fill="#eef4ff", stroke=NEG, sw=1.6, pad=10)
    frags.append(nb)
    frags.append(text(833, 300, "правок ядра: 0", size=13, bold=True, color=FIELD))
    frags.append(text(833, 336, "(ядро не відкривають)", size=11, color=MUTED))
    render(os.path.join(IMG, 'edit-location.svg'), W, H, *frags,
           title="Куди сідає «+1 правка», коли додаєш варіант")


# ── Фігура (proj): дві осі — дешева й дорога ─────────────────────────────────
def fig_two_axes_registry():
    W, H = 980, 430
    frags = []
    frags.append(line(W / 2, 42, W / 2, H - 18, color="#d0d5db", sw=1.2, dash="5,5"))

    # ЛІВОРУЧ: додати варіант — ripple ядра = 0
    lc = 245
    frags.append(text(lc, 62, "Вісь «додати варіант»", size=14, bold=True))
    ct, ctw, cth = textbox(lc, 122, "Exporter — контракт\n(ядро, закрите)", size=12, bold=True,
                           fill="#eafaf1", stroke=FIELD, sw=2.2, pad=10)
    xs = [100, 205, 310, 415]
    cols = [MUTED, MUTED, MUTED, FIELD]     # четвертий — новий
    labs = ["csv", "json", "xml", "parquet"]
    for nm, x, col in zip(labs, xs, cols):
        tgt = lc + (x - lc) * 0.4
        frags.append(arrow(x, 250, tgt, 122 + cth / 2 + 2, color=col, sw=1.6))
        frags.append(fitbox(x - 37, 250, 74, 38, nm, size=12, fill=FILL, stroke=col, sw=1.5))
    frags.append(ct)
    frags.append(plus(452, 250, r=9))
    frags.append(fitbox(lc - 170, 336, 340, 46,
                        "новий чіпляється сам · ядро не змінене · ripple ядра = 0",
                        size=12, fill="#eafaf1", stroke=FIELD, sw=1.4))

    # ПРАВОРУЧ: змінити контракт — ripple = N
    rc = W / 2 + 245
    frags.append(text(rc, 62, "Вісь «змінити контракт»", size=14, bold=True))
    ct2, _, cth2 = textbox(rc, 122, "Exporter — контракт\n(+ новий параметр)", size=12, bold=True,
                           fill="#fdecea", stroke=POS, sw=2.6, pad=10)
    xs2 = [rc - 145, rc - 48, rc + 48, rc + 145]
    for nm, x in zip(labs, xs2):
        src = rc + (x - rc) * 0.4
        frags.append(arrow(src, 122 + cth2 / 2 + 2, x, 248, color=POS, sw=1.6))
        frags.append(fitbox(x - 37, 250, 74, 38, nm, size=12, fill=FILL, stroke=POS, sw=1.5))
    frags.append(ct2)
    frags.append(fitbox(rc - 172, 336, 344, 46,
                        "контракт змінився → правити ВСІ N реалізацій · ripple = N",
                        size=12, fill="#fdecea", stroke=POS, sw=1.4))
    render(os.path.join(IMG, 'two-axes-registry.svg'), W, H, *frags,
           title="Реєстр дешевий на одній осі, дорогий на іншій")


if __name__ == "__main__":
    fig_tree()
    fig_ripple()
    fig_binding()
    fig_hist_timeline()
    fig_hist_ladders()
    fig_fanin_fanout()
    fig_breakeven()
    fig_wrong_axis()
    fig_ripple_count()
    fig_ripple_mass()
    fig_ocp_inversion()
    fig_where_edit_lives()
    fig_two_axes_registry()
    print("figures written to", IMG)
