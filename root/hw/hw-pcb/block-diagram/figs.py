# -*- coding: utf-8 -*-
"""Фігури теми «Блок-схема системи». Запуск: python figs.py  → ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)
P = lambda name: os.path.join(OUT, name)


def block(cx, cy, w, h, label, sub=None, fill="#eef3fb", stroke=NEG):
    """Прямокутний блок із назвою (і дрібним підписом-функцією під нею)."""
    out = rect(cx - w/2, cy - h/2, w, h, fill=fill, stroke=stroke, sw=2, rx=6)
    if sub:
        out += text(cx, cy - 3, label, size=14, bold=True)
        out += text(cx, cy + 15, sub, size=11, color=MUTED)
    else:
        out += text(cx, cy + 5, label, size=14, bold=True)
    return out


def sumnode(cx, cy, r=15):
    """Суматор: кружок із хрестиком."""
    out = circle(cx, cy, r, fill="#fff", stroke=INK, sw=2)
    out += line(cx - r*0.6, cy, cx + r*0.6, cy, color=INK, sw=1.4)
    out += line(cx, cy - r*0.6, cx, cy + r*0.6, color=INK, sw=1.4)
    return out


# ── 1. Те саме коло: принципова схема ↔ блок-схема ──────────────────────────
def fig_schematic_vs_block():
    W, H = 760, 330
    f = []
    f.append(text(190, 52, "Принципова схема", size=15, bold=True))
    f.append(text(575, 52, "Блок-схема", size=15, bold=True))
    f.append(line(380, 70, 380, 300, color=MUTED, sw=1, dash="5,5"))

    # ── ліворуч: «начинка» — купка деталей ──
    # три каскади транзисторів-резисторів натяком
    bx = 70
    for i in range(3):
        x = bx + i*90
        f.append(rect(x, 110, 22, 50, fill="#fff", stroke=INK, sw=1.6, rx=2))   # резистор
        f.append(circle(x+11, 200, 13, fill="#fff", stroke=INK, sw=1.6))        # транзистор
        f.append(line(x+11, 110, x+11, 90, color=INK, sw=1.4))
        f.append(line(x+11, 213, x+11, 250, color=INK, sw=1.4))
        f.append(line(x+11, 160, x+11, 187, color=INK, sw=1.4))
        if i < 2:
            f.append(line(x+24, 200, x+90-2, 200, color=INK, sw=1.4))
    f.append(line(40, 250, 290, 250, color=INK, sw=1.6))   # спільна шина
    f.append(text(190, 285, "десятки деталей, важко охопити задум", size=11, color=MUTED))

    # ── праворуч: три блоки + стрілки ──
    block_y = 175
    f.append(block(478, block_y, 88, 56, "Вхід", "давач", fill="#eef3fb"))
    f.append(block(595, block_y, 92, 56, "Підсил.", "× 100", fill="#e9f7ef", stroke=FIELD))
    f.append(block(708, block_y, 80, 56, "Вихід", "АЦП", fill="#eef3fb"))
    f.append(arrow(405, block_y, 478-44, block_y, color=INK))
    f.append(arrow(478+44, block_y, 595-46, block_y, color=INK))
    f.append(arrow(595+46, block_y, 708-40, block_y, color=INK))
    f.append(text(575, 285, "що → що → що: задум видно з першого погляду", size=11, color=MUTED))
    render(P("schematic-vs-block.svg"), W, H, *f)


# ── 2. Анатомія блок-схеми: блок, стрілка-сигнал, суматор, гілка ────────────
def fig_anatomy():
    W, H = 720, 300
    f = []
    y = 150
    # суматор зліва
    f.append(sumnode(120, y))
    f.append(text(120, 200, "суматор", size=12, color=MUTED))
    f.append(plus(105, 128, r=7))
    f.append(minus(105, 175, r=7))
    # вхід у суматор
    f.append(arrow(40, y, 105, y, color=INK))
    f.append(text(60, 138, "вхід", size=12))
    # блок 1
    f.append(block(300, y, 120, 64, "Блок", "функція H(s)", fill="#e9f7ef", stroke=FIELD))
    f.append(arrow(135, y, 240, y, color=INK))
    # гілка-відведення
    f.append(circle(480, y, 4, fill=INK, stroke=INK))
    f.append(arrow(360, y, 478, y, color=INK))
    f.append(text(430, 138, "сигнал", size=12, color=MUTED))
    # вихід далі
    f.append(arrow(482, y, 680, y, color=INK))
    f.append(text(620, 138, "вихід", size=12))
    # відгалуження вниз і назад у суматор (петля ЗЗ)
    f.append(line(480, y, 480, 250, color=INK, sw=1.8))
    f.append(line(480, 250, 120, 250, color=INK, sw=1.8))
    f.append(arrow(120, 250, 120, y+15, color=INK))
    f.append(block(300, 250, 120, 40, "Зворотний шлях", fill="#fdecea", stroke=POS))
    # підписи елементів
    f.append(text(300, 95, "блок = операція над сигналом", size=12, color=MUTED))
    f.append(text(560, 235, "стрілка = напрям сигналу", size=12, color=MUTED))
    render(P("anatomy.svg"), W, H, *f)


# ── 3. Каскад: коефіцієнти перемножуються ───────────────────────────────────
def fig_cascade():
    W, H = 720, 230
    f = []
    y = 120
    f.append(arrow(30, y, 95, y, color=INK))
    f.append(text(55, y-14, "1 мВ", size=12))
    f.append(block(160, y, 110, 60, "Каскад A", "× 10", fill="#eef3fb"))
    f.append(arrow(215, y, 290, y, color=INK))
    f.append(text(252, y-14, "10 мВ", size=11, color=MUTED))
    f.append(block(355, y, 110, 60, "Каскад B", "× 20", fill="#eef3fb"))
    f.append(arrow(410, y, 485, y, color=INK))
    f.append(text(447, y-14, "200 мВ", size=11, color=MUTED))
    f.append(block(550, y, 110, 60, "Каскад C", "× 5", fill="#eef3fb"))
    f.append(arrow(605, y, 690, y, color=INK))
    f.append(text(660, y-14, "1 В", size=12))
    # підсумок
    box = fitbox(150, 175, 420, 40,
                 "Загальний коефіцієнт = 10 × 20 × 5 = 1000",
                 size=14, bold=True, fill="#fffbe6", stroke="#b8860b")
    f.append(box)
    render(P("cascade.svg"), W, H, *f)


# ── 4. Один блок можна розкрити в схему (рівні абстракції) ───────────────────
def fig_zoom_levels():
    W, H = 720, 250
    f = []
    # блок «Підсилювач»
    f.append(block(150, 120, 150, 70, "Підсилювач", "× 100", fill="#e9f7ef", stroke=FIELD))
    f.append(text(150, 205, "ОДИН блок на верхньому рівні", size=11, color=MUTED))
    # стрілка «розкрити»
    f.append(arrow(245, 120, 360, 120, color=INK))
    f.append(text(302, 102, "розкрити", size=12, color=MUTED))
    # «начинка» блоку — ОП із двома резисторами (інвертуючий)
    ox = 540
    f.append(rect(ox-150, 55, 300, 130, fill="#fbfcfe", stroke=MUTED, sw=1.4, rx=8))
    # трикутник ОП
    f.append('<path d="M %d %d L %d %d L %d %d Z" fill="#fff" stroke="%s" stroke-width="2"/>'
             % (ox, 95, ox, 165, ox+55, 130, INK))
    f.append(text(ox+18, 134, "−", size=16, color=NEG, bold=True))
    # вхідний резистор
    f.append(rect(ox-110, 118, 30, 14, fill="#fff", stroke=INK, sw=1.6, rx=2))
    f.append(line(ox-130, 125, ox-110, 125, color=INK, sw=1.4))
    f.append(line(ox-80, 125, ox, 125, color=INK, sw=1.4))
    f.append(line(ox-12, 95, ox-12, 80, color=INK, sw=1.4))
    # резистор ЗЗ
    f.append(rect(ox-25, 70, 30, 14, fill="#fff", stroke=INK, sw=1.6, rx=2))
    f.append(line(ox-12, 80, ox-25, 80, color=INK, sw=1.4))
    f.append(line(ox+5, 80, ox+70, 80, color=INK, sw=1.4))
    f.append(line(ox+70, 80, ox+70, 130, color=INK, sw=1.4))
    f.append(line(ox+55, 130, ox+90, 130, color=INK, sw=1.4))
    f.append(text(ox, 205, "та сама річ — повна схема", size=11, color=MUTED))
    render(P("zoom-levels.svg"), W, H, *f)


# ── 5. Каскад H(s): чому ДОБУТОК, а не сума (вставка math) ───────────────────
def fig_cascade_product():
    W, H = 720, 250
    f = []
    y = 105
    f.append(arrow(28, y, 92, y, color=INK))
    f.append(text(58, y - 14, "X", size=14, bold=True, italic=True))
    f.append(block(165, y, 120, 58, "H₁", "× 10", fill="#eef3fb"))
    f.append(arrow(225, y, 300, y, color=INK))
    f.append(text(262, y - 14, "10·X", size=12, color=MUTED))
    f.append(block(375, y, 120, 58, "H₂", "× 20", fill="#eef3fb"))
    f.append(arrow(435, y, 545, y, color=INK))
    f.append(text(490, y - 14, "200·X", size=12, color=MUTED))
    f.append(block(620, y, 120, 58, "H₃", "× 5", fill="#eef3fb"))
    f.append(arrow(680, y, 712, y, color=INK))
    f.append(text(700, y - 14, "Y", size=14, bold=True, italic=True))
    box = fitbox(150, 168, 420, 56,
                 "Y / X = H₁·H₂·H₃ = 10·20·5 = 1000\n(множення накладається на множення)",
                 size=14, bold=True, fill="#fffbe6", stroke="#b8860b")
    f.append(box)
    render(P("cascade-product.svg"), W, H, *f)


# ── 6. Виведення замкненої петлі: G = A/(1+A·β) ──────────────────────────────
def fig_loop_derivation():
    W, H = 720, 360
    f = []
    y = 120
    # суматор
    f.append(sumnode(120, y))
    f.append(plus(104, 100, r=7))
    f.append(minus(104, 142, r=7))
    f.append(arrow(40, y, 105, y, color=INK))
    f.append(text(58, y - 12, "X", size=14, bold=True, italic=True))
    # помилка E
    f.append(arrow(135, y, 245, y, color=INK))
    f.append(text(190, y - 12, "E", size=13, bold=True, italic=True, color=POS))
    # прямий блок A
    f.append(block(310, y, 120, 60, "A", "пряме", fill="#e9f7ef", stroke=FIELD))
    # вузол-відгалуження
    f.append(arrow(370, y, 520, y, color=INK))
    f.append(circle(520, y, 4.5, fill=INK, stroke=INK))
    f.append(arrow(524, y, 700, y, color=INK))
    f.append(text(560, y - 12, "Y", size=14, bold=True, italic=True))
    # назад через β
    f.append(line(520, y, 520, 235, color=INK, sw=1.8))
    f.append(line(520, 235, 510, 235, color=INK, sw=1.8))
    f.append(block(310, 235, 120, 46, "β", "зворотне", fill="#fdecea", stroke=POS))
    f.append(line(250, 235, 120, 235, color=INK, sw=1.8))
    f.append(arrow(120, 235, 120, y + 16, color=INK))
    f.append(text(430, 222, "β·Y", size=13, bold=True, italic=True, color=POS))
    # три рядки виведення
    f.append(line(40, 285, 680, 285, color=MUTED, sw=1, dash="4,4"))
    f.append(text(48, 308, "E = X − β·Y", size=14, anchor="start"))
    f.append(text(48, 330, "Y = A·E = A·(X − β·Y)", size=14, anchor="start"))
    box = fitbox(430, 295, 250, 42, "G = Y/X = A / (1 + A·β)",
                 size=15, bold=True, fill="#fffbe6", stroke="#b8860b")
    f.append(box)
    render(P("loop-derivation.svg"), W, H, *f)


# ── 7. Три правила згортання типових з'єднань ────────────────────────────────
def fig_reduction_rules():
    W, H = 760, 470
    f = []

    def small(cx, cy, lab, w=64, h=40, fill="#eef3fb", stroke=NEG):
        out = rect(cx - w/2, cy - h/2, w, h, fill=fill, stroke=stroke, sw=1.8, rx=5)
        out += text(cx, cy + 5, lab, size=14, bold=True, italic=True)
        return out

    # — Рядок 1: послідовне → добуток —
    y1 = 70
    f.append(text(30, y1 - 38, "Послідовне (каскад)", size=13, bold=True, anchor="start"))
    f.append(arrow(40, y1, 88, y1, color=INK))
    f.append(small(120, y1, "H₁"))
    f.append(arrow(152, y1, 200, y1, color=INK))
    f.append(small(232, y1, "H₂"))
    f.append(arrow(264, y1, 312, y1, color=INK))
    f.append(text(360, y1 + 5, "⟶", size=26, color=MUTED))
    f.append(arrow(400, y1, 440, y1, color=INK))
    f.append(small(500, y1, "H₁·H₂", w=96, fill="#e9f7ef", stroke=FIELD))
    f.append(arrow(548, y1, 596, y1, color=INK))
    f.append(text(680, y1 + 5, "добуток", size=13, color=MUTED))

    # — Рядок 2: паралельне → сума —
    y2 = 200
    f.append(text(30, y2 - 58, "Паралельне (через суматор)", size=13, bold=True, anchor="start"))
    f.append(circle(80, y2, 5, fill=INK, stroke=INK))
    f.append(arrow(40, y2, 78, y2, color=INK))
    f.append(line(80, y2, 80, y2 - 40, color=INK, sw=1.8))
    f.append(line(80, y2, 80, y2 + 40, color=INK, sw=1.8))
    f.append(small(160, y2 - 40, "H₁"))
    f.append(small(160, y2 + 40, "H₂"))
    f.append(arrow(112, y2 - 40, 128, y2 - 40, color=INK))
    f.append(arrow(112, y2 + 40, 128, y2 + 40, color=INK))
    f.append(line(192, y2 - 40, 250, y2 - 40, color=INK, sw=1.8))
    f.append(line(192, y2 + 40, 250, y2 + 40, color=INK, sw=1.8))
    f.append(line(250, y2 - 40, 250, y2 - 15, color=INK, sw=1.8))
    f.append(line(250, y2 + 40, 250, y2 + 15, color=INK, sw=1.8))
    f.append(sumnode(250, y2, r=14))
    f.append(plus(238, y2 - 26, r=6))
    f.append(plus(238, y2 + 26, r=6))
    f.append(arrow(264, y2, 312, y2, color=INK))
    f.append(text(360, y2 + 5, "⟶", size=26, color=MUTED))
    f.append(arrow(400, y2, 440, y2, color=INK))
    f.append(small(500, y2, "H₁+H₂", w=96, fill="#e9f7ef", stroke=FIELD))
    f.append(arrow(548, y2, 596, y2, color=INK))
    f.append(text(680, y2 + 5, "сума", size=13, color=MUTED))

    # — Рядок 3: перенос вузла-відгалуження через блок —
    y3 = 360
    f.append(text(30, y3 - 48, "Перенос вузла крізь блок", size=13, bold=True, anchor="start"))
    f.append(arrow(40, y3, 78, y3, color=INK))
    f.append(small(110, y3, "H"))
    f.append(arrow(142, y3, 200, y3, color=INK))
    f.append(circle(200, y3, 5, fill=INK, stroke=INK))
    f.append(arrow(204, y3, 250, y3, color=INK))
    f.append(line(200, y3, 200, y3 + 40, color=INK, sw=1.8))
    f.append(arrow(200, y3 + 40, 250, y3 + 40, color=INK))
    f.append(text(225, y3 - 12, "Y", size=12, italic=True, color=MUTED))
    f.append(text(225, y3 + 56, "Y", size=12, italic=True, color=MUTED))
    f.append(text(360, y3 + 5, "⟶", size=26, color=MUTED))
    # після переносу: вузол ПЕРЕД блоком, гілка дістає свій 1/H? ні — гілку×H
    f.append(arrow(400, y3, 438, y3, color=INK))
    f.append(circle(438, y3, 5, fill=INK, stroke=INK))
    f.append(small(490, y3, "H", fill="#e9f7ef", stroke=FIELD))
    f.append(arrow(522, y3, 560, y3, color=INK))
    f.append(line(438, y3, 438, y3 + 40, color=INK, sw=1.8))
    f.append(arrow(438, y3 + 40, 548, y3 + 40, color=INK))
    f.append(small(580, y3 + 40, "H", w=52, h=34, fill="#e9f7ef", stroke=FIELD))
    f.append(arrow(606, y3 + 40, 640, y3 + 40, color=INK))
    f.append(text(690, y3 - 6, "гілка має", size=12, color=MUTED))
    f.append(text(690, y3 + 10, "набути H", size=12, color=MUTED))
    render(P("reduction-rules.svg"), W, H, *f)


# ── 8. Що бачив Блек: плетиво деталей ↔ петля сигналу (вставка hist) ─────────
def fig_what_black_saw():
    W, H = 760, 360
    f = []
    f.append(text(195, 44, "На принциповій схемі", size=15, bold=True))
    f.append(text(575, 44, "Те, що треба було побачити", size=15, bold=True))
    f.append(line(380, 62, 380, 330, color=MUTED, sw=1, dash="5,5"))

    # ── ліворуч: ланцюг ламп-повторювачів, тоне в деталях ──
    bx = 56
    for i in range(3):
        x = bx + i*84
        f.append('<ellipse cx="%d" cy="%d" rx="16" ry="26" fill="#fff" stroke="%s" stroke-width="1.6"/>'
                 % (x+11, 150, INK))
        f.append(line(x+11, 124, x+11, 104, color=INK, sw=1.4))
        f.append(line(x+11, 176, x+11, 210, color=INK, sw=1.4))
        f.append(rect(x, 94, 22, 10, fill="#fff", stroke=INK, sw=1.4, rx=2))   # резистор
        f.append(circle(x+11, 224, 7, fill="#fff", stroke=INK, sw=1.4))        # конденсатор натяком
        if i < 2:
            f.append(line(x+27, 150, x+84-5, 150, color=INK, sw=1.4))
    f.append(line(42, 250, 290, 250, color=INK, sw=1.6))   # спільна шина
    f.append(text(195, 286, "лампи, резистори, дроти —", size=11, color=MUTED))
    f.append(text(195, 303, "де тут петля сигналу?", size=11, color=MUTED))

    # ── праворуч: підсилювач зі ЗЗ як петля блоків ──
    y = 150
    f.append(sumnode(468, y))
    f.append(plus(452, 128, r=7))
    f.append(minus(452, 174, r=7))
    f.append(arrow(414, y, 453, y, color=INK))
    f.append(text(430, 120, "вхід", size=11))
    f.append(block(598, y, 112, 56, "Підсилювач", "× A", fill="#e9f7ef", stroke=FIELD))
    f.append(arrow(483, y, 542, y, color=INK))
    f.append(circle(690, y, 4.5, fill=INK, stroke=INK))
    f.append(arrow(654, y, 688, y, color=INK))
    f.append(arrow(692, y, 730, y, color=INK))
    f.append(text(712, 120, "вихід", size=11))
    # зворотний шлях через β назад у суматор
    f.append(line(690, y, 690, 250, color=POS, sw=1.8))
    f.append(line(690, 250, 581, 250, color=POS, sw=1.8))
    f.append(block(525, 250, 112, 38, "Частина β", fill="#fdecea", stroke=POS))
    f.append(line(469, 250, 468, 250, color=POS, sw=1.8))
    f.append(line(468, 250, 468, y + 15, color=POS, sw=1.8))
    f.append(arrow(468, y + 30, 468, y + 13, color=POS))
    f.append(text(575, 314, "видно петлю: вихід вертається на вхід", size=11, color=MUTED))
    render(P("what-black-saw.svg"), W, H, *f)


# ── 9. Хто відточив апарат: смуга часу ──────────────────────────────────────
def fig_history_timeline():
    W, H = 770, 300
    f = []
    y = 150
    f.append(line(48, y, 712, y, color=INK, sw=2))
    f.append(arrow(702, y, 714, y, color=INK))

    marks = [
        (95,  "1927",      FIELD, "#e9f7ef"),
        (255, "1932",      NEG,   "#eef3fb"),
        (420, "1940-45",   NEG,   "#eef3fb"),
        (560, "1939-45",   POS,   "#fdecea"),
        (680, "1950-60-ті", "#b8860b", "#fffbe6"),
    ]
    for x, yr, col, fill in marks:
        f.append(circle(x, y, 6, fill=fill, stroke=col, sw=2))
        f.append(text(x, y - 28, yr, size=12, bold=True))

    cards = [
        (95,  y + 26, "Блек",       "ескіз петлі\nзворотного зв'язку", "#e9f7ef", FIELD),
        (255, y - 98, "Найквіст",   "критерій\nстійкості",            "#eef3fb", NEG),
        (420, y + 26, "Боде",       "діаграми,\nзапас стійкості",      "#eef3fb", NEG),
        (560, y - 98, "війна",      "радари,\nнаведення",              "#fdecea", POS),
        (676, y + 26, "TRW · NASA", "функційні\nблок-схеми",           "#fffbe6", "#b8860b"),
    ]
    for x, cy, who, what, fill, col in cards:
        bw, bh = 124, 58
        f.append(rect(x - bw/2, cy, bw, bh, fill=fill, stroke=col, sw=1.6, rx=6))
        f.append(text(x, cy + 21, who, size=13, bold=True))
        for i, ln in enumerate(what.split("\n")):
            f.append(text(x, cy + 37 + i*14, ln, size=10, color=MUTED))
        if cy > y:
            f.append(line(x, y + 6, x, cy, color=MUTED, sw=1))
        else:
            f.append(line(x, cy + bh, x, y - 6, color=MUTED, sw=1))
    render(P("history-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_schematic_vs_block()
    fig_anatomy()
    fig_cascade()
    fig_zoom_levels()
    fig_cascade_product()
    fig_loop_derivation()
    fig_reduction_rules()
    fig_what_black_saw()
    fig_history_timeline()
    print("ok: 9 figures ->", OUT)
