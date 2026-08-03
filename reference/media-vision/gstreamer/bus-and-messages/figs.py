# -*- coding: utf-8 -*-
"""Фігури до теми «Шина повідомлень: події й помилки конвеєра»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


# ── 1. Два канали: дані всередині конвеєра, повідомлення назовні ────────────
def fig_two_channels():
    W, H = 960, 430
    f = []

    # підписи двох світів
    f.append(text(270, 48, 'потокові нитки конвеєра', size=14, bold=True, color=MUTED))
    f.append(text(790, 48, 'нитка застосунку', size=14, bold=True, color=MUTED))

    # межа ниток — двома відрізками, щоб не різати напис усередині шини
    f.append(line(600, 66, 600, 192, color=MUTED, sw=1.6, dash='7,6'))
    f.append(line(600, 280, 600, 400, color=MUTED, sw=1.6, dash='7,6'))

    # коробка конвеєра
    f.append(rect(40, 70, 440, 320, fill='#ffffff'))
    f.append(text(60, 94, 'конвеєр', size=13, color=MUTED, anchor='start'))

    els = [('джерело', 150), ('декодер', 235), ('приймач', 320)]
    boxes = []
    for name, cy in els:
        b, w, h = textbox(180, cy, name, size=14)
        f.append(b)
        boxes.append((cy, w, h))

    # потік даних згори вниз
    for i in range(len(boxes) - 1):
        y1 = boxes[i][0] + boxes[i][2] / 2
        y2 = boxes[i + 1][0] - boxes[i + 1][2] / 2
        f.append(arrow(180, y1 + 2, 180, y2 - 2))
    f.append(text(268, 190, 'буфери й події', size=12, anchor='start'))
    f.append(text(268, 208, 'ідуть тут', size=12, anchor='start', color=MUTED))

    # повідомлення назовні
    for cy, w, h in boxes:
        f.append(line(180 + w / 2 + 4, cy, 496, cy, color=POS, sw=1.5, dash='5,5'))
        f.append(arrow(496, cy, 524, cy, color=POS, sw=1.6))

    bb, bw, bh = textbox(600, 235, ['шина', '(черга', 'повідомлень)'],
                         size=13, fill='#fdecea', stroke=POS, min_w=140)
    f.append(bb)

    f.append(arrow(600 + bw / 2 + 6, 235, 700, 235))
    ab, aw, ah = textbox(800, 235, ['головний цикл', 'і обробник'], size=13, min_w=180)
    f.append(ab)

    render(os.path.join(OUT, 'two-channels.svg'), W, H, *f)


# ── 2. Шлях одного повідомлення від елемента до застосунку ──────────────────
def fig_message_path():
    W, H = 820, 640
    f = []
    CX = 250

    steps = [
        (70,  ['елемент постить', 'повідомлення']),
        (185, ['sync-обробник', '(у нитці, що постить)']),
        (315, ['черга шини', 'FIFO, без верхньої межі']),
        (470, ['джерело подій', 'у головному циклі']),
        (575, ['обробник застосунку:', 'розбір і реакція']),
    ]
    ys = []
    for cy, lines in steps:
        b, w, h = textbox(CX, cy, lines, size=13, min_w=250)
        f.append(b)
        ys.append((cy, h))

    for i in range(len(ys) - 1):
        y1 = ys[i][0] + ys[i][1] / 2
        y2 = ys[i + 1][0] - ys[i + 1][1] / 2
        f.append(arrow(CX, y1 + 2, CX, y2 - 2))

    # межа ниток між чергою і головним циклом
    f.append(line(30, 400, 790, 400, color=MUTED, sw=1.6, dash='7,6'))
    f.append(text(770, 392, 'межа ниток', size=12, color=MUTED, anchor='end'))

    # бічна гілка: DROP
    db, dw, dh = textbox(620, 185, ['GST_BUS_DROP:', 'повідомлення', 'зникає тут'],
                         size=12, fill='#fdecea', stroke=POS, min_w=200)
    f.append(arrow(CX + 125 + 4, 185, 620 - dw / 2 - 6, 185, color=POS))
    f.append(db)

    # бічна гілка: ASYNC
    ab, aw, ah = textbox(620, 315, ['GST_BUS_ASYNC:', 'нитка-постач чекає,', 'доки застосунок'
                                    , 'не обробить'], size=12, fill='#eaf0fd',
                         stroke=NEG, min_w=200)
    f.append(arrow(CX + 125 + 4, 315, 620 - aw / 2 - 6, 315, color=NEG))
    f.append(ab)

    f.append(text(CX + 16, 258, 'GST_BUS_PASS', size=12, anchor='start', color=MUTED))

    render(os.path.join(OUT, 'message-path.svg'), W, H, *f)


# ── 3. Bin не пропускає EOS, доки не відзвітують усі приймачі ───────────────
def fig_eos_aggregation():
    W, H = 1060, 380
    f = []

    s1, w1, h1 = textbox(120, 130, ['приймач', 'відео'], size=13, min_w=150)
    s2, w2, h2 = textbox(120, 260, ['приймач', 'звуку'], size=13, min_w=150)
    f.append(s1)
    f.append(s2)

    bb, bw, bh = textbox(400, 195, ['bin рахує EOS:', '1 із 2 — тримає в собі',
                                    '2 із 2 — постить один'], size=13, min_w=280)
    f.append(bb)

    f.append(arrow(120 + w1 / 2 + 6, 130, 400 - bw / 2 - 6, 165))
    f.append(arrow(120 + w2 / 2 + 6, 260, 400 - bw / 2 - 6, 225))
    f.append(text(212, 114, 'EOS', size=12, color=POS, anchor='start'))
    f.append(text(212, 292, 'EOS', size=12, color=POS, anchor='start'))

    cb, cw, ch = textbox(730, 195, ['шина конвеєра'], size=13, min_w=180)
    f.append(cb)
    f.append(arrow(400 + bw / 2 + 6, 195, 730 - cw / 2 - 6, 195))
    f.append(text(590, 178, 'один EOS', size=12, color=POS))

    ab, aw, ah = textbox(950, 195, ['застосунок'], size=13, min_w=150)
    f.append(ab)
    f.append(arrow(730 + cw / 2 + 6, 195, 950 - aw / 2 - 6, 195))

    f.append(text(530, 340, 'поодинокі EOS від приймачів застосунок не бачить',
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'eos-aggregation.svg'), W, H, *f)


# ── 4. Біти GstMessageType і межа 1 << 31 (до вставки api-bus) ──────────────
def _row(items, cy, size=12, pad=10, gap=22, x0=40, minw=0, **kw):
    """Ряд рамок зліва направо; ширина кожної — під найдовший рядок."""
    ws = [max(minw, max(text_width(ln, size) for ln in it) + 2 * pad) for it in items]
    frags, geom = [], []
    x = x0
    for it, w in zip(items, ws):
        cx = x + w / 2
        b, bw, bh = textbox(cx, cy, it, size=size, pad=pad, min_w=w, **kw)
        frags.append(b)
        geom.append((cx, bw, bh))
        x += w + gap
    return frags, geom


def fig_message_type_bits():
    W, H = 1000, 470
    f = []

    f.append(text(40, 52, 'Звичайні типи — окремий біт на тип',
                  size=15, bold=True, anchor='start'))
    boxes, _ = _row([['1 << 0', 'EOS'],
                     ['1 << 1', 'ERROR'],
                     ['1 << 5', 'BUFFERING'],
                     ['…', '…'],
                     ['1 << 30', 'HAVE_CONTEXT']], 104, minw=104)
    f.extend(boxes)

    nb, nw, nh = textbox(818, 104, ['маска — це АБО:', 'ERROR | EOS = 0x03'],
                         size=12, min_w=250)
    f.append(nb)

    f.append(text(40, 196, 'Розширені типи — номер за межею, а не біт',
                  size=15, bold=True, anchor='start'))
    boxes2, _ = _row([['1 << 31', 'EXTENDED', '0x80000000'],
                      ['EXTENDED + 1', 'DEVICE_ADDED', '0x80000001'],
                      ['EXTENDED + 2', 'DEVICE_REMOVED', '0x80000002'],
                      ['EXTENDED + 6', 'REDIRECT', '0x80000006'],
                      ['EXTENDED + 8', 'INSTANT_RATE_REQUEST', '0x80000008']],
                     250, minw=104)
    f.extend(boxes2)

    f.append(text(40, 330, 'Чому маскою їх не спіймати',
                  size=15, bold=True, anchor='start'))
    tb, tw, th = textbox(500, 400,
                         ['GST_MESSAGE_DEVICE_ADDED & GST_MESSAGE_EOS',
                          '0x80000001 & 0x00000001 = 0x00000001 ≠ 0',
                          'фільтр «лише EOS» ловить DEVICE_ADDED'],
                         size=13, fill='#fdecea', stroke=POS)
    f.append(tb)

    render(os.path.join(OUT, 'message-type-bits.svg'), W, H, *f)


# ── 5. Хто володіє повідомленням у кожному зі способів (до вставки api-bus) ──
def fig_message_ownership():
    W, H = 800, 380
    f = []

    f.append(text(400, 34, 'Хто володіє повідомленням', size=15, bold=True))

    rows = [
        ('колбек стеження (GstBusFunc)', 'позичене — не звільняти', FIELD, '#eaf7ee'),
        ('sync-обробник: PASS або ASYNC', 'позичене — не звільняти', FIELD, '#eaf7ee'),
        ('sync-обробник: DROP', 'ваше — gst_message_unref()', POS, '#fdecea'),
        ('gst_bus_pop / peek / timed_pop', 'ваше — gst_message_unref()', POS, '#fdecea'),
        ('gst_bus_post / post_message', 'шина забрала — не чіпати', NEG, '#eaf0fd'),
    ]
    y = 80
    for src, duty, col, bg in rows:
        lb, lw, lh = textbox(200, y, src, size=13, min_w=320)
        f.append(lb)
        f.append(arrow(366, y, 434, y, color=col))
        rb, rw, rh = textbox(590, y, duty, size=13, min_w=300,
                             fill=bg, stroke=col)
        f.append(rb)
        y += 62

    render(os.path.join(OUT, 'message-ownership.svg'), W, H, *f)


# ── 6. Реакція на BUFFERING: намір застосунку проти фактичного стану ────────
def fig_proj_buffering_cycle():
    W, H = 1010, 450
    f = []

    tb, tw, th = textbox(505, 55, 'повідомлення BUFFERING', size=13, min_w=300)
    f.append(tb)

    conds = [
        (170, ['конвеєр живий', '(set_state дав NO_PREROLL)']),
        (505, ['percent < 100']),
        (840, ['percent = 100']),
    ]
    cgeom = []
    for cx, lines in conds:
        b, w, h = textbox(cx, 165, lines, size=13, min_w=250)
        f.append(b)
        cgeom.append((cx, w, h))

    f.append(arrow(430, 55 + th / 2 + 2, 210, 165 - cgeom[0][2] / 2 - 6))
    f.append(arrow(505, 55 + th / 2 + 2, 505, 165 - cgeom[1][2] / 2 - 6))
    f.append(arrow(580, 55 + th / 2 + 2, 800, 165 - cgeom[2][2] / 2 - 6))

    acts = [
        (170, ['стану НЕ чіпаємо:', 'джерело не спиниться,', 'а пауза лише накопичить',
               'відставання'], FILL, LINE),
        (505, ['set_state(PAUSED):', 'приймач не гратиме', 'порожнечу'], '#fdecea', POS),
        (840, ['set_state(PLAYING):', 'повертаємось', 'до наміру'], '#eaf0fd', NEG),
    ]
    for i, (cx, lines, fill, stroke) in enumerate(acts):
        b, w, h = textbox(cx, 315, lines, size=12, min_w=250, fill=fill, stroke=stroke)
        f.append(arrow(cx, 165 + cgeom[i][2] / 2 + 2, cx, 315 - h / 2 - 6,
                       color=stroke if i else LINE))
        f.append(b)

    f.append(text(505, 425, 'намір застосунку весь час PLAYING — коливається лише фактичний стан',
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'proj-buffering-cycle.svg'), W, H, *f)


# ── 7. Порядок кроків програми: чому кожен саме тут ─────────────────────────
def fig_proj_run_order():
    W, H = 1030, 630
    f = []

    steps = [
        (['gst_init(), конвеєр, елементи'],
         ['нитки ще не запущено —', 'постити нікому й нічого']),
        (['gst_bus_add_watch()'],
         ['ДО першого set_state:', 'інакше ранні повідомлення нікому забрати']),
        (['set_state(PAUSED)'],
         ['розвідка: NO_PREROLL', 'означає живий конвеєр']),
        (['set_state(PLAYING)'],
         ['керування повертається одразу,', 'кадри йдуть у чужих нитках']),
        (['g_main_loop_run()'],
         ['уся програма живе тут:', 'робота — в обробнику шини']),
        (['g_main_loop_quit()', 'з обробника EOS або ERROR'],
         ['єдина дорога назовні —', 'через повідомлення']),
        (['set_state(NULL)'],
         ['шину скинуто: після цього рядка', 'вона вже нічого не віддасть']),
        (['remove_watch, unref bus,', 'unref pipeline'],
         ['стеження тримає посилання —', 'знімаємо його першим']),
    ]

    y = 70
    prev_bottom = None
    for left, right in steps:
        b, w, h = textbox(250, y, left, size=13, min_w=400)
        if prev_bottom is not None:
            f.append(arrow(250, prev_bottom + 2, 250, y - h / 2 - 6))
        f.append(b)
        f.append(mtext(490, y - 13 * 1.3 / 2 + 13 * 0.35, right,
                       size=13, color=MUTED, anchor='start'))
        prev_bottom = y + h / 2
        y += 70

    render(os.path.join(OUT, 'proj-run-order.svg'), W, H, *f)


fig_two_channels()
fig_message_path()
fig_eos_aggregation()
fig_message_type_bits()
fig_message_ownership()
fig_proj_buffering_cycle()
fig_proj_run_order()
print('ok')
