# -*- coding: utf-8 -*-
"""Фігури до теми «Заплямоване ядро: прапорці taint»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def families():
    """Три роди прапорців taint і питання, яке кожен рід ставить до звіту."""
    W, H = 1180, 470
    out = ''

    cols = [
        (200, 'Сторонній код у ядрі',
         'P  O  E  F  R  C  K  X',
         ['виконується код, якого немає',
          'в дереві ядра або якого ядро',
          'не перевіряло'],
         'Питання: чи міг цей код\nзіпсувати пам\'ять раніше?',
         POS),
        (590, 'Ядро вже спотикалося',
         'D  W  B  L  M',
         ['збій, попередження, зіпсована',
          'сторінка, зависання або',
          'апаратна помилка вже були'],
         'Питання: де в журналі\nнайперша з цих подій?',
         NEG),
        (980, 'Середовище не типове',
         'S  A  I  T  N  U  J',
         ['залізо поза специфікацією,',
          'підмінені таблиці, обхід вади',
          'прошивки, тестовий режим'],
         'Питання: чи однакові умови\nу вас і в розробника?',
         FIELD),
    ]

    for cx, head, letters, body, quest, tone in cols:
        frag, w, h = textbox(cx, 70, head, size=17, bold=True, min_w=330,
                             fill='#ffffff', stroke=tone, sw=2.2)
        out += frag
        frag, w, h = textbox(cx, 145, letters, size=20, bold=True, min_w=330,
                             fill='#f4f6f8', stroke=tone, sw=1.8, color=tone)
        out += frag
        out += mtext(cx, 215, body, size=14, color=INK, lh=1.45)
        frag, w, h = textbox(cx, 350, quest, size=14, min_w=330,
                             fill='#ffffff', stroke=MUTED, sw=1.4, color=MUTED)
        out += frag

    out += mtext(W / 2, 440,
                 ['Маска одна на все ядро: біти лише додаються й не знімаються до перезавантаження.'],
                 size=15, color=INK, bold=True)

    return render(os.path.join(IMG, 'taint-families.svg'), W, H, out,
                  title='Три роди прапорців taint')


def timeline():
    """Мітки накопичуються від першої події; вікно підозри відкривається на ній."""
    W, H = 1180, 470
    out = ''

    y_axis = 250
    x0, x1 = 90, 1100
    out += line(x0, y_axis, x1, y_axis, color=MUTED, sw=2)

    events = [
        (200, '02:10', 'завантажено зовнішній\nмодуль (DKMS)', 'O E', POS),
        (450, '02:11', 'модуль записав\nповз свою структуру', 'O E', MUTED),
        (700, '04:30', 'спрацював WARN()\nу файловій системі', 'O E W', NEG),
        (960, '05:47', 'oops у сторонній\nзадачі — та, що в звіті', 'O E W D', POS),
    ]

    for x, when, what, mask, tone in events:
        out += circle(x, y_axis, 9, fill='#ffffff', stroke=tone)
        out += line(x, y_axis - 9, x, y_axis - 46, color=MUTED, sw=1.2, dash='4,4')
        out += line(x, y_axis + 9, x, y_axis + 46, color=MUTED, sw=1.2, dash='4,4')
        frag, w, h = textbox(x, 120, what, size=13.5, min_w=230,
                             fill='#ffffff', stroke=tone, sw=1.6)
        out += frag
        out += text(x, y_axis - 22, when, size=13, color=MUTED)
        frag, w, h = textbox(x, y_axis + 78, 'маска: ' + mask, size=14, bold=True,
                             min_w=170, fill=FILL, stroke=LINE, sw=1.4)
        out += frag

    out += arrow(200, 400, 1010, 400, color=POS)
    out += text(605, 428, 'вікно підозри: усе після першої мітки', size=15, color=POS, bold=True)

    return render(os.path.join(IMG, 'taint-timeline.svg'), W, H, out,
                  title='Одна аварія, чотири події: що бачить заголовок звіту')


def header_positions():
    """Поле «Tainted:» у заголовку oops: двадцять фіксованих позицій."""
    W, H = 1180, 380
    out = ''

    letters = ['P', 'F', 'S', 'R', 'M', 'B', 'U', 'D', 'A', 'W',
               'C', 'I', 'O', 'E', 'L', 'K', 'X', 'T', 'N', 'J']
    on_bits = {0, 9, 12, 13}

    out += text(W / 2, 46, 'Поле «Tainted:» у заголовку oops — рівно двадцять позицій',
                size=17, bold=True)
    out += text(W / 2, 74, 'позиція = номер біта; порядок ніколи не міняється',
                size=13, color=MUTED)

    x0, stride, cw, cy0, cell_h = 50, 54, 46, 110, 56
    for i, ltr in enumerate(letters):
        x = x0 + i * stride
        on = i in on_bits
        out += rect(x, cy0, cw, cell_h,
                    fill='#fdecea' if on else BG,
                    stroke=POS if on else MUTED, sw=2.0 if on else 1.2)
        out += text(x + cw / 2, cy0 + cell_h / 2 + 7, ltr, size=19, bold=True,
                    color=POS if on else MUTED)
        out += text(x + cw / 2, cy0 + cell_h + 22, str(i), size=12, color=MUTED)

    frag, w, h = textbox(320, 250, 'біт стоїть → друкується літера', size=14,
                         min_w=430, fill='#fdecea', stroke=POS, sw=1.6, color=POS)
    out += frag
    frag, w, h = textbox(860, 250, 'біт не стоїть → пробіл; на позиції 0 — літера G',
                         size=14, min_w=430, fill=BG, stroke=MUTED, sw=1.4, color=MUTED)
    out += frag

    out += text(W / 2, 340, 'Приклад: стоять P, W, O, E  →  1 + 512 + 4096 + 8192 = 12801',
                size=15, bold=True)

    return render(os.path.join(IMG, 'taint-header-positions.svg'), W, H, out,
                  title='Двадцять позицій поля Tainted у заголовку oops')


def two_masks():
    """Звідки береться біт, крізь які двері проходить і в яку з двох масок падає."""
    W, H = 1240, 530
    out = ''

    sources = [
        (210, 'Метадані модуля',
         ['ліцензія · intree · підпис · test',
          '→ P   O   E   N   C'], POS),
        (620, 'Код ядра',
         ['WARN() · oops · BUG() · add_taint()',
          '→ W   D   B   L   M'], NEG),
        (1030, 'Простір користувача',
         ['запис у /proc/sys/kernel/tainted',
          '→ будь-який біт, лише додаванням'], FIELD),
    ]

    for cx, head, body, tone in sources:
        frag, w, h = textbox(cx, 100, [head] + body, size=13.5, min_w=360,
                             fill='#ffffff', stroke=tone, sw=1.8)
        out += frag

    frag, w, h = textbox(620, 250,
                         ['add_taint(flag, lockdep_ok) — єдині двері',
                          'тут-таки спрацьовує panic_on_taint'],
                         size=15, bold=True, min_w=600, fill=FILL, stroke=LINE, sw=2)
    out += frag

    out += arrow(210, 140, 490, 218, color=MUTED)
    out += arrow(620, 140, 620, 218, color=MUTED)
    out += arrow(1030, 140, 750, 218, color=MUTED)

    frag, w, h = textbox(350, 412,
                         ['tainted_mask — одна на все ядро',
                          'живе до перезавантаження, біти не знімаються',
                          'читати: /proc/sys/kernel/tainted, заголовок oops'],
                         size=13.5, min_w=520, fill='#ffffff', stroke=POS, sw=1.8)
    out += frag

    frag, w, h = textbox(890, 412,
                         ['mod->taints — своя в кожного модуля',
                          'зникає разом із rmmod',
                          'читати: /sys/module/<назва>/taint, /proc/modules'],
                         size=13.5, min_w=520, fill='#ffffff', stroke=MUTED, sw=1.8)
    out += frag

    out += arrow(500, 285, 350, 370, color=POS)
    out += arrow(740, 285, 890, 370, color=MUTED)
    out += text(175, 330, 'усі плями', size=13, color=POS)
    out += text(1055, 330, 'лише плями модулів', size=13, color=MUTED)

    out += text(620, 500,
                'Маска ядра переживає вивантаження модуля — тому в звіті лишається слід від того, кого вже немає.',
                size=15, color=INK, bold=True)

    return render(os.path.join(IMG, 'taint-two-masks.svg'), W, H, out,
                  title='Джерела плям і дві маски')


if __name__ == '__main__':
    print(families())
    print(timeline())
    print(two_masks())
    print(header_positions())
