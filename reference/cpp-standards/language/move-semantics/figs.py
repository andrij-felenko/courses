# -*- coding: utf-8 -*-
"""Фігури до теми «Семантика переміщення і rvalue-посилання»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Копія дублює буфер, переміщення переписує вказівник ──────────────────
def fig_copy_vs_move():
    W, H = 940, 430
    f = []

    # Панель «Копіювання»
    f.append(text(60, 100, "Копіювання", size=15, color=INK, anchor="start", bold=True))
    f.append(fitbox(60, 116, 140, 64, "a\nptr, size", size=13))
    f.append(arrow(203, 148, 247, 148))
    f.append(fitbox(250, 116, 150, 64, "буфер\n8 МіБ", size=13))
    f.append(arrow(403, 148, 496, 148, color=MUTED))
    f.append(fitbox(500, 116, 150, 64, "копія\n8 МіБ", size=13))
    f.append(arrow(766, 148, 654, 148))
    f.append(fitbox(770, 116, 140, 64, "b\nptr, size", size=13))
    f.append(text(470, 208, "нова ділянка в купі + побайтове перенесення",
                  size=11, color=MUTED))

    f.append(line(40, 236, 900, 236, color=MUTED, sw=1, dash="6 5"))

    # Панель «Переміщення»
    f.append(text(60, 285, "Переміщення", size=15, color=INK, anchor="start", bold=True))
    f.append(fitbox(60, 301, 140, 64, "a\nnullptr, 0", size=13))
    f.append(fitbox(250, 301, 150, 64, "той самий\nбуфер 8 МіБ", size=13,
                    fill="#e8f6ee", stroke=FIELD))
    f.append(text(586, 314, "3 присвоєння", size=11, color=MUTED))
    f.append(arrow(766, 333, 404, 333))
    f.append(fitbox(770, 301, 140, 64, "b\nptr, size", size=13))
    f.append(text(480, 396, "купа не чіпається; джерело лишається живим, але порожнім",
                  size=11, color=MUTED))

    render(os.path.join(OUT, 'copy-vs-move.svg'), W, H, *f,
           title="Що робить копіювання і що робить переміщення")


# ── 2. Таблиця зв'язування: категорія аргументу × тип параметра ─────────────
def fig_binding():
    W, H = 890, 372
    f = []

    cols = [(250, "T&"), (450, "const T&"), (650, "T&&")]
    CW, RH = 200, 75

    f.append(fitbox(40, 60, 210, 40, "аргумент \\ параметр", size=11,
                    fill="#eceff3", color=MUTED))
    for x, name in cols:
        f.append(fitbox(x, 60, CW, 40, name, size=14, fill="#eceff3", bold=True))

    rows = [
        (100, "lvalue без const\n(іменована змінна)",
         [("обирається", "win"), ("підходить", "ok"), ("не зв'яжеться", "no")]),
        (175, "lvalue із const\n(константа)",
         [("не зв'яжеться", "no"), ("обирається", "win"), ("не зв'яжеться", "no")]),
        (250, "rvalue\n(тимчасове, std::move)",
         [("не зв'яжеться", "no"), ("підходить", "ok"), ("обирається", "win")]),
    ]
    style = {
        "win": dict(fill="#e8f6ee", stroke=FIELD, color=INK, bold=True),
        "ok":  dict(fill="#f4f6f8", stroke=LINE, color=INK, bold=False),
        "no":  dict(fill="#ffffff", stroke=MUTED, color=MUTED, bold=False),
    }
    for y, label, cells in rows:
        f.append(fitbox(40, y, 210, RH, label, size=12, fill="#fbfcfd"))
        for (x, _), (txt, kind) in zip(cols, cells):
            f.append(fitbox(x, y, CW, RH, txt, size=12, **style[kind]))

    f.append(text(445, 352, "«обирається» — саме цей варіант виграє розв'язання перевантажень",
                  size=11, color=MUTED))

    render(os.path.join(OUT, 'binding.svg'), W, H, *f,
           title="Категорія аргументу вирішує, яка перевантага спрацює")


# ── 3. Чому vector іноді копіює замість переміщувати ────────────────────────
def fig_vector_grow():
    W, H = 900, 428
    f = []

    f.append(fitbox(300, 50, 300, 46, "vector виріс — треба новий буфер", size=13))
    f.append(arrow(450, 98, 450, 126))
    f.append(fitbox(255, 128, 390, 50, "конструктор переміщення T — noexcept?",
                    size=13, fill="#fff7e6", stroke=POS, bold=True))

    f.append(line(450, 180, 450, 210))
    f.append(line(215, 210, 685, 210))
    f.append(text(160, 216, "так", size=12, color=FIELD, bold=True))
    f.append(text(742, 216, "ні", size=12, color=POS, bold=True))
    f.append(arrow(215, 212, 215, 248))
    f.append(arrow(685, 212, 685, 248))

    f.append(fitbox(60, 250, 310, 76,
                    "переміщує елементи:\nперезапис вказівників,\nстарі порожніють",
                    size=12, fill="#e8f6ee", stroke=FIELD))
    f.append(fitbox(530, 250, 310, 76,
                    "копіює елементи:\nнове виділення для кожного,\nстарі лишаються цілі",
                    size=12, fill="#fdecea", stroke=POS))

    f.append(arrow(215, 328, 215, 356))
    f.append(arrow(685, 328, 685, 356))
    f.append(fitbox(60, 358, 310, 52, "дешево; кидати нема чому,\nтож відкат не потрібен",
                    size=12))
    f.append(fitbox(530, 358, 310, 52, "дорого; зате при винятку\nстарий буфер — точка відкату",
                    size=12))

    render(os.path.join(OUT, 'vector-grow.svg'), W, H, *f,
           title="Чому vector іноді копіює замість переміщувати")


# ── 4. Хроніка паперів: від auto_ptr_ref до C++11 ──────────────────────────
def fig_move_timeline():
    W, H = 1180, 470
    f = []
    f.append(text(W // 2, 46, "Шлях rvalue-посилання крізь папери WG21",
                  size=16, color=INK, bold=True))

    base = 250
    f.append(line(40, base, W - 40, base, color=MUTED, sw=2))

    items = [
        ("1997\nC++98: auto_ptr\nі милиця auto_ptr_ref", FILL, LINE),
        ("вересень 2002\nN1377: токен &&\nяк rvalue-посилання", "#e8f6ee", FIELD),
        ("вересень 2004\nN1690: && бере й lvalue\n→ згортання посилань", FILL, LINE),
        ("березень 2005\nN1770 — формулювання\nN1771 — бібліотека", FILL, LINE),
        ("грудень 2008\nN2812: відкат\nприв’язки до lvalue", "#fdecea", POS),
        ("2011\nC++11: переміщення\nв стандарті", "#e8f6ee", FIELD),
    ]
    x0, step, bw, bh = 110, 190, 176, 108
    for i, (s, fill, stroke) in enumerate(items):
        cx = x0 + i * step
        above = (i % 2 == 0)
        by = base - 55 - bh if above else base + 55
        f.append(fitbox(cx - bw / 2, by, bw, bh, s, size=12, fill=fill, stroke=stroke))
        if above:
            f.append(line(cx, by + bh, cx, base - 10, color=MUTED, sw=1.4))
        else:
            f.append(line(cx, base + 10, cx, by, color=MUTED, sw=1.4))
        f.append(circle(cx, base, 8, fill=BG, stroke=stroke, sw=2.4))

    render(os.path.join(OUT, 'hist-timeline.svg'), W, H, *f,
           title="Хроніка паперів WG21 про переміщення")


# ── 5. Анатомія одного push_back із перерозподілом (вставка proj-buffer-move) ─
def fig_push_back_anatomy():
    W, H = 950, 505
    f = []

    f.append(text(302, 62, "що відбувається всередині", size=13, color=MUTED, bold=True))
    f.append(text(750, 62, "що додають лічильники", size=13, color=MUTED, bold=True))

    steps = [
        (80, "тимчасовий Buffer(1 МіБ)\nстворюється у виразі виклику", "ctor ×1"),
        (154, "vector просить у купи сирий масив на 4 елементи —\nконструкторів там ще немає", "1 виділення"),
        (228, "новий елемент будується з тимчасового —\nце переміщення завжди", "move-ctor ×1"),
        (392, "старий масив звільняється,\nтимчасовий гине наприкінці виразу", "dtor ×3"),
    ]
    for y, left, right in steps:
        f.append(fitbox(52, y, 500, 56, left, size=13))
        f.append(fitbox(580, y, 340, 56, right, size=13, fill="#f4f6f8"))

    # крок 4 — розгалуження за noexcept
    f.append(fitbox(52, 302, 500, 72,
                    "два наявні елементи переносяться\nу новий масив", size=13))
    f.append(fitbox(580, 302, 340, 34, "noexcept: move-ctor ×2",
                    size=12, fill="#e8f6ee", stroke=FIELD, bold=True))
    f.append(fitbox(580, 340, 340, 34, "без noexcept: copy-ctor ×2 + 2 МіБ",
                    size=12, fill="#fdecea", stroke=POS, bold=True))

    for i, y in enumerate([80, 154, 228, 302, 392]):
        f.append(circle(26, y + 28, 15, fill=BG, stroke=MUTED, sw=1.2))
        f.append(text(26, y + 33, str(i + 1), size=13, color=MUTED, bold=True))

    for y1, y2 in [(136, 152), (210, 226), (284, 300), (374, 390)]:
        f.append(arrow(302, y1, 302, y2))

    f.append(text(475, 478,
                  "числа — для кроку з місткості 2 на 4; множник зростання — властивість реалізації",
                  size=11, color=MUTED))

    render(os.path.join(OUT, 'push-back-anatomy.svg'), W, H, *f,
           title="Що робить push_back, коли місткість вичерпано")


if __name__ == '__main__':
    fig_copy_vs_move()
    fig_binding()
    fig_vector_grow()
    fig_move_timeline()
    fig_push_back_anatomy()
    print("ok")
