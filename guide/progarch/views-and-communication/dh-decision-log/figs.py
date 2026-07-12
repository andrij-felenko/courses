# -*- coding: utf-8 -*-
"""Фігури до кроку «Наскрізний слід рішень» (progarch / views-and-communication).
Дві SVG: evaporation (проблема — «чому» випаровується без нитки) і radio-trace
(конкретний слід ADR-007 від драйвера до фітнес-функції). Генерує ./img/*.svg."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GREEN_FILL = "#eafaf1"
RED_FILL   = "#fdecea"
BLUE_FILL  = "#eaf0fd"


def down(cx, y1, y2, color=INK, sw=1.8):
    """Коротка стрілка вниз (у проміжку між рамками)."""
    return arrow(cx, y1, cx, y2, color=color, sw=sw)


def ghost(cx, cy, label, size=13):
    """Червона пунктирна рамка — «запису/якоря нема» (відсутній вузол графа)."""
    w = max(122, text_width(label, size) + 22)
    h = 34
    x, y = cx - w / 2, cy - h / 2
    r = ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" fill="%s" '
         'stroke="%s" stroke-width="2" stroke-dasharray="5 4"/>' % (x, y, w, h, RED_FILL, POS))
    r += text(cx, cy + size * 0.35, label, size=size, color=POS)
    return r


def cap(cx, y, s):
    return text(cx, y, s, size=12, italic=True, color=MUTED)


def head(cx, y, s):
    return text(cx, y, s, size=15, bold=True, color=INK)


def fig_evaporation():
    W, H = 900, 420
    parts = []
    # роздільник між панелями
    parts.append(line(450, 46, 450, 404, color=MUTED, sw=1.2, dash="4 5"))
    # заголовки панелей
    parts.append(text(225, 64, "БЕЗ СЛІДУ", size=15, bold=True, color=INK))
    parts.append(text(675, 64, "НАСКРІЗНИЙ СЛІД", size=15, bold=True, color=INK))

    # ── ліва панель: код лишається, «чому» випаровується ──
    b, w, h = textbox(225, 130, ["ЧОМУ?", "сили · відкинуті варіанти"],
                      size=13, color=MUTED, stroke=MUTED, fill=FILL)
    parts.append(b)
    # слід випаровування — пунктир угору, без голови
    parts.append(line(225, 231, 225, 158, color=MUTED, sw=1.6, dash="3 5"))
    b, w, h = textbox(225, 250, "структура / черга", size=14)
    parts.append(b)
    parts.append(line(225, 267, 225, 328, color=LINE, sw=1.5))
    b, w, h = textbox(225, 345, "код", size=14)
    parts.append(b)

    # ── права панель: «чому» — ланка в ланцюгу ──
    b, w, h = textbox(675, 108, "драйвер", size=14)
    parts.append(b)
    parts.append(down(675, 125, 176))
    b, w, h = textbox(675, 193, "ADR-007  —  тут «чому»", size=14,
                      stroke=FIELD, fill=GREEN_FILL, sw=2, bold=True)
    parts.append(b)
    parts.append(down(675, 210, 261))
    b, w, h = textbox(675, 278, "структура / черга", size=14)
    parts.append(b)
    parts.append(down(675, 295, 341))
    b, w, h = textbox(675, 358, "код", size=14)
    parts.append(b)

    render(os.path.join(IMG, 'evaporation.svg'), W, H, *parts,
           title="Без нитки «чому» випаровується; ланкою — тримається")


def fig_radio_trace():
    W, H = 820, 660
    parts = []
    cx = 410
    bw = 470
    x = cx - bw / 2
    rungs = [
        (["ДРАЙВЕР — дерево корисності",
          "нове залізо без правки ядра (В,В)"], None),
        (["ПРИПУЩЕННЯ — журнал припущень",
          "«обраний стандарт переможе» — не факт"], None),
        (["РІШЕННЯ · ADR-007",
          "радіо за портом DevicePort; старт на Zigbee"], "red"),
        (["В'Ю — контейнерна (DH на папері)",
          "межу-адаптер видно однією рамкою"], None),
        (["КОД",
          "DevicePort / ZigbeeAdapter — «Zigbee» в одному файлі"], None),
        (["ФІТНЕС-ФУНКЦІЯ — сторож",
          "логіка хаба не імпортує радіо → падає в CI"], None),
    ]
    centers = [96, 192, 288, 384, 480, 576]
    bh = 62
    for (lines, mark), cy in zip(rungs, centers):
        y = cy - bh / 2
        if mark == "red":
            parts.append(fitbox(x, y, bw, bh, lines, size=14,
                                 stroke=POS, fill=RED_FILL, sw=2.2))
        else:
            parts.append(fitbox(x, y, bw, bh, lines, size=14))
    # ланцюг-нитка вниз (між рамками)
    for c1, c2 in zip(centers, centers[1:]):
        parts.append(down(cx, c1 + bh / 2, c2 - bh / 2, color=INK, sw=2))

    # ліворуч: читаєш угору — ЧОМУ
    parts.append(arrow(70, 560, 70, 95, color=NEG, sw=2))
    b, w, h = textbox(70, 66, "ЧОМУ", size=13, bold=True,
                      color=NEG, stroke=NEG, fill=BLUE_FILL)
    parts.append(b)
    # праворуч: читаєш униз — ДЕ
    parts.append(arrow(750, 95, 750, 560, color=FIELD, sw=2))
    b, w, h = textbox(750, 590, "ДЕ", size=13, bold=True,
                      color=FIELD, stroke=FIELD, fill=GREEN_FILL)
    parts.append(b)

    render(os.path.join(IMG, 'radio-trace.svg'), W, H, *parts,
           title="Слід рішення ADR-007 — від драйвера до гарди")


def fig_shift():
    """Зсув погляду: 1992 (структура + слабке обґрунтування) → 2005 (рішення —
    тіло, структура — лише слід). Фігура/тло міняються місцями. → architecture-as-decisions.svg"""
    W, H = 900, 430
    parts = []
    parts.append(line(450, 50, 450, 408, color=MUTED, sw=1.2, dash="4 6"))
    parts.append(text(225, 66, "1992 · Перрі й Вульф", size=15, bold=True, color=INK))
    parts.append(text(675, 66, "2004–2005 · Бош і Янсен", size=15, bold=True, color=INK))

    # ── ліворуч: структура тверда, обґрунтування — бліда третя нога ──
    b, w, h = textbox(225, 135, ["СТРУКТУРА", "елементи · форма"],
                      size=13, stroke=INK, fill=FILL)
    parts.append(b)
    parts.append(line(225, 163, 225, 222, color=MUTED, sw=1.4, dash="3 5"))
    b, w, h = textbox(225, 250, ["обґрунтування", "«чому» — третя нога"],
                      size=13, stroke=MUTED, fill=BG, color=MUTED)
    parts.append(b)
    parts.append(mtext(225, 322,
                       ["«Чому» назвали — та лишили примітивом.",
                        "Втратив його → дрейф і ерозія."],
                       size=12, color=MUTED, lh=1.35))

    # ── праворуч: рішення — тверде тіло, структура — лише їхній слід ──
    b, w, h = textbox(675, 135, ["НАБІР РІШЕНЬ", "перша-класний артефакт"],
                      size=13, stroke=FIELD, fill=GREEN_FILL)
    parts.append(b)
    parts.append(arrow(675, 163, 675, 220, color=INK, sw=1.8))
    b, w, h = textbox(675, 250, ["структура", "= лише слід рішень"],
                      size=13, stroke=MUTED, fill=BG, color=MUTED)
    parts.append(b)
    parts.append(mtext(675, 322,
                       ["Рішення — тіло архітектури.",
                        "Не спіймав одразу → випаровується."],
                       size=12, color=MUTED, lh=1.35))

    render(os.path.join(IMG, 'architecture-as-decisions.svg'), W, H, *parts,
           title="Що вважали архітектурою: зсув 1992 → 2005")


def fig_trace_breaks():
    """Чотири способи, у які рветься слід (проєкт-перевірка): висяча згадка, сирота,
    обірваний ланцюг, цикл замін. 2×2 сітка. → trace-breaks.svg"""
    W, H = 940, 700
    parts = []
    # хрест-роздільник між чотирма клітинами
    parts.append(line(470, 46, 470, 688, color=MUTED, sw=1.1, dash="4 5"))
    parts.append(line(30, 378, 910, 378, color=MUTED, sw=1.1, dash="4 5"))

    # ── TL · Висяча згадка: коміт/діаграма → ADR, якого нема ──
    parts.append(head(245, 80, "Висяча згадка"))
    b, w, h = textbox(245, 152, "коміт / діаграма", size=13)
    parts.append(b)
    parts.append(arrow(245, 172, 245, 214, color=POS, sw=1.9))
    parts.append(ghost(245, 250, "ADR-042 — нема"))
    parts.append(cap(245, 330, "посилання веде в порожнечу"))

    # ── TR · Сирота: ухвалений ADR без жодного якоря ──
    parts.append(head(695, 80, "Сирота"))
    b, w, h = textbox(695, 152, "ADR-014 · ухвалено", size=13,
                      stroke=FIELD, fill=GREEN_FILL, sw=2)
    parts.append(b)
    parts.append(arrow(695, 172, 695, 214, color=POS, sw=1.9))
    parts.append(ghost(695, 250, "якоря нема"))
    parts.append(cap(695, 330, "ухвалене ні до чого не прив'язане"))

    # ── BL · Обірваний ланцюг: superseded → ADR, якого нема ──
    parts.append(head(245, 422, "Обірваний ланцюг"))
    b, w, h = textbox(245, 496, "ADR-031 · superseded", size=13)
    parts.append(b)
    parts.append(arrow(245, 516, 245, 560, color=POS, sw=1.9))
    parts.append(text(302, 543, "замінено", size=11, color=MUTED))
    parts.append(ghost(245, 598, "ADR-099 — нема"))
    parts.append(cap(245, 664, "ланцюг упирається в порожнечу"))

    # ── BR · Цикл замін: ADR-050 ↔ ADR-051 ──
    parts.append(head(695, 422, "Цикл замін"))
    b, w, h = textbox(695, 480, "ADR-050", size=13, stroke=POS, fill=RED_FILL, sw=2)
    parts.append(b)
    b, w, h = textbox(695, 606, "ADR-051", size=13, stroke=POS, fill=RED_FILL, sw=2)
    parts.append(b)
    parts.append(arrow(651, 502, 651, 584, color=POS, sw=1.9))   # 050 → 051
    parts.append(arrow(739, 584, 739, 502, color=POS, sw=1.9))   # 051 → 050
    parts.append(cap(695, 664, "кожен замінює одне одного"))

    render(os.path.join(IMG, 'trace-breaks.svg'), W, H, *parts,
           title="Чотири розриви нитки сліду, що їх ловить обхідник")


if __name__ == '__main__':
    fig_evaporation()
    fig_radio_trace()
    fig_shift()
    fig_trace_breaks()
    print("ok: evaporation.svg, radio-trace.svg, architecture-as-decisions.svg, trace-breaks.svg")
