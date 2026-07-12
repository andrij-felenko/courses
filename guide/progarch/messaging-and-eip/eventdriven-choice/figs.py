# -*- coding: utf-8 -*-
"""Фігури до кроку «Вибір подієвого підходу»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREYFILL = "#eef0f3"   # «вимкнене» положення — приглушене
GREENF   = "#eafaf0"   # «увімкнене» положення — зелене поле


def fig_three_switches():
    """Три незалежні тумблери: комунікація / читання-запис / джерело правди."""
    W, H = 1060, 470
    frags = []

    # розділювачі трьох панелей
    for sx in (360, 700):
        frags.append(line(sx, 40, sx, 440, color=MUTED, sw=1, dash="4,6"))

    panels = [
        (185, "Комунікація · EDA",
         "як компонент дізнається,\nщо щось сталося?",
         "ВИМК · дефолт\nпрямий виклик\n(спитай сам)",
         "УВІМК\nреакція на подію\n(тобі скажуть)"),
        (525, "Читання ⁄ запис · CQRS",
         "одна модель на запис\nі читання — чи дві?",
         "ВИМК · дефолт\nодна модель\nна обидва боки",
         "УВІМК\nдві моделі:\nкоманда ⁄ запит"),
        (865, "Джерело правди · ES",
         "правда — це поточний\nстан чи журнал змін?",
         "ВИМК · дефолт\nзберігаю\nпоточний стан",
         "УВІМК\nзберігаю журнал,\nстан = згортка"),
    ]

    for cx, title, question, off, on in panels:
        frags.append(text(cx, 62, title, size=16, bold=True))
        frags.append(mtext(cx, 96, question, size=12.5, color=MUTED, lh=1.25))
        # ВИМК (приглушене)
        frags.append(textbox(cx, 210, off, size=13, fill=GREYFILL,
                             stroke=MUTED, color=MUTED, min_w=210)[0])
        # маленька «непов'язаність» — стрілка-риска вниз до УВІМК
        frags.append(line(cx, 258, cx, 300, color=MUTED, sw=1, dash="3,4"))
        # УВІМК (зелене поле)
        frags.append(textbox(cx, 340, on, size=13, fill=GREENF,
                             stroke=FIELD, min_w=210)[0])

    render(os.path.join(IMG, "three-switches.svg"), W, H, *frags)


def fig_reversibility_gradient():
    """Вісь зворотності: EDA/CQRS — двобічні двері; ES — однобічні."""
    W, H = 1060, 360
    frags = []
    AXY = 168

    # підкладка-градієнт (світле ліворуч -> темніше праворуч) під віссю
    band = [(95, 380, "#f7f8fa"), (380, 700, "#e8ebee"), (700, 965, "#d6dbe1")]
    for x0, x1, col in band:
        frags.append(rect(x0, AXY - 15, x1 - x0, 30, fill=col, stroke=col, sw=0.5, rx=0))
    # сама вісь
    frags.append(arrow(95, AXY, 965, AXY, color=INK, sw=2))

    # кінцеві ярлики під віссю (правий — осторонь від дроп-лінії ES при x=860)
    frags.append(text(150, AXY + 40, "двобічні двері", size=12.5, color=MUTED, italic=True))
    frags.append(text(150, AXY + 58, "вернувся дешево", size=11.5, color=MUTED, italic=True))
    frags.append(text(945, AXY + 40, "однобічні", size=12.5, color=POS, italic=True))
    frags.append(text(945, AXY + 58, "двері", size=11.5, color=POS, italic=True))

    # вузли на осі
    def node(x, fill, stroke):
        return circle(x, AXY, 8, fill=fill, stroke=stroke, sw=2)

    # EDA
    frags.append(line(280, 128, 280, AXY - 8, color=MUTED, sw=1))
    frags.append(textbox(280, 96, "EDA\nяк компоненти говорять —\nпереставляється легко",
                         size=12.5, fill=GREENF, stroke=FIELD, min_w=250)[0])
    frags.append(node(280, GREENF, FIELD))
    # CQRS
    frags.append(line(555, 128, 555, AXY - 8, color=MUTED, sw=1))
    frags.append(textbox(555, 96, "CQRS\nдві моделі можна злити\nназад — з зусиллям",
                         size=12.5, fill=GREENF, stroke=FIELD, min_w=250)[0])
    frags.append(node(555, GREENF, FIELD))
    # ES (однобічні двері)
    frags.append(node(860, "#fdecea", POS))
    frags.append(line(860, AXY + 8, 860, 232, color=POS, sw=1))
    frags.append(textbox(860, 268, "ES · події = правда назавжди\nсхему лише доповнити,\nне переписати минуле",
                         size=12.5, fill="#fdecea", stroke=POS, min_w=270)[0])

    render(os.path.join(IMG, "reversibility-gradient.svg"), W, H, *frags)


REDF = "#fdecea"   # «конфлікт ⁄ проблема» — червоне поле


def fig_birth_glue_split():
    """Історія конфляції: три народження → злиплося в „event-driven" → розчеплено."""
    W, H = 1120, 520
    frags = []

    # ── ярусні підписи ліворуч (italic, приглушені) ─────────────────────────
    frags.append(text(72, 72, "народилися", size=11, color=MUTED, italic=True))
    frags.append(text(72, 88, "нарізно", size=11, color=MUTED, italic=True))
    frags.append(text(72, 250, "злиплося", size=11, color=MUTED, italic=True))
    frags.append(text(72, 416, "свідомо", size=11, color=MUTED, italic=True))
    frags.append(text(72, 432, "розчепили", size=11, color=MUTED, italic=True))

    # ── три народження (верхній ярус) ───────────────────────────────────────
    births = [
        (235, "1988 · CQS\nБертран Меєр\nмасштаб: один метод"),
        (560, "2005 · Event Sourcing\nМартін Фаулер\nмасштаб: сховище"),
        (885, "2010 · CQRS\nҐреґ Янг\nмасштаб: компонент"),
    ]
    for cx, s in births:
        frags.append(textbox(cx, 80, s, size=13, min_w=210)[0])

    # ── конфляція (середній ярус, червоне поле) ─────────────────────────────
    frags.append(textbox(560, 250,
                         "„event-driven“\nодне слово — три ідеї, три роки, три масштаби",
                         size=13, fill=REDF, stroke=POS, min_w=360)[0])

    # стрілки-сходження: три народження → конфляція
    frags.append(arrow(235, 116, 455, 222, color=MUTED, sw=1.6))
    frags.append(arrow(560, 116, 560, 222, color=MUTED, sw=1.6))
    frags.append(arrow(885, 116, 665, 222, color=MUTED, sw=1.6))

    # ── розчеплення (нижній ярус, зелене поле) ──────────────────────────────
    frags.append(textbox(340, 425,
                         "2012 · Ґреґ Янг\n„CQRS is not an Architecture“\nES — лише варіант сховища",
                         size=13, fill=GREENF, stroke=FIELD, min_w=250)[0])
    frags.append(textbox(790, 425,
                         "2017 · Мартін Фаулер + ThoughtWorks\n„What do you mean by Event-Driven?“\nслово → чотири окремі патерни",
                         size=13, fill=GREENF, stroke=FIELD, min_w=250)[0])

    # стрілки-роздвоєння: конфляція → два розчеплення
    frags.append(line(560, 275, 560, 336, color=MUTED, sw=1.6))
    frags.append(arrow(560, 336, 340, 388, color=MUTED, sw=1.6))
    frags.append(arrow(560, 336, 790, 388, color=MUTED, sw=1.6))

    render(os.path.join(IMG, "birth-glue-split.svg"), W, H, *frags)


def fig_four_systems():
    """2×2: вісь джерела правди × вісь читання → чотири системи й ціна кожної."""
    W, H = 1140, 560
    frags = []
    frags.append(text(W / 2, 34, "Одна дія над замком — дві осі, чотири системи",
                      size=18, bold=True))
    # підписи осей
    frags.append(text(700, 66, "джерело правди  →", size=14, bold=True, color=MUTED))
    frags.append(text(140, 150, "читання  ↓", size=14, bold=True, color=MUTED))
    # заголовки колонок (вісь правди): ліва — вимк (сіре), права — увімк (зелене)
    frags.append(textbox(485, 108, "CRUD · перезапис стану", size=13.5,
                         fill=GREYFILL, stroke=MUTED, color=MUTED, min_w=360)[0])
    frags.append(textbox(915, 108, "журнал подій · append + згортка", size=13.5,
                         fill=GREENF, stroke=FIELD, min_w=360)[0])
    # заголовки рядків (вісь читання)
    frags.append(textbox(140, 245, "та сама модель\nзгортка на читанні", size=12.5,
                         fill=GREYFILL, stroke=MUTED, color=MUTED, min_w=200)[0])
    frags.append(textbox(140, 455, "окрема проєкція\nCQRS", size=12.5,
                         fill=GREENF, stroke=FIELD, min_w=200)[0])

    def cell(x, y, code, title, bill, fill):
        w, h = 410, 190
        out = rect(x, y, w, h, fill=fill, stroke=LINE, sw=1.5, rx=8)
        out += text(x + 26, y + 36, code, size=18, bold=True, color=MUTED, anchor="start")
        out += text(x + w / 2, y + 42, title, size=16, bold=True)
        yy = y + 82
        for ln, col in bill:
            out += text(x + 34, yy, ln, size=13, color=col, anchor="start")
            yy += 26
        return out

    frags.append(cell(280, 150, "✗ ✗", "Звичайний CRUD — дефолт", [
        ("сховище: O(1) на замок", MUTED),
        ("лаг читання: 0", MUTED),
        ("аудит ⁄ переграти: нема", POS),
        ("схема подій: ні до чого", MUTED),
    ], FILL))
    frags.append(cell(710, 150, "✓ ✗", "ES, одна модель", [
        ("сховище: журнал росте", MUTED),
        ("лаг: 0, та згортка O(n)", POS),
        ("аудит ⁄ переграти: Є", FIELD),
        ("схема подій: замкнена", POS),
    ], "#f0f7f2"))
    frags.append(cell(280, 360, "✗ ✓", "CRUD + CQRS", [
        ("сховище: + читацька модель", MUTED),
        ("лаг читання: є", POS),
        ("аудит ⁄ переграти: нема", POS),
        ("пастка: подвійний запис", POS),
    ], "#f0f7f2"))
    frags.append(cell(710, 360, "✓ ✓", "ES + CQRS — дует", [
        ("сховище: журнал + проєкція", MUTED),
        ("лаг читання: є", POS),
        ("аудит ⁄ переграти: Є", FIELD),
        ("схема подій: замкнена", POS),
    ], GREENF))

    render(os.path.join(IMG, "four-systems.svg"), W, H, *frags)


def fig_dual_write():
    """Подвійний запис (стан+подія) як небезпека — і transactional outbox як лік."""
    W, H = 1140, 450
    frags = []
    frags.append(line(570, 40, 570, 410, color=MUTED, sw=1, dash="4,6"))

    # ── ліворуч: небезпека ──
    frags.append(text(285, 40, "✗  Подвійний запис — два сховища, одна надія",
                      size=15, bold=True, color=POS))
    frags.append(textbox(285, 92, "handler: send(lock)", size=13,
                         fill=FILL, stroke=LINE, min_w=230)[0])
    frags.append(arrow(245, 118, 168, 208, color=LINE, sw=1.6))
    frags.append(arrow(325, 118, 402, 208, color=POS, sw=1.6))
    frags.append(textbox(165, 242, "БД: state=locked\n✓ записано", size=12.5,
                         fill=GREENF, stroke=FIELD, min_w=185)[0])
    frags.append(textbox(405, 242, "шина: DoorLocked\n✗ впала", size=12.5,
                         fill=REDF, stroke=POS, color=POS, min_w=185)[0])
    frags.append(mtext(285, 328, "процес упав МІЖ кроками:\nстан пішов уперед, подія загубилась —\nдва сховища тихо розійшлися",
                       size=12.5, color=POS, lh=1.35))

    # ── праворуч: лік ──
    frags.append(text(855, 40, "✓  Один запис + outbox — одна транзакція",
                      size=15, bold=True, color=FIELD))
    frags.append(textbox(855, 92, "handler: send(lock)", size=13,
                         fill=FILL, stroke=LINE, min_w=230)[0])
    frags.append(arrow(855, 118, 855, 166, color=LINE, sw=1.6))
    frags.append(textbox(855, 210, "ОДНА локальна транзакція:\n• journal += DoorLocked\n• outbox  += DoorLocked",
                         size=12.5, fill=GREENF, stroke=FIELD, min_w=300)[0])
    frags.append(arrow(855, 262, 855, 310, color=LINE, sw=1.6))
    frags.append(textbox(855, 344, "relay (окремо, з повтором):\nчитає outbox → шина, ідемпотентно",
                         size=12.5, fill=FILL, stroke=LINE, min_w=300)[0])

    render(os.path.join(IMG, "dual-write-outbox.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_three_switches()
    fig_reversibility_gradient()
    fig_birth_glue_split()
    fig_four_systems()
    fig_dual_write()
    print("OK: three-switches.svg, reversibility-gradient.svg, birth-glue-split.svg, "
          "four-systems.svg, dual-write-outbox.svg")
