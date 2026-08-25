# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «Tower Pro SG90 — мікросерво 9g».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

MOTOR = "#c0392b"
GEAR = "#8a6d00"
POT = "#7d3c98"
BRAIN = "#2457d6"


# ── 1. Внутрішній замкнений контур: мозок → мотор → редуктор → вал ⇄ потенціометр
def fig_loop():
    W, H = 916, 470
    f = [text(W / 2, 30, "Що всередині: замкнений контур, що жене вал до заданого кута",
              size=16, bold=True)]

    # блоки в ряд: PWM-вхід → мозок → мотор → редуктор → вал
    def block(x, y, w, h, title, sub, fill, stroke):
        f.append(rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.8, rx=10))
        f.append(text(x + w / 2, y + h / 2 - 6, title, size=12.5, bold=True, color=INK))
        f.append(text(x + w / 2, y + h / 2 + 12, sub, size=9.5, color=MUTED))

    y0 = 110
    bh = 66
    # координати блоків
    sig_x, sig_w = 40, 120
    brain_x, brain_w = 200, 150
    mot_x, mot_w = 400, 120
    gear_x, gear_w = 560, 130
    shaft_x, shaft_w = 730, 110

    block(sig_x, y0, sig_w, bh, "PWM-вхід", "імпульс 1..2 мс", "#eef2f8", NEG)
    block(brain_x, y0, brain_w, bh, "Мозок (IC)", "порівняти й керувати", "#e8eefc", BRAIN)
    block(mot_x, y0, mot_w, bh, "DC-мотор", "швидко, слабко", "#fdecea", MOTOR)
    block(gear_x, y0, gear_w, bh, "Редуктор", "повільно, сильно", "#fff6e5", GEAR)
    block(shaft_x, y0, shaft_w, bh, "Вал-качалка", "кут виходу", "#eef6ef", FIELD)

    yc = y0 + bh / 2
    # стрілки вперед по ланцюгу
    f.append(arrow(sig_x + sig_w, yc, brain_x, yc, color=INK, sw=2))
    f.append(arrow(brain_x + brain_w, yc, mot_x, yc, color=INK, sw=2))
    f.append(arrow(mot_x + mot_w, yc, gear_x, yc, color=INK, sw=2))
    f.append(arrow(gear_x + gear_w, yc, shaft_x, yc, color=INK, sw=2))

    # потенціометр під валом, зчитує кут
    pot_x, pot_w = 730, 110
    pot_y, pot_h = 300, 58
    f.append(rect(pot_x, pot_y, pot_w, pot_h, fill="#f3e9f8", stroke=POT, sw=1.8, rx=10))
    f.append(text(pot_x + pot_w / 2, pot_y + 24, "Потенціометр", size=12, bold=True, color=POT))
    f.append(text(pot_x + pot_w / 2, pot_y + 42, "міряє реальний кут", size=9.5, color=MUTED))

    # вал крутить потенціометр (вниз)
    f.append(arrow(shaft_x + shaft_w / 2, y0 + bh, pot_x + pot_w / 2, pot_y, color=POT, sw=2))
    f.append(text(shaft_x + shaft_w / 2 + 60, (y0 + bh + pot_y) / 2 + 4,
                  "вал крутить", size=10, color=POT, anchor="start"))

    # зворотний зв'язок: потенціометр → мозок (довга дуга низом)
    fb_y = pot_y + pot_h / 2
    brain_cy = y0 + bh + 40
    # горизонталь від потенціометра ліворуч до під-мозку, тоді вгору в мозок
    f.append(line(pot_x, fb_y, brain_x + brain_w / 2, fb_y, color=POT, sw=2, dash="6,5"))
    f.append(arrow(brain_x + brain_w / 2, fb_y, brain_x + brain_w / 2, y0 + bh, color=POT, sw=2))
    f.append(text((pot_x + brain_x + brain_w / 2) / 2, fb_y - 10,
                  "зворотний зв'язок: «а де я насправді?»", size=10.5, bold=True, color=POT))

    # підпис ланцюга помилки
    b, _, _ = textbox(W / 2, 440,
                      "мозок віднімає реальний кут від заданого; є різниця — крутить мотор у бік її зменшення, доки не збіжаться",
                      size=11.5, fill=FILL, stroke=LINE, min_w=780)
    f.append(b)
    render(os.path.join(IMG, "loop.svg"), W, H, *f)


# ── 2. PWM: ширина імпульсу задає кут (період 20 мс = 50 Гц) ──────────────────
def fig_pwm():
    W, H = 860, 540
    f = [text(W / 2, 30, "Керування: ширина імпульсу — це кут, повтор кожні 20 мс",
              size=16, bold=True)]

    # три доріжки: 1.0 / 1.5 / 2.0 мс, кожна зі своєю качалкою праворуч
    rows = [
        (1.0, "1.0 мс", "0°", "крайнє проти годинника"),
        (1.5, "1.5 мс", "90°", "середина (нейтраль)"),
        (2.0, "2.0 мс", "180°", "крайнє за годинником"),
    ]
    # геометрія осі часу
    ax0 = 60             # x=0 мс
    span_ms = 21.0       # показуємо трохи більше за період
    ax1 = 560            # правий край осі
    px_per_ms = (ax1 - ax0) / span_ms
    period = 20.0
    lo, hi = 90, 40      # рівні низу/верху сигналу (y)

    ry0 = 95
    rdy = 140
    for i, (ms, lab, ang, note) in enumerate(rows):
        y = ry0 + i * rdy
        base = y + 60           # нульова лінія доріжки
        top = y + 18            # верх імпульсу
        # вісь часу
        f.append(line(ax0, base, ax1 + 10, base, color=MUTED, sw=1.3))
        # мітка 0 і 20 мс
        f.append(text(ax0, base + 16, "0", size=9, color=MUTED))
        f.append(line(ax0 + period * px_per_ms, base - 4, ax0 + period * px_per_ms, base + 4,
                      color=MUTED, sw=1.3))
        f.append(text(ax0 + period * px_per_ms, base + 16, "20 мс", size=9, color=MUTED))

        # імпульс: низ-верх-низ
        w_px = ms * px_per_ms
        x1 = ax0
        x2 = ax0 + w_px
        col = MOTOR if i != 1 else FIELD
        f.append(line(x1, base, x1, top, color=col, sw=2.4))
        f.append(line(x1, top, x2, top, color=col, sw=2.4))
        f.append(line(x2, top, x2, base, color=col, sw=2.4))
        # тривалість імпульсу
        f.append(text((x1 + x2) / 2, top - 8, lab, size=11, bold=True, color=col))
        # решта періоду — низ, тоді наступний імпульс (пунктир)
        f.append(line(x2, base, ax0 + period * px_per_ms, base, color=MUTED, sw=1.3))
        nx1 = ax0 + period * px_per_ms
        nx2 = nx1 + w_px
        if nx2 < ax1 + 10:
            f.append(line(nx1, base, nx1, top, color=col, sw=2, dash="4,3"))
            f.append(line(nx1, top, min(nx2, ax1 + 10), top, color=col, sw=2, dash="4,3"))

        # качалка праворуч: сектор із стрілкою під кутом
        gx, gy, gr = 690, base - 22, 44
        f.append(circle(gx, gy, gr, fill="#fafbfc", stroke=INK, sw=1.6))
        # мапа: 0°→ліво(180° мат.), 90°→вгору, 180°→право(0° мат.)
        import math
        # кут стрілки в екранних координатах: 0° сервокута = вліво, 180° = вправо
        theta = math.radians(180 - float(ang.rstrip("°")))
        ex = gx + gr * 0.86 * math.cos(theta)
        ey = gy - gr * 0.86 * math.sin(theta)
        f.append(line(gx, gy, ex, ey, color=col, sw=3))
        f.append(circle(gx, gy, 4, fill=col, stroke="none", sw=0))
        f.append(text(gx + gr + 30, gy - 6, ang, size=13, bold=True, color=col, anchor="start"))
        f.append(text(gx + gr + 30, gy + 12, note, size=9.5, color=MUTED, anchor="start"))

    b, _, _ = textbox(W / 2, 508,
                      "тільки ширина імпульсу несе команду; 1.5 мс — нейтраль. Каталожні межі 0.5..2.4 мс б'ють об упори — тримайся 1..2 мс.",
                      size=11, fill=FILL, stroke=LINE, min_w=790)
    f.append(b)
    render(os.path.join(IMG, "pwm.svg"), W, H, *f)


# ── 3. Розводка пін-у-пін: 3 дроти, окреме живлення, спільна земля ────────────
def fig_wiring():
    W, H = 880, 500
    f = [text(W / 2, 30, "Підключення: три дроти, живлення окреме, земля спільна",
              size=16, bold=True)]

    ORG = "#e67e22"          # оранжевий — сигнал
    BRN = "#6e4b2a"          # коричневий — земля

    # МК ліворуч (угорі)
    mx, my, mw, mh = 40, 70, 165, 150
    f.append(rect(mx, my, mw, mh, fill="#eef2f8", stroke=INK, sw=1.8, rx=10))
    f.append(text(mx + mw / 2, my + 26, "Мікроконтролер", size=12.5, bold=True))
    f.append(text(mx + mw / 2, my + 44, "PWM-вивід", size=10, color=MUTED))

    # серво праворуч
    sx, sy, sw_, sh = 640, 70, 200, 200
    f.append(rect(sx, sy, sw_, sh, fill="#eef6ef", stroke=INK, sw=1.8, rx=10))
    f.append(text(sx + sw_ / 2, sy + 26, "SG90", size=12.5, bold=True))
    f.append(text(sx + sw_ / 2, sy + 44, "3-дротовий роз'єм", size=10, color=MUTED))

    # окреме живлення 5 В (блок унизу-ліворуч)
    px, py, pw, ph = 40, 330, 165, 60
    f.append(rect(px, py, pw, ph, fill="#fdecea", stroke=MOTOR, sw=1.8, rx=10))
    f.append(text(px + pw / 2, py + 25, "Живлення 5 В", size=12, bold=True, color=MOTOR))
    f.append(text(px + pw / 2, py + 44, "≥1 А, не з плати!", size=9.5, color=MUTED))

    # три контакти на СЕРВІ (лівий край), добре рознесені по вертикалі
    ysig = sy + 80
    ypwr = sy + 120
    ygnd = sy + 160
    xin = sx                 # лівий край серво
    servo_pins = [
        ("Сигнал", "оранжевий", ORG, ysig),
        ("+5 В", "червоний", MOTOR, ypwr),
        ("GND", "коричневий", BRN, ygnd),
    ]
    for name, colour, col, y in servo_pins:
        f.append(circle(xin, y, 3.5, fill=col, stroke="none", sw=0))
        f.append(text(xin + 14, y + 1, name, size=11, bold=True, color=col, anchor="start"))
        f.append(text(xin + 14, y + 17, colour, size=9, color=MUTED, anchor="start"))

    # ── СИГНАЛ (оранжевий): від МК-виводу до серва, верхня чиста доріжка ──
    f.append(circle(mx + mw, ysig, 3.5, fill=ORG, stroke="none", sw=0))
    f.append(text(mx + mw - 12, ysig - 9, "IO", size=9, color=INK, anchor="end"))
    f.append(line(mx + mw, ysig, xin, ysig, color=ORG, sw=2))

    # ── +5 В (червоний): від живлення вгору по x=290, тоді вправо до серва ──
    xpwr_v = 290
    f.append(line(px + pw, py + ph / 2, xpwr_v, py + ph / 2, color=MOTOR, sw=2))
    f.append(line(xpwr_v, py + ph / 2, xpwr_v, ypwr, color=MOTOR, sw=2))
    f.append(line(xpwr_v, ypwr, xin, ypwr, color=MOTOR, sw=2))

    # ── GND (коричневий): спільна точка-вузол, від МК і від живлення разом ──
    # вертикаль-шина землі стоїть праворуч від +5В-вертикалі, щоб не збігатися
    xgnd_v = 350
    # від МК: вниз по x=(mx+mw+30) до рівня ygnd, тоді вправо у вузол
    xmcu_drop = mx + mw + 30
    f.append(circle(mx + mw, my + mh - 24, 3.5, fill=BRN, stroke="none", sw=0))
    f.append(text(mx + mw - 12, my + mh - 33, "GND", size=9, color=INK, anchor="end"))
    f.append(line(mx + mw, my + mh - 24, xmcu_drop, my + mh - 24, color=BRN, sw=2))
    f.append(line(xmcu_drop, my + mh - 24, xmcu_drop, ygnd, color=BRN, sw=2))
    f.append(line(xmcu_drop, ygnd, xin, ygnd, color=BRN, sw=2))
    # від живлення (−): вниз із ПРАВОГО краю блока (не крізь підпис) і вправо
    ybus = ygnd + 55
    xpwr_drop = px + pw - 22          # правий край блока живлення, повз центр-підпис
    f.append(line(xpwr_drop, py + ph, xpwr_drop, ybus, color=BRN, sw=2))
    f.append(line(xpwr_drop, ybus, xgnd_v, ybus, color=BRN, sw=2))
    f.append(line(xgnd_v, ybus, xgnd_v, ygnd, color=BRN, sw=2))
    # вузол спільної землі на лінії ygnd
    f.append(circle(xgnd_v, ygnd, 4.5, fill=BRN, stroke="none", sw=0))
    f.append(text(xgnd_v + 130, ybus + 22, "спільна земля — один вузол", size=10.5, bold=True,
                  color=BRN, anchor="start"))

    b, _, _ = textbox(W / 2, 470,
                      "живлення серва — від окремого джерела, НЕ з ніжки 5 В плати;\nземля плати й джерела мусить сходитись в одному вузлі, інакше сигнал «не бачать»",
                      size=11, fill=FILL, stroke=LINE, min_w=780)
    f.append(b)
    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


# ── 4. Три коду-шкали над однією фізичною віссю ширини імпульсу ────────────────
def fig_scales():
    """Одна фізична вісь (ширина імпульсу, мс) — і три способи назвати те саме
    число з коду: Servo.write(кут), writeMicroseconds(мкс), лічильник PCA9685."""
    W, H = 940, 520
    f = [text(W / 2, 32, "Одна вісь ширини імпульсу — три способи назвати її з коду",
              size=16, bold=True)]

    # фізична вісь часу: 1.0 .. 2.0 мс (робоче вікно), з широким запасом обабіч
    ax0, ax1 = 245, 800          # x-межі осі (лишаємо місце написам шкал ліворуч)
    ms_lo, ms_hi = 1.0, 2.0
    axy = 290                    # y осі
    span = ms_hi - ms_lo
    def X(ms):
        return ax0 + (ms - ms_lo) / span * (ax1 - ax0)

    # сама вісь із поділками на 1.0 / 1.25 / 1.5 / 1.75 / 2.0
    f.append(line(ax0 - 14, axy, ax1 + 14, axy, color=INK, sw=2.2))
    ticks = [1.0, 1.25, 1.5, 1.75, 2.0]
    for ms in ticks:
        x = X(ms)
        f.append(line(x, axy - 7, x, axy + 7, color=INK, sw=1.8))
        f.append(text(x, axy + 26, ("%.2f мс" % ms).replace(".00", ".0"),
                      size=11, bold=True, color=INK))
    f.append(text(W / 2, axy + 50, "ФІЗИЧНА ШИРИНА ІМПУЛЬСУ (те, що серво насправді бачить)",
                  size=11, bold=True, color=MUTED))

    # заголовки трьох шкал — окремим стовпчиком ЛІВОРУЧ від осі, кожен на своєму рівні
    lab_x = 26

    # ── шкала 1 (зверху): Servo.write(кут 0..180) ──
    y1 = axy - 150
    f.append(text(lab_x, y1 - 5, "Servo.write(кут)", size=12.5, bold=True,
                  color=BRAIN, anchor="start"))
    f.append(text(lab_x, y1 + 12, "0..180 → 1..2 мс", size=9.5, color=MUTED, anchor="start"))
    for ms, ang in [(1.0, "0"), (1.5, "90"), (2.0, "180")]:
        x = X(ms)
        f.append(circle(x, y1, 4, fill=BRAIN, stroke="none", sw=0))
        # короткий стуб-вирівнювання лише біля осі (щоб не перетинати чужі написи)
        f.append(line(x, axy - 22, x, axy - 8, color=BRAIN, sw=1.3, dash="4,4"))
        f.append(text(x, y1 - 9, "write(%s)" % ang, size=10.5, bold=True, color=BRAIN))

    # ── шкала 2 (ближче до осі, зверху): writeMicroseconds(1000..2000) ──
    y2 = axy - 66
    f.append(text(lab_x, y2 - 5, "writeMicroseconds", size=12.5, bold=True,
                  color=FIELD, anchor="start"))
    f.append(text(lab_x, y2 + 12, "прямо в мкс", size=9.5, color=MUTED, anchor="start"))
    for ms, us in [(1.0, "1000"), (1.5, "1500"), (2.0, "2000")]:
        x = X(ms)
        f.append(circle(x, y2, 4, fill=FIELD, stroke="none", sw=0))
        f.append(text(x, y2 - 9, us, size=10.5, bold=True, color=FIELD))

    # ── шкала 3 (знизу): лічильник PCA9685 (12 біт, 4096 кроків @ 50 Гц) ──
    # крок @50Гц = 20мс/4096 ≈ 4.88 мкс; count = ширина_мкс / 4.88
    y3 = axy + 130
    f.append(text(lab_x, y3 - 4, "PCA9685 count", size=12.5, bold=True,
                  color=POT, anchor="start"))
    f.append(text(lab_x, y3 + 13, "0..4095 @ 50 Гц", size=9.5, color=MUTED, anchor="start"))
    f.append(text(lab_x, y3 + 29, "крок ≈ 4.88 мкс", size=9.5, color=MUTED, anchor="start"))
    for ms, cnt in [(1.0, "≈205"), (1.5, "≈307"), (2.0, "≈410")]:
        x = X(ms)
        f.append(circle(x, y3, 4, fill=POT, stroke="none", sw=0))
        # короткий стуб-вирівнювання лише біля осі (не тягнемо крізь підпис осі)
        f.append(line(x, axy + 8, x, axy + 22, color=POT, sw=1.3, dash="4,4"))
        f.append(text(x, y3 + 6, cnt, size=10.5, bold=True, color=POT))

    b, _, _ = textbox(W / 2, 480,
                      "усі три рядки — ОДНЕ число ширини під різними іменами;\nкалібрування = які мкс дають рівно 0° і 180° на ЦЬОМУ екземплярі",
                      size=11, fill=FILL, stroke=LINE, min_w=760)
    f.append(b)
    render(os.path.join(IMG, "scales.svg"), W, H, *f)


# ── 5. Народження сервостандарту: від дискретних команд до ширини імпульсу ─────
def fig_history():
    """Історична фігура для вставки hist-servo-standard.md:
    еволюція керування — escapement (кілька дискретних позицій) →
    рід/reed (набір каналів) → Galloping Ghost (миготіння) →
    Digicon 1962 (пропорційна ширина 1..2 мс, нейтраль 1.5 мс) — жива й досі."""
    W, H = 900, 500
    f = [text(W / 2, 30, "Як команда до серва ставала пропорційною: чотири покоління",
              size=16, bold=True)]

    # спільна вісь років
    ax0, ax1 = 70, 830
    axy = 150
    f.append(line(ax0, axy, ax1, axy, color=INK, sw=2))
    for yr, lab in [(1937, "1937"), (1950, "1950"), (1954, "1954"),
                    (1962, "1962"), (2010, "…нині")]:
        x = ax0 + (yr - 1937) / (2010 - 1937) * (ax1 - ax0)
        f.append(line(x, axy - 5, x, axy + 5, color=INK, sw=1.6))
        f.append(text(x, axy + 22, lab, size=10.5, color=MUTED))

    # чотири блоки-покоління, кожен зі своїм «виходом»
    STEP = "#2457d6"
    gens = [
        (90,  "Escapement", "гумовий джгут, кілька\nдискретних позицій керма",
         "ліво · центр · право", "#fdecea", POS),
        (280, "Reed / рід", "тонові канали, кермо\nсмикають «блимаючи»",
         "набір увімк/вимк", "#fff6e5", GEAR),
        (500, "Galloping Ghost", "один канал миготить —\nсереднє дає плавність",
         "квазі-плавно, дрижить", "#eef6ef", FIELD),
        (720, "Digicon 1962", "ШИРИНА імпульсу 1..2 мс,\nнейтраль 1.5 мс, 50 Гц",
         "справді пропорційно", "#e8eefc", STEP),
    ]
    by, bw, bh = 250, 165, 120
    for bx, ttl, sub, out, fill, col in gens:
        f.append(rect(bx, by, bw, bh, fill=fill, stroke=col, sw=1.9, rx=11))
        f.append(text(bx + bw / 2, by + 24, ttl, size=12.5, bold=True, color=col))
        f.append(mtext(bx + bw / 2, by + 46, sub, size=9.3, color=INK, lh=1.25))
        f.append(line(bx + 14, by + bh - 30, bx + bw - 14, by + bh - 30,
                      color=MUTED, sw=1))
        f.append(text(bx + bw / 2, by + bh - 12, out, size=9.5, bold=True, color=col))

    # стрілки «поглиблення» між блоками
    for i in range(len(gens) - 1):
        x1 = gens[i][0] + bw
        x2 = gens[i + 1][0]
        f.append(arrow(x1, by + bh / 2, x2, by + bh / 2, color=INK, sw=2))

    # підпис-висновок унизу — рамкою, з запасом ширини
    b, _, _ = textbox(W / 2, 440,
                      "Спільною мовою серв стала не частота й не напруга, а тривалість «високого»:\n"
                      "домовленість 1962 року (Спренґ і Метіс, Digicon) пережила лампи, транзистори й цифру — їй кориться й дешевий SG90.",
                      size=11, fill=FILL, stroke=LINE, min_w=820)
    f.append(b)
    render(os.path.join(IMG, "servo-standard-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_loop()
    fig_pwm()
    fig_wiring()
    fig_scales()
    fig_history()
    print("OK: 5 figures ->", IMG)
