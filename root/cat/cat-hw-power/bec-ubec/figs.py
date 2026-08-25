# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: лінійний BEC (тепло) проти імпульсного UBEC (buck) ─────────────
def fig_linear_vs_switching():
    W, H = 820, 470
    frags = []

    frags.append(text(W / 2, 52,
                      "Та сама задача: з 11.1 В (3S) зробити 5 В для 3 А серв. Куди дінеться зайва потужність?",
                      size=13, color=MUTED))

    colw = 350
    lx = 36
    rx = W - 36 - colw
    top = 80
    boxh = 320

    # ── ЛІВА: лінійний BEC ──
    frags.append(rect(lx, top, colw, boxh, fill="#fbeeee", stroke=POS, sw=1.6, rx=10))
    frags.append(text(lx + colw / 2, top + 28, "Лінійний BEC", size=18, color=POS, bold=True))
    frags.append(text(lx + colw / 2, top + 48, "прохідний транзистор, палить різницю", size=12, color=MUTED))

    # вхід -> чип -> вихід
    bx, by, bw, bh = lx + colw / 2 - 45, top + 92, 90, 56
    frags.append(line(lx + colw / 2, top + 62, lx + colw / 2, by, color=POS, sw=3))
    frags.append(text(lx + 48, top + 78, "11.1 В · 3 А", size=12, color=POS, bold=True, anchor="start"))
    frags.append(rect(bx, by, bw, bh, fill="#ffffff", stroke=POS, sw=2, rx=6))
    frags.append(text(bx + bw / 2, by + bh / 2 + 5, "Q", size=22, color=POS, bold=True))
    frags.append(line(lx + colw / 2, by + bh, lx + colw / 2, by + bh + 34, color=FIELD, sw=3))
    frags.append(text(lx + 48, by + bh + 26, "5 В · 3 А", size=12, color=FIELD, bold=True, anchor="start"))

    # тепло вбік
    frags.append(arrow(bx + bw, by + bh / 2, bx + bw + 66, by + bh / 2, color=POS, sw=2.5))
    frags.append(text(bx + bw + 74, by + bh / 2 - 6, "тепло", size=13, color=POS, bold=True, anchor="start"))

    b1 = fitbox(lx + 24, top + 220, colw - 48, 38,
                "P_втрат = (11.1 − 5) · 3 = 18.3 Вт у тепло",
                size=13, fill="#ffffff", stroke=POS, color=INK, bold=True)
    frags.append(b1)
    b2 = fitbox(lx + 24, top + 266, colw - 48, 38,
                "ККД = 5 / 11.1 ≈ 45 %. Радіатор гарячий.",
                size=13, fill="#ffffff", stroke=POS, color=INK)
    frags.append(b2)

    # ── ПРАВА: імпульсний UBEC (buck) ──
    frags.append(rect(rx, top, colw, boxh, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=10))
    frags.append(text(rx + colw / 2, top + 28, "Імпульсний UBEC", size=18, color=FIELD, bold=True))
    frags.append(text(rx + colw / 2, top + 48, "buck: ключ + котушка, перекачує заряд", size=12, color=MUTED))

    mx, my, mw, mh = rx + colw / 2 - 45, top + 92, 90, 56
    frags.append(line(rx + colw / 2, top + 62, rx + colw / 2, my, color=POS, sw=3))
    frags.append(text(rx + 48, top + 78, "11.1 В · 1.4 А", size=12, color=POS, bold=True, anchor="start"))
    frags.append(rect(mx, my, mw, mh, fill="#ffffff", stroke=FIELD, sw=2, rx=6))
    frags.append(text(mx + mw / 2, my + mh / 2 + 5, "buck", size=15, color=FIELD, bold=True))
    frags.append(line(rx + colw / 2, my + mh, rx + colw / 2, my + mh + 34, color=FIELD, sw=3))
    frags.append(text(rx + 48, my + mh + 26, "5 В · 3 А", size=12, color=FIELD, bold=True, anchor="start"))

    # трохи тепла
    frags.append(arrow(mx + mw, my + mh / 2, mx + mw + 52, my + mh / 2, color=MUTED, sw=1.8))
    frags.append(text(mx + mw + 60, my + mh / 2 - 6, "мало", size=12, color=MUTED, anchor="start"))

    b3 = fitbox(rx + 24, top + 220, colw - 48, 38,
                "Струм на вході ПАДАЄ: 15 Вт на вихід ≈ 1.4 А зверху",
                size=13, fill="#ffffff", stroke=FIELD, color=INK, bold=True)
    frags.append(b3)
    b4 = fitbox(rx + 24, top + 266, colw - 48, 38,
                "ККД > 90 %. Ледь теплий.",
                size=13, fill="#ffffff", stroke=FIELD, color=INK)
    frags.append(b4)

    frags.append(text(W / 2, H - 20,
                      "Лінійний бере з батареї СТІЛЬКИ Ж струму, скільки віддає, і різницю палить. Імпульсний бере МЕНШЕ струму на вищій напрузі — тому й економний.",
                      size=11, color=MUTED))

    render(os.path.join(IMG, "linear-vs-switching.svg"), W, H, *frags,
           title="Чому UBEC імпульсний, а не лінійний")


# ── Фігура 2: підключення пін-у-пін (LiPo → UBEC → приймач; ESC-BEC вимкнено) ─
def fig_wiring():
    W, H = 860, 500
    frags = []

    frags.append(text(W / 2, 50,
                      "Зовнішній UBEC живить приймач; вбудований BEC регулятора ВИМКНЕНО.",
                      size=13, color=MUTED))

    # три вертикальні колонки-блоки, підписи-лінії йдуть у широких проміжках між ними
    # ── БАТАРЕЯ (ліва колонка) ──
    batx, baty, batw, bath = 40, 210, 110, 100
    frags.append(rect(batx, baty, batw, bath, fill=FILL, stroke=LINE, sw=1.6, rx=8))
    frags.append(text(batx + batw / 2, baty + 40, "LiPo 3S", size=16, bold=True))
    frags.append(text(batx + batw / 2, baty + 64, "11.1 В", size=13, color=MUTED))
    frags.append(plus(batx + batw - 16, baty + 18))
    frags.append(minus(batx + batw - 16, baty + bath - 18))

    ypos = baty + 18          # плюсова шина від батареї
    yneg = baty + bath - 18   # мінусова шина від батареї

    # вузол розгалуження плюса
    node_x = 200
    frags.append(line(batx + batw, ypos, node_x, ypos, color=POS, sw=3))
    frags.append(circle(node_x, ypos, 4.5, fill=POS, stroke=POS, sw=1))
    node_xn = 230
    frags.append(line(batx + batw, yneg, node_xn, yneg, color=NEG, sw=3))
    frags.append(circle(node_xn, yneg, 4.5, fill=NEG, stroke=NEG, sw=1))

    # ── ESC (середня колонка, верх) ──
    escx, escy, escw, esch = 330, 130, 160, 96
    frags.append(rect(escx, escy, escw, esch, fill="#eef0f4", stroke=LINE, sw=1.6, rx=8))
    frags.append(text(escx + escw / 2, escy + 36, "ESC", size=17, bold=True))
    frags.append(text(escx + escw / 2, escy + 58, "регулятор мотора", size=11, color=MUTED))
    frags.append(text(escx + escw / 2, escy + 76, "(BEC усередині)", size=10, color=MUTED))
    frags.append(arrow(escx + escw / 2, escy, escx + escw / 2, escy - 28, color=INK, sw=2))
    frags.append(text(escx + escw / 2, escy - 36, "мотор", size=12, bold=True))
    # силове живлення батарея → ESC
    frags.append(line(node_x, ypos, node_x, escy + 30, color=POS, sw=3))
    frags.append(line(node_x, escy + 30, escx, escy + 30, color=POS, sw=3))
    frags.append(line(node_xn, yneg, node_xn, escy + esch - 16, color=NEG, sw=3))
    frags.append(line(node_xn, escy + esch - 16, escx, escy + esch - 16, color=NEG, sw=3))

    # ── UBEC (середня колонка, низ) ──
    ubx, uby, ubw, ubh = 330, 320, 160, 96
    frags.append(rect(ubx, uby, ubw, ubh, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=8))
    frags.append(text(ubx + ubw / 2, uby + 38, "UBEC", size=17, color=FIELD, bold=True))
    frags.append(text(ubx + ubw / 2, uby + 60, "buck 5 В · 3 А", size=12, color=MUTED))
    # силове живлення батарея → UBEC
    frags.append(line(node_x, ypos, node_x, uby + 30, color=POS, sw=3))
    frags.append(line(node_x, uby + 30, ubx, uby + 30, color=POS, sw=3))
    frags.append(line(node_xn, yneg, node_xn, uby + ubh - 16, color=NEG, sw=3))
    frags.append(line(node_xn, uby + ubh - 16, ubx, uby + ubh - 16, color=NEG, sw=3))

    # ── ПРИЙМАЧ (права колонка) ──
    rxx, rxy, rxw, rxh = 660, 210, 160, 140
    frags.append(rect(rxx, rxy, rxw, rxh, fill=FILL, stroke=NEG, sw=1.8, rx=8))
    frags.append(text(rxx + rxw / 2, rxy + 26, "Приймач", size=15, color=NEG, bold=True))
    ch_y = rxy + 56
    for i, lbl in enumerate(["THR", "AILE → серво", "ELEV → серво"]):
        yy = ch_y + i * 28
        frags.append(circle(rxx + 22, yy, 3.5, fill=FIELD, stroke=FIELD, sw=1))
        frags.append(circle(rxx + 32, yy, 3.5, fill=POS, stroke=POS, sw=1))
        frags.append(circle(rxx + 42, yy, 3.5, fill=NEG, stroke=NEG, sw=1))
        frags.append(text(rxx + 54, yy + 4, lbl, size=11, color=INK, anchor="start"))

    # UBEC → приймач: спільна плюсова 5 В шина (обходить приймач знизу-справа)
    busy = 448                      # горизонтальна 5В-шина, у порожньому просторі під блоками
    xret1 = rxx + rxw + 24          # правий обхід (плюс)
    xret2 = rxx + rxw + 42          # правий обхід (земля)
    frags.append(line(ubx + ubw, uby + 30, 600, uby + 30, color=FIELD, sw=3))
    frags.append(line(600, uby + 30, 600, busy, color=FIELD, sw=3))
    frags.append(line(600, busy, xret1, busy, color=FIELD, sw=3))
    frags.append(line(xret1, busy, xret1, rxy + rxh - 22, color=FIELD, sw=3))
    frags.append(line(xret1, rxy + rxh - 22, rxx + rxw, rxy + rxh - 22, color=FIELD, sw=3))
    # земля UBEC → приймач (трохи нижча шина)
    frags.append(line(ubx + ubw, uby + ubh - 16, 622, uby + ubh - 16, color=NEG, sw=3))
    frags.append(line(622, uby + ubh - 16, 622, busy + 16, color=NEG, sw=3))
    frags.append(line(622, busy + 16, xret2, busy + 16, color=NEG, sw=3))
    frags.append(line(xret2, busy + 16, xret2, rxy + rxh - 8, color=NEG, sw=3))
    frags.append(line(xret2, rxy + rxh - 8, rxx + rxw, rxy + rxh - 8, color=NEG, sw=3))

    # ESC → приймач: ЛИШЕ сигнал THR (плюс обрізано). Обходить приймач зверху.
    sigy = 116                      # верхня сигнальна лінія, у порожньому просторі згори
    frags.append(line(escx + escw, escy + 30, 560, escy + 30, color=FIELD, sw=2))
    frags.append(line(560, escy + 30, 560, sigy, color=FIELD, sw=2))
    frags.append(line(560, sigy, 648, sigy, color=FIELD, sw=2))
    frags.append(line(648, sigy, 648, ch_y, color=FIELD, sw=2))
    frags.append(line(648, ch_y, rxx + 22, ch_y, color=FIELD, sw=2))

    # позначка «червоний дріт обрізано»: хрестик на неіснуючому плюсі ESC→приймач
    cutx, cuty = 530, escy + 30
    frags.append(line(cutx - 9, cuty - 9, cutx + 9, cuty + 9, color=POS, sw=3))
    frags.append(line(cutx - 9, cuty + 9, cutx + 9, cuty - 9, color=POS, sw=3))

    # ── підписи у порожніх зонах, ПОДАЛІ від ліній й одне від одного ──
    frags.append(text(escx + escw / 2, escy + esch + 26, "від ESC до приймача — лише", size=11, color=MUTED))
    frags.append(text(escx + escw / 2, escy + esch + 42, "сигнал газу, плюс обрізано ✂", size=11, color=POS, bold=True))
    frags.append(text(460, busy - 12, "UBEC → спільна шина +5 В приймача", size=11, color=FIELD, bold=True, anchor="middle"))

    frags.append(text(W / 2, H - 18,
                      "Два регулятори на одну шину 5 В воювали б за напругу — тому вбудований BEC вимикають, живить лише UBEC.",
                      size=11, color=MUTED))

    render(os.path.join(IMG, "wiring.svg"), W, H, *frags,
           title="Підключення UBEC: батарея · ESC · приймач")


# ── Фігура 3: 3-контактний роз'єм серво і де сидить BEC ──────────────────────
def fig_servo_plug():
    W, H = 720, 340
    frags = []

    frags.append(text(W / 2, 52,
                      "Стандартний 3-контактний роз'єм (JR/Futaba). BEC заганяє 5 В у СЕРЕДНІЙ контакт — спільну плюсову шину приймача.",
                      size=12, color=MUTED))

    # роз'єм — корпус із трьома «ямками»
    px, py, pw, ph = 250, 110, 220, 90
    frags.append(rect(px, py, pw, ph, fill="#2b2b2b", stroke="#111", sw=2, rx=8))

    labels = [
        ("сигнал", "жовт./біл.", FIELD, "S"),
        ("+5 В", "черв.", POS, "+"),
        ("земля", "чорн./кор.", NEG, "−"),
    ]
    n = 3
    for i, (name, wire, col, sym) in enumerate(labels):
        cx = px + pw * (i + 0.5) / n
        # контакт
        frags.append(rect(cx - 18, py + ph - 6, 36, 40, fill=col, stroke="#333", sw=1.2, rx=4))
        frags.append(text(cx, py + ph / 2 + 6, sym, size=22, color="#f4f6f8", bold=True))
        # підписи внизу
        frags.append(text(cx, py + ph + 54, name, size=14, color=col, bold=True))
        frags.append(text(cx, py + ph + 74, wire, size=11, color=MUTED))

    # стрілка: BEC живить середній контакт
    frags.append(arrow(px - 70, py + ph / 2, px, py + ph / 2, color=POS, sw=2.5))
    frags.append(text(px - 74, py + ph / 2 - 10, "BEC → +5 В", size=13, color=POS, bold=True, anchor="end"))
    frags.append(text(px - 74, py + ph / 2 + 12, "у середній контакт", size=11, color=MUTED, anchor="end"))

    frags.append(text(W / 2, H - 16,
                      "Усі канали приймача ділять цю одну шину +5 В — тому джерело живлення має бути рівно одне.",
                      size=11, color=MUTED))

    render(os.path.join(IMG, "servo-plug.svg"), W, H, *frags,
           title="Куди BEC подає 5 В: середній контакт роз'єму")


# ── Фігура 4 (proj): сигнал серва — кадр 20 мс, кут у ширині імпульсу 1..2 мс ─
def fig_servo_pulse():
    W, H = 920, 470
    f = [text(W / 2, 34, "Сигнал серва: кадр завжди 20 мс, а кут задає ширина імпульсу 1…2 мс",
              size=15, bold=True)]

    tracks = [
        ("1.0 мс", 0.05, "крайнє положення (0°)", POS),
        ("1.5 мс", 0.075, "центр (90°)", FIELD),
        ("2.0 мс", 0.10, "інше крайнє (180°)", NEG),
    ]
    x0 = 260
    plot_w = 540
    ms_to_px = plot_w / 20.0
    lo_y_gap = 114
    top = 96

    for i, (lbl, frac, note, col) in enumerate(tracks):
        base = top + i * lo_y_gap
        high = base - 44
        pulse_ms = frac * 20.0

        # підпис доріжки ліворуч (два рядки, з запасом від осі)
        f.append(text(120, base - 22, lbl, size=14, bold=True, color=col, anchor="middle"))
        f.append(text(120, base - 4, note, size=9.5, color=MUTED, anchor="middle"))

        # базова лінія (0) на всю ширину кадру
        f.append(line(x0, base, x0 + plot_w, base, color=MUTED, sw=1.2))

        px = x0
        pw = pulse_ms * ms_to_px
        f.append(line(px, base, px, high, color=col, sw=2.6))
        f.append(line(px, high, px + pw, high, color=col, sw=2.6))
        f.append(line(px + pw, high, px + pw, base, color=col, sw=2.6))
        f.append(line(px + pw, base, x0 + plot_w, base, color=col, sw=2.6))

        # ширина імпульсу — підпис ПРАВОРУЧ від полички, щоб не накладатись на фронт
        f.append(text(px + pw + 40, high + 4, lbl, size=10.5, bold=True, color=col, anchor="start"))

    fy = top + 2 * lo_y_gap + 30
    f.append(arrow(x0, fy, x0 + plot_w, fy, color=INK, sw=1.6))
    f.append(arrow(x0 + plot_w, fy, x0, fy, color=INK, sw=1.6))
    f.append(text(x0 + plot_w / 2, fy - 8, "один кадр = 20 мс  (частота 50 Гц)", size=11, bold=True, anchor="middle"))
    f.append(text(x0 + plot_w / 2, fy + 20, "кадр повторюється щоразу; змінюється лише ширина полички", size=10, color=MUTED, anchor="middle"))

    b, _, _ = textbox(W / 2, 448,
                      "Контролер щодвадцять мілісекунд шле один імпульс. Його ТРИВАЛІСТЬ (не висота, не частота кадру) і є командою кута: 1 мс, 1.5 мс, 2 мс.",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "servo-pulse.svg"), W, H, *f)


# ── Фігура 5 (proj): стагер — одночасний старт проти рознесеного в часі ───────
def fig_stagger():
    W, H = 1020, 540
    f = [text(W / 2, 34, "Стагер: рознести пускові піки серв у часі, щоб їхня сума не просадила шину",
              size=15, bold=True)]

    x0 = 160
    plot_w = 720
    t_max = 380.0
    ms_to_px = plot_w / t_max
    stack_h = 22

    def bump(t_start, base_y, col, dur, h, lbl=None):
        out = []
        xs = x0 + t_start * ms_to_px
        xe = x0 + (t_start + dur) * ms_to_px
        out.append(rect(xs, base_y - h, xe - xs, h, fill="#fdecea", stroke=col, sw=1.6, rx=3))
        if lbl:
            out.append(text((xs + xe) / 2, base_y - h - 7, lbl, size=9, color=col, anchor="middle"))
        return out, xs, xe

    # ── ПАНЕЛЬ А: усі серва стартують РАЗОМ (піки стосом) ──
    ay = 168
    f.append(text(x0, ay - 108, "А. Усі команди одним кадром → піки збіглися", size=13, bold=True, color=POS, anchor="start"))
    f.append(line(x0, ay, x0 + plot_w, ay, color=INK, sw=1.6))
    f.append(text(x0 - 10, ay + 4, "струм", size=9.5, color=MUTED, anchor="end"))
    f.append(text(x0 - 10, ay + 18, "0", size=9, color=MUTED, anchor="end"))
    for i in range(4):
        by = ay - i * stack_h
        seg, _, _ = bump(60, by, POS, 90, stack_h, lbl=("4 серва разом" if i == 3 else None))
        f.extend(seg)
    lim_y = ay - int(2.4 * stack_h)
    f.append(line(x0, lim_y, x0 + plot_w, lim_y, color=NEG, sw=1.8, dash="6,4"))
    f.append(text(x0 + plot_w, lim_y - 8, "межа струму UBEC", size=10.5, bold=True, color=NEG, anchor="end"))
    f.append(text(x0 + 60 * ms_to_px + 120, ay - 4 * stack_h + 4, "сума ПРОБИЛА межу → просадка, brown-out",
                  size=11, bold=True, color=POS, anchor="start"))

    # ── ПАНЕЛЬ Б: ті самі команди, рознесені в часі ──
    by0 = 420
    f.append(text(x0, by0 - 108, "Б. Кожному серву свій такт → піки не збігаються", size=13, bold=True, color=FIELD, anchor="start"))
    f.append(line(x0, by0, x0 + plot_w, by0, color=INK, sw=1.6))
    f.append(text(x0 - 10, by0 + 4, "струм", size=9.5, color=MUTED, anchor="end"))
    f.append(text(x0 - 10, by0 + 18, "0", size=9, color=MUTED, anchor="end"))
    starts = [15, 105, 195, 285]
    for i, st in enumerate(starts):
        seg, _, _ = bump(st, by0, FIELD, 70, stack_h, lbl="серво %d" % (i + 1))
        f.extend(seg)
    lim_y2 = by0 - int(2.4 * stack_h)
    f.append(line(x0, lim_y2, x0 + plot_w, lim_y2, color=NEG, sw=1.8, dash="6,4"))
    f.append(text(x0 + plot_w, lim_y2 - 8, "та сама межа UBEC", size=10.5, bold=True, color=NEG, anchor="end"))
    f.append(text(x0 + 15 * ms_to_px, by0 - stack_h - 30, "кожен пік сам по собі, під межею",
                  size=11, bold=True, color=FIELD, anchor="start"))
    f.append(arrow(x0 + 15 * ms_to_px, by0 + 26, x0 + 105 * ms_to_px, by0 + 26, color=MUTED, sw=1.2))
    f.append(text(x0 + 60 * ms_to_px, by0 + 42, "затримка ~90 мс між сервами", size=9.5, color=MUTED, anchor="middle"))

    b, _, _ = textbox(W / 2, 514,
                      "Той самий рух і той самий UBEC — контролер лише шле команди не всі за раз, а по черзі, і сумарний струм не збирається в один високий пік.",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "stagger.svg"), W, H, *f)


# ── Фігура 6 (hist): дуга слова «battery eliminator» крізь провал ────────────
def fig_eliminator_arc():
    """Вертикальна вісь часу: перша епоха (лампове радіо) → провал → друга
    епоха (моделізм). Уся суть — розрив: слово майже вмерло й воскресло на
    задачі тієї ж форми. Написи стоять ОБАБІЧ осі, кожен у своїй колонці,
    подалі від осі й одне від одного — накладань бути не повинно."""
    W, H = 940, 812
    frags = []

    frags.append(text(W / 2, 52,
                      "«Усувати батарею» = взяти живлення з наявного джерела, а не возити зайве.",
                      size=13, color=MUTED))
    frags.append(text(W / 2, 72,
                      "Слово має провал і воскресіння через десятиліття.",
                      size=13, color=MUTED))

    axx = W / 2
    ytop, ybot = 100, H - 78

    # три смуги-епохи як тло
    def band(y1, y2, fill):
        frags.append(rect(64, y1, W - 128, y2 - y1, fill=fill, stroke="none", sw=0, rx=12))

    band(104, 342, "#eef6ef")       # перша епоха — зелений відтінок
    band(354, 486, "#fbeeee")       # провал — червоний відтінок
    band(498, ybot + 8, "#eef2fb")  # друга епоха — синій відтінок

    # центральна вісь часу (поверх смуг)
    frags.append(line(axx, ytop, axx, ybot, color=INK, sw=2))
    frags.append(text(axx, ytop - 12, "час ↓", size=11, color=MUTED))

    # заголовки епох — угорі своєї смуги, з великим вертикальним запасом до вузлів
    frags.append(text(axx, 126, "ПЕРША ЕПОХА · лампове радіо 1920-х", size=15, color=FIELD, bold=True))
    frags.append(text(axx, 376, "ПРОВАЛ · усувати вже нічого", size=15, color=POS, bold=True))
    frags.append(text(axx, 520, "ДРУГА ЕПОХА · радіомоделі", size=15, color=NEG, bold=True))

    L = axx - 46   # права межа лівої колонки (anchor=end)
    R = axx + 46   # ліва межа правої колонки (anchor=start)
    # (y, рік, сторона -1/+1, колір, рядки) ; сторона 0 = місток по центру
    nodes = [
        (196, "1920-ті",  -1, FIELD, ["Три батареї A / B / C:",
                                       "накал, анод, сітка.",
                                       "Кислота тече, розетка",
                                       "поруч — та лампа гуде"]),
        (198, "~1923–24", +1, FIELD, ["Мак-Каллоу (Westinghouse)",
                                       "показує AC-лампу:",
                                       "можливо, але гуде"]),
        (288, "1924–25",  -1, FIELD, ["Роджерс (Торонто,",
                                       "канадець) прибирає гул,",
                                       "патентує; з 08.1925 —",
                                       "«Rogers Batteryless»,",
                                       "1-й мереж. приймач"]),
        (292, "~1926",    +1, FIELD, ["RCA виводить свою",
                                       "AC-лампу; індустрія",
                                       "рушає слідом"]),

        (424, "1928–30",  -1, POS,   ["Усувачі масові (Philco,",
                                       "Galvin → Motorola) —",
                                       "але вже застарівають"]),
        (428, "1930-ті",  +1, POS,   ["Нові приймачі й так",
                                       "без батарей → усувати",
                                       "нічого. Слово вмирає"]),

        (566, None,        0, NEG,   None),  # місток-збіг форми задачі
        (628, "~1980-ті", -1, NEG,   ["Модель: тяга + приймач —",
                                       "знову ДВА джерела, як",
                                       "A і B. Комерц. BEC ~сер.80-х"]),
        (632, "далі",     +1, NEG,   ["BEC спершу в приймачі,",
                                       "потім функцію бере ESC"]),
        (720, "UBEC",     -1, NEG,   ["Окрема коробочка;",
                                       "«U» = Universal. Марка",
                                       "стала загальним словом"]),
    ]

    for (y, year, side, col, lines) in nodes:
        if lines is None:
            frags.append(circle(axx, y, 8, fill="#fff", stroke=NEG, sw=2.5))
            b = fitbox(axx - 210, y - 22, 420, 44,
                       "ТА САМА ФОРМА ЗАДАЧІ: джерело вже на борту — усунь другу батарею",
                       size=12, fill="#fff", stroke=NEG, color=INK, bold=True)
            frags.append(b)
            continue
        frags.append(circle(axx, y, 6, fill=col, stroke="#fff", sw=2))
        yhead = y - (len(lines) - 1) * 7 - 4
        if side < 0:
            frags.append(line(axx - 6, y, L + 4, y, color=col, sw=1.1, dash="3,3"))
            frags.append(text(L, yhead, year, size=12, color=col, bold=True, anchor="end"))
            frags.append(mtext(L, yhead + 15, lines, size=11, color=INK, anchor="end", lh=1.28))
        else:
            frags.append(line(axx + 6, y, R - 4, y, color=col, sw=1.1, dash="3,3"))
            frags.append(text(R, yhead, year, size=12, color=col, bold=True, anchor="start"))
            frags.append(mtext(R, yhead + 15, lines, size=11, color=INK, anchor="start", lh=1.28))

    frags.append(text(W / 2, H - 34,
                      "Назва — слід розв'язаної проблеми: чекає, поки задача тієї ж форми",
                      size=11, color=MUTED))
    frags.append(text(W / 2, H - 18,
                      "випливе в іншому ремеслі, про яке її перші автори й не думали.",
                      size=11, color=MUTED))

    render(os.path.join(IMG, "eliminator-arc.svg"), W, H, *frags,
           title="Дуга слова «battery eliminator»: 1920-ті → провал → BEC")


if __name__ == "__main__":
    fig_linear_vs_switching()
    fig_wiring()
    fig_servo_plug()
    fig_servo_pulse()
    fig_stagger()
    fig_eliminator_arc()
    print("figs done")
