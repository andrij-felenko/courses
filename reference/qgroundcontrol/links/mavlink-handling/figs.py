# -*- coding: utf-8 -*-
"""Фігури до теми «Обробка MAVLink: розбір, версії, канали» довідника QGroundControl."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

BAND = "#eef2f6"
SOFT = "#ffffff"
WARM = "#fdf3e7"
COLD = "#eaf0fd"
GOOD = "#eaf7ef"


# ───────────────── 1. Канал як слот стану ─────────────────
def fig_channel_slots():
    W, H = 1240, 700
    f = []

    f.append(text(W / 2, 34, "Номер каналу індексує глобальний стан бібліотеки", size=17, bold=True))

    # ліворуч: джерела
    f.append(rect(30, 70, 340, 470, fill=BAND, stroke="#c8d2dc", sw=1.2, rx=10))
    f.append(text(200, 100, "джерела кадрів у застосунку", size=13, color=MUTED))

    srcs = [
        (140, "серійний порт\n(радіомодем 57600)"),
        (250, "UDP-сокет\n(апарат у мережі)"),
        (360, "канал відтворення\n(файл телеметрії)"),
        (462, "перекодування ArduPilot\n(з'єднання немає)"),
    ]
    for y, label in srcs:
        f.append(fitbox(56, y - 34, 288, 68, label, size=13, fill=SOFT))

    # праворуч: масиви стану
    f.append(rect(690, 70, 520, 470, fill=BAND, stroke="#c8d2dc", sw=1.2, rx=10))
    f.append(text(950, 100, "глобальні масиви розбирача", size=13, color=MUTED))

    rows = [
        (140, "m_mavlink_status[0]", "фаза автомата, прапорці версії, seq", GOOD),
        (250, "m_mavlink_status[1]", "недозібраний кадр другого потоку", GOOD),
        (360, "m_mavlink_status[2]", "стан відтворення логу", GOOD),
        (462, "m_mavlink_status[3]", "слот під м'ютексом, без з'єднання", WARM),
    ]
    for y, name, note, col in rows:
        f.append(fitbox(716, y - 34, 250, 68, name, size=13, fill=col, bold=True))
        f.append(mtext(986, y - 4, note.split("\n"), size=12, color=MUTED, anchor="start"))

    # стрілки джерело → слот
    for (y, _), (ry, _, _, _) in zip(srcs, rows):
        f.append(arrow(352, y, 700, ry))

    # підпис номерів каналів на стрілках
    for i, (y, _) in enumerate(srcs):
        f.append(text(526, y - 12, "канал %d" % i, size=12, color=NEG))

    # стеля
    f.append(fitbox(190, 580, 860, 80,
                    "MAVLINK_COMM_NUM_BUFFERS = 16 на Linux, Windows, macOS   ·   4 на решті систем\n"
                    "стільки слотів — стільки одночасних розборів; вільного слота немає — канал не відкриється",
                    size=14, fill=COLD))

    render(os.path.join(OUT, 'channel-slots.svg'), W, H, *f)


# ───────────────── 2. Порції, кадри й вердикти ─────────────────
def fig_parse_verdicts():
    W, H = 1260, 640
    f = []

    f.append(text(W / 2, 34, "Порції каналу і межі кадрів не збігаються", size=17, bold=True))

    # смуга байтів
    y0 = 80
    f.append(rect(40, y0, 1180, 62, fill=BAND, stroke="#c8d2dc", sw=1.2, rx=8))

    # порції
    chunks = [(40, 300, "порція 1: 300 Б"), (340, 240, "порція 2: 240 Б"), (580, 420, "порція 3: 420 Б"),
              (1000, 220, "порція 4: 220 Б")]
    for x, w, label in chunks:
        f.append(rect(x, y0, w, 62, fill=SOFT, stroke=NEG, sw=1.6, rx=8))
        f.append(text(x + w / 2, y0 + 38, label, size=12, color=NEG))

    # кадри під смугою
    y1 = 190
    frames = [(70, 180, "кадр A", GOOD), (270, 210, "кадр B", GOOD), (500, 150, "сміття", WARM),
              (680, 250, "кадр C", GOOD), (960, 190, "кадр D", GOOD)]
    for x, w, label, col in frames:
        f.append(rect(x, y1, w, 56, fill=col, stroke=LINE, sw=1.4, rx=8))
        f.append(text(x + w / 2, y1 + 34, label, size=13))

    f.append(text(60, y1 - 14, "кадри в потоці", size=12, color=MUTED, anchor="start"))
    f.append(text(60, y0 - 12, "те, що віддає канал", size=12, color=MUTED, anchor="start"))

    # вертикальні позначки розриву
    for x in (340, 580, 1000):
        f.append(line(x, y0 + 62, x, y1 - 4, color=NEG, sw=1.2, dash="4 4"))

    # автомат
    f.append(arrow(W / 2, 270, W / 2, 320))
    f.append(fitbox(370, 322, 520, 64, "mavlink_parse_char(канал, байт, &msg, &status)\nстан між викликами лишається у слоті каналу",
                    size=13, fill=COLD))

    # вердикти
    verdicts = [
        (60, "INCOMPLETE", "кадр ще будується —\nмайже кожен байт", BAND),
        (370, "OK", "кадр цілий,\nіде далі", GOOD),
        (680, "BAD_CRC", "пошкоджені байти\nАБО невідоме повідомлення", WARM),
        (990, "BAD_SIGNATURE", "кадр цілий,\nпідпис не той", WARM),
    ]
    for x, name, note, col in verdicts:
        f.append(fitbox(x, 460, 210, 44, name, size=14, bold=True, fill=col))
        f.append(mtext(x + 105, 534, note.split("\n"), size=12, color=MUTED))
        f.append(arrow(x + 105, 392, x + 105, 456))

    render(os.path.join(OUT, 'parse-verdicts.svg'), W, H, *f)


# ───────────────── 3. Версійний фільтр ─────────────────
def fig_version_gate():
    W, H = 1180, 720
    f = []

    f.append(text(W / 2, 34, "Що станція робить із кадром залежно від версії", size=17, bold=True))

    cx = 420

    f.append(fitbox(cx - 150, 70, 300, 50, "вердикт розбирача", size=14, bold=True, fill=COLD))
    f.append(arrow(cx, 120, cx, 168))

    f.append(fitbox(cx - 190, 170, 380, 54, "framing == MAVLINK_FRAMING_OK ?", size=14, fill=SOFT))

    # ні → геть
    f.append(arrow(cx + 190, 197, 830, 197))
    f.append(text(700, 186, "ні", size=12, color=MUTED))
    f.append(fitbox(830, 170, 300, 54, "кадр відкинуто", size=14, fill=WARM))

    f.append(arrow(cx, 224, cx, 272))
    f.append(text(cx + 22, 252, "так", size=12, color=MUTED))

    f.append(fitbox(cx - 190, 274, 380, 54, "стартовий байт: 0xFD чи 0xFE ?", size=14, fill=SOFT))

    # 0xFD ліворуч униз
    f.append(arrow(cx - 60, 328, cx - 60, 386))
    f.append(text(cx - 130, 360, "0xFD (версія 2)", size=12, color=FIELD))

    # 0xFE праворуч
    f.append(arrow(cx + 190, 301, 830, 301))
    f.append(text(690, 290, "0xFE (версія 1)", size=12, color=POS))
    f.append(fitbox(830, 274, 300, 54, "HEARTBEAT або RADIO_STATUS ?", size=13, fill=SOFT))

    # гілка v1
    f.append(arrow(980, 328, 980, 384))
    f.append(text(1006, 360, "ні", size=12, color=MUTED, anchor="start"))
    f.append(fitbox(830, 386, 300, 76, "кадр відкинуто,\nномер послідовності НЕ враховано", size=13, fill=WARM))

    f.append(arrow(830, 301, 700, 301))
    f.append(arrow(980, 462, 980, 516))
    f.append(fitbox(830, 518, 300, 76, "після 10 с без жодного кадру v2 —\nодне попередження операторові", size=13, fill=WARM))

    # гілка v2
    f.append(fitbox(cx - 210, 388, 300, 76, "лічильники втрат,\nпересилання, запис у лог", size=13, fill=GOOD))
    f.append(arrow(cx - 60, 464, cx - 60, 518))
    f.append(fitbox(cx - 210, 520, 300, 76, "emit messageReceived\n→ маршрутизація", size=13, fill=GOOD))

    # виняток v1, що доходить
    f.append(line(700, 301, 700, 620, color=FIELD, sw=1.4, dash="5 4"))
    f.append(arrow(700, 620, 420, 620))
    f.append(text(716, 616, "так: серцебиття старого апарата", size=12, color=FIELD, anchor="start"))
    f.append(fitbox(120, 596, 300, 54, "доходить до застосунку", size=13, fill=GOOD))

    render(os.path.join(OUT, 'version-gate.svg'), W, H, *f)


# ───────────────── 4. Лічильник дірок у нумерації ─────────────────
def fig_seq_loss():
    W, H = 1220, 620
    f = []

    f.append(text(W / 2, 34, "Втрати рахують із дірок у нумерації кадрів", size=17, bold=True))

    # шкала прийнятих номерів
    y = 120
    seq = [("249", True), ("250", True), ("251", True), ("252", False), ("253", False),
           ("254", True), ("255", False), ("0", False), ("1", True)]
    x = 90
    for label, got in seq:
        col = GOOD if got else WARM
        stroke = LINE if got else POS
        f.append(rect(x, y, 108, 58, fill=col, stroke=stroke, sw=1.6, rx=8))
        f.append(text(x + 54, y + 36, label, size=15, bold=True))
        x += 118

    f.append(text(70, y - 16, "номери послідовності одного відправника", size=12, color=MUTED, anchor="start"))
    f.append(text(70, y + 92, "зелене — прийнято станцією · червоне — не долетіло", size=12, color=MUTED, anchor="start"))

    # обчислення
    f.append(fitbox(80, 250, 520, 150,
                    "прийнято 254, попередній 251\n"
                    "очікуваний = 251 + 1 = 252\n"
                    "254 ≥ 252 → втрачено 254 − 252 = 2",
                    size=14, fill=COLD))

    f.append(fitbox(640, 250, 520, 150,
                    "прийнято 1, попередній 254\n"
                    "очікуваний = 254 + 1 = 255\n"
                    "1 < 255 → втрачено 1 + 256 − 255 = 2",
                    size=14, fill=COLD))

    f.append(text(340, 424, "звичайний розрив", size=13, color=MUTED))
    f.append(text(900, 424, "розрив через межу байта", size=13, color=MUTED))

    # сліпа пляма
    f.append(fitbox(80, 470, 1080, 96,
                    "СЛІПА ПЛЯМА: номер займає один байт, тож лічильник міряє різницю за модулем 256.\n"
                    "Рівно 256 загублених кадрів дадуть різницю 0, а 300 загублених виглядатимуть як 44.",
                    size=14, fill=WARM))

    render(os.path.join(OUT, 'seq-loss.svg'), W, H, *f)


# ═══════════ фігури до вставки math-loss-counting.md ═══════════

def _poly(pts, color=INK, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (px, py) for px, py in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (s, color, sw, d))


# ───────── 5. Пилка: що зараховує лічильник при розриві L ─────────
def fig_loss_sawtooth():
    W, H = 1240, 790
    f = []
    f.append(text(W / 2, 34, "Скільки втрат зараховує лічильник при розриві завдовжки L кадрів",
                  size=17, bold=True))

    X0, X1, YB, YT = 140, 1140, 540, 120
    LMAX, VMAX = 800.0, 290.0

    def sx(L):
        return X0 + (X1 - X0) * L / LMAX

    def sy(v):
        return YB - (YB - YT) * v / VMAX

    for L in (0, 128, 256, 384, 512, 640, 768):
        f.append(line(sx(L), YB, sx(L), YT, color="#dde3ea", sw=1.0))
        f.append(text(sx(L), YB + 26, str(L), size=13, color=MUTED))
    for v in (0, 64, 128, 192, 255):
        f.append(line(X0, sy(v), X1, sy(v), color="#dde3ea", sw=1.0))
        f.append(text(X0 - 14, sy(v) + 5, str(v), size=13, color=MUTED, anchor="end"))

    f.append(line(X0, YB, X1 + 18, YB, color=LINE, sw=1.6))
    f.append(line(X0, YB, X0, YT - 18, color=LINE, sw=1.6))
    f.append(text(X0 - 40, YT - 34, "зараховано втрат", size=14, bold=True, anchor="start"))
    f.append(text((X0 + X1) / 2, YB + 58, "L — скільки кадрів насправді не долетіло", size=14))

    # зуби пилки
    f.append(_poly([(sx(0), sy(0)), (sx(254), sy(254))], color=FIELD, sw=3.2))
    for base in (256, 512):
        f.append(_poly([(sx(base), sy(0)), (sx(base + 254), sy(254))], color=POS, sw=3.2))
    f.append(_poly([(sx(768), sy(0)), (sx(800), sy(32))], color=POS, sw=3.2))
    # згини
    for top in (254, 510, 766):
        f.append(_poly([(sx(top), sy(254)), (sx(top + 2), sy(0))], color=POS, sw=1.6, dash="5,4"))

    # нулі згину
    for L in (256, 512, 768):
        f.append(circle(sx(L), sy(0), 7, fill=BG, stroke=POS, sw=2.4))

    # приклад L = 300 → 44
    f.append(line(sx(300), YB, sx(300), sy(44), color=NEG, sw=1.4, dash="5,4"))
    f.append(line(X0, sy(44), sx(300), sy(44), color=NEG, sw=1.4, dash="5,4"))
    f.append(circle(sx(300), sy(44), 6, fill=NEG, stroke=NEG, sw=1.5))
    f.append(text(sx(300), YB + 46, "300", size=13, color=NEG, bold=True))
    f.append(text(X0 - 14, sy(44) + 5, "44", size=13, color=NEG, bold=True, anchor="end"))

    f.append(text(sx(120), sy(232), "точна зона", size=14, color=FIELD, bold=True, anchor="start"))

    f.append(fitbox(80, 620, 540, 130,
                    "Точно — лише поки L ≤ 254.\n"
                    "Далі показано L за модулем 256:\n"
                    "L = 300 → 44,  L = 700 → 188,\n"
                    "а L = 256, 512, 768 → рівно 0.",
                    size=15, fill=COLD))
    f.append(fitbox(660, 620, 500, 130,
                    "L = 255 має власний провал: кадр приходить\n"
                    "із номером попереднього, і код зараховує його\n"
                    "як дубль. 255 загублених кадрів не рахуються\n"
                    "взагалі — так само, як 256.",
                    size=15, fill=WARM))

    render(os.path.join(OUT, 'loss-sawtooth.svg'), W, H, *f)


# ───────── 6. Інерція накопичувального середнього ─────────
def fig_running_loss():
    W, H = 1240, 790
    f = []
    f.append(text(W / 2, 34, "Канал зіпсувався на десятій хвилині: що показує індикатор",
                  size=17, bold=True))

    X0, X1, YB, YT = 150, 1150, 520, 110
    TMAX, VMAX = 2400.0, 55.0

    def sx(t):
        return X0 + (X1 - X0) * t / TMAX

    def sy(v):
        return YB - (YB - YT) * v / VMAX

    for t, lab in ((0, "0"), (600, "10 хв"), (1200, "20 хв"), (1800, "30 хв"), (2400, "40 хв")):
        f.append(line(sx(t), YB, sx(t), YT, color="#dde3ea", sw=1.0))
        f.append(text(sx(t), YB + 26, lab, size=13, color=MUTED))
    for v in (0, 10, 20, 30, 40, 50):
        f.append(line(X0, sy(v), X1, sy(v), color="#dde3ea", sw=1.0))
        f.append(text(X0 - 14, sy(v) + 5, "%d %%" % v, size=13, color=MUTED, anchor="end"))

    f.append(line(X0, YB, X1 + 18, YB, color=LINE, sw=1.6))
    f.append(line(X0, YB, X0, YT - 18, color=LINE, sw=1.6))
    f.append(text((X0 + X1) / 2, YB + 58, "час від під'єднання", size=14))

    # справжні втрати
    f.append(_poly([(sx(0), sy(0)), (sx(600), sy(0))], color=POS, sw=2.6, dash="8,5"))
    f.append(_poly([(sx(600), sy(0)), (sx(600), sy(50))], color=POS, sw=2.6, dash="8,5"))
    f.append(_poly([(sx(600), sy(50)), (sx(2400), sy(50))], color=POS, sw=2.6, dash="8,5"))
    f.append(text(sx(1000), sy(50) - 16, "справжні втрати — 50 %", size=15, color=POS,
                  bold=True, anchor="start"))

    # показник
    pts = [(sx(0), sy(0)), (sx(600), sy(0))]
    t = 600.0
    while t <= 2400.0:
        pts.append((sx(t), sy(50.0 * (t - 600.0) / t)))
        t += 10.0
    f.append(_poly(pts, color=NEG, sw=3.0))
    f.append(text(sx(1750), sy(28), "показник на екрані", size=15, color=NEG,
                  bold=True, anchor="start"))

    for t in (610.0, 660.0, 900.0, 1200.0, 2400.0):
        f.append(circle(sx(t), sy(50.0 * (t - 600.0) / t), 6, fill=NEG, stroke=NEG, sw=1.5))

    f.append(fitbox(90, 600, 1060, 92,
                    "Через 10 с після поломки на екрані 0.8 %, через хвилину — 4.5 %, через п'ять — 16.7 %.\n"
                    "Половини справжніх втрат показник досягає рівно тоді, коли поганий відтинок став\n"
                    "таким же довгим, як добрий перед ним, — тут через десять хвилин, на позначці 25 %.",
                    size=15, fill=COLD))
    f.append(fitbox(90, 706, 1060, 64,
                    "Крива не залежить від частоти телеметрії: чисельник і знаменник ростуть однаково.\n"
                    "Важить лише те, яку частку всього з'єднання канал був поганий.",
                    size=15, fill=GOOD))

    render(os.path.join(OUT, 'running-loss.svg'), W, H, *f)


# ───────── 7. Період оновлення проти якости каналу ─────────
def fig_update_period():
    W, H = 1240, 740
    f = []
    f.append(text(W / 2, 34, "Як часто оновлюється число: кожне 31-ше ПРИЙНЯТЕ повідомлення",
                  size=17, bold=True))
    f.append(text(W / 2, 62, "T = 31 / (r · (1 − ℓ)),   r = 50 надісланих повідомлень за секунду",
                  size=15, color=MUTED))

    X0, X1, YB, YT = 170, 1050, 520, 130
    VMAX = 20.0

    def sx(l):
        return X0 + (X1 - X0) * l

    def sy(v):
        return YB - (YB - YT) * v / VMAX

    # рамка довідкової таблиці нижче — сітку ведемо ПОВЗ неї (розрив), а не крізь напис
    BX0, BY0, BX1, BY1 = 215, 155, 615, 355

    def vline_gap(x, y1, y2):
        ytop, ybot = min(y1, y2), max(y1, y2)
        if BX0 < x < BX1 and ytop < BY1 and ybot > BY0:
            f.append(line(x, ytop, x, BY0, color="#dde3ea", sw=1.0))
            f.append(line(x, BY1, x, ybot, color="#dde3ea", sw=1.0))
        else:
            f.append(line(x, y1, x, y2, color="#dde3ea", sw=1.0))

    def hline_gap(y, x1, x2):
        xleft, xright = min(x1, x2), max(x1, x2)
        if BY0 < y < BY1 and xleft < BX1 and xright > BX0:
            f.append(line(xleft, y, BX0, y, color="#dde3ea", sw=1.0))
            f.append(line(BX1, y, xright, y, color="#dde3ea", sw=1.0))
        else:
            f.append(line(x1, y, x2, y, color="#dde3ea", sw=1.0))

    for l, lab in ((0, "0"), (0.2, "20 %"), (0.4, "40 %"), (0.6, "60 %"), (0.8, "80 %"), (1.0, "100 %")):
        vline_gap(sx(l), YB, YT)
        f.append(text(sx(l), YB + 26, lab, size=13, color=MUTED))
    for v in (0, 5, 10, 15, 20):
        hline_gap(sy(v), X0, X1)
        f.append(text(X0 - 14, sy(v) + 5, "%d с" % v, size=13, color=MUTED, anchor="end"))

    f.append(line(X0, YB, X1 + 18, YB, color=LINE, sw=1.6))
    f.append(line(X0, YB, X0, YT - 18, color=LINE, sw=1.6))
    f.append(text(X0 - 46, YT - 36, "період оновлення", size=14, bold=True, anchor="start"))
    f.append(text((X0 + X1) / 2, YB + 58, "ℓ — справжня частка втрачених кадрів", size=14))

    pts = []
    l = 0.0
    while l <= 0.969:
        pts.append((sx(l), sy(0.62 / (1.0 - l))))
        l += 0.005
    f.append(_poly(pts, color=NEG, sw=3.0))

    f.append(line(sx(1.0), YB, sx(1.0), YT - 10, color=POS, sw=2.0, dash="7,5"))
    f.append(text(sx(1.0), YT - 22, "ℓ = 1", size=14, color=POS, bold=True))
    f.append(mtext(1145, 300, ["повна тиша:", "нових значень", "немає взагалі"],
                   size=13, color=POS))

    for l in (0.0, 0.5, 0.8, 0.9, 0.95):
        f.append(circle(sx(l), sy(0.62 / (1.0 - l)), 6, fill=NEG, stroke=NEG, sw=1.5))

    f.append(fitbox(215, 155, 400, 200,
                    "ℓ = 0      →  0.62 с\n"
                    "ℓ = 0.5   →  1.24 с\n"
                    "ℓ = 0.8   →  3.10 с\n"
                    "ℓ = 0.9   →  6.20 с\n"
                    "ℓ = 0.95 →  12.4 с",
                    size=17, fill=COLD))

    f.append(fitbox(90, 606, 1060, 100,
                    "Період оновлення обернено пропорційний частці кадрів, що доходять: що гірший канал,\n"
                    "то рідше змінюється число на екрані. При повній тиші сигнал не виходить ніколи —\n"
                    "і замість «100 % втрат» оператор бачить останнє пораховане значення.",
                    size=15, fill=WARM))

    render(os.path.join(OUT, 'update-period.svg'), W, H, *f)


# ───────── 8. Дві обгортки над одним автоматом (вставка proj-parse-channel) ─────────
def fig_proj_verdict_gate():
    W, H = 1260, 720
    f = []

    f.append(text(W / 2, 36, "Один автомат — дві обгортки з різною поведінкою",
                  size=18, bold=True))

    # ── верхній ряд: байт → автомат → чотири вердикти ──
    f.append(fitbox(40, 76, 210, 92, "черговий байт\nіз порції", size=15, fill=SOFT))

    f.append(fitbox(300, 68, 330, 108,
                    "mavlink_frame_char_buffer()\nавтомат + слот стану каналу",
                    size=15, fill=BAND, bold=True))
    f.append(arrow(256, 122, 294, 122))

    verdicts = [
        (76,  "0  INCOMPLETE", "кадр ще не добудовано", COLD),
        (152, "1  OK", "цілий кадр, забирай", GOOD),
        (228, "2  BAD_CRC", "сума не зійшлася або чужий msgid", WARM),
        (304, "3  BAD_SIGNATURE", "сума ціла, підпис ні", WARM),
    ]
    for y, name, note, col in verdicts:
        f.append(fitbox(700, y, 250, 60, name, size=15, fill=col, bold=True))
        f.append(mtext(966, y + 34, [note], size=13, color=MUTED, anchor="start"))
    f.append(arrow(636, 122, 694, 106))
    f.append(arrow(636, 122, 694, 182))
    f.append(arrow(636, 122, 694, 258))
    f.append(arrow(636, 122, 694, 334))

    f.append(line(40, 400, W - 40, 400, color="#c8d2dc", sw=1.2, dash="6 5"))

    # ── нижній ряд: дві публічні обгортки ──
    f.append(rect(40, 424, 570, 258, fill=BAND, stroke="#c8d2dc", sw=1.2, rx=10))
    f.append(text(325, 456, "mavlink_frame_char(chan, …)", size=16, bold=True))
    f.append(fitbox(66, 476, 518, 66,
                    "віддає вердикт як є: 0, 1, 2, 3", size=15, fill=GOOD))
    f.append(fitbox(66, 556, 518, 108,
                    "усі чотири лічильники можливі,\n"
                    "але ресинхронізацію після битого кадру\n"
                    "робиш ти сам",
                    size=15, fill=SOFT))

    f.append(rect(650, 424, 570, 258, fill=BAND, stroke="#c8d2dc", sw=1.2, rx=10))
    f.append(text(935, 456, "mavlink_parse_char(chan, …)", size=16, bold=True))
    f.append(fitbox(676, 476, 518, 66,
                    "2 і 3 перетворює на 0, віддає лише 0 і 1", size=15, fill=WARM))
    f.append(fitbox(676, 556, 518, 108,
                    "ресинк робить сам — але тільки на 0xFD\n"
                    "і не чіпає ні magic, ні прапорця версії;\n"
                    "лічильник поганих сум лишиться порожнім",
                    size=15, fill=SOFT))

    render(os.path.join(OUT, 'proj-verdict-gate.svg'), W, H, *f)


fig_channel_slots()
fig_parse_verdicts()
fig_version_gate()
fig_seq_loss()
fig_loss_sawtooth()
fig_running_loss()
fig_update_period()
fig_proj_verdict_gate()
print("ok")
