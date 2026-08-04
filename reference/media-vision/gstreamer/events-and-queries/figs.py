# -*- coding: utf-8 -*-
"""Фігури до теми «Події й запити на падах: сигналізація вздовж конвеєра»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


# ── 1. Типова маршрутизація: напрямок вирішує, куди елемент розмножить подію ──
def fig_event_routing():
    W, H = 1120, 480
    f = []

    f.append(text(280, 60, 'подія за течією', size=15, bold=True))
    f.append(text(840, 60, 'подія проти течії', size=15, bold=True))

    # ── ліва панель: один вхід, три виходи ──
    ib, iw, ih = textbox(110, 240, ['від', 'верхнього'], size=12, min_w=120)
    f.append(ib)
    eb, ew, eh = textbox(290, 240, ['елемент', 'із трьома', 'виходами'], size=13, min_w=170)
    f.append(eb)
    f.append(arrow(110 + iw / 2 + 6, 240, 290 - ew / 2 - 6, 240))
    f.append(text(200, 218, 'sink', size=11, color=MUTED))

    for cy in (140, 240, 340):
        ob, ow, oh = textbox(480, cy, 'src', size=12, min_w=110)
        f.append(arrow(290 + ew / 2 + 6, 240, 480 - ow / 2 - 6, cy, color=NEG))
        f.append(ob)
    f.append(text(290, 400, 'розмножується на всі src-пади', size=12, color=NEG))

    # ── роздільник панелей ──
    f.append(line(570, 90, 570, 420, color=MUTED, sw=1.4, dash='7,6'))

    # ── права панель: три входи, один вихід ──
    ob2, ow2, oh2 = textbox(1020, 240, ['від', 'нижнього'], size=12, min_w=120)
    f.append(ob2)
    eb2, ew2, eh2 = textbox(840, 240, ['елемент', 'із трьома', 'входами'], size=13, min_w=170)
    f.append(eb2)
    f.append(arrow(1020 - ow2 / 2 - 6, 240, 840 + ew2 / 2 + 6, 240))
    f.append(text(930, 218, 'src', size=11, color=MUTED))

    for cy in (140, 240, 340):
        sb, sw_, sh = textbox(650, cy, 'sink', size=12, min_w=110)
        f.append(arrow(840 - ew2 / 2 - 6, 240, 650 + sw_ / 2 + 6, cy, color=POS))
        f.append(sb)
    f.append(text(840, 400, 'розмножується на всі sink-пади', size=12, color=POS))

    render(os.path.join(OUT, 'event-routing.svg'), W, H, *f)


# ── 2. Серіалізований сигнал стоїть у черзі, позачерговий іде повз неї ───────
def fig_serialized_vs_oob():
    W, H = 1040, 430
    f = []

    up, uw, uh = textbox(120, 210, ['верхній', 'елемент'], size=13, min_w=160)
    dn, dw, dh = textbox(910, 210, ['нижній', 'елемент'], size=13, min_w=160)

    # черга
    f.append(text(500, 148, 'черга: queue max-size-time = 200 мс', size=12, color=MUTED))
    f.append(rect(265, 162, 470, 96, fill=BG))

    cells = [(305, ['подія'], '#fdecea', POS),
             (375, ['буфер'], FILL, LINE),
             (445, ['буфер'], FILL, LINE),
             (515, ['буфер'], FILL, LINE),
             (585, ['буфер'], FILL, LINE),
             (655, ['буфер'], FILL, LINE)]
    for cx, lines, fill, stroke in cells:
        cb, cw, ch = textbox(cx, 210, lines, size=11, min_w=62, fill=fill, stroke=stroke)
        f.append(cb)

    f.append(arrow(120 + uw / 2 + 6, 210, 259, 210))
    f.append(arrow(741, 210, 910 - dw / 2 - 6, 210))
    f.append(up)
    f.append(dn)

    # позачерговий шлях — над чергою
    f.append(line(120, 210 - uh / 2 - 4, 120, 96, color=POS, sw=1.8, dash='6,5'))
    f.append(line(120, 96, 910, 96, color=POS, sw=1.8, dash='6,5'))
    f.append(arrow(910, 96, 910, 210 - dh / 2 - 6, color=POS))
    f.append(text(515, 80, 'позачергово: негайно, у нитці відправника', size=13, color=POS))

    f.append(text(500, 310, 'серіалізовано: місце в черзі за буферами — доїде через 200 мс',
                  size=13))
    f.append(text(500, 340, 'а якщо черга повна й ніхто не забирає — не доїде ніколи',
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'serialized-vs-oob.svg'), W, H, *f)


# ── 3. Липкі події живуть на паді й програються новому партнерові ────────────
def fig_sticky_replay():
    W, H = 1100, 430
    f = []

    sb, sw_, sh = textbox(250, 150, ['src-пад tee тримає:',
                                     '40 · stream-start',
                                     '50 · caps',
                                     '70 · segment'], size=13, min_w=320)
    f.append(sb)

    nb, nw, nh = textbox(830, 150, ['новий src-пад,',
                                    'створений о 10-й хвилині:',
                                    'потоку не бачив'], size=13, min_w=320)
    f.append(nb)

    f.append(arrow(250 + sw_ / 2 + 8, 150, 830 - nw / 2 - 8, 150))
    f.append(text(540, 128, 'віддає весь набір', size=12, color=NEG))

    f.append(text(540, 248, 'порядок вручення — за номером типу', size=12, color=MUTED))

    seq = [(160, ['1 · stream-start']),
           (400, ['2 · caps']),
           (640, ['3 · segment']),
           (900, ['і аж тоді', 'перший буфер'])]
    geom = []
    for cx, lines in seq:
        b, w, h = textbox(cx, 330, lines, size=13, min_w=200)
        geom.append((cx, w))
        f.append(b)
    for i in range(len(geom) - 1):
        x1 = geom[i][0] + geom[i][1] / 2 + 6
        x2 = geom[i + 1][0] - geom[i + 1][1] / 2 - 6
        f.append(arrow(x1, 330, x2, 330))

    render(os.path.join(OUT, 'sticky-replay.svg'), W, H, *f)


# ── 4. Запит: контейнер опитує всі приймачі й зводить відповіді ──────────────
def fig_query_fill():
    W, H = 1120, 470
    f = []

    ab, aw, ah = textbox(120, 200, ['програма'], size=13, min_w=170)
    bb, bw, bh = textbox(390, 200, ['конвеєр', '(контейнер)'], size=13, min_w=200)
    f.append(arrow(120 + aw / 2 + 6, 200, 390 - bw / 2 - 6, 200))
    f.append(text(255, 178, 'тривалість?', size=12, color=NEG))
    f.append(ab)
    f.append(bb)

    v1, w1, h1 = textbox(720, 110, ['приймач відео'], size=13, min_w=220)
    v2, w2, h2 = textbox(720, 290, ['приймач звуку'], size=13, min_w=220)
    f.append(arrow(390 + bw / 2 + 6, 185, 720 - w1 / 2 - 6, 115))
    f.append(arrow(390 + bw / 2 + 6, 215, 720 - w2 / 2 - 6, 285))
    f.append(v1)
    f.append(v2)
    f.append(text(560, 82, '12.400 с', size=12, color=MUTED))
    f.append(text(560, 330, '12.960 с', size=12, color=MUTED))

    fb, fw, fh = textbox(990, 200, ['зведення:', 'найбільше з двох', '12.960 с'],
                         size=13, min_w=210, fill='#eaf0fd', stroke=NEG)
    f.append(arrow(720 + w1 / 2 + 6, 125, 990 - fw / 2 - 6, 180))
    f.append(arrow(720 + w2 / 2 + 6, 275, 990 - fw / 2 - 6, 220))
    f.append(fb)

    # відповідь повертається тим самим об'єктом
    f.append(line(990, 200 + fh / 2 + 6, 990, 410, color=NEG, sw=1.6))
    f.append(line(990, 410, 120, 410, color=NEG, sw=1.6))
    f.append(arrow(120, 410, 120, 200 + ah / 2 + 6, color=NEG))
    f.append(text(555, 396, 'заповнений об\'єкт запиту повертається тому, хто питав',
                  size=12, color=NEG))

    render(os.path.join(OUT, 'query-fill.svg'), W, H, *f)


# ── 5. Дві осі: напрямок × серіалізація ─────────────────────────────────────
def fig_two_axes():
    W, H = 1060, 480
    f = []

    f.append(text(470, 92, 'за течією', size=15, bold=True))
    f.append(text(810, 92, 'проти течії', size=15, bold=True))

    rows = [
        (210, ['серіалізовано:', 'місце в черзі'],
         ['caps · segment · tag', 'eos · gap',
          'запит на алокацію', 'запит-бар\'єр'],
         ['кінець скидання', '(іде в обидва боки)']),
        (370, ['позачергово:', 'негайно'],
         ['початок скидання', '(іде в обидва боки)'],
         ['seek · qos · latency', 'reconfigure · step',
          'запити про тривалість,', 'позицію, планування']),
    ]

    for cy, head, left, right in rows:
        hb, hw, hh = textbox(170, cy, head, size=13, min_w=230, fill=BG, stroke=MUTED)
        f.append(hb)
        lb, lw, lh = textbox(470, cy, left, size=12, min_w=300)
        f.append(lb)
        rb, rw, rh = textbox(810, cy, right, size=12, min_w=300,
                             fill='#eaf0fd', stroke=NEG)
        f.append(rb)

    f.append(text(530, 452, 'місце сигналу в цій сітці визначає всю його поведінку',
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'two-axes.svg'), W, H, *f)


# ── 6. Розкладка бітів у числі типу події (до api-довідки) ──────────────────
def fig_event_type_bits():
    W, H = 1180, 510
    f = []

    f.append(text(590, 48, 'тип події — одне число: номер, зсунутий на 8 бітів, плюс прапорці',
                  size=14, bold=True))

    x0, cw = 110, 60
    bits = '0011001000001110'          # GST_EVENT_CAPS = 0x320E = 12814

    f.append(text(350, 100, 'номер типу — 8 старших бітів', size=13, bold=True))
    f.append(text(830, 100, 'прапорці — 8 молодших бітів', size=13, bold=True))

    for i, b in enumerate(bits):
        cx = x0 + cw * i + cw / 2
        f.append(text(cx, 128, str(15 - i), size=11, color=MUTED))
        if i < 8:
            f.append(rect(x0 + cw * i, 140, cw, 54, fill=FILL, stroke=LINE, rx=4))
            f.append(text(cx, 174, b, size=17, bold=True))
        else:
            on = (b == '1')
            f.append(rect(x0 + cw * i, 140, cw, 54,
                          fill='#eaf0fd' if on else BG, stroke=NEG, rx=4))
            f.append(text(cx, 174, b, size=17, bold=True,
                          color=NEG if on else MUTED))

    f.append(line(590, 92, 590, 212, color=MUTED, sw=1.4, dash='6,5'))

    f.append(text(350, 226, '50 = 0b00110010', size=12, color=MUTED))
    f.append(text(830, 226, '14 = DOWNSTREAM | SERIALIZED | STICKY', size=12, color=MUTED))

    names = [('біт 0', 'UPSTREAM'), ('біт 1', 'DOWNSTREAM'), ('біт 2', 'SERIALIZED'),
             ('біт 3', 'STICKY'), ('біт 4', 'STICKY_MULTI')]
    for i, (n, s) in enumerate(names):
        bx, bw, bh = textbox(134 + 228 * i, 300, [n, s], size=12, min_w=210,
                             fill=BG, stroke=NEG)
        f.append(bx)

    steps = [(300, ['номер 50', '50 · 256 = 12800']),
             (590, ['прапорці', '2 | 4 | 8 = 14']),
             (880, ['разом', '12800 + 14 = 12814'])]
    for cx, lines in steps:
        sb, sw_, sh = textbox(cx, 395, lines, size=13, min_w=260)
        f.append(sb)

    f.append(text(590, 470,
                  'GST_EVENT_CAPS у журналі й налагоджувачі видно саме як 12814',
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'event-type-bits.svg'), W, H, *f)


# ── 7. Вимір трасувальника: дві власні події, дві точки спостереження ───────
def fig_probe_timeline():
    W, H = 1180, 580
    f = []

    def X(t):                      # t — мілісекунди від миті надсилання
        return 300 + 3.0 * t

    f.append(text(600, 48, 'дві власні події, послані в ту саму мить: де кожна виринула',
                  size=15, bold=True))

    # ── дві доріжки: вхід і вихід тієї самої черги ──
    l1, l1w, l1h = textbox(150, 190, ['queue.sink', 'вхід у чергу'], size=12, min_w=140)
    l2, l2w, l2h = textbox(150, 440, ['queue.src', 'вихід із черги'], size=12, min_w=140)
    f.append(line(270, 190, 1110, 190, color=MUTED, sw=1.4))
    f.append(line(270, 440, 1110, 440, color=MUTED, sw=1.4))
    f.append(l1)
    f.append(l2)

    # ── вісь часу ──
    f.append(line(270, 505, 1110, 505, color=MUTED, sw=1.4))
    for t in (0, 50, 100, 150, 200, 250):
        f.append(line(X(t), 499, X(t), 511, color=MUTED, sw=1.4))
        f.append(text(X(t), 532, str(t), size=12, color=MUTED))
    f.append(text(690, 558, 'мс від миті надсилання', size=12, color=MUTED))

    # ── позачергова: та сама мить на обох доріжках ──
    f.append(line(X(0), 450, X(0), 495, color=MUTED, sw=1.2, dash='4,4'))
    f.append(line(X(0), 199, X(0), 283, color=NEG, sw=1.8, dash='6,5'))
    f.append(arrow(X(0), 347, X(0), 431, color=NEG))
    f.append(circle(X(0), 190, 10, fill='#eaf0fd', stroke=NEG, sw=2))
    f.append(circle(X(0), 440, 10, fill='#eaf0fd', stroke=NEG, sw=2))
    ob, ow, oh = textbox(300, 315, ['позачергова подія:',
                                    'вхід і вихід — одна мить,',
                                    'та сама нитка T1'],
                         size=12, min_w=190, fill=BG, stroke=NEG)
    f.append(ob)

    # ── серіалізована: заїхала в чергу й виїхала на 200 мс пізніше ──
    f.append(line(X(230), 450, X(230), 495, color=MUTED, sw=1.2, dash='4,4'))
    f.append(arrow(413, 199, 982, 431, color=POS))
    f.append(circle(X(35), 190, 10, fill='#fdecea', stroke=POS, sw=2))
    f.append(circle(X(230), 440, 10, fill='#fdecea', stroke=POS, sw=2))
    sb, sw_, sh = textbox(600, 385, ['серіалізована подія:',
                                     '30 мс до пробудження нитки',
                                     '+ 200 мс черги = 230 мс'],
                          size=12, min_w=190, fill=BG, stroke=POS)
    f.append(sb)

    render(os.path.join(OUT, 'probe-timeline.svg'), W, H, *f)


fig_event_routing()
fig_serialized_vs_oob()
fig_sticky_replay()
fig_query_fill()
fig_two_axes()
fig_event_type_bits()
fig_probe_timeline()
print('ok')
