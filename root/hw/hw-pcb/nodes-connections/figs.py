# -*- coding: utf-8 -*-
"""Фігури до теми «Вузли й з'єднання» та вставки «Нетлист і ERC».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# ── Локальні константи кольорів (літерали приймає svgkit) ────────────────────
WIRE   = "#cf8b5e"   # тепла мідь — колір дроту мітки
ORANGE = "#e08030"   # попередження середнього рівня
GREYLN = "#e4e4e4"   # ледь помітна роздільна лінія
FL_FILL = "#eef2fb"  # заливка прапорця-мітки
GREEN_FILL = "#eef7f0"
GREY_FILL  = "#f7f7f7"
WARM_FILL  = "#fff8ee"


def junction(cx, cy, r=6.5, color=INK):
    """Точка з'єднання (вузол) — суцільний кружечок."""
    return circle(cx, cy, r, fill=color, stroke=color, sw=1)


# ── 1. Вузол — одна електрична точка ─────────────────────────────────────────
def fig_node():
    W, H = 820, 320
    f = [text(W / 2, 30, "Вузол — одна електрична точка, хоч як розкидана",
              size=18, bold=True),
         text(W / 2, 52,
              "усі виводи, сполучені дротом, — той самий вузол з одним потенціалом",
              size=11.5, color=MUTED, italic=True)]

    bus_y = 130
    # зелена шина
    f.append(line(120, bus_y, 700, bus_y, color=FIELD, sw=4))
    # чотири вертикальні стуби до деталей
    for x in (180, 320, 460, 600):
        f.append(line(x, bus_y, x, 170, color=FIELD, sw=4))
        f.append(rect(x - 14, 170, 28, 40, fill=BG, stroke=INK, sw=1.5, rx=3))
        f.append(circle(x, bus_y, 5, fill=FIELD, stroke=FIELD, sw=1))
    # вивід угору-ліворуч з міткою «А»
    f.append(line(120, bus_y, 120, 110, color=FIELD, sw=4))
    f.append(circle(120, 110, 5, fill=FIELD, stroke=FIELD, sw=1))
    f.append(text(120, 100, "А", size=14, color=FIELD, bold=True))

    # підписи
    f.append(text(410, 250,
                  "Хоч до вузла А під'єднано чотири деталі в різних місцях —",
                  size=11.5, color=INK, bold=True))
    f.append(text(410, 272,
                  "це ОДНА точка кола (один потенціал), бо все сполучено суцільним дротом.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "node.svg"), W, H, *f)


# ── 2. Крапка вирішує все ─────────────────────────────────────────────────────
def fig_dot_vs_cross():
    W, H = 820, 340
    f = [text(W / 2, 30, "Крапка вирішує все: з'єднано чи ні", size=19, bold=True),
         text(W / 2, 52,
              "жирна крапка на перетині = дроти з'єднані; немає крапки = просто перетинаються",
              size=11.5, color=MUTED, italic=True)]

    # ледь помітний роздільник
    f.append(line(410, 78, 410, 290, color=GREYLN, sw=1.4, dash="4,5"))

    # ── ліворуч: із крапкою ──
    f.append(text(210, 110, "Із крапкою — З'ЄДНАНО", size=13.5, color=FIELD, bold=True))
    f.append(line(110, 200, 310, 200, color=INK, sw=2.4))
    f.append(line(210, 145, 210, 255, color=INK, sw=2.4))
    f.append(junction(210, 200))
    f.append(text(210, 290, "одна спільна точка (вузол)", size=11, color=FIELD, bold=True))

    # ── праворуч: без крапки ──
    f.append(text(610, 110, "Без крапки — НЕ з'єднано", size=13.5, color=POS, bold=True))
    f.append(line(510, 200, 710, 200, color=INK, sw=2.4))
    f.append(line(610, 145, 610, 255, color=INK, sw=2.4))
    f.append(text(610, 290, "дроти йдуть повз — різні вузли", size=11, color=POS, bold=True))
    render(os.path.join(IMG, "dot-vs-cross.svg"), W, H, *f)


# ── 3. Три способи показати перетин ──────────────────────────────────────────
def fig_hop():
    W, H = 860, 320
    f = [text(W / 2, 30, "Три способи показати перетин дротів", size=19, bold=True),
         text(W / 2, 52,
              "з'єднання — крапкою; непоєднаний перетин — просто навхрест або «містком»",
              size=11.5, color=MUTED, italic=True)]

    y = 190
    # col1 — з'єднано
    f.append(text(160, 110, "З'єднано", size=12.5, color=FIELD, bold=True))
    f.append(line(80, y, 240, y, color=INK, sw=2.4))
    f.append(line(160, 140, 160, 240, color=INK, sw=2.4))
    f.append(junction(160, y))
    f.append(text(160, 270, "крапка", size=10, color=MUTED))

    # col2 — не з'єднано (сучасно)
    f.append(text(430, 110, "Не з'єднано (сучасно)", size=12.5, color=POS, bold=True))
    f.append(line(350, y, 510, y, color=INK, sw=2.4))
    f.append(line(430, 140, 430, 240, color=INK, sw=2.4))
    f.append(text(430, 270, "просто навхрест", size=10, color=MUTED))

    # col3 — не з'єднано (місток)
    f.append(text(700, 110, "Не з'єднано («місток»)", size=12.5, color=POS, bold=True))
    f.append(line(700, 140, 700, 240, color=INK, sw=2.4))
    f.append(line(620, y, 692, y, color=INK, sw=2.4))
    f.append('<path d="M 692,%g A 8 8 0 0 1 708,%g" fill="none" stroke="%s" '
             'stroke-width="2.4"/>' % (y, y, INK))
    f.append(line(708, y, 780, y, color=INK, sw=2.4))
    f.append(text(700, 270, "дріт «перестрибує»", size=10, color=MUTED))
    render(os.path.join(IMG, "hop.svg"), W, H, *f)


# ── 4. Уникайте двозначного 4-перехрестя ─────────────────────────────────────
def fig_ambiguous():
    W, H = 820, 340
    f = [text(W / 2, 30, "Уникайте двозначного 4-перехрестя", size=19, bold=True),
         text(W / 2, 52,
              "крапка на схрещенні чотирьох дротів читається погано — чи її не загубили?",
              size=11.5, color=MUTED, italic=True)]

    # ── ліворуч: двозначно ──
    f.append(text(210, 110, "Так — двозначно", size=13, color=POS, bold=True))
    f.append(line(110, 200, 310, 200, color=INK, sw=2.4))
    f.append(line(210, 145, 210, 255, color=INK, sw=2.4))
    f.append(junction(210, 200))
    f.append(text(210, 290, "одна крапка на 4 дроти — ризик помилки", size=10, color=POS))

    # стрілка-перехід
    f.append(text(415, 200, "→", size=30, color=INK, bold=True))

    # ── праворуч: два Т-з'єднання ──
    f.append(text(630, 110, "Краще — два Т-з'єднання", size=13, color=FIELD, bold=True))
    f.append(line(530, 180, 730, 180, color=INK, sw=2.4))
    f.append(line(530, 220, 730, 220, color=INK, sw=2.4))
    f.append(line(580, 180, 580, 255, color=INK, sw=2.4))
    f.append(junction(580, 180, r=6))
    f.append(line(680, 145, 680, 220, color=INK, sw=2.4))
    f.append(junction(680, 220, r=6))
    f.append(text(630, 290, "кожне з'єднання однозначне", size=10, color=FIELD, bold=True))
    render(os.path.join(IMG, "ambiguous.svg"), W, H, *f)


# ── 5. Іменовані ланцюги: з'єднання без дроту ────────────────────────────────
def fig_net_labels():
    W, H = 820, 330
    f = [text(W / 2, 30, "Іменовані ланцюги: з'єднання без дроту", size=19, bold=True),
         text(W / 2, 52,
              "однакова назва (мітка) означає одне коло — навіть якщо лінії не з'єднані",
              size=11.5, color=MUTED, italic=True)]

    # пристрої
    f.append(rect(120, 120, 60, 70, fill=BG, stroke=INK, sw=1.5, rx=4))
    f.append(text(150, 160, "U1", size=11, color=INK, bold=True))
    f.append(rect(640, 120, 60, 70, fill=BG, stroke=INK, sw=1.5, rx=4))
    f.append(text(670, 160, "U2", size=11, color=INK, bold=True))

    # дроти від U1 (праворуч) — танові
    f.append(line(180, 140, 230, 140, color=WIRE, sw=2.2))
    f.append(line(180, 175, 230, 175, color=WIRE, sw=2.2))
    # прапорці-мітки U1 (вістрям ліворуч у дріт)
    f.append('<polygon points="230,140 240,131 282,131 282,149 240,149" '
             'fill="%s" stroke="%s" stroke-width="1.6"/>' % (FL_FILL, POS))
    f.append(text(260, 144, "+5В", size=10.5, color=POS, bold=True))
    f.append('<polygon points="230,175 240,166 282,166 282,184 240,184" '
             'fill="%s" stroke="%s" stroke-width="1.6"/>' % (FL_FILL, NEG))
    f.append(text(260, 179, "GND", size=10.5, color=NEG, bold=True))

    # дроти від U2 (ліворуч) — дзеркально
    f.append(line(590, 140, 640, 140, color=WIRE, sw=2.2))
    f.append(line(590, 175, 640, 175, color=WIRE, sw=2.2))
    f.append('<polygon points="590,140 580,131 538,131 538,149 580,149" '
             'fill="%s" stroke="%s" stroke-width="1.6"/>' % (FL_FILL, POS))
    f.append(text(560, 144, "+5В", size=10.5, color=POS, bold=True))
    f.append('<polygon points="590,175 580,166 538,166 538,184 580,184" '
             'fill="%s" stroke="%s" stroke-width="1.6"/>' % (FL_FILL, NEG))
    f.append(text(560, 179, "GND", size=10.5, color=NEG, bold=True))

    # концептуальні пунктирні стрілки «та сама назва → з'єднано»
    f.append(line(296, 140, 528, 140, color=POS, sw=1.6, dash="5,4"))
    f.append(line(296, 175, 528, 175, color=NEG, sw=1.6, dash="5,4"))
    f.append(text(410, 128, "та сама назва → з'єднано", size=10, color=POS, bold=True))

    # підсумкова рамка
    f.append(rect(150, 240, 520, 60, fill=GREEN_FILL, stroke=FIELD, sw=1.6, rx=10))
    f.append(text(410, 264,
                  "Так схему не захаращують довгими лініями: «+5В» тут і «+5В» там — це одне коло.",
                  size=11.5, color=INK, bold=True))
    f.append(text(410, 286,
                  "Особливо зручно для живлення (+5В, GND) і шин сигналів (напр. SDA, SCL).",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "net-labels.svg"), W, H, *f)


# ── 6. Нетлист: як редактор «зафарбовує» вузли ───────────────────────────────
def fig_netlist():
    W, H = 900, 420
    f = [text(W / 2, 30, "Нетлист: як редактор «зафарбовує» вузли сам",
              size=17.5, bold=True),
         text(W / 2, 51,
              "редактор будує граф пінів і дротів і шукає зв'язні компоненти — "
              "кожна стає одним ланцюгом (вузлом)",
              size=9.5, color=MUTED, italic=True)]

    # ── ліворуч: схема ──
    # зелений ланцюг
    f.append(line(120, 140, 260, 140, color=FIELD, sw=2.5))
    f.append(line(200, 140, 200, 210, color=FIELD, sw=2.5))
    f.append(junction(200, 140, r=4, color=FIELD))
    for (cx, cy) in ((120, 140), (264, 140), (200, 214)):
        f.append(junction(cx, cy, r=4, color=FIELD))
    f.append(text(120, 131, "R1.1", size=9, color=FIELD, bold=True))
    f.append(text(264, 131, "U1.in", size=9, color=FIELD, bold=True))
    f.append(text(200, 205, "+5В", size=9, color=FIELD, bold=True))
    f.append(text(200, 126, "крапка з'єднує", size=9, color=MUTED))

    # синій ланцюг
    f.append(line(120, 262, 260, 262, color=NEG, sw=2.5))
    f.append(junction(120, 262, r=4, color=NEG))
    f.append(junction(264, 262, r=4, color=NEG))
    f.append(text(120, 253, "R1.2", size=9, color=NEG, bold=True))
    f.append(text(264, 253, "U1.out", size=9, color=NEG, bold=True))
    f.append(text(190, 304, "схема (піни + дроти)", size=9, color=INK, bold=True))

    # стрілка 1 → граф
    f.append(arrow(330, 210, 400, 210, color=INK, sw=2.4))
    f.append(text(365, 198, "граф →", size=9, color=MUTED))

    # ── середня рамка: зв'язні компоненти ──
    f.append(rect(420, 120, 200, 180, fill="#fafafa", stroke=MUTED, sw=1.5, rx=10))
    f.append(text(520, 144, "зв'язні компоненти", size=10.5, color=INK, bold=True))
    f.append(text(438, 172, "• union(R1.1, +5В) [дріт]", size=9, color=FIELD, anchor="start"))
    f.append(text(438, 190, "• union(…, U1.in) [крапка]", size=9, color=FIELD, anchor="start"))
    f.append(text(438, 216, "• union(R1.2, U1.out) [дріт]", size=9, color=NEG, anchor="start"))
    f.append(text(438, 244, "кожен набір = 1 ланцюг", size=9.5, color=INK, bold=True, anchor="start"))
    f.append(text(438, 262, "той самий вузол", size=9, color=MUTED, anchor="start"))

    # стрілка 2 → нетлист
    f.append(arrow(640, 210, 710, 210, color=INK, sw=2.4))

    # ── права рамка: нетлист ──
    f.append(rect(720, 120, 160, 180, fill=GREEN_FILL, stroke=FIELD, sw=1.6, rx=10))
    f.append(text(800, 144, "НЕТЛИСТ", size=11, color=FIELD, bold=True))
    f.append(text(736, 172, "Net1 (+5В):", size=9.5, color=INK, bold=True, anchor="start"))
    f.append(text(746, 188, "R1.1, U1.in", size=9, color=MUTED, anchor="start"))
    f.append(text(736, 216, "Net2:", size=9.5, color=INK, bold=True, anchor="start"))
    f.append(text(746, 232, "R1.2, U1.out", size=9, color=MUTED, anchor="start"))
    f.append(text(736, 264, "+ мітки за іменем", size=9, color=MUTED, anchor="start"))
    f.append(text(736, 278, "зливаються в один", size=9, color=MUTED, anchor="start"))

    # ── нижня рамка ──
    f.append(rect(120, 348, 660, 42, fill=GREY_FILL, stroke=MUTED, sw=1.4, rx=8))
    f.append(text(450, 367,
                  "Це пошук зв'язних компонент графа: дроти й крапки «зливають» піни в набори;",
                  size=9, color=INK, bold=True))
    f.append(text(450, 383,
                  "однакові мітки-імена (+5В, GND) теж зливаються — навіть без намальованого дроту.",
                  size=9, color=MUTED, italic=True))
    render(os.path.join(IMG, "netlist.svg"), W, H, *f)


# ── 7. ERC: автоматична перевірка електричних правил ─────────────────────────
def fig_erc():
    W, H = 880, 400
    f = [text(W / 2, 30, "ERC: автоматична перевірка електричних правил",
              size=17.5, bold=True),
         text(W / 2, 51,
              "маючи нетлист, редактор перевіряє кожен ланцюг і пін на типові помилки — "
              "та не на «правильність задуму»",
              size=9.5, color=MUTED, italic=True)]

    # ── Case A: два виходи на ланцюг ──
    f.append(text(180, 96, "Два виходи на ланцюг", size=10.5, color=POS, bold=True))
    f.append(rect(108, 116, 42, 30, fill=BG, stroke=NEG, sw=1.6, rx=4))
    f.append(text(129, 135, "OUT", size=9, color=INK, bold=True))
    f.append(rect(210, 116, 42, 30, fill=BG, stroke=NEG, sw=1.6, rx=4))
    f.append(text(231, 135, "OUT", size=9, color=INK, bold=True))
    f.append(line(150, 131, 210, 131, color=INK, sw=2))
    f.append(text(180, 164, "⚠ конфлікт (закоротка)", size=9, color=POS, bold=True))

    # ── Case B: висячий вхід ──
    f.append(text(450, 96, "Висячий вхід", size=10.5, color=ORANGE, bold=True))
    f.append(rect(432, 116, 42, 30, fill=BG, stroke=FIELD, sw=1.6, rx=4))
    f.append(text(453, 135, "IN", size=9, color=INK, bold=True))
    f.append(line(432, 131, 400, 131, color=INK, sw=2))
    f.append(circle(400, 131, 3, fill="none", stroke=ORANGE, sw=1.5))
    f.append(text(450, 164, "⚠ нічим не керований", size=9, color=ORANGE, bold=True))

    # ── Case C: живлення без джерела ──
    f.append(text(712, 96, "Живлення без джерела", size=10.5, color=POS, bold=True))
    f.append(rect(690, 116, 44, 30, fill=BG, stroke=POS, sw=1.6, rx=4))
    f.append(text(712, 135, "VCC", size=9, color=INK, bold=True))
    f.append(text(712, 164, "⚠ пін живлення «висить»", size=9, color=POS, bold=True))

    # ── середня рамка: чого ERC не ловить ──
    f.append(rect(110, 206, 660, 84, fill=WARM_FILL, stroke=ORANGE, sw=1.5, rx=10))
    f.append(text(440, 230,
                  "Підступ, який ERC НЕ ловить: дроти, що ЛЕДЬ не торкаються",
                  size=10.5, color=INK, bold=True))
    f.append(line(300, 260, 400, 260, color=INK, sw=2.5))
    f.append(line(406, 260, 520, 260, color=INK, sw=2.5))
    f.append(text(403, 248, "зазор", size=9, color=POS, bold=True))
    f.append(text(440, 282,
                  "виглядає з'єднано, а насправді — два різні ланцюги (бо кінці не зійшлися)",
                  size=9, color=MUTED, italic=True))

    # ── нижня рамка ──
    f.append(rect(110, 308, 660, 40, fill=GREY_FILL, stroke=MUTED, sw=1.4, rx=8))
    f.append(text(440, 326,
                  "ERC — це перевірка ПРАВИЛ (конфлікти пінів, висячі входи), а не правильності задуму.",
                  size=9.5, color=INK, bold=True))
    f.append(text(440, 342,
                  "Він ловить «два виходи б'ються», та не «ти поставив не той резистор».",
                  size=9, color=MUTED, italic=True))
    render(os.path.join(IMG, "erc.svg"), W, H, *f)


if __name__ == "__main__":
    fig_node()
    fig_dot_vs_cross()
    fig_hop()
    fig_ambiguous()
    fig_net_labels()
    fig_netlist()
    fig_erc()
    print("OK: 7 SVG -> img/")
