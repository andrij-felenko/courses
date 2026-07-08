# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: ланцюг сигналу — несуча 38 кГц → пачки → перевернута обвідна ────
def signal_chain():
    W, H = 860, 470
    frags = []

    # осі часу для двох доріжок
    x0, x1 = 90, 800
    top_y = 130      # базова лінія верхньої доріжки (світло пульта)
    bot_y = 340      # базова лінія нижньої доріжки (вихід S)
    amp = 42

    # підписи доріжок ліворуч (поза графіком, не накладаються на хвилі)
    frags.append(text(x0 - 12, top_y - 60, "світло", size=12, color=INK, anchor="end", bold=True))
    frags.append(text(x0 - 12, top_y - 44, "пульта", size=12, color=INK, anchor="end", bold=True))
    frags.append(text(x0 - 12, top_y + 44, "38 кГц", size=10, color=MUTED, anchor="end"))

    frags.append(text(x0 - 12, bot_y - 34, "вихід S", size=12, color=INK, anchor="end", bold=True))
    frags.append(text(x0 - 12, bot_y - 18, "приймача", size=12, color=INK, anchor="end", bold=True))

    # ── розкладка пачок і пауз уздовж часу (умовний кадр) ──
    # (початок, ширина) кожної пачки-мітки; між ними — паузи
    bursts = [(120, 90), (250, 40), (330, 40), (410, 90), (560, 40), (640, 40)]

    # верхня доріжка: у кожній пачці — щільне миготіння (несуча), поза пачками — рівна лінія
    frags.append(line(x0, top_y, x1, top_y, color="#c9ccd1", sw=1))  # осьова
    for (bx, bw) in bursts:
        # несуча: часті вертикальні штрихи вгору-вниз від осі
        n = max(6, int(bw / 7))
        for k in range(n + 1):
            xx = bx + bw * k / n
            frags.append(line(xx, top_y - amp, xx, top_y + amp, color=POS, sw=1.4))
        # рамка-обвідна пачки (легка), щоб читалося «пачка»
        frags.append(rect(bx - 2, top_y - amp - 4, bw + 4, 2 * amp + 8,
                          fill="none", stroke="#e2a6a0", sw=1, rx=3))
    # ярлики «пачка» / «пауза» — ПІД верхньою доріжкою, у чистій смузі
    frags.append(text(120 + 45, top_y + amp + 24, "пачка", size=10, color=POS))
    frags.append(text((410 + 250) / 2 + 20, top_y + amp + 24, "пауза", size=10, color=MUTED))

    # ── нижня доріжка: перевернута обвідна ──
    # спокій = ВИСОКО (1), пачка = НИЗЬКО (0). Малюємо як цифровий меандр.
    hi = bot_y - amp        # рівень «1»
    lo = bot_y + amp        # рівень «0»
    # позначки рівнів праворуч (за графіком)
    frags.append(text(x1 + 12, hi + 4, "«1» спокій", size=10, color=MUTED, anchor="start"))
    frags.append(text(x1 + 12, lo + 4, "«0» пачка", size=10, color=NEG, anchor="start"))
    frags.append(line(x0, hi, x1, hi, color="#e5e7eb", sw=1, dash="3,4"))
    frags.append(line(x0, lo, x1, lo, color="#e5e7eb", sw=1, dash="3,4"))

    # будуємо цифрову лінію: high скрізь, low під час пачок
    pts = [(x0, hi)]
    for (bx, bw) in bursts:
        pts.append((bx, hi))
        pts.append((bx, lo))
        pts.append((bx + bw, lo))
        pts.append((bx + bw, hi))
    pts.append((x1, hi))
    for i in range(len(pts) - 1):
        (ax, ay), (bx2, by2) = pts[i], pts[i + 1]
        frags.append(line(ax, ay, bx2, by2, color=NEG, sw=2.4))

    # вісь часу знизу зі стрілкою
    frags.append(arrow(x0, 420, x1, 420, color=LINE))
    frags.append(text(x1, 442, "час", size=11, color=INK, anchor="end"))

    # пояснення переходу між доріжками — стрілка «прибрали несучу»
    b, w_, h_ = textbox((x0 + x1) / 2, 235, "приймач прибирає несучу\nі перевертає сигнал",
                        size=11, fill="#eef6ee", stroke=FIELD, sw=1.4, color=FIELD)
    frags.append(b)

    render(os.path.join(OUT, 'ir-signal-chain.svg'), W, H, *frags,
           title="Від миготіння пульта до перевернутої обвідної на виході")


# ── Фігура 2: розводка KY-022 пін-у-пін до плати ─────────────────────────────
def wiring():
    W, H = 820, 520
    frags = []

    # ── модуль KY-022 ліворуч ──
    mx, my, mw, mh = 70, 120, 220, 250
    frags.append(rect(mx, my, mw, mh, fill="#eaf0fd", stroke=NEG, sw=2, rx=12))
    frags.append(text(mx + mw / 2, my - 16, "KY-022 (модуль)", size=13, color=INK, bold=True))
    # чорна намистина-приймач
    frags.append(circle(mx + mw / 2, my + 70, 26, fill="#1a1a1a", stroke="#1a1a1a", sw=1))
    frags.append(text(mx + mw / 2, my + 74, "1838", size=11, color="#ffffff", bold=True))
    frags.append(text(mx + mw / 2, my + 118, "приймач", size=10, color=MUTED))
    # світлодіод-індикатор
    frags.append(circle(mx + 40, my + 70, 8, fill="#fdecea", stroke=POS, sw=1.6))
    frags.append(text(mx + 40, my + 96, "LED", size=9, color=POS))

    # три штирі гребінки на правому краї модуля
    pin_x = mx + mw
    pins = [
        (my + 60,  "S",  "сигнал",   LINE),
        (my + 125, "",   "живлення", POS),
        (my + 190, "−",  "земля",    NEG),
    ]
    for (py, lab, _desc, col) in pins:
        frags.append(rect(pin_x - 4, py - 9, 22, 18, fill="#c9a44a", stroke="#8a6d20", sw=1.2, rx=3))
        if lab:
            frags.append(text(pin_x + 7, py + 4, lab, size=11, color="#1a1a1a", bold=True))
    frags.append(text(mx + mw / 2, my + mh + 22, "живлення — середній штир", size=10, color=MUTED))

    # ── плата праворуч ──
    bx, by, bw, bh = 560, 120, 200, 250
    frags.append(rect(bx, by, bw, bh, fill="#eef6ee", stroke=FIELD, sw=2, rx=12))
    frags.append(text(bx + bw / 2, by - 16, "плата (5 В)", size=13, color=INK, bold=True))
    # контактні точки на лівому краї плати
    b_pins = [
        (by + 60,  "D2",  LINE),
        (by + 125, "5V",  POS),
        (by + 190, "GND", NEG),
    ]
    for (py, lab, col) in b_pins:
        frags.append(circle(bx, py, 6, fill=FILL, stroke=col, sw=1.6))
        frags.append(text(bx + 16, py + 4, lab, size=11, color=col, anchor="start", bold=True))

    # ── три дроти між ними (по горизонталі — рівні збігаються) ──
    wire_x0 = pin_x + 18
    wire_x1 = bx
    wire_specs = [
        (my + 60,  by + 60,  LINE, "сигнал S → D2"),
        (my + 125, by + 125, POS,  "живлення → 5V"),
        (my + 190, by + 190, NEG,  "земля − → GND"),
    ]
    for (ly, ry, col, lab) in wire_specs:
        # горизонтальні рівні однакові → пряма лінія
        frags.append(line(wire_x0, ly, wire_x1, ry, color=col, sw=2.4))

    # підписи дротів — у чистому полі внизу, окремим рядком (не на лініях)
    ley = 486
    frags.append(text(W / 2, ley, "сигнал S → D2   ·   живлення (середній) → 5V   ·   земля − → GND",
                     size=11, color=INK))

    # ── необов'язковий конденсатор 0.1 мкФ — окремим інсетом унизу ліворуч ──
    # (не тягнемо дашти через зайнятий канал дротів: показуємо самодостатньою
    #  рамкою, щоб жодна лінія не перетнула написів)
    ix, iy, iw, ih = 70, 400, 300, 66
    frags.append(rect(ix, iy, iw, ih, fill="#fbfbfb", stroke=MUTED, sw=1.2, rx=8))
    # символ конденсатора всередині рамки, ліворуч
    csx = ix + 34
    ccy = iy + ih / 2
    frags.append(line(csx - 16, ccy, csx - 3, ccy, color=POS, sw=1.6))     # підвід від «+»
    frags.append(line(csx - 3, ccy - 13, csx - 3, ccy + 13, color=INK, sw=2.4))  # пластина
    frags.append(line(csx + 3, ccy - 13, csx + 3, ccy + 13, color=INK, sw=2.4))  # пластина
    frags.append(line(csx + 3, ccy, csx + 16, ccy, color=NEG, sw=1.6))     # підвід до «−»
    frags.append(text(csx - 20, ccy - 20, "+", size=13, color=POS, bold=True))
    frags.append(text(csx + 20, ccy - 20, "−", size=13, color=NEG, bold=True))
    # підпис праворуч у рамці
    frags.append(text(ix + 78, ccy - 8, "0.1 мкФ між + і − модуля", size=11,
                     color=INK, anchor="start"))
    frags.append(text(ix + 78, ccy + 12, "необов'язково — проти брудного живлення", size=9,
                     color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'ky022-wiring.svg'), W, H, *frags,
           title="KY-022 → плата: три дроти, живлення посередині")


# ── Фігура 3 (для вставки proj): натиск → повтори → тиша → відпущення ─────────
def hold_repeat():
    """Часова стрічка кадрів NEC при утриманні кнопки + що бачить код."""
    W, H = 900, 430
    frags = []

    x0, x1 = 70, 840
    axis_y = 150             # базова лінія стрічки кадрів
    # вісь часу
    frags.append(arrow(x0, axis_y + 120, x1, axis_y + 120, color=LINE))
    frags.append(text(x1, axis_y + 142, "час", size=11, color=INK, anchor="end"))

    # кадри: (x-центр, ширина, тип)  тип: "full" перший, "rep" повтор
    frames = [
        (150, 46, "full"),
        (330, 20, "rep"),
        (410, 20, "rep"),
        (490, 20, "rep"),
        (570, 20, "rep"),
    ]
    fh = 46                  # висота стовпчика кадру
    for (cx, w, kind) in frames:
        col = NEG if kind == "full" else POS
        fill = "#eaf0fd" if kind == "full" else "#fdecea"
        frags.append(rect(cx - w / 2, axis_y - fh, w, fh, fill=fill, stroke=col, sw=2, rx=4))

    # підписи типів кадрів — з ЗАПАСОМ, над стовпчиками, у чистій смузі
    frags.append(text(150, axis_y - fh - 30, "повний кадр", size=11, color=NEG, bold=True))
    frags.append(text(150, axis_y - fh - 14, "адреса+команда", size=9, color=MUTED))
    frags.append(text(450, axis_y - fh - 30, "куці кадри-повтори", size=11, color=POS, bold=True))
    frags.append(text(450, axis_y - fh - 14, "прапорець IS_REPEAT", size=9, color=MUTED))

    # інтервал 110 мс між повторами (стрілка з підписом у чистому просторі)
    iy = axis_y + 26
    frags.append(line(330, axis_y, 330, iy + 8, color="#c9ccd1", sw=1, dash="3,3"))
    frags.append(line(410, axis_y, 410, iy + 8, color="#c9ccd1", sw=1, dash="3,3"))
    frags.append(arrow(330, iy, 410, iy, color=MUTED, sw=1.4))
    frags.append(arrow(410, iy, 330, iy, color=MUTED, sw=1.4))
    frags.append(text(370, iy - 6, "≈110 мс", size=9, color=MUTED))

    # «тиша» після останнього повтору → відпущення
    gap_x0 = 570 + 10
    frags.append(line(gap_x0, axis_y - fh, gap_x0, axis_y + 8, color="#c9ccd1", sw=1, dash="3,3"))
    frags.append(text((gap_x0 + x1) / 2, axis_y - 12, "тиша > RELEASE_MS", size=10, color=INK))
    frags.append(text((gap_x0 + x1) / 2, axis_y + 6, "→ кнопку відпущено", size=10, color=MUTED))

    # ── нижня доріжка: що робить КОД під кожним кадром ──
    code_y = axis_y + 70
    reacts = [
        (150, "крок +\nheldCommand=кнопка", FIELD),
        (330, "лише мітка\nчасу", MUTED),
        (410, "лише мітка\nчасу", MUTED),
        (490, "лише мітка\nчасу", MUTED),
        (570, "лише мітка\nчасу", MUTED),
    ]
    for (cx, s, col) in reacts:
        frags.append(line(cx, axis_y, cx, code_y - 16, color="#e5e7eb", sw=1))
    # перший — виділена дія
    frags.append(text(150, code_y, "код: КРОК дії", size=10, color=FIELD, bold=True))
    frags.append(text(150, code_y + 15, "+ беремо на утримання", size=9, color=MUTED))
    # повтори — код їх лише відмічає
    frags.append(text(450, code_y, "код: лише оновлює lastFrameMs", size=10, color=INK))
    frags.append(text(450, code_y + 15, "крутіння веде власний таймер REPEAT_MS", size=9, color=MUTED))

    render(os.path.join(OUT, 'hold-repeat.svg'), W, H, *frags,
           title="Утримання кнопки: перший кадр діє, повтори лише тримають лічильник")


if __name__ == '__main__':
    signal_chain()
    wiring()
    hold_repeat()
    print("figures written")
