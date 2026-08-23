# -*- coding: utf-8 -*-
"""Фігури до теми «Monolith-first проти «спершу сервіси»» (root/course/progarch/monolith-vs-microservices/monolith-first-or-never)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREEN_TINT = "#eafaf0"
RED_TINT = "#fdecea"
BLUE_TINT = "#eef2fb"
NEUT = "#f7f8fa"

def path_elem(d, color=LINE, sw=1.5, fill="none"):
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"/>' % (d, color, sw, fill)

def fig_boundary_refactoring_cost():
    """Залежність сумарних витрат на розробку від нестабільності доменних меж (Monolith vs Microservices)."""
    W, H = 960, 480
    frags = []

    frags.append(text(W / 2, 30, "Залежність сумарної вартості змін від нестабільності доменних меж", size=15, bold=True))

    # Вісі графіку
    ox, oy = 100, 400
    w_axis, h_axis = 780, 320
    frags.append(line(ox, oy, ox + w_axis, oy, color=LINE, sw=2))
    frags.append(line(ox, oy, ox, oy - h_axis, color=LINE, sw=2))

    # Підписи вісей
    frags.append(text(ox + w_axis - 20, oy + 35, "Нестабільність меж домену (Domain Volatility)", size=12, color=INK, bold=True, anchor="end"))
    frags.append(text(ox - 65, oy - h_axis + 20, "Вартість змін (TCO & Friction)", size=12, color=INK, bold=True, anchor="start"))

    # Позначки на осі X
    frags.append(text(ox + 120, oy + 20, "Низька (зрілий домен)", size=11, color=MUTED))
    frags.append(text(ox + 650, oy + 20, "Висока (зелений газон / стартап)", size=11, color=MUTED))

    # Крива моноліта (низька базова ціна, повільне зростання при зміні меж)
    frags.append(path_elem("M %d %d Q %d %d %d %d" % (ox + 40, oy - 40, ox + 400, oy - 80, ox + 740, oy - 150),
                           color=NEG, sw=3, fill="none"))
    frags.append(text(ox + 600, oy - 170, "Модульний моноліт (Monolith-First)", size=13, color=NEG, bold=True, anchor="start"))

    # Крива мікросервісів (висока початкова ціна, експоненціальний вибух при рефакторингу меж)
    frags.append(path_elem("M %d %d Q %d %d %d %d" % (ox + 40, oy - 150, ox + 380, oy - 170, ox + 740, oy - 330),
                           color=POS, sw=3, fill="none"))
    frags.append(text(ox + 520, oy - 315, "Спершу мікросервіси (Microservices-First)", size=13, color=POS, bold=True, anchor="start"))

    # Точка перетину (поріг доцільності)
    cx, cy = ox + 300, oy - 100
    frags.append(circle(cx, cy, 6, fill=FIELD, stroke=LINE, sw=1.5))
    frags.append(line(cx, cy, cx, oy, color=FIELD, sw=1.5, dash="4 4"))

    # Текстова вставка-пояснення для зеленого газону
    frags.append(rect(ox + 460, oy - 110, 310, 80, fill=RED_TINT, stroke=POS, sw=1.2, rx=6))
    frags.append(text(ox + 615, oy - 90, "Пастка передчасних сервісів:", size=11, color=POS, bold=True))
    frags.append(text(ox + 615, oy - 70, "Рефакторинг помилкових меж у мережі", size=10, color=INK))
    frags.append(text(ox + 615, oy - 52, "коштує в 10–50 разів дорожче!", size=10, color=POS, bold=True))

    render(os.path.join(IMG, "boundary-refactoring-cost.svg"), W, H, *frags,
           title="Залежність вартості рефакторингу від нестабільності доменних меж")


def fig_modular_monolith_isolation():
    """Спектр архітектурних стилів: спагеті-моноліт, модульний моноліт та мікросервіси."""
    W, H = 960, 440
    frags = []

    frags.append(text(W / 2, 30, "Архітектурний спектр: від спагеті до ізольованих мікросервісів", size=15, bold=True))

    styles = [
        ("1. Спагеті-моноліт", "«Big Ball of Mud»", "Хаотичні виклики коду,\nпрямі SQL JOIN між таблицями,\nнульова модуляризація.", RED_TINT, POS),
        ("2. Модульний моноліт", "«Monolith-First» (Дефолт)", "Суворі мовні модулі (Façade),\nізольовані схеми БД в 1 процесі,\nвиклики в пам'яті (150 нс).", GREEN_TINT, FIELD),
        ("3. Мікросервіси", "«Service-First»", "Фізичні мережеві межі,\nокремі процеси й бази даних,\nRPC/Event затримка (5 мс).", BLUE_TINT, NEG)
    ]

    for i, (title, subtitle, desc, bg, stroke_color) in enumerate(styles):
        cx = 160 + i * 320
        cy = 190
        frags.append(rect(cx - 140, cy - 110, 280, 250, fill=bg, stroke=stroke_color, sw=2, rx=10))
        frags.append(text(cx, cy - 80, title, size=14, bold=True, color=INK))
        frags.append(text(cx, cy - 60, subtitle, size=12, italic=True, color=stroke_color))

        lines = desc.split('\n')
        for j, line in enumerate(lines):
            frags.append(text(cx, cy - 10 + j * 22, line, size=11, color=INK))

    # Пояснювальний висновок знизу
    frags.append(rect(40, 340, 880, 75, fill=NEUT, stroke=LINE, sw=1.2, rx=8))
    frags.append(text(W / 2, 362, "💡 Ключовий висновок для зеленого газону", size=13, bold=True, color=INK))
    frags.append(text(W / 2, 390, "Альтернативою поганим мікросервісам є не спагеті-моноліт, а МОДУЛЬНИЙ моноліт. Збереження чистоти меж у пам'яті дає гнучкість без мережевого податку.", size=11, color=MUTED))

    render(os.path.join(IMG, "modular-monolith-isolation.svg"), W, H, *frags,
           title="Спектр архітектурних стилів")


def fig_greenfield_decision_tree():
    """Дерево рішень для вибору архітектури зеленого газону."""
    W, H = 980, 520
    frags = []

    frags.append(text(W / 2, 30, "Дерево рішень для зеленого газону: Monolith-First vs Сервіси", size=15, bold=True))

    # Старт
    frags.append(rect(390, 60, 200, 45, fill=NEUT, stroke=LINE, sw=1.8, rx=6))
    frags.append(text(490, 87, "Новий проєкт («зелений газон»)", size=12, bold=True))

    frags.append(arrow(490, 105, 490, 140, color=LINE, sw=2))

    # Питання 1
    frags.append(rect(240, 140, 500, 60, fill=BLUE_TINT, stroke=NEG, sw=1.8, rx=8))
    frags.append(text(490, 165, "Чи доведені й стабільні межі домену з 1-го дня?", size=12, bold=True))
    frags.append(text(490, 185, "(Переписання v2 / готова галузева модель / досвідчена команда)", size=10, color=MUTED))

    # Гілка 1: НІ -> Моноліт-First
    frags.append(arrow(240, 170, 140, 170, color=POS, sw=2))
    frags.append(text(190, 160, "Ні (невизначеність)", size=10, color=POS, bold=True))
    frags.append(rect(20, 140, 120, 60, fill=GREEN_TINT, stroke=FIELD, sw=2, rx=8))
    frags.append(text(80, 165, "MONOLITH-FIRST", size=11, bold=True, color=FIELD))
    frags.append(text(80, 185, "(Модульний моноліт)", size=10, color=MUTED))

    # Гілка 1: ТАК -> Питання 2
    frags.append(arrow(490, 200, 490, 250, color=FIELD, sw=2))
    frags.append(text(505, 225, "Так", size=10, color=FIELD, bold=True))

    # Питання 2
    frags.append(rect(240, 250, 500, 65, fill=BLUE_TINT, stroke=NEG, sw=1.8, rx=8))
    frags.append(text(490, 275, "Чи є фізична асиметрія (PCI-DSS, C++/GPU vs Python, 80+ інженерів)?", size=12, bold=True))
    frags.append(text(490, 298, "(Закон Конвея на старті / жорсткі регуляторні чи апаратні вимоги)", size=10, color=MUTED))

    # Гілка 2: ТАК -> Greenfield Microservices
    frags.append(arrow(740, 282, 840, 282, color=FIELD, sw=2))
    frags.append(text(785, 272, "Так (Вимоги)", size=10, color=FIELD, bold=True))
    frags.append(rect(840, 250, 120, 65, fill=GREEN_TINT, stroke=FIELD, sw=2, rx=8))
    frags.append(text(900, 277, "GREENFIELD", size=11, bold=True, color=FIELD))
    frags.append(text(900, 297, "SERVICES", size=11, bold=True, color=FIELD))

    # Гілка 2: НІ -> Моноліт-First
    frags.append(arrow(490, 315, 490, 365, color=POS, sw=2))
    frags.append(text(505, 340, "Ні (немає фізичної потреби)", size=10, color=POS, bold=True))

    # Результат Дефолту
    frags.append(rect(310, 365, 360, 75, fill=GREEN_TINT, stroke=FIELD, sw=2.5, rx=10))
    frags.append(text(490, 392, "ГОЛОВНИЙ ДЕФОЛТ: МОДУЛЬНИЙ МОНОЛІТ", size=13, bold=True, color=FIELD))
    frags.append(text(490, 420, "Будуємо суворі модулі в 1 процесі → розпилюємо лише за потребою", size=11, color=MUTED))

    render(os.path.join(IMG, "greenfield-decision-tree.svg"), W, H, *frags,
           title="Дерево рішень для вибору архітектури зеленого газону")

if __name__ == "__main__":
    fig_boundary_refactoring_cost()
    fig_modular_monolith_isolation()
    fig_greenfield_decision_tree()
