# -*- coding: utf-8 -*-
"""Фігури до кроку «Контекст як кандидат у сервіс» (guide/progarch/ddd-lite)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def cohesion(cx, cy, dot=5):
    """Щільний кластер: 4 вузли, з'єднані всіма ребрами (висока зв'язність)."""
    pts = [(cx - 34, cy - 26), (cx + 34, cy - 26),
           (cx - 34, cy + 26), (cx + 34, cy + 26)]
    out = []
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            out.append(line(pts[i][0], pts[i][1], pts[j][0], pts[j][1],
                            color=INK, sw=1.2))
    for (px, py) in pts:
        out.append(circle(px, py, dot, fill=INK, stroke=INK, sw=1))
    return out


def fig_seam_menu():
    """Один деплой, 4 контексти-модулі; тонкі стики між ними — червоні шви-розрізи."""
    W, H = 980, 560
    frags = []

    # ── контейнер розгортання ──
    frags.append(rect(40, 80, 900, 400, fill="#fbfcfd", stroke=LINE, sw=2, rx=10))
    frags.append(text(56, 104, "одне розгортання (модульний моноліт)",
                      size=13, color=MUTED, anchor="start"))

    ctx = [
        (150, "Телеметрія", "потік вимірів"),
        (380, "Твін", "дзеркало дому"),
        (610, "Автоматизації", "правила «якщо…то»"),
        (840, "Ідентичність", "хто ти й що можна"),
    ]
    seams = [265, 495, 725]

    # модулі-контексти (щільні всередині)
    for cx, name, sub in ctx:
        frags.append(rect(cx - 75, 185, 150, 270, fill=FILL, stroke=LINE, sw=1.6, rx=8))
        frags.append(text(cx, 214, name, size=14, bold=True))
        frags.append(text(cx, 234, sub, size=11, color=MUTED))
        frags += cohesion(cx, 372)

    # тонкі стики через шви (низьке зчеплення: рідко й тонко)
    box_edges = [(225, 305), (455, 535), (685, 765)]
    for (r, l) in box_edges:
        frags.append(line(r, 300, l, 300, color=MUTED, sw=1.2))

    # шви — червоні пунктирні лінії розрізу + підпис-пігулка
    for sx in seams:
        frags.append(line(sx, 158, sx, 468, color=POS, sw=1.8, dash="7,6"))
        b, _, _ = textbox(sx, 138, "шов", size=12, fill="#fdecea",
                          stroke=POS, color=POS, bold=True, pad=7)
        frags.append(b)

    # легенда під контейнером
    frags.append(line(150, 512, 210, 512, color=MUTED, sw=1.2))
    frags.append(text(220, 516, "тонкий стик — низьке зчеплення",
                      size=12, color=MUTED, anchor="start"))
    frags.append(line(560, 512, 620, 512, color=POS, sw=1.8, dash="7,6"))
    frags.append(text(630, 516, "шов — де розріз у сервіс найдешевший",
                      size=12, color=POS, anchor="start"))

    render(os.path.join(IMG, "seam-menu.svg"), W, H, *frags,
           title="Карта контекстів = меню можливих сервісів")


def fig_two_realizations():
    """Та сама межа «автоматизації → твін»: у пам'яті проти мережею."""
    W, H = 980, 470
    frags = [line(490, 74, 490, 452, color=MUTED, sw=1, dash="4,5")]

    # ═══ ЛІВОРУЧ: у пам'яті ═══
    frags.append(text(255, 96, "У ПАМ'ЯТІ  (один процес)", size=15, bold=True, color=FIELD))
    b, _, _ = textbox(150, 160, "Автоматизації", size=13)
    frags.append(b)
    b, _, _ = textbox(360, 160, "Твін", size=13)
    frags.append(b)
    frags.append(arrow(212, 160, 306, 160, color=FIELD, sw=2.4))
    frags.append(text(258, 142, "виклик у пам'яті", size=11, color=MUTED))
    frags.append(text(258, 196, "~ наносекунди", size=12, color=FIELD, bold=True))

    lgood = [
        "один процес — спільна пам'ять",
        "одна транзакція: усе або нічого",
        "без часткової відмови",
        "без серіалізації, версій, таймаутів",
    ]
    for i, s in enumerate(lgood):
        y = 258 + i * 34
        frags.append(circle(70, y - 4, 4, fill=FIELD, stroke=FIELD, sw=1))
        frags.append(text(86, y, s, size=13, color=INK, anchor="start"))

    # ═══ ПРАВОРУЧ: мережею ═══
    frags.append(text(735, 96, "МЕРЕЖЕЮ  (два процеси)", size=15, bold=True, color=POS))
    b, _, _ = textbox(600, 160, "Автоматизації", size=13)
    frags.append(b)
    b, _, _ = textbox(880, 160, "Твін", size=13)
    frags.append(b)
    # зона мережі
    frags.append(rect(690, 138, 100, 44, fill="#fdecea", stroke=POS, sw=1.4, rx=8))
    frags.append(text(740, 164, "мережа", size=12, color=POS))
    # запит іде (суцільна), відповідь непевна (пунктир + «?»)
    frags.append(arrow(662, 160, 688, 160, color=POS, sw=2.2))
    frags.append(line(792, 160, 842, 160, color=POS, sw=2.0, dash="6,5"))
    frags.append(text(817, 150, "?", size=16, color=POS, bold=True))
    frags.append(text(740, 200, "~ мілісекунди", size=12, color=POS, bold=True))

    lbad = [
        "два процеси — мережа між ними",
        "×10⁴–10⁵ повільніше за пам'ять",
        "часткова відмова: пішов — а відповідь?",
        "серіалізація, версії, таймаути, повтори",
    ]
    for i, s in enumerate(lbad):
        y = 258 + i * 34
        frags.append(circle(536, y - 4, 4, fill=POS, stroke=POS, sw=1))
        frags.append(text(552, y, s, size=13, color=INK, anchor="start"))

    render(os.path.join(IMG, "two-realizations.svg"), W, H, *frags,
           title="Та сама межа — різний дріт")


def fig_ruler_lineage():
    """Родовід «лінійки» (для вставки hist-): від контексту-для-моделі (2003)
    крізь усталення мікросервісів до контестованої евристики (2018)."""
    W, H = 1260, 372
    axis_y = 195
    frags = [line(95, axis_y, 1158, axis_y, color=MUTED, sw=2),
             arrow(1158, axis_y, 1184, axis_y, color=MUTED, sw=2)]

    # (x, рядки, заливка, колір-точки, ряд 'top'|'bot')
    beats = [
        (150,  ["2003", "Еванс:", "контекст"],                 "#eef2fb", NEG, "top"),
        (340,  ["2011–12", "слово під", "Венецією"],           "#eef2fb", NEG, "bot"),
        (530,  ["бер. 2014", "Lewis+Fowler:", "контекст ↔ сервіс"], "#eef2fb", NEG, "top"),
        (720,  ["лют. 2015", "Newman:", "межа = контекст"],    "#eef2fb", NEG, "bot"),
        (910,  ["черв. 2015", "Fowler:", "моноліт-спершу"],    "#eef2fb", NEG, "top"),
        (1100, ["2018", "Khononov:", "контекст ≠ сервіс"],     "#fdecea", POS, "bot"),
    ]
    cy_top, cy_bot = 100, 292
    for x, lines, fillc, dotc, row in beats:
        cy = cy_top if row == "top" else cy_bot
        b, w, h = textbox(x, cy, "\n".join(lines), size=13, fill=fillc, stroke=dotc)
        if row == "top":
            frags.append(line(x, cy + h / 2, x, axis_y - 7, color=MUTED, sw=1.4))
        else:
            frags.append(line(x, axis_y + 7, x, cy - h / 2, color=MUTED, sw=1.4))
        frags.append(b)
        frags.append(circle(x, axis_y, 7, fill=fillc, stroke=dotc, sw=2.6))

    # легенда (нижче за всі рамки, щоб не накластися)
    frags.append(circle(430, 348, 6, fill="#eef2fb", stroke=NEG, sw=2.2))
    frags.append(text(444, 352, "усталені віхи", size=12, color=MUTED, anchor="start"))
    frags.append(circle(742, 348, 6, fill="#fdecea", stroke=POS, sw=2.2))
    frags.append(text(756, 352, "спірна евристика (2018)", size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "ruler-lineage.svg"), W, H, *frags,
           title="Як контекст став лінійкою для сервісів")


if __name__ == "__main__":
    fig_seam_menu()
    fig_two_realizations()
    fig_ruler_lineage()
    print("OK: seam-menu.svg, two-realizations.svg, ruler-lineage.svg")
