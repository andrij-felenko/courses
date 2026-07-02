# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1: карта підродин — де кожна сидить за напругою й швидкістю
#   вісь X — напруга живлення (5 В праворуч, 3.3 В і нижче ліворуч)
#   вісь Y — швидкодія (затримка): вгорі швидше (менша затримка)
# ─────────────────────────────────────────────────────────────────────────────
def fig_map():
    W, H = 720, 470
    L, R, T, B = 90, 660, 70, 400          # межі поля координат
    frags = []

    # осі
    frags.append(line(L, B, R, B, color=INK, sw=2))
    frags.append(line(L, B, L, T, color=INK, sw=2))
    frags.append(text((L + R) / 2, B + 46, "напруга живлення →", size=13, color=MUTED))
    # підписи напруг знизу
    for x, lab in [(L + 40, "1.8 В"), (215, "2.5 В"), (360, "3.3 В"), (R - 55, "5 В")]:
        frags.append(line(x, B, x, B + 6, color=MUTED, sw=1.2))
        frags.append(text(x, B + 22, lab, size=11, color=MUTED))
    # вертикальний підпис швидкодії
    frags.append(text(0, 0, "швидше (менша затримка) ↑", size=13, color=MUTED,
                      anchor="middle"))
    frags[-1] = ('<g transform="translate(30,%d) rotate(-90)">%s</g>'
                 % ((T + B) // 2, text(0, 0, "швидше (менша затримка) ↑",
                                        size=13, color=MUTED)))

    # точки: (x, y, назва, живлення-текст, затримка-текст, drive)
    # y менше = вище = швидше
    pts = [
        (R - 55, 348, "74LS", "5 В (BJT)", "≈ 10 нс", "8 мА"),
        (R - 55, 300, "74HC", "2–6 В", "≈ 8 нс", "4 мА"),
        (R - 55, 258, "74HCT", "5 В", "≈ 10 нс", "4 мА"),
        (R - 55, 150, "74AHC", "2–5.5 В", "≈ 5 нс", "8 мА"),
        (360,    118, "74LVC", "1.65–3.6 В", "≈ 4 нс", "24 мА"),
    ]
    for x, y, name, volt, dly, drv in pts:
        frags.append(circle(x, y, 7, fill=FIELD, stroke=INK, sw=1.6))
        # ярлик збоку від точки, щоб не налазив на осі
        lx = x - 14
        b, _, _ = textbox(lx - 62, y, "%s\n%s · %s\n%s" % (name, volt, dly, drv),
                          size=11, pad=6, fill=FILL, stroke=LINE, sw=1.2, bold=False)
        frags.append(b)

    # стрілка «еволюція» від LS до LVC
    frags.append(('<path d="M %d %d Q %d %d %d %d" fill="none" stroke="%s" '
                  'stroke-width="1.6" stroke-dasharray="5,4" marker-end="url(#arrow)"/>'
                  % (R - 75, 340, 470, 190, 385, 128, POS)))
    frags.append(text(505, 235, "спуск напруги", size=11, color=POS, italic=True))
    frags.append(text(505, 251, "+ ріст швидкодії", size=11, color=POS, italic=True))

    render(os.path.join(OUT, 'subfamily-map.svg'), W, H, *frags,
           title="П'ять підродин на карті «напруга × швидкодія»")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2: два типи входу — CMOS-поріг проти TTL-порога — і хто читає TTL-«1»
#   спільна шкала 0..5 В; показуємо, що TTL-вихід дає лише 2.4 В (VOH),
#   HC-вхід хоче 3.5 В (провал), а HCT/LS/LVC-вхід хоче 2.0 В (дотягує)
# ─────────────────────────────────────────────────────────────────────────────
def fig_thresholds():
    W, H = 720, 430
    frags = []

    # шкала напруг зліва
    sx = 70
    y0, y5 = 380, 70                       # 0 В внизу, 5 В угорі
    def yv(v):                             # напруга -> y
        return y0 + (y5 - y0) * (v / 5.0)
    frags.append(line(sx, y0, sx, y5, color=INK, sw=2))
    for v in range(0, 6):
        frags.append(line(sx - 5, yv(v), sx, yv(v), color=INK, sw=1.2))
        frags.append(text(sx - 12, yv(v) + 4, "%d" % v, size=11, color=MUTED, anchor="end"))
    frags.append(text(sx - 30, (y0 + y5) / 2, "В", size=12, color=MUTED))

    # колонка 1: що ВИДАЄ 5 В TTL-вихід (VOH ≥ 2.4)
    c1 = 200
    frags.append(rect(c1 - 45, yv(2.4), 90, y0 - yv(2.4), fill="#e9f7ee", stroke=FIELD, sw=1.6))
    frags.append(line(c1 - 55, yv(2.4), c1 + 55, yv(2.4), color=FIELD, sw=2))
    frags.append(text(c1, yv(2.4) - 8, "VOH(min) = 2.4 В", size=11, color=FIELD, bold=True))
    frags.append(text(c1, y0 + 24, "видає", size=12, bold=True))
    frags.append(text(c1, y0 + 40, "5 В TTL-вихід", size=11, color=MUTED))

    # колонка 2: CMOS-вхід (HC) вимагає ≥ 3.5 В
    c2 = 420
    frags.append(rect(c2 - 45, y5, 90, yv(3.5) - y5, fill="#fdecea", stroke=POS, sw=1.6))
    frags.append(line(c2 - 55, yv(3.5), c2 + 55, yv(3.5), color=POS, sw=2))
    frags.append(text(c2, yv(3.5) - 8, "VIH = 3.5 В", size=11, color=POS, bold=True))
    frags.append(text(c2, y0 + 24, "CMOS-вхід", size=12, bold=True))
    frags.append(text(c2, y0 + 40, "74HC", size=11, color=MUTED))
    # провал між 2.4 і 3.5
    frags.append(('<rect x="%d" y="%.1f" width="90" height="%.1f" fill="#fff6d6" '
                  'stroke="#d9a400" stroke-width="1.2" stroke-dasharray="4,3"/>'
                  % (c2 - 45, yv(3.5), yv(2.4) - yv(3.5))))
    frags.append(text(c2, (yv(3.5) + yv(2.4)) / 2 + 4, "провал", size=11, color="#a07800"))

    # колонка 3: TTL-вхід (HCT/LS/LVC) вимагає ≥ 2.0 В
    c3 = 620
    frags.append(rect(c3 - 45, y5, 90, yv(2.0) - y5, fill="#fdecea", stroke=POS, sw=1.6))
    frags.append(line(c3 - 55, yv(2.0), c3 + 55, yv(2.0), color=POS, sw=2))
    frags.append(text(c3, yv(2.0) - 8, "VIH = 2.0 В", size=11, color=POS, bold=True))
    frags.append(text(c3, y0 + 24, "TTL-вхід", size=12, bold=True))
    frags.append(text(c3, y0 + 40, "HCT · LS · LVC", size=11, color=MUTED))
    # запас: від 2.0 до 2.4 — зелена смужка «дотягує»
    frags.append(rect(c3 - 45, yv(2.4), 90, yv(2.0) - yv(2.4), fill="#e9f7ee", stroke=FIELD, sw=1.2))
    frags.append(text(c3, (yv(2.0) + yv(2.4)) / 2 + 4, "запас", size=10, color=FIELD))

    # рівень 2.4 продовжити пунктиром через усі колонки
    frags.append(line(c1 + 45, yv(2.4), c3 + 45, yv(2.4), color=FIELD, sw=1, dash="3,4"))

    render(os.path.join(OUT, 'input-thresholds.svg'), W, H, *frags,
           title="Той самий сигнал, два пороги входу: провал у HC, запас у HCT/LS/LVC")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 3: дерево вибору підродини за трьома питаннями
# ─────────────────────────────────────────────────────────────────────────────
def fig_choose():
    W, H = 720, 430
    frags = []

    q1, _, _ = textbox(200, 60, "Яка напруга\nвузла?", size=13, pad=10,
                       fill="#eef3ff", stroke=NEG, sw=1.8, bold=True, min_w=150)
    frags.append(q1)

    # гілка 3.3 В і нижче -> LVC
    frags.append(arrow(200, 92, 200, 150, color=NEG))
    frags.append(text(120, 128, "3.3 В і нижче", size=11, color=MUTED))
    lvc, _, _ = textbox(200, 175, "74LVC / 74AUP\n(вхід терпить 5 В —\nміст «вниз»)",
                        size=12, pad=9, fill="#e9f7ee", stroke=FIELD, sw=1.6, min_w=190)
    frags.append(lvc)

    # гілка 5 В -> питання про джерело
    frags.append(arrow(255, 78, 500, 78, color=NEG))
    frags.append(text(360, 66, "5 В", size=11, color=MUTED))
    q2, _, _ = textbox(555, 78, "Джерело —\nстарий 5 В TTL?", size=12, pad=9,
                       fill="#eef3ff", stroke=NEG, sw=1.8, bold=True, min_w=175)
    frags.append(q2)

    # так -> HCT/AHCT
    frags.append(arrow(555, 108, 555, 165, color=NEG))
    frags.append(text(520, 140, "так", size=11, color=MUTED))
    hct, _, _ = textbox(555, 190, "74HCT / 74AHCT\n(вхід під TTL-поріг\n2.0 В)",
                        size=12, pad=9, fill="#e9f7ee", stroke=FIELD, sw=1.6, min_w=185)
    frags.append(hct)

    # ні -> HC/AHC
    frags.append(arrow(618, 78, 690, 78, color=NEG))
    frags.append(('<path d="M 690 78 Q 705 78 705 120 L 705 250 Q 705 285 660 285" '
                  'fill="none" stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>' % NEG))
    frags.append(text(700, 100, "ні", size=11, color=MUTED))
    hc, _, _ = textbox(555, 285, "74HC / 74AHC\n(усе на одній 5 В;\nAHC — коли треба швидше)",
                       size=12, pad=9, fill="#e9f7ee", stroke=FIELD, sw=1.6, min_w=230)
    frags.append(hc)

    # нижня примітка-питання про швидкість/струм
    note, _, _ = textbox(200, 300, "Треба помітно швидше\nчи сильніший вихід?\n→ бери «A»-варіант\n(AHC замість HC)",
                         size=12, pad=10, fill=FILL, stroke=LINE, sw=1.4, min_w=230)
    frags.append(note)
    frags.append(line(200, 200, 200, 253, color=MUTED, sw=1, dash="3,4"))

    render(os.path.join(OUT, 'choose-subfamily.svg'), W, H, *frags,
           title="Як обрати підродину: напруга → джерело → швидкість")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 4 (вставка comp): типова розпіновка одновентильного чипа
#   корпус SOT-23-5 / SC-70, вигляд ЗВЕРХУ; 2 входи + 1 вихід + Vcc + GND.
#   Показуємо «діагональ»: входи ліворуч (1,2), вихід і живлення праворуч,
#   а всередині — сам вентиль, щоб було видно, куди що йде.
# ─────────────────────────────────────────────────────────────────────────────
def fig_pinout():
    W, H = 720, 430
    frags = []

    # корпус чипа (прямокутник тіла) з ключем-крапкою біля піна 1
    bx, by, bw, bh = 250, 120, 220, 190
    frags.append(rect(bx, by, bw, bh, fill="#eef1f5", stroke=INK, sw=2, rx=10))
    frags.append(text(bx + bw / 2, by - 14, "вигляд зверху (SOT-23-5 / SC-70)",
                      size=12, color=MUTED))
    # крапка-ключ біля піна 1 (лівий нижній кут — типово)
    frags.append(circle(bx + 16, by + bh - 16, 4, fill=INK, stroke=INK, sw=1))

    # ніжки: три ліворуч (piny 1,2,3 знизу вгору), дві праворуч (4,5)
    leg = 30
    def pin_left(cy, num, name, sub):
        y = cy
        frags.append(line(bx, y, bx - leg, y, color=INK, sw=3))
        frags.append(circle(bx - leg, y, 3, fill=INK))
        frags.append(text(bx - leg - 8, y - 8, "%d" % num, size=12, color=MUTED, anchor="end"))
        b, _, _ = textbox(bx - leg - 62, y + 4, "%s\n%s" % (name, sub),
                          size=11, pad=5, fill=FILL, stroke=LINE, sw=1.2)
        frags.append(b)
    def pin_right(cy, num, name, sub, col=INK):
        y = cy
        frags.append(line(bx + bw, y, bx + bw + leg, y, color=INK, sw=3))
        frags.append(circle(bx + bw + leg, y, 3, fill=INK))
        frags.append(text(bx + bw + leg + 8, y - 8, "%d" % num, size=12, color=MUTED))
        b, _, _ = textbox(bx + bw + leg + 60, y + 4, "%s\n%s" % (name, sub),
                          size=11, pad=5, fill=FILL, stroke=LINE, sw=1.2, color=col)
        frags.append(b)

    yA, yB, yG = by + 40, by + 95, by + 150     # piny 1,2,3 ліворуч
    y5, y4     = by + 55, by + 135              # piny 5,4 праворуч
    pin_left(yA, 1, "A", "вхід")
    pin_left(yB, 2, "B", "вхід")
    pin_left(yG, 3, "GND", "земля")
    pin_right(y5, 5, "Vcc", "живлення", col=POS)
    pin_right(y4, 4, "Y", "вихід", col=NEG)

    # символ вентиля всередині (умовний «≥1 / &»): просто трикутник-натяк
    gx, gy = bx + bw / 2, by + bh / 2 - 8
    frags.append(('<path d="M %d %d L %d %d L %d %d Z" fill="#ffffff" '
                  'stroke="%s" stroke-width="1.6"/>'
                  % (gx - 24, gy - 22, gx - 24, gy + 22, gx + 22, gy, INK)))
    frags.append(circle(gx + 27, gy, 4, fill="#ffffff", stroke=INK, sw=1.4))  # кулька інверсії (як приклад)
    frags.append(text(gx - 6, gy + 4, "1", size=12, color=MUTED))
    # тонкі внутрішні зв'язки вхід→вентиль, вентиль→вихід
    frags.append(line(bx, yA, gx - 24, gy - 12, color=MUTED, sw=1, dash="3,3"))
    frags.append(line(bx, yB, gx - 24, gy + 12, color=MUTED, sw=1, dash="3,3"))
    frags.append(line(gx + 31, gy, bx + bw, y4, color=MUTED, sw=1, dash="3,3"))

    # примітка внизу
    note, _, _ = textbox(W / 2, H - 30,
                         "5 ніжок: 2 входи + 1 вихід + Vcc + GND. "
                         "Розташування піна 1 — за крапкою-ключем; звіряй із даташитом.",
                         size=11, pad=8, fill="#fff6d6", stroke="#d9a400", sw=1.2, min_w=560)
    frags.append(note)

    render(os.path.join(OUT, 'single-gate-pinout.svg'), W, H, *frags,
           title="Типова розпіновка одновентильного чипа (5 виводів)")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 5 (вставка comp): дві головні лінії класу — LVC проти AUP
#   осі: X — до якої напруги терпить вхід (3.6 В у AUP, 5 В у LVC)
#        Y — статичний струм спокою (log-натяк): AUP ≈ 0.9 мкА, LVC — більший
#   щоб читач бачив, що вибір усередині класу — це «терпимість входу ↔ економність»
# ─────────────────────────────────────────────────────────────────────────────
def fig_class_variants():
    W, H = 720, 400
    frags = []
    L, R, T, B = 110, 620, 80, 300
    frags.append(line(L, B, R, B, color=INK, sw=2))
    frags.append(line(L, B, L, T, color=INK, sw=2))
    frags.append(text((L + R) / 2, B + 52, "до якої напруги терпить вхід →", size=13, color=MUTED))
    frags.append(('<g transform="translate(34,%d) rotate(-90)">%s</g>'
                  % ((T + B) // 2, text(0, 0, "статичний струм спокою ↑ (більший)",
                                         size=12, color=MUTED))))
    # мітки X
    for x, lab in [(230, "3.6 В"), (R - 60, "5 В")]:
        frags.append(line(x, B, x, B + 6, color=MUTED, sw=1.2))
        frags.append(text(x, B + 22, lab, size=11, color=MUTED))

    # дві точки-родини
    # AUP: терпить 3.6 В, струм крихітний (низько) → внизу ліворуч
    ax, ay = 230, 250
    frags.append(circle(ax, ay, 8, fill="#e9f7ee", stroke=FIELD, sw=2))
    b, _, _ = textbox(ax + 96, ay, "клас AUP\n0.8–3.6 В · вхід терпить 3.6 В\nICC ≈ 0.9 мкА · tpd ≈ 3.2 нс",
                      size=11, pad=7, fill=FILL, stroke=FIELD, sw=1.4, min_w=250)
    frags.append(b)
    # LVC: терпить 5 В, струм більший (вище) → вгорі праворуч
    lx, ly = R - 60, 150
    frags.append(circle(lx, ly, 8, fill="#e9f7ee", stroke=NEG, sw=2))
    b, _, _ = textbox(lx - 150, ly, "клас LVC\n1.65–3.6 В · вхід терпить 5 В\nсильний вихід (≈ 24 мА) · tpd ≈ 3.5 нс",
                      size=11, pad=7, fill=FILL, stroke=NEG, sw=1.4, min_w=250)
    frags.append(b)

    # стрілка-компроміс між ними
    frags.append(('<path d="M %d %d Q %d %d %d %d" fill="none" stroke="%s" '
                  'stroke-width="1.4" stroke-dasharray="5,4" marker-end="url(#arrow)"/>'
                  % (ax + 10, ay - 8, 380, 180, lx - 12, ly + 10, MUTED)))
    frags.append(text(400, 235, "більше терпить вхід і сильніший вихід —", size=10.5, color=MUTED))
    frags.append(text(400, 250, "але й струму більше; AUP — навпаки, ощадність", size=10.5, color=MUTED))

    render(os.path.join(OUT, 'class-variants.svg'), W, H, *frags,
           title="Дві лінії дрібної логіки: AUP (ощадність) ↔ LVC (терпить 5 В)")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 6 (вставка math-drive-fanout): розклад повної ємності на виводі
#   ліворуч — стовпчик C_повна = входи + доріжка + власна ємність виходу
#   праворуч — та сама сума як «бюджет»: стеля C_max, з якої доріжка забирає
#              свою частку, а залишок ділиться на входи
# ─────────────────────────────────────────────────────────────────────────────
def fig_cap_budget():
    W, H = 720, 440
    frags = []

    # спільна вертикальна шкала пікофарад (0 внизу, до 40 пФ угорі)
    base = 380                    # y для 0 пФ
    top = 80                      # y для верху шкали
    pf_max = 40.0                 # верх шкали, пФ
    def yp(pf):                   # пФ -> y
        return base + (top - base) * (pf / pf_max)

    bw = 96                       # ширина стовпчиків

    # ── лівий стовпчик: із чого складається C_повна (знизу вгору) ────────────
    cx = 190
    segs = [
        (15.0, "#e9f7ee", FIELD,     "доріжка\n15 пФ"),
        (4.0,  "#eef3ff", NEG,       "C_вих 4 пФ"),
        (20.0, "#fdf0e6", "#c0672b", "входи\n4×5 = 20 пФ"),
    ]
    acc = 0.0
    for val, fill, stroke, lab in segs:
        y_lo, y_hi = yp(acc), yp(acc + val)
        frags.append(rect(cx - bw / 2, y_hi, bw, y_lo - y_hi, fill=fill, stroke=stroke, sw=1.6))
        frags.append(fitbox(cx - bw / 2 + 3, y_hi + 3, bw - 6, (y_lo - y_hi) - 6,
                            lab, size=11, pad=2, fill="none", stroke="none"))
        acc += val
    frags.append(text(cx, base + 24, "C_повна = 39 пФ", size=12, bold=True))

    # ── права колонка: бюджет — стеля C_max, доріжка знизу, залишок під входи ─
    dx = 540
    cmax = 36.0                   # стеля C_max за прикладом (t = 30 нс)
    # фон повного бюджету до стелі
    frags.append(rect(dx - bw / 2, yp(cmax), bw, base - yp(cmax),
                      fill="#fbfbfb", stroke=LINE, sw=1.4))
    # межа стелі
    frags.append(line(dx - bw / 2 - 12, yp(cmax), dx + bw / 2 + 12, yp(cmax), color=INK, sw=2))
    frags.append(text(dx, yp(cmax) - 10, "C_max = 36 пФ", size=11, bold=True))
    # доріжка забирає нижні 15 пФ
    frags.append(rect(dx - bw / 2, yp(15.0), bw, base - yp(15.0),
                      fill="#e9f7ee", stroke=FIELD, sw=1.6))
    frags.append(text(dx, (base + yp(15.0)) / 2 + 4, "доріжка 15", size=10, color=FIELD))
    # залишок під входи (пунктиром)
    frags.append(('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="4" '
                  'fill="#fdf0e6" stroke="#c0672b" stroke-width="1.6" '
                  'stroke-dasharray="5,3"/>' % (dx - bw / 2, yp(cmax), bw, yp(15.0) - yp(cmax))))
    frags.append(fitbox(dx - bw / 2 + 3, yp(cmax) + 4, bw - 6, yp(15.0) - yp(cmax) - 8,
                        "залишок 21 пФ\n→ 4 входи", size=10, pad=2, fill="none", stroke="none"))
    frags.append(text(dx, base + 24, "бюджет (t = 30 нс)", size=12, bold=True))

    # шкала пФ між колонками
    sx = 360
    frags.append(line(sx, base, sx, top, color=MUTED, sw=1.2))
    for pf in (0, 10, 20, 30, 40):
        frags.append(line(sx - 4, yp(pf), sx + 4, yp(pf), color=MUTED, sw=1))
        frags.append(text(sx + 17, yp(pf) + 4, "%d" % pf, size=10, color=MUTED))
    frags.append(text(sx, top - 14, "пФ", size=11, color=MUTED))

    render(os.path.join(OUT, 'cap-budget.svg'), W, H, *frags,
           title="Повна ємність на виводі: зі складових — і як бюджет під входи")


if __name__ == "__main__":
    fig_map()
    fig_thresholds()
    fig_choose()
    fig_pinout()
    fig_class_variants()
    fig_cap_budget()
    print("figures written to", OUT)
