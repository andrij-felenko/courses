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


if __name__ == "__main__":
    fig_tree()
    fig_ripple()
    fig_binding()
    fig_hist_timeline()
    fig_hist_ladders()
    print("figures written to", IMG)
