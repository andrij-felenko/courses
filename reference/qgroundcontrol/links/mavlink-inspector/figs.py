# -*- coding: utf-8 -*-
"""Фігури до теми «Інспектор MAVLink: перегляд сирого трафіку» довідника QGroundControl."""
import sys, os, math
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
GREY = "#c8d2dc"


def _poly(pts, color=INK, sw=2.2, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (px, py) for px, py in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (s, color, sw, d))


# ───────────────── 1. Точка врізання ─────────────────
def fig_tap_point():
    W, H = 1300, 850
    f = []
    f.append(text(W / 2, 36, "Дві гілки ростуть з однієї точки", size=18, bold=True))

    # верх: канал і розбирач
    f.append(fitbox(430, 66, 440, 58, "канал: серійний, UDP, файл логу", size=15, fill=SOFT))
    f.append(arrow(650, 124, 650, 158))
    f.append(fitbox(430, 160, 440, 58, "розбирач MAVLink", size=15, fill=SOFT, bold=True))

    # відкинуте
    f.append(arrow(874, 189, 934, 189))
    f.append(fitbox(936, 148, 340, 82,
                    "погана сума, невідомий номер,\nстара версія протоколу —\nдалі не йде взагалі",
                    size=13, fill=WARM))

    f.append(arrow(650, 220, 650, 252))
    f.append(fitbox(400, 254, 500, 58, "emit messageReceived(link, message)",
                    size=15, fill=COLD, bold=True))

    # розгалуження
    f.append(arrow(560, 312, 350, 366))
    f.append(arrow(740, 312, 950, 366))

    left = [
        (368, "маршрутизація за sysid і compid"),
        (452, "Vehicle — об'єкт апарата"),
        (536, "група фактів"),
        (620, "віджет на екрані"),
    ]
    for y, label in left:
        f.append(fitbox(120, y, 460, 58, label, size=14, fill=BAND))
    for y, _ in left[:-1]:
        f.append(arrow(350, y + 58, 350, y + 82))

    right = [
        (368, "інспектор"),
        (452, "система за sysid"),
        (536, "рядок за трійкою ключа"),
        (620, "поля з опису повідомлення"),
    ]
    for y, label in right:
        f.append(fitbox(720, y, 460, 58, label, size=14, fill=GOOD))
    for y, _ in right[:-1]:
        f.append(arrow(950, y + 58, 950, y + 82))

    # підсумки
    f.append(fitbox(120, 706, 460, 108,
                    "ЧОТИРИ ланки тлумачення.\nПорожньо на екрані — зламатися\nмогла будь-яка з них.",
                    size=14, fill=BAND))
    f.append(fitbox(720, 706, 460, 108,
                    "ЖОДНОГО тлумачення.\nЩо є в списку — те станція\nсправді прийняла й розібрала.",
                    size=14, fill=GOOD))

    render(os.path.join(OUT, 'tap-point.svg'), W, H, *f)


# ───────────────── 2. Ключ рядка ─────────────────
def fig_message_identity():
    W, H = 1320, 700
    f = []
    f.append(text(W / 2, 36, "Однаковий номер повідомлення — різні рядки списку",
                  size=18, bold=True))

    f.append(text(340, 90, "прийняті кадри", size=14, color=MUTED))
    f.append(text(1000, 90, "рядки списку інспектора", size=14, color=MUTED))

    rows = [
        ("msgid 147 · comp 1 · id = 0", "BATTERY_STATUS [0] · comp 1", GOOD),
        ("msgid 147 · comp 1 · id = 1", "BATTERY_STATUS [1] · comp 1", GOOD),
        ("msgid 147 · comp 154 · id = 0", "BATTERY_STATUS [0] · comp 154", GOOD),
        ("msgid 251 · comp 1 · name = thr", "NAMED_VALUE_FLOAT [thr]", COLD),
        ("msgid 251 · comp 1 · name = rpm", "NAMED_VALUE_FLOAT [rpm]", COLD),
    ]
    y = 116
    for src, dst, col in rows:
        f.append(fitbox(80, y, 520, 60, src, size=14, fill=SOFT))
        f.append(arrow(608, y + 30, 728, y + 30))
        f.append(fitbox(736, y, 500, 60, dst, size=14, fill=col, bold=True))
        y += 84

    f.append(fitbox(80, 552, 1156, 60,
                    "ключ рядка = (номер повідомлення, компонент, значення розрізняльного поля)",
                    size=16, fill=COLD, bold=True))
    f.append(fitbox(80, 624, 1156, 56,
                    "третю частину ключа беруть із поля, яке в XML-описі помічене атрибутом instance=\"true\"",
                    size=14, fill=BAND))

    render(os.path.join(OUT, 'message-identity.svg'), W, H, *f)


# ───────────────── 3. Дешевий і дорогий шлях кадру ─────────────────
def fig_decode_gate():
    W, H = 1300, 760
    f = []
    f.append(text(W / 2, 36, "Що застосунок робить із кожним прийнятим кадром",
                  size=18, bold=True))

    cx = 400
    f.append(fitbox(cx - 240, 70, 480, 58, "кадр із сигналу messageReceived", size=15, fill=COLD))
    f.append(arrow(cx, 128, cx, 160))

    f.append(fitbox(cx - 240, 162, 480, 58, "знайти рядок за трійкою ключа", size=15, fill=SOFT))
    f.append(arrow(cx, 220, cx, 252))

    f.append(fitbox(cx - 240, 254, 480, 76,
                    "лічильник + 1\nзберегти копію кадру", size=15, fill=GOOD, bold=True))
    f.append(arrow(cx, 330, cx, 362))

    f.append(fitbox(cx - 240, 364, 480, 76,
                    "рядок розгорнутий\nабо поле винесене на графік?", size=15, fill=SOFT))

    # ні → праворуч
    f.append(arrow(cx + 240, 402, cx + 400, 402))
    f.append(text(cx + 320, 390, "ні", size=13, color=MUTED))
    f.append(fitbox(cx + 408, 372, 380, 60, "усе, кадр відпрацьовано", size=14, fill=BAND))

    f.append(arrow(cx, 440, cx, 476))
    f.append(text(cx + 26, 466, "так", size=13, color=MUTED))

    f.append(fitbox(cx - 240, 478, 480, 96,
                    "розкласти поля:\nmemcpy → рядок → сигнал інтерфейсу",
                    size=15, fill=WARM, bold=True))
    f.append(arrow(cx, 574, cx, 606))
    f.append(fitbox(cx - 240, 608, 480, 76,
                    "поле на графіку — ще й у відро\nмінімуму й максимуму", size=15, fill=WARM))

    # арифметика праворуч
    f.append(rect(880, 470, 380, 244, fill=BAND, stroke=GREY, sw=1.2, rx=10))
    f.append(text(1070, 502, "40 повідомлень, 200 кадрів/с,", size=14, color=MUTED))
    f.append(text(1070, 524, "12 полів у середньому", size=14, color=MUTED))
    f.append(fitbox(908, 542, 324, 70,
                    "розкладати все:\n200 × 12 = 2400 за секунду", size=14, fill=WARM))
    f.append(fitbox(908, 624, 324, 70,
                    "лише вибране (10 Гц):\n10 × 12 = 120 за секунду", size=14, fill=GOOD))

    render(os.path.join(OUT, 'decode-gate.svg'), W, H, *f)


# ───────────────── 4. Відра з парою мінімум-максимум ─────────────────
def fig_chart_buckets():
    W, H = 1320, 790
    f = []
    f.append(text(W / 2, 36, "Проріджування у відра зберігає сплеск, який гине при кроковому",
                  size=18, bold=True))

    X0, X1, YB, YT = 130, 1180, 470, 110
    N = 300
    VMAX = 100.0

    def val(i):
        if i == 181:
            return 95.0
        return 42.0 + 9.0 * math.sin(i / 17.0) + 3.5 * math.sin(i / 3.7 + 1.0)

    def sx(i):
        return X0 + (X1 - X0) * i / float(N - 1)

    def sy(v):
        return YB - (YB - YT) * v / VMAX

    # сітка й осі
    for v in (0, 20, 40, 60, 80):
        f.append(line(X0, sy(v), X1, sy(v), color="#dde3ea", sw=1.0))
        f.append(text(X0 - 16, sy(v) + 5, str(v), size=13, color=MUTED, anchor="end"))
    f.append(line(X0, YB, X1 + 18, YB, color=LINE, sw=1.6))
    f.append(line(X0, YB, X0, YT - 14, color=LINE, sw=1.6))
    f.append(text((X0 + X1) / 2, YB + 60, "час — 15 відер по ширині поля", size=15))

    # межі відер
    B = 15
    per = N // B
    for b in range(1, B):
        x = sx(b * per)
        f.append(line(x, YB, x, YT, color="#e8edf2", sw=1.0))

    # сирий сигнал
    f.append(_poly([(sx(i), sy(val(i))) for i in range(N)], color=MUTED, sw=1.2))

    # пари мінімум-максимум по відрах
    for b in range(B):
        vs = [val(i) for i in range(b * per, (b + 1) * per)]
        xm = sx(b * per + per / 2.0)
        f.append(line(xm, sy(min(vs)), xm, sy(max(vs)), color=FIELD, sw=5.0))

    # крокове проріджування
    naive = [(sx(i), sy(val(i))) for i in range(0, N, per)]
    f.append(_poly(naive, color=POS, sw=2.2, dash="8,5"))
    for px, py in naive:
        f.append(circle(px, py, 4.5, fill=POS, stroke=POS, sw=1.2))

    # позначка сплеску
    f.append(text(sx(181), sy(95) - 16, "одиничний сплеск", size=14, color=INK, bold=True))

    # легенда під полем
    f.append(fitbox(130, 530, 330, 62, "сірим — усі відліки", size=14, fill=SOFT))
    f.append(fitbox(490, 530, 330, 62, "зеленим — пара на відро", size=14, fill=GOOD))
    f.append(fitbox(850, 530, 330, 62, "червоним — кожен 20-й", size=14, fill=WARM))

    f.append(fitbox(130, 616, 1050, 70,
                    "Пара «найменше — найбільше» лишає від відра вертикальний штрих: сплеск, що трапився\n"
                    "будь-де всередині відра, доживає до екрана на повну висоту.",
                    size=15, fill=GOOD))
    f.append(fitbox(130, 700, 1050, 70,
                    "Кроковий вибір «кожен N-й» дає таку саму кількість точок, але сплеск між кроками\n"
                    "просто не потрапляє у вибірку — і графік стає гладким та брехливим.",
                    size=15, fill=WARM))

    render(os.path.join(OUT, 'chart-buckets.svg'), W, H, *f)


# ───────────────── 5. Дерево об'єктів інтерфейсу ─────────────────
def fig_object_tree():
    W, H = 1400, 820
    f = []
    f.append(text(W / 2, 38, "Дерево об'єктів інспектора: хто кого тримає і що сповіщає про зміну",
                  size=18, bold=True))

    LX, LW = 80, 540          # ліва колонка — самі об'єкти
    RX, RW = 690, 630         # права колонка — сигнали цього рівня
    LCX = LX + LW / 2

    rows = [
        (86,
         "MAVLinkInspectorController\nзареєстрований як тип QML — створюється з QML",
         COLD, True,
         "systemsChanged — з'явився або зник апарат\n"
         "activeSystemChanged — інший активний апарат\n"
         "timeScalesChanged, rangeListChanged — не спрацьовують ніколи"),
        (232,
         "QGCMAVLinkSystem — апарат за sysid\nтипом QML НЕ зареєстрований",
         SOFT, False,
         "compIDsChanged — побачено новий компонент\n"
         "selectedChanged — вибрано інший рядок списку"),
        (378,
         "QGCMAVLinkMessage — рядок списку\nтипом QML НЕ зареєстрований",
         SOFT, False,
         "countChanged — прийшов кадр (на КОЖЕН кадр)\n"
         "actualRateHzChanged — раз на секунду\n"
         "targetRateHzChanged, selectedChanged, fieldSelectedChanged"),
        (524,
         "QGCMAVLinkMessageField — поле\nтипом QML НЕ зареєстрований",
         SOFT, False,
         "valueChanged — рядок значення став іншим\n"
         "seriesChanged — поле стало кривою або перестало нею бути\n"
         "selectableChanged — поле визнано невибірним"),
    ]

    for y, label, fill, bold, sigs in rows:
        f.append(fitbox(LX, y, LW, 84, label, size=16, fill=fill, bold=bold))
        f.append(fitbox(RX, y, RW, 84, sigs, size=13, fill=BAND))

    # стрілки вниз із підписом властивості, що веде на рівень нижче
    steps = [
        (170, 232, "systems : QmlObjectListModel   (CONSTANT)"),
        (316, 378, "messages : QmlObjectListModel   (CONSTANT)"),
        (462, 524, "fields : QmlObjectListModel   (CONSTANT)"),
    ]
    for y0, y1, label in steps:
        f.append(arrow(LCX, y0, LCX, y1))
        f.append(text(LCX + 18, (y0 + y1) / 2 + 5, label, size=13, color=MUTED, anchor="start"))

    # окремий контролер графіка
    f.append(fitbox(RX, 640, RW, 96,
                    "MAVLinkChartController — другий тип QML\n"
                    "chartFields тримає ТІ САМІ об'єкти полів\n"
                    "chartFieldsChanged, rangeX*/rangeY*Changed, plotPixelWidthChanged",
                    size=13, fill=COLD))
    f.append(arrow(LX + LW, 566, RX + RW / 2, 640, color=MUTED))

    f.append(fitbox(LX, 640, LW, 96,
                    "Створити з QML можна лише два контролери.\n"
                    "Систему, рядок і поле беруть уже готовими —\n"
                    "через властивості й get(i) моделі.",
                    size=14, fill=GOOD))

    render(os.path.join(OUT, 'object-tree.svg'), W, H, *f)


# ───────────────── 6. Ваги рекуренти ─────────────────
def fig_rate_weights():
    W, H = 1240, 700
    A, B = 0.8, 0.2
    f = []
    f.append(text(W / 2, 36, "Скільки тактів насправді пам'ятає показник частоти",
                  size=18, bold=True))

    # ── ліва панель: ваги 0.8·0.2^k
    f.append(text(350, 78, "рекурента 0.2·попереднє + 0.8·нове", size=15, bold=True))
    base = 470
    top_h = 340.0
    scale = top_h / A
    xs = [140, 224, 308, 392, 476, 560]
    f.append(line(100, base, 614, base, color=INK, sw=2))
    names = ["n", "n−1", "n−2", "n−3", "n−4", "n−5"]
    for k, cx in enumerate(xs):
        w = A * (B ** k)
        h = max(3.0, w * scale)
        f.append(rect(cx - 25, base - h, 50, h, fill=COLD, stroke=NEG, sw=1.6, rx=3))
        f.append(text(cx, base + 26, names[k], size=14))
        f.append(text(cx, base + 52, "%.3f" % w, size=13, color=MUTED))
    # дужка над двома першими
    f.append(line(115, 104, 249, 104, color=POS, sw=2.4))
    f.append(line(115, 104, 115, 118, color=POS, sw=2.4))
    f.append(line(249, 104, 249, 118, color=POS, sw=2.4))
    f.append(text(182, 94, "0.96 усієї ваги", size=14, color=POS, bold=True))

    # ── права панель: рівне середнє за 3 такти
    f.append(text(900, 78, "для порівняння: рівне середнє за 3 такти", size=15, bold=True))
    xs2 = [790, 900, 1010]
    for k, cx in enumerate(xs2):
        h = (1.0 / 3.0) * scale
        f.append(rect(cx - 30, base - h, 60, h, fill=GOOD, stroke=FIELD, sw=1.6, rx=3))
        f.append(text(cx, base + 26, names[k], size=14))
        f.append(text(cx, base + 52, "0.333", size=13, color=MUTED))
    f.append(line(720, base, 1150, base, color=INK, sw=2))

    f.append(fitbox(90, 566, 520, 104,
                    "Вага падає в п'ять разів за такт. Третій такт назад важить 0.032 —\n"
                    "стовпчик уже не видно. Ефективна кількість відліків\n"
                    "(1 − 0.2²) / 0.8² = 1.5.",
                    size=15, fill=COLD))
    f.append(fitbox(660, 566, 490, 104,
                    "Три рівні ваги — це справді вікно на три такти.\n"
                    "Рекурента коштує один множник і одне число пам'яті,\n"
                    "але й пам'ятає вона в двічі менше.",
                    size=15, fill=GOOD))

    render(os.path.join(OUT, 'rate-weights.svg'), W, H, *f)


# ───────────────── 7. Перехідна характеристика ─────────────────
def fig_rate_step():
    W, H = 1240, 640
    A, B = 0.8, 0.2
    f = []
    f.append(text(W / 2, 36, "Наростання і спад: похибка ділиться на п'ять щотакту",
                  size=18, bold=True))

    X0, X1 = 150, 1150
    Y0, Y1 = 480, 110          # Y0 — нуль, Y1 — 11 Гц
    TN = 12
    def sx(t): return X0 + t * (X1 - X0) / (TN + 0.6)
    def sy(v): return Y0 - v * (Y0 - Y1) / 11.0

    # осі
    f.append(line(X0, Y0, X1, Y0, color=INK, sw=2))
    f.append(line(X0, Y0, X0, Y1, color=INK, sw=2))
    for v in (0, 5, 10):
        f.append(line(X0 - 7, sy(v), X0, sy(v), color=INK, sw=1.6))
        f.append(text(X0 - 16, sy(v) + 5, str(v), size=13, anchor="end", color=MUTED))
    f.append(text(X0 - 16, sy(11) - 6, "Гц", size=13, anchor="end", color=MUTED))

    # істинний потік: 10 Гц з такту 1 по такт 6
    true_pts = [(sx(0), sy(0)), (sx(0.5), sy(0)), (sx(0.5), sy(10)),
                (sx(6.5), sy(10)), (sx(6.5), sy(0)), (sx(TN + 0.4), sy(0))]
    f.append(_poly(true_pts, color=MUTED, sw=2.0, dash="9,6"))
    f.append(text(sx(5.0), sy(10) - 24, "істинний потік 10 Гц", size=14, color=MUTED))

    # показник
    r = 0.0
    pts, vals = [], []
    for n in range(1, TN + 1):
        c = 10 if 1 <= n <= 6 else 0
        r = B * r + A * c
        vals.append(r)
        pts.append((sx(n), sy(r)))
        f.append(line(sx(n), Y0, sx(n), Y0 + 7, color=INK, sw=1.4))
        f.append(text(sx(n), Y0 + 26, str(n), size=13, color=MUTED))
    f.append(_poly(pts, color=NEG, sw=2.6))
    for px, py in pts:
        f.append(circle(px, py, 5.0, fill=NEG, stroke=NEG, sw=1.2))

    # підписи значень — тільки там, де вони читаються
    f.append(text(sx(1) + 6, sy(vals[0]) + 26, "8.0", size=13, color=NEG, anchor="start"))
    f.append(text(sx(2) + 4, sy(vals[1]) + 26, "9.6", size=13, color=NEG, anchor="start"))
    f.append(text(sx(3) + 4, sy(vals[2]) + 30, "9.92", size=13, color=NEG, anchor="start"))
    f.append(text(sx(7) + 10, sy(vals[6]) + 4, "2.0", size=13, color=NEG, anchor="start"))
    f.append(text(sx(8) + 10, sy(vals[7]) - 8, "0.40", size=13, color=NEG, anchor="start"))
    f.append(text(sx(9) + 10, sy(vals[8]) - 26, "0.08", size=13, color=NEG, anchor="start"))

    f.append(text(sx(TN) + 34, Y0 + 26, "такт", size=13, color=MUTED, anchor="start"))

    f.append(fitbox(150, 520, 490, 96,
                    "Три такти — і показник за 0.08 Гц від істини.\n"
                    "Кожен наступний такт ріже залишок похибки вп'ятеро:\n"
                    "10 · 0.2ⁿ.",
                    size=15, fill=COLD))
    f.append(fitbox(680, 520, 470, 96,
                    "Спад — та сама геометрія, дзеркально.\n"
                    "Чотири такти мовчання — і на екрані 0.0:\n"
                    "тому зниклий рядок видно за кілька секунд.",
                    size=15, fill=WARM))

    render(os.path.join(OUT, 'rate-step.svg'), W, H, *f)


# ───────────────── 8. Пилка на повільному повідомленні ─────────────────
def fig_rate_sawtooth():
    W, H = 1240, 660
    A, B = 0.8, 0.2
    P = 5
    f = []
    f.append(text(W / 2, 36, "Повільне повідомлення: середнє правильне, показник — ніколи",
                  size=18, bold=True))

    X0, X1 = 150, 1140
    Y0, Y1 = 452, 120
    TN = 20
    def sx(t): return X0 + t * (X1 - X0) / (TN + 0.6)
    def sy(v): return Y0 - v * (Y0 - Y1) / 0.9

    f.append(line(X0, Y0, X1, Y0, color=INK, sw=2))
    f.append(line(X0, Y0, X0, Y1, color=INK, sw=2))
    for v in (0.0, 0.2, 0.4, 0.6, 0.8):
        f.append(line(X0 - 7, sy(v), X0, sy(v), color=INK, sw=1.6))
        f.append(text(X0 - 16, sy(v) + 5, "%.1f" % v, size=13, anchor="end", color=MUTED))
    f.append(text(X0 - 16, sy(0.88) - 4, "Гц", size=13, anchor="end", color=MUTED))

    # істинна частота = середнє показника = 0.2
    f.append(line(X0, sy(0.2), X1, sy(0.2), color=FIELD, sw=2.2, dash="9,6"))
    f.append(text(X1 - 8, sy(0.2) - 12, "істина 0.2 Гц = середнє показника",
                  size=14, color=FIELD, anchor="end", bold=True))

    r = 0.0
    pts = []
    for n in range(1, TN + 1):
        c = 1 if n % P == 0 else 0
        r = B * r + A * c
        pts.append((sx(n), sy(r)))
    f.append(_poly(pts, color=NEG, sw=2.6))
    for px, py in pts:
        f.append(circle(px, py, 4.2, fill=NEG, stroke=NEG, sw=1.1))

    # позначки приходу кадрів під віссю
    for n in range(P, TN + 1, P):
        f.append(line(sx(n), Y0 + 6, sx(n), Y0 + 26, color=POS, sw=2.6))
    f.append(text(sx(P), Y0 + 46, "кадр", size=13, color=POS))
    f.append(text(sx(TN), Y0 + 46, "кадр", size=13, color=POS))

    f.append(text(sx(5), sy(0.8) - 16, "0.80", size=14, color=NEG, bold=True))
    f.append(text(sx(6) + 12, sy(0.16) - 10, "0.16", size=13, color=NEG, anchor="start"))
    f.append(text(sx(8) + 8, sy(0.02) - 12, "0.01 · · · 0.00", size=13, color=NEG, anchor="start"))

    f.append(fitbox(150, 500, 480, 130,
                    "Пік дорівнює 0.8 незалежно від справжньої частоти:\n"
                    "один кадр у порожньому такті дає 0.8·1. Так само\n"
                    "стрибне і рядок, що приходить раз на хвилину.\n"
                    "Різницю несе лише те, ЯК ЧАСТО спалахує пік.",
                    size=15, fill=WARM))
    f.append(fitbox(670, 500, 470, 130,
                    "Середнє за цикл — рівно 0.2 Гц, зміщення нульове.\n"
                    "Але око бачить не середнє, а одне число: три такти\n"
                    "з п'яти на екрані стоїть 0.0.",
                    size=15, fill=COLD))

    render(os.path.join(OUT, 'rate-sawtooth.svg'), W, H, *f)


# ───────── Проєкт: як поле дістають із навантаження ─────────
def fig_proj_payload_layout():
    W, H = 1340, 720
    f = []
    f.append(text(W / 2, 34, "Поле дістають із навантаження за зсувом, який дав опис",
                  size=18, bold=True))

    # ── масив розгортається в елементи ───────────────────────────────
    f.append(text(W / 2, 76,
                  "voltages — uint16_t[10] за зсувом 10: одне поле опису стає десятьма полями списку",
                  size=15, color=MUTED))

    cells = [("voltages[0]", "зсув 10", COLD), ("voltages[1]", "зсув 12", COLD),
             ("voltages[2]", "зсув 14", COLD), ("voltages[3]", "зсув 16", COLD),
             ("…", "", SOFT), ("voltages[9]", "зсув 28", COLD)]
    cw, gap = 150, 14
    x0 = (W - (len(cells) * cw + (len(cells) - 1) * gap)) / 2
    for i, (a, b, col) in enumerate(cells):
        label = a if not b else a + "\n" + b
        f.append(fitbox(x0 + i * (cw + gap), 100, cw, 64, label, size=14, fill=col))

    f.append(fitbox(x0, 186, len(cells) * cw + (len(cells) - 1) * gap, 54,
                    "зсув елемента = зсув масиву + номер елемента × розмір типу",
                    size=15, fill=GOOD, bold=True))

    # ── розширення й вирівнювання ────────────────────────────────────
    f.append(text(W / 2, 282,
                  "BATTERY_STATUS, байти 40–53: розширені поля дописано в кінець без пересортування",
                  size=15, color=MUTED))

    bw, bgap = 76, 5
    pitch = bw + bgap
    n = 14
    bx0 = (W - (n * bw + (n - 1) * bgap)) / 2

    def bx(byte):
        return bx0 + (byte - 40) * pitch

    def bcx(byte):
        return bx(byte) + bw / 2

    for byte, label in ((40, "charge_state · uint8"), (49, "mode · uint8")):
        body, bwd, bht = textbox(bcx(byte), 330, label, size=13, fill=BAND)
        f.append(body)
        f.append(line(bcx(byte), 330 + bht / 2, bcx(byte), 368, color=GREY, sw=1.4))

    for byte in range(40, 54):
        if 41 <= byte <= 48:
            col = COLD
        elif 50 <= byte <= 53:
            col = WARM
        else:
            col = SOFT
        f.append(fitbox(bx(byte), 368, bw, 58, str(byte), size=15, fill=col))

    f.append(fitbox(bx(41), 442, 8 * pitch - bgap, 54,
                    "voltages_ext — uint16_t[4], зсув 41", size=15, fill=COLD, bold=True))
    f.append(fitbox(bx(50), 442, 4 * pitch - bgap, 54,
                    "fault_bitmask — uint32_t, зсув 50", size=15, fill=WARM, bold=True))

    f.append(fitbox(bx(40), 516, n * pitch - bgap, 78,
                    "Початок навантаження кратний восьми, але 41 не ділиться на два, а 50 — на чотири.\n"
                    "Жоден із цих двох зсувів не вирівняний під свій тип.",
                    size=15, fill=BAND))
    f.append(fitbox(bx(40), 614, n * pitch - bgap, 78,
                    "Тому єдиний правильний доступ — memcpy у локальну змінну потрібного типу:\n"
                    "він не вимагає вирівнювання й не порушує правил псевдонімів.",
                    size=15, fill=GOOD, bold=True))

    render(os.path.join(OUT, 'proj-payload-layout.svg'), W, H, *f)


# ───────── Проєкт: втрата чи подвоєння — за номером послідовности ─────────
def fig_proj_seq_doubling():
    W, H = 1300, 600
    f = []
    f.append(text(W / 2, 34, "Один лічильник послідовности розрізняє втрату й подвоєння",
                  size=18, bold=True))
    f.append(text(W / 2, 74, "номери послідовности, як вони прийшли", size=14, color=MUTED))

    LX, LW = 56, 232
    CX, CW, CG = 312, 54, 8
    VX, VW = 950, 292

    lanes = [
        ("рівний потік", [(str(41 + i), SOFT) for i in range(10)],
         "пропусків 0 · дублів 0", GOOD),
        ("радіо губить кадри",
         [("41", SOFT), ("42", SOFT), ("—", WARM), ("—", WARM), ("45", SOFT),
          ("46", SOFT), ("47", SOFT), ("—", WARM), ("49", SOFT), ("50", SOFT)],
         "пропусків 3 · дублів 0\nчастота НИЖЧА за підтверджену", WARM),
        ("той самий апарат\nдвома каналами",
         [(str(41 + i // 2), SOFT if i % 2 == 0 else COLD) for i in range(10)],
         "пропусків 0 · дублів 5\nчастота ВДВІЧІ більша", COLD),
    ]

    y = 100
    for label, cells, verdict, vcol in lanes:
        f.append(fitbox(LX, y, LW, 64, label, size=15, fill=BAND))
        for i, (val, col) in enumerate(cells):
            f.append(fitbox(CX + i * (CW + CG), y, CW, 64, val, size=16, fill=col))
        f.append(fitbox(VX, y, VW, 64, verdict, size=14, fill=vcol, bold=True))
        y += 116

    f.append(fitbox(LX, 452, 590, 106,
                    "d = (прийнятий номер − попередній) за модулем 256\n"
                    "d = 1 — усе гаразд · d = 0 — той самий кадр удруге\n"
                    "2 ≤ d < 128 — d − 1 кадрів не долетіло",
                    size=15, fill=SOFT))
    f.append(fitbox(686, 452, 556, 106,
                    "Половина кадрів здубльована — це не дивна\n"
                    "прошивка, а той самий апарат, під'єднаний\n"
                    "двома каналами: рядок один, а потоків два.",
                    size=15, fill=COLD))

    render(os.path.join(OUT, 'proj-seq-doubling.svg'), W, H, *f)


fig_tap_point()
fig_message_identity()
fig_decode_gate()
fig_chart_buckets()
fig_proj_payload_layout()
fig_proj_seq_doubling()
fig_object_tree()
fig_rate_weights()
fig_rate_step()
fig_rate_sawtooth()
print("ok")
