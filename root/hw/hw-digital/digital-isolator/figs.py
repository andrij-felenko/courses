# -*- coding: utf-8 -*-
"""Фігури до теми «Цифровий ізолятор».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def barrier(f, x, y0, y1, label="бар'єр"):
    """Вертикальна ізоляційна стінка (пунктир) із підписом."""
    f.append(line(x, y0, x, y1, color=FIELD, sw=2.4, dash="6,5"))
    f.append(text(x, y0 - 6, label, size=10.5, color=FIELD, bold=True))


def gnd(f, cx, cy, color=LINE):
    """Символ землі."""
    f.append(line(cx, cy, cx, cy + 12, color=color, sw=2))
    f.append(line(cx - 13, cy + 12, cx + 13, cy + 12, color=color, sw=2.4))
    f.append(line(cx - 8, cy + 17, cx + 8, cy + 17, color=color, sw=2))
    f.append(line(cx - 3, cy + 22, cx + 3, cy + 22, color=color, sw=1.6))


# ── 1. Дві причини рвати провід: безпека і земляна петля ─────────────────────
def fig_why_isolate():
    W, H = 720, 430
    f = [text(W / 2, 26, "Дві причини розірвати провід між двома боками",
              size=15, bold=True)]
    bx = W / 2

    # ── верхня половина: безпека ──
    f.append(text(bx, 60, "1. Безпека: небезпечний потенціал не має вийти на слабкий бік",
                  size=12, bold=True, color=POS))
    barrier(f, bx, 78, 168, "бар'єр")
    # силовий бік
    f.append(rect(90, 96, 150, 58, fill="#fdecea", stroke=POS, sw=2, rx=8))
    f.append(text(165, 118, "силовий бік", size=12, bold=True, color=INK))
    f.append(text(165, 137, "сотні вольтів", size=10.5, color=POS))
    # керувальний бік
    f.append(rect(W - 240, 96, 150, 58, fill="#eef6ef", stroke=FIELD, sw=2, rx=8))
    f.append(text(W - 165, 118, "керування + людина", size=11, bold=True, color=INK))
    f.append(text(W - 165, 137, "3.3 В, дотик", size=10.5, color=FIELD))
    # стінка блокує потенціал
    f.append(arrow(245, 125, bx - 10, 125, color=POS, sw=2.2))
    f.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.4"/>'
             % (bx + 3, 110, bx + 3, 140, POS))  # відбій
    f.append(text((245 + bx) / 2, 112, "напруга впирається", size=10, color=POS))
    f.append(text(bx + 60, 125, "стінка не пускає", size=10.5, color=FIELD, anchor="start"))

    f.append(line(40, 200, W - 40, 200, color="#d6dde6", sw=1.2, dash="5,5"))

    # ── нижня половина: земляна петля ──
    f.append(text(bx, 232, "2. Шум: спільна земля дає петлю зі зрівнювальним струмом",
                  size=12, bold=True, color=NEG))
    # два пристрої
    f.append(rect(90, 258, 150, 52, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=8))
    f.append(text(165, 288, "пристрій A", size=12, bold=True, color=INK))
    f.append(rect(W - 240, 258, 150, 52, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=8))
    f.append(text(W - 165, 288, "пристрій B", size=12, bold=True, color=INK))
    # спільна земля з петлею (ліворуч від бар'єра — «як було»)
    f.append(text(bx, 258, "БЕЗ розриву:", size=10.5, italic=True, color=MUTED))
    gnd(f, 165, 322, color=NEG)
    gnd(f, W - 165, 322, color=NEG)
    f.append(line(165, 344, W - 165, 344, color=NEG, sw=2))
    f.append(text(bx, 338, "різні «нулі» → струм тече по спільній землі", size=10.5, color=NEG))
    # стрілка струму
    f.append(arrow(300, 344, 420, 344, color=POS, sw=2))
    f.append(text(bx, 368, "зрівнювальний струм наводить шум у сигнал", size=10.5, color=POS))
    f.append(text(bx, 398,
                  "Розрив землі забирає контур: різниця лишається, а струму нема куди текти",
                  size=11.5, italic=True, color=FIELD))
    render(os.path.join(IMG, "why-isolate.svg"), W, H, *f)


# ── 2. Два містки крізь бар'єр: ємнісний і магнітний ────────────────────────
def fig_two_couplers():
    W, H = 720, 380
    f = [text(W / 2, 26, "Два способи провести сигнал крізь непровідну стінку",
              size=15, bold=True)]

    # ── ліва половина: ємнісний ──
    cx = 190
    f.append(rect(40, 52, 300, 296, fill="#eef2f8", stroke=NEG, sw=1.6, rx=10))
    f.append(text(cx, 76, "Ємнісний зв'язок", size=13.5, bold=True, color=INK))
    f.append(text(cx, 94, "(дві пластинки + діелектрик)", size=10.5, color=MUTED))
    # дві пластини
    py = 150
    f.append(line(80, py, 165, py, color=NEG, sw=2))            # підвід зліва
    f.append(line(165, py - 26, 165, py + 26, color=INK, sw=4))  # пластина 1
    f.append(line(215, py - 26, 215, py + 26, color=INK, sw=4))  # пластина 2
    f.append(line(215, py, 300, py, color=POS, sw=2))           # відвід справа
    # бар'єр між пластинами
    f.append(line(190, py - 40, 190, py + 40, color=FIELD, sw=2.2, dash="5,4"))
    f.append(text(190, py - 48, "діелектрик", size=9.5, color=FIELD))
    f.append(text(cx, py + 62, "постійна напруга не проходить", size=10.5, color=NEG))
    f.append(text(cx, py + 80, "швидка зміна наводить струм", size=10.5, color=POS))
    # маленькі стрілки: DC впирається, AC проходить
    f.append(arrow(110, py + 108, 160, py + 108, color=POS, sw=1.8))
    f.append(text(cx, py + 112, "тільки зміна", size=10, color=POS, anchor="start"))
    f.append(text(cx, py + 138, "→ переходить на другу пластину", size=10, color=INK))

    # ── права половина: магнітний ──
    cx2 = W - 190
    f.append(rect(W - 340, 52, 300, 296, fill="#fbeee6", stroke=POS, sw=1.6, rx=10))
    f.append(text(cx2, 76, "Магнітний зв'язок", size=13.5, bold=True, color=INK))
    f.append(text(cx2, 94, "(дві котушки, спільне поле)", size=10.5, color=MUTED))
    # дві котушки (спіральки як дуги)
    ly = 150
    x1c, x2c = cx2 - 42, cx2 + 42
    for k in range(3):
        f.append('<path d="M %.0f %.0f a 8 8 0 1 1 0.1 0" fill="none" stroke="%s" stroke-width="2.2"/>'
                 % (x1c, ly - 24 + k * 16, NEG))
        f.append('<path d="M %.0f %.0f a 8 8 0 1 0 -0.1 0" fill="none" stroke="%s" stroke-width="2.2"/>'
                 % (x2c, ly - 24 + k * 16, POS))
    f.append(line(x1c - 8, ly - 30, x1c - 30, ly - 30, color=NEG, sw=2))
    f.append(line(x1c - 8, ly + 30, x1c - 30, ly + 30, color=NEG, sw=2))
    f.append(line(x2c + 8, ly - 30, x2c + 30, ly - 30, color=POS, sw=2))
    f.append(line(x2c + 8, ly + 30, x2c + 30, ly + 30, color=POS, sw=2))
    # бар'єр між котушками
    f.append(line(cx2, ly - 44, cx2, ly + 44, color=FIELD, sw=2.2, dash="5,4"))
    f.append(text(cx2, ly - 52, "ізоляція", size=9.5, color=FIELD))
    f.append(text(cx2, ly + 62, "постійний струм не проходить", size=10.5, color=NEG))
    f.append(text(cx2, ly + 80, "зміна струму = змінне поле", size=10.5, color=POS))
    f.append(text(cx2, ly + 138, "→ наводить напругу в другій котушці", size=10, color=INK))

    f.append(text(W / 2, 366, "Обидва містки пропускають лише ЗМІНУ — на цьому все й будується",
                  size=12, italic=True, color=INK))
    render(os.path.join(IMG, "two-couplers.svg"), W, H, *f)


def _pulse_frame(W, H, title):
    return [text(W / 2, 24, title, size=15, bold=True)]


def _axis_row(f, x0, y, w, label, col=MUTED):
    f.append(line(x0, y, x0 + w, y, color="#d6dde6", sw=1.2))
    f.append(text(x0 - 8, y - 22, label, size=11, color=col, anchor="end", bold=True))


# ── 3. Кодування фронтами ───────────────────────────────────────────────────
def fig_edge_coding():
    W, H = 720, 380
    f = _pulse_frame(W, H, "Кодування фронтами: імпульс на кожну зміну, тригер тримає рівень")
    x0, w = 150, 500
    hi, lo = 34, 0            # рівні над базою рядка

    # перемикання входу: точки зміни
    edges = [0.12, 0.42, 0.66, 0.86]   # частки ширини
    # вхід починається на 0, чергує
    def to_px(t):
        return x0 + t * w

    # ── рядок 1: вхід ──
    y1 = 90
    _axis_row(f, x0, y1, w, "вхід")
    lvl = 0
    prev = x0
    pts = []
    xs = [0.0] + edges + [1.0]
    cur = 0
    seq = []
    for i in range(len(edges) + 1):
        seq.append(cur)
        cur ^= 1
    # намалюємо ступінчастий вхід
    y_for = lambda b: y1 - (hi if b else lo)
    segx = x0
    b = 0
    poly = ["%.1f,%.1f" % (x0, y_for(0))]
    for e in edges:
        ex = to_px(e)
        poly.append("%.1f,%.1f" % (ex, y_for(b)))
        b ^= 1
        poly.append("%.1f,%.1f" % (ex, y_for(b)))
    poly.append("%.1f,%.1f" % (x0 + w, y_for(b)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(poly), NEG))

    # ── рядок 2: імпульси крізь бар'єр ──
    y2 = 200
    _axis_row(f, x0, y2, w, "крізь\nбар'єр", col=FIELD)
    b = 0
    for e in edges:
        ex = to_px(e)
        b ^= 1
        if b == 1:  # наростання: одинарний імпульс угору (POS)
            f.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" stroke-width="2.6"/>'
                     % (ex - 10, y2, ex, y2 - 30, ex + 6, y2, ex + 10, y2, POS))
        else:       # спадання: подвійний імпульс униз (POS інша форма)
            f.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" stroke-width="2.6"/>'
                     % (ex - 12, y2, ex - 6, y2 + 26, ex, y2, ex + 4, y2 + 26, ex + 10, y2, ex + 12, y2, POS))
    f.append(text(x0 + w + 6, y2 - 18, "↑ одна форма", size=9.5, color=POS, anchor="start"))
    f.append(text(x0 + w + 6, y2 + 20, "↓ інша форма", size=9.5, color=POS, anchor="start"))

    # ── рядок 3: вихід (тригер тримає) ──
    y3 = 310
    _axis_row(f, x0, y3, w, "вихід")
    y_for3 = lambda bb: y3 - (hi if bb else lo)
    b = 0
    poly3 = ["%.1f,%.1f" % (x0, y_for3(0))]
    for e in edges:
        ex = to_px(e)
        poly3.append("%.1f,%.1f" % (ex, y_for3(b)))
        b ^= 1
        poly3.append("%.1f,%.1f" % (ex, y_for3(b)))
    poly3.append("%.1f,%.1f" % (x0 + w, y_for3(b)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(poly3), INK))
    f.append(text(W / 2, 356, "Рівень відновлено з фронтів: між імпульсами крізь бар'єр не йде нічого",
                  size=11.5, italic=True, color=MUTED))
    render(os.path.join(IMG, "edge-coding.svg"), W, H, *f)


# ── 4. Кодування несучою OOK ────────────────────────────────────────────────
def fig_ook_coding():
    W, H = 720, 380
    f = _pulse_frame(W, H, "Кодування несучою (OOK): є коливання — «1», нема — «0»")
    x0, w = 150, 500
    hi = 34

    def to_px(t):
        return x0 + t * w

    # вхідний рівень: 1 на інтервалах
    ones = [(0.10, 0.40), (0.58, 0.80)]   # де тримається «1»
    # ── рядок 1: вхід ──
    y1 = 90
    _axis_row(f, x0, y1, w, "вхід")
    yb = y1
    yt = y1 - hi
    poly = ["%.1f,%.1f" % (x0, yb)]
    cursor = 0.0
    for (a, b) in ones:
        poly += ["%.1f,%.1f" % (to_px(a), yb), "%.1f,%.1f" % (to_px(a), yt),
                 "%.1f,%.1f" % (to_px(b), yt), "%.1f,%.1f" % (to_px(b), yb)]
    poly.append("%.1f,%.1f" % (x0 + w, yb))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(poly), NEG))

    # ── рядок 2: несуча крізь бар'єр ──
    y2 = 200
    _axis_row(f, x0, y2, w, "крізь\nбар'єр", col=FIELD)
    # синус лише всередині «1»
    for (a, b) in ones:
        pts = []
        n = 120
        xa, xb = to_px(a), to_px(b)
        for i in range(n + 1):
            t = i / n
            xx = xa + (xb - xa) * t
            yy = y2 - 26 * math.sin(t * (xb - xa) / 6.0)
            pts.append("%.1f,%.1f" % (xx, yy))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0"/>' % (" ".join(pts), POS))
    # підписи «несуча» / «тиша»
    f.append(text(to_px(0.25), y2 + 40, "несуча біжить", size=10, color=POS))
    f.append(text(to_px(0.49), y2 + 40, "тиша", size=10, color=MUTED))
    f.append(text(to_px(0.69), y2 + 40, "несуча", size=10, color=POS))

    # ── рядок 3: вихід ──
    y3 = 310
    _axis_row(f, x0, y3, w, "вихід")
    yb3, yt3 = y3, y3 - hi
    poly3 = ["%.1f,%.1f" % (x0, yb3)]
    for (a, b) in ones:
        poly3 += ["%.1f,%.1f" % (to_px(a), yb3), "%.1f,%.1f" % (to_px(a), yt3),
                  "%.1f,%.1f" % (to_px(b), yt3), "%.1f,%.1f" % (to_px(b), yb3)]
    poly3.append("%.1f,%.1f" % (x0 + w, yb3))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(poly3), INK))
    f.append(text(W / 2, 356, "Стан «1» підтверджено безперервно, поки триває несуча — без «зависання»",
                  size=11.5, italic=True, color=MUTED))
    render(os.path.join(IMG, "ook-coding.svg"), W, H, *f)


# ── 5. Два живлення: кожен острів окремо ────────────────────────────────────
def fig_two_supplies():
    W, H = 720, 360
    f = [text(W / 2, 26, "Розв'язка рве і сигнал, і землю, і живлення — на кожен бік своє",
              size=15, bold=True)]
    bx = W / 2
    barrier(f, bx, 60, 270, "бар'єр")

    # ── лівий острів ──
    f.append(rect(70, 80, 220, 150, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=10))
    f.append(text(180, 104, "бік керування", size=12.5, bold=True, color=INK))
    # живлення + земля лівого
    f.append(line(110, 124, 110, 108, color=POS, sw=2))
    f.append(text(110, 100, "VccI", size=10, color=POS))
    f.append(text(180, 150, "своя логіка", size=11, color=MUTED))
    gnd(f, 180, 190, color=NEG)
    f.append(text(180, 226, "земля I", size=10, color=NEG))

    # ── правий острів ──
    f.append(rect(W - 290, 80, 220, 150, fill="#fbeee6", stroke=POS, sw=1.8, rx=10))
    f.append(text(W - 180, 104, "дальній бік", size=12.5, bold=True, color=INK))
    f.append(line(W - 110, 124, W - 110, 108, color=POS, sw=2))
    f.append(text(W - 110, 100, "VccO", size=10, color=POS))
    f.append(text(W - 180, 150, "своя логіка", size=11, color=MUTED))
    gnd(f, W - 180, 190, color=POS)
    f.append(text(W - 180, 226, "земля O", size=10, color=POS))

    # сигнал крізь бар'єр
    f.append(arrow(290, 150, W - 290, 150, color=INK, sw=2))
    f.append(text(bx, 142, "біт", size=11, bold=True, color=INK))

    # заборонена спільна шина (пунктир, перекреслена)
    f.append(line(110, 300, W - 110, 300, color=MUTED, sw=1.8, dash="7,5"))
    f.append(line(110, 124, 110, 300, color=MUTED, sw=1.4, dash="4,4"))
    f.append(line(W - 110, 124, W - 110, 300, color=MUTED, sw=1.4, dash="4,4"))
    # перекреслення на бар'єрі
    f.append(text(bx, 296, "✗", size=22, color=POS, bold=True))
    f.append(text(bx, 326, "спільна шина живлення звела б землі назад — розв'язки нема",
                  size=11.5, italic=True, color=POS))
    render(os.path.join(IMG, "two-supplies.svg"), W, H, *f)


if __name__ == "__main__":
    fig_why_isolate()
    fig_two_couplers()
    fig_edge_coding()
    fig_ook_coding()
    fig_two_supplies()
    print("OK: 5 figures ->", IMG)
