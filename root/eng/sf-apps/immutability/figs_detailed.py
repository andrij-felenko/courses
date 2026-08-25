# -*- coding: utf-8 -*-
"""Фігури для детальної статті «Незмінність як прийом дизайну».
Окремий генератор, щоб не чіпати figs.py базової статті. Вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def shallow_vs_deep():
    """Дві панелі: поверхнева незмінність (заморожено лише обгортку, а внутрішній
    список мінливий — правка сусіда протікає) проти глибокої/транзитивної."""
    W, H = 820, 500
    frags = []

    def panel(y0, title, collab_label, collab_fill, collab_stroke,
              actor_kind, footer, footer_color, collide):
        f = []
        f.append(text(W / 2, y0, title, size=16, bold=True))
        cy = y0 + 82
        # обгортка (сама завжди «заморожена» — зелена)
        f.append(fitbox(70, cy - 32, 200, 64, "обгортка\n(поля const)", size=13,
                        fill="#eafaf0", stroke=FIELD, sw=2.0, bold=True))
        # внутрішній об'єкт, на який показує поле
        f.append(fitbox(350, cy - 32, 220, 64, collab_label, size=13,
                        fill=collab_fill, stroke=collab_stroke, sw=2.0, bold=True))
        # поле-посилання обгортка -> внутрішній
        f.append(arrow(272, cy, 348, cy, color=LINE, sw=2.0))
        f.append(text(310, cy - 14, "поле →", size=12, color=MUTED))
        # зовнішній діяч
        f.append(fitbox(640, cy - 24, 150, 48, "чужий код", size=13, fill=FILL, stroke=LINE))
        col = POS if actor_kind == 'write' else FIELD
        f.append(arrow(638, cy, 572, cy, color=col, sw=2.0))
        lbl = "пише" if actor_kind == 'write' else "лише читає"
        f.append(text(606, cy - 14, lbl, size=12, color=col, bold=(actor_kind == 'write')))
        if collide:
            f.append(text(460, cy - 46, "⚡ правка протікає", size=13, color=POS, bold=True))
        f.append(text(W / 2, cy + 58, footer, size=13, color=footer_color, bold=True))
        return f

    frags += panel(46, "Поверхнева незмінність: заморожено лише верх",
                   "внутрішній список\nМІНЛИВИЙ", "#fdecea", POS, 'write',
                   "правка сусіда протікає крізь «незмінну» обгортку", POS, True)
    frags.append(line(40, 262, W - 40, 262, color=MUTED, sw=1, dash='4,5'))
    frags += panel(300, "Глибока (транзитивна) незмінність: заморожено до дна",
                   "внутрішній список\nтеж незмінний", "#eafaf0", FIELD, 'read',
                   "мутувати нічого — ділити безпечно на будь-яку глибину", FIELD, False)
    render(os.path.join(OUT, 'shallow-vs-deep.svg'), W, H, *frags)


def identity_vs_equality():
    """Об'єкт-значення (важить лише вміст, різні примірники взаємозамінні) проти
    сутності (важить, який саме — однаковий вміст не робить їх одним)."""
    W, H = 800, 410
    f = []
    # верх: об'єкт-значення
    f.append(text(W / 2, 40, "Об’єкт-значення: важить лише вміст", size=16, bold=True))
    f.append(fitbox(150, 78, 170, 74, "Money\n100 UAH\n@адреса A", size=13,
                    fill="#eafaf0", stroke=FIELD, sw=2.0))
    f.append(fitbox(480, 78, 170, 74, "Money\n100 UAH\n@адреса B", size=13,
                    fill="#eafaf0", stroke=FIELD, sw=2.0))
    f.append(text(400, 106, "≡", size=26, color=FIELD, bold=True))
    f.append(text(400, 134, "рівні за значенням", size=12, color=MUTED))
    f.append(text(W / 2, 182, "різні примірники, та сама цінність — байдуже, котрий саме",
                  size=13, color=FIELD, bold=True))
    # роздільник
    f.append(line(40, 210, W - 40, 210, color=MUTED, sw=1, dash='4,5'))
    # низ: сутність
    f.append(text(W / 2, 250, "Сутність: важить, ЯКА саме", size=16, bold=True))
    f.append(fitbox(150, 288, 170, 74, "Рахунок #A1\nбаланс 100\nвідкритий 2020", size=13,
                    fill=FILL, stroke=LINE, sw=2.0))
    f.append(fitbox(480, 288, 170, 74, "Рахунок #A2\nбаланс 100\nвідкритий 2020", size=13,
                    fill=FILL, stroke=LINE, sw=2.0))
    f.append(text(400, 316, "≠", size=26, color=POS, bold=True))
    f.append(text(400, 344, "різні сутності", size=12, color=POS))
    f.append(text(W / 2, 392, "той самий вміст, але два різні рахунки — не переплутати",
                  size=13, color=POS, bold=True))
    render(os.path.join(OUT, 'identity-vs-equality.svg'), W, H, *f)


def core_shell_cell():
    """Функціональне ядро на незмінних значеннях + єдина мінлива комірка-посилання
    на краю: читач бере знімок без замків, писар CAS-підмінює версію."""
    W, H = 820, 410
    f = []
    f.append(text(W / 2, 34, "Мутабельність зведена в одну видну точку", size=16, bold=True))
    # вхід
    f.append(fitbox(165, 66, 190, 44, "вхід: подія / запит", size=13, fill=FILL, stroke=LINE))
    f.append(arrow(260, 112, 260, 150, color=LINE, sw=2.0))
    # ядро
    f.append(rect(110, 152, 300, 150, fill="#eafaf0", stroke=FIELD, sw=2.2))
    f.append(text(260, 196, "Незмінне ядро", size=15, color=INK, bold=True))
    f.append(text(260, 224, "чисті обчислення", size=13, color=INK))
    f.append(text(260, 248, "над незмінними значеннями", size=13, color=INK))
    # комірка
    f.append(rect(560, 165, 210, 140, fill="#fdecea", stroke=POS, sw=2.2))
    f.append(text(665, 205, "Комірка стану", size=15, color=INK, bold=True))
    f.append(text(665, 232, "ЄДИНА мінлива точка", size=12, color=INK))
    f.append(text(665, 258, "посилання → vN", size=13, color=INK))
    # стрілки між ядром і коміркою
    f.append(arrow(558, 200, 412, 200, color=NEG, sw=2.0))
    f.append(text(485, 186, "знімок vN (читання)", size=12, color=NEG))
    f.append(arrow(412, 274, 558, 274, color=POS, sw=2.0))
    f.append(text(485, 260, "нова vN+1 → CAS", size=12, color=POS))
    # примітка + підпис
    f.append(text(665, 330, "зміна лише тут", size=12, color=POS, bold=True))
    f.append(text(W / 2, 384,
                  "Читач бере незмінний знімок без замків; писар підміняє посилання однією атомарною дією.",
                  size=12, color=MUTED))
    render(os.path.join(OUT, 'core-shell-cell.svg'), W, H, *f)


if __name__ == '__main__':
    shallow_vs_deep()
    identity_vs_equality()
    core_shell_cell()
    print('done')
