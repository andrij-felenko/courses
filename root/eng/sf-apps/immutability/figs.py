# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def shared_mutable_vs_immutable():
    """Дві панелі: угорі мінливий об'єкт (запис від двох аліасів → зіткнення/баг),
    унизу незмінний (усі троє лише читають → безпечно ділити)."""
    W, H = 760, 620

    # три джерела ліворуч у кожній панелі; центральна комірка праворуч
    src_x = 150            # центр стовпчика джерел
    cell_x = 560           # центр комірки-об'єкта
    src_w, src_h = 150, 46
    cell_w, cell_h = 150, 96

    def panel(y0, title, cell_label, cell_fill, cell_stroke, rows, collide, footer, footer_color):
        f = []
        # заголовок панелі
        f.append(text(W / 2, y0, title, size=16, bold=True))
        gy = y0 + 46            # y першого джерела
        gap = 66                # крок між джерелами
        cy = gy + gap           # центр комірки — навпроти середнього джерела
        # комірка-об'єкт
        f.append(fitbox(cell_x - cell_w / 2, cy - cell_h / 2, cell_w, cell_h,
                        cell_label, size=14, fill=cell_fill, stroke=cell_stroke, sw=2.2, bold=True))
        # джерела + стрілки
        for i, (name, kind) in enumerate(rows):
            sy = gy + i * gap
            f.append(fitbox(src_x - src_w / 2, sy - src_h / 2, src_w, src_h,
                            name, size=13, fill=FILL, stroke=LINE))
            col = POS if kind == 'write' else NEG
            # стрілка від правого краю джерела до лівого краю комірки
            ax1 = src_x + src_w / 2 + 4
            ay1 = sy
            ax2 = cell_x - cell_w / 2 - 6
            ay2 = cy + (sy - cy) * 0.34      # трохи сходяться до комірки, не збігаючись
            f.append(arrow(ax1, ay1, ax2, ay2, color=col, sw=2.0))
            # мітка read/write — над початком стрілки, поза лініями
            lbl = 'пише' if kind == 'write' else 'читає'
            f.append(text(ax1 + 96, ay1 - 9, lbl, size=12, color=col, bold=(kind == 'write')))
        # знак зіткнення на комірці (лише для мінливої)
        if collide:
            f.append(text(cell_x, cy - cell_h / 2 - 12, '⚡ конфлікт запису',
                          size=13, color=POS, bold=True))
        # підпис-висновок під коміркою
        f.append(text(cell_x, cy + cell_h / 2 + 30, footer, size=13, color=footer_color, bold=True))
        return f

    top = panel(
        44, 'Мінливий об’єкт: право писати відкрите всім',
        'спільний\nоб’єкт', '#fdecea', POS,
        [('функція A', 'write'), ('функція B', 'read'), ('функція C', 'write')],
        collide=True,
        footer='баг: чужа зміна прилітає здалеку', footer_color=POS)

    bot = panel(
        340, 'Незмінний об’єкт: писати не може ніхто',
        'незмінний\nоб’єкт', '#eafaf0', FIELD,
        [('функція A', 'read'), ('функція B', 'read'), ('функція C', 'read')],
        collide=False,
        footer='безпечно ділити без замків', footer_color=FIELD)

    # роздільник між панелями
    sep = line(40, 320, W - 40, 320, color=MUTED, sw=1, dash='4,5')

    render(os.path.join(OUT, 'shared-mutable-vs-immutable.svg'), W, H, sep, *top, *bot)


if __name__ == '__main__':
    shared_mutable_vs_immutable()
    print('done')
