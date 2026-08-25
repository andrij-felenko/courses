# -*- coding: utf-8 -*-
"""Фігури до теми «Шум у сигналі».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# Детермінований «шум» без numpy — простий LCG, щоб фігури були відтворні.
class Rng:
    def __init__(self, seed=1):
        self.s = seed & 0x7fffffff
    def next(self):
        self.s = (1103515245 * self.s + 12345) & 0x7fffffff
        return self.s / 0x7fffffff
    def sym(self, amp):           # симетричний шум у [-amp, +amp]
        return (self.next() - 0.5) * 2 * amp


def poly(points, color, sw, dash=None, lj="round"):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="%s" stroke-linecap="round"%s/>'
            % (" ".join("%.1f,%.1f" % p for p in points), color, sw, lj, d))


# ── 1. Чого хочемо (істина) і що маємо (зашумлені відліки) ───────────────────
# Ідея: кожен відлік = справжнє значення + випадкова добавка; хмара точок
# обліплює плавну криву. Око одразу бачить, що «правда» в потоці є — лише
# розмита шумом, і завдання фільтра — відновити криву з хмари.
def fig_noisy_stream():
    W, H = 680, 300
    ox, oy = 70, 250            # початок осей (низ-ліво)
    top = 60
    rng = Rng(7)
    f = []
    f.append(line(ox, oy, ox, top, color=MUTED, sw=1.4))
    f.append(arrow(ox, top + 12, ox, top, color=MUTED, sw=1.4))
    f.append(line(ox, oy, 642, oy, color=MUTED, sw=1.4))
    f.append(arrow(628, oy, 642, oy, color=MUTED, sw=1.4))
    f.append(text(ox - 8, top + 4, "значення", 11, MUTED, "end"))
    f.append(text(636, oy + 18, "час →", 11, MUTED, "middle"))

    def truval(t):              # плавна крива-«правда»
        return 150 - 32 * math.sin(t * 2.3)

    true_pts = []
    n = 62
    for i in range(n + 1):
        t = i / n
        true_pts.append((ox + t * (628 - ox), truval(t)))
    # сині відліки: правда + шум (рідше, ніж крива)
    for i in range(0, n + 1, 2):
        x, yt = true_pts[i]
        f.append(circle(x, yt + rng.sym(16), 3, fill=NEG, stroke=NEG, sw=1))
    f.append(poly(true_pts, FIELD, 2.6))

    f.append(text(ox + 28, 92, "істинне значення (хочемо)", 11, FIELD, "start", bold=True))
    f.append(text(ox + 240, 214, "відліки давача (маємо)", 11, NEG, "start", bold=True))
    render(os.path.join(OUT, "noisy-stream.svg"), W, H, *f,
           title="Чого хочемо й що маємо: істина і зашумлені відліки")


# ── 2. Три способи, якими давач бреше — і три різні ліки ─────────────────────
# Ідея, яку важко передати словами: «шум» не один, а ТРИ різні геометрії —
# симетричне тремтіння, поодинокі викиди, повільне сповзання, — і кожній
# потрібен СВІЙ лік. Три панелі поруч роблять різницю очевидною.
def fig_three_lies():
    W, H = 720, 260
    panels = [
        ("випадкове тремтіння", NEG,  "усереднення / фільтр", "jitter"),
        ("поодинокі викиди",    POS,  "медіана / відсів",     "spikes"),
        ("повільний дрейф",     "#caa24a", "калібрування",    "drift"),
    ]
    pw, gap, x0, py0, ph = 224, 8, 16, 50, 192
    rng = Rng(3)
    f = []
    for k, (title, col, cure, kind) in enumerate(panels):
        x = x0 + k * (pw + gap)
        f.append(rect(x, py0, pw, ph, fill="#fbfbfb", stroke=col, sw=1.4, rx=8))
        f.append(text(x + pw / 2, py0 + 22, title, 12, col, "middle", bold=True))
        mid = py0 + 95
        lx, rx = x + 24, x + pw - 8
        f.append(line(lx, mid, rx, mid, color="#e4e4e4", sw=1, dash="4,3"))
        pts = []
        nn = 24
        for i in range(nn + 1):
            xx = lx + (rx - lx) * i / nn
            if kind == "jitter":
                yy = mid + rng.sym(14)
            elif kind == "spikes":
                yy = mid + (rng.sym(2))
                if i in (8, 17):
                    yy = mid - 32
            else:  # drift — повільне сповзання вгору
                yy = mid + 16 - 32 * i / nn + rng.sym(2)
            pts.append((xx, yy))
        f.append(poly(pts, col, 1.7))
        f.append(text(x + pw / 2, py0 + 162, "лік:", 10, MUTED, "middle", bold=True))
        f.append(text(x + pw / 2, py0 + 178, cure, 11, col, "middle", bold=True))
    render(os.path.join(OUT, "three-lies.svg"), W, H, *f,
           title="Три способи, якими давач «бреше» — і три різні ліки")


# ── 3. Сигнал і шум в одному потоці ──────────────────────────────────────────
# Ідея: корисний сигнал (повільна зелена крива) і шум (швидке синє тремтіння)
# живуть в ОДНОМУ потоці чисел; вони різняться швидкістю, та коли швидкості
# зближуються — ідеально розділити неможливо. Накладені криві показують це
# наочніше за будь-який опис.
def fig_signal_noise():
    W, H = 680, 290
    ox, oy, top = 70, 240, 60
    rng = Rng(11)
    f = []
    f.append(line(ox, oy, ox, top, color=MUTED, sw=1.4))
    f.append(arrow(ox, top + 12, ox, top, color=MUTED, sw=1.4))
    f.append(line(ox, oy, 642, oy, color=MUTED, sw=1.4))
    f.append(arrow(628, oy, 642, oy, color=MUTED, sw=1.4))
    f.append(text(636, oy + 18, "час →", 11, MUTED, "middle"))

    def sig(t):                  # повільна корисна зміна
        return 150 + 55 * math.sin(t * 3.0 + 0.4)

    n = 80
    clean, noisy = [], []
    for i in range(n + 1):
        t = i / n
        x = ox + t * (628 - ox)
        s = sig(t)
        clean.append((x, s))
        noisy.append((x, s + rng.sym(20)))
    f.append(poly(noisy, NEG, 1.4))
    f.append(poly(clean, FIELD, 2.6))
    f.append(text(ox + 22, 86, "сигнал — справжня зміна величини", 10.5, FIELD, "start", bold=True))
    f.append(text(ox + 210, 224, "сигнал + шум — те, що зчитав давач", 10.5, NEG, "start", bold=True))
    f.append(text(W / 2, 274,
                  "фільтр пропускає сигнал і гасить шум — та вони частково перекриваються",
                  11, MUTED, "middle", italic=True))
    render(os.path.join(OUT, "signal-noise.svg"), W, H, *f,
           title="Сигнал (хочемо) і шум (заважає) — розділити їх і є задача")


# ── 4. Головний компроміс: згладжування ↔ затримка ──────────────────────────
# Ідея: на різкій сходинці легкий фільтр одразу стрибає за нею (швидко, та
# шумно), а важкий повзе до нового значення з помітним запізненням (гладко,
# та із затримкою). Дві реакції на ОДНУ сходинку — це і є плата за гладкість.
def fig_tradeoff():
    W, H = 700, 300
    ox, oy, top = 70, 250, 60
    rng = Rng(5)
    f = []
    f.append(line(ox, oy, ox, top, color=MUTED, sw=1.4))
    f.append(arrow(ox, top + 12, ox, top, color=MUTED, sw=1.4))
    f.append(line(ox, oy, 642, oy, color=MUTED, sw=1.4))
    f.append(arrow(628, oy, 642, oy, color=MUTED, sw=1.4))
    f.append(text(636, oy + 18, "час →", 11, MUTED, "middle"))

    step_x = 294
    lo, hi = 193, 117           # рівні «до» і «після» сходинки
    # справжня сходинка (сіра, пунктир)
    f.append(poly([(ox, lo), (step_x, lo), (step_x, hi), (628, hi)], MUTED, 1.6, dash="5,3"))
    f.append(text(ox + 34, lo - 11, "справжня зміна", 10, MUTED, "start", italic=True))

    # легкий фільтр: майже миттєво на новий рівень, але тремтить
    light = []
    for x in range(ox, 631, 7):
        base = lo if x < step_x else hi
        light.append((x, base + rng.sym(8)))
    f.append(poly(light, NEG, 1.6))
    f.append(text(step_x + 6, 86, "легкий фільтр: швидко, та шумно", 10, NEG, "start", bold=True))

    # важкий фільтр: гладко повзе до нового рівня (експонента)
    heavy = []
    for x in range(ox, 631, 7):
        if x < step_x:
            y = lo
        else:
            k = (x - step_x) / (628 - step_x)
            y = hi + (lo - hi) * math.exp(-3.0 * k)
        heavy.append((x, y))
    f.append(poly(heavy, POS, 2.2))
    f.append(text(step_x + 60, 168, "важкий фільтр: гладко, та з затримкою", 10, POS, "start", bold=True))
    render(os.path.join(OUT, "tradeoff.svg"), W, H, *f,
           title="Головний компроміс: згладжування ↔ затримка")


# ── 5. Фільтрувати в залізі (RC) чи в програмі (числа) ───────────────────────
# Ідея: дві ПЛОЩАДКИ для фільтра. Аналогова RC-ланка стоїть перед АЦП —
# дешева, але фіксована й дрейфує; цифровий фільтр працює над уже
# оцифрованими числами — гнучкий, без дрейфу, але їсть такти. Два «світи»
# поруч показують, чому на практиці тримають обидва.
def fig_digital_analog():
    W, H = 700, 250
    f = []
    # ── ліва панель: аналог ──
    ax = 24
    f.append(rect(ax, 50, 320, 170, fill="#fbf6ee", stroke="#caa24a", sw=1.4, rx=8))
    f.append(text(ax + 160, 72, "аналоговий: RC-ланка", 12, "#9a7a1e", "middle", bold=True))
    # резистор-«зигзаг» + конденсатор на землю
    f.append(line(60, 130, 110, 130, color=INK, sw=2))
    f.append(poly([(110, 130), (118, 122), (128, 138), (138, 122),
                   (148, 138), (158, 122), (166, 130)], INK, 2))
    f.append(line(166, 130, 230, 130, color=INK, sw=2))
    f.append(line(230, 130, 230, 150, color=INK, sw=2))
    f.append(line(216, 150, 244, 150, color=INK, sw=3))
    f.append(line(216, 158, 244, 158, color=INK, sw=3))
    f.append(line(230, 158, 230, 178, color=INK, sw=2))
    f.append(line(60, 178, 280, 178, color=INK, sw=1.6))
    f.append(line(60, 130, 60, 178, color=INK, sw=1.6))
    f.append(text(ax + 160, 200, "фіксована, дрейфує, дешева", 10, INK, "middle", italic=True))

    # ── права панель: цифра ──
    dx = 360
    f.append(rect(dx, 50, 316, 170, fill="#eef4fb", stroke=NEG, sw=1.4, rx=8))
    f.append(text(dx + 158, 72, "цифровий: фільтр у коді", 12, NEG, "middle", bold=True))
    for cx, cy in [(400, 112), (440, 130), (480, 112), (520, 130)]:
        f.append(circle(cx, cy, 3, fill=NEG, stroke=NEG, sw=1))
    f.append(arrow(548, 116, 588, 116, color=INK, sw=1.8))
    f.append(rect(588, 100, 60, 34, fill="#fff", stroke=FIELD, sw=1.5, rx=5))
    f.append(text(618, 121, "filter()", 10, FIELD, "middle", bold=True))
    f.append(text(dx + 158, 160, "відліки АЦП → програма", 10, INK, "middle", italic=True))
    f.append(text(dx + 158, 200, "гнучка, без дрейфу, їсть такти", 10, INK, "middle", italic=True))
    render(os.path.join(OUT, "digital-analog.svg"), W, H, *f,
           title="Фільтрувати в залізі (RC) чи в програмі (числа)")


# ── 6. Задача й скриня фільтрів ──────────────────────────────────────────────
# Ідея: уся тема стискається в один конвеєр — зашумлений потік → фільтр →
# чиста оцінка, — а під ним лежить скриня з трьох інструментів, вибір між
# якими вирішує компроміс згладжування ↔ затримка.
def fig_chapter_map():
    W, H = 700, 240
    f = []
    f.append(rect(40, 80, 150, 56, fill="#eef4fb", stroke=NEG, sw=1.6, rx=8))
    f.append(mtext(115, 104, ["зашумлений", "потік відліків"], 11.5, NEG, "middle", bold=True))
    f.append(rect(275, 80, 150, 56, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=8))
    f.append(text(350, 104, "ФІЛЬТР", 13, FIELD, "middle", bold=True))
    f.append(text(350, 122, "(дешевий, у реальному часі)", 9, INK, "middle", italic=True))
    f.append(rect(510, 80, 150, 56, fill="#f1f7f1", stroke=FIELD, sw=1.6, rx=8))
    f.append(mtext(585, 104, ["чиста", "оцінка величини"], 11.5, FIELD, "middle", bold=True))
    f.append(arrow(192, 108, 273, 108, color=INK, sw=2))
    f.append(arrow(427, 108, 508, 108, color=INK, sw=2))
    f.append(text(W / 2, 176,
                  "інструменти: ковзне середнє · медіана · експоненційне згладжування",
                  11.5, INK, "middle", bold=True))
    f.append(text(W / 2, 200,
                  "…а вибір між ними вирішує компроміс згладжування ↔ затримка",
                  11, MUTED, "middle", italic=True))
    render(os.path.join(OUT, "chapter-map.svg"), W, H, *f,
           title="Задача теми: зашумлений потік → чиста оцінка")


if __name__ == "__main__":
    fig_noisy_stream()
    fig_three_lies()
    fig_signal_noise()
    fig_tradeoff()
    fig_digital_analog()
    fig_chapter_map()
    print("OK: 6 figures ->", OUT)
