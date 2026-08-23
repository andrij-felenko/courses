# -*- coding: utf-8 -*-
"""Фігури до кроку «Проєктування КІХ-фільтрів».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

import math

IDEAL = "#2457d6"   # ідеал / ціль — холодне синє
REAL  = "#c0392b"   # реальний фільтр / брижі — гаряче
GOOD  = "#27ae60"   # вікно / прийнятне — зелене
GOLD  = "#b9770e"   # акцент / попередження


# ── 1. Конвеєр проєктування: від чисел до коефіцієнтів ───────────────────────
def fig_from_spec():
    W, H = 820, 250
    f = [text(W / 2, 26, "Від специфікації до коефіцієнтів", size=15, bold=True)]

    steps = [
        (["Специфікація", "5 чисел", "(fp, fs, Ap, As, fд)"], IDEAL),
        (["Ідеальний", "sinc", "(нескінченний)"], IDEAL),
        (["Вікно", "× обрізати", "(M+1 відводів)"], GOOD),
        (["Коефіцієнти", "b[0..M]", "(готовий фільтр)"], GOOD),
        (["Перевірка", "крива в масці?", "(так / переробити)"], GOLD),
    ]
    cw = 150
    x = 14
    cy = 120
    for i, (lines, col) in enumerate(steps):
        f.append(rect(x, cy - 52, cw, 104, fill=FILL, stroke=col, sw=1.8))
        f.append(text(x + cw / 2, cy - 24, lines[0], size=12.5, color=col, bold=True))
        f.append(line(x + 14, cy - 12, x + cw - 14, cy - 12, color="#dddddd", sw=1.1))
        f.append(text(x + cw / 2, cy + 8, lines[1], size=12, color=INK))
        f.append(text(x + cw / 2, cy + 30, lines[2], size=9.5, color=MUTED, italic=True))
        if i < len(steps) - 1:
            f.append(arrow(x + cw + 1, cy, x + cw + 13, cy, color=INK, sw=2))
        x += cw + 14

    f.append(text(W / 2, 232,
                  "числа з минулого кроку входять зліва — звідси й починаємо рахувати ваги",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "from-spec.svg"), W, H, *f)


# ── 2. Обрізаний sinc → явище Ґіббса: брижі, що не зникають ───────────────────
def fig_truncation_gibbs():
    W, H = 760, 340
    f = [text(W / 2, 26, "Чому грубий обрив sinc не працює", size=15, bold=True)]

    # осі частотної характеристики |H|
    ax_x0, ax_x1 = 80, 700
    base = 250          # рівень 0 (низ графіка)
    top = 70            # рівень 1.0 (пропускання)
    fc = 360            # межа зрізу по екрану

    f.append(line(ax_x0, base, ax_x1, base, color=INK, sw=1.4))      # вісь частоти
    f.append(line(ax_x0, base, ax_x0, top - 6, color=INK, sw=1.4))   # вісь |H|
    f.append(text(ax_x1, base + 18, "частота →", size=10, color=MUTED, anchor="end", italic=True))
    f.append(text(ax_x0 - 8, top, "1.0", size=10, color=MUTED, anchor="end"))
    f.append(text(ax_x0 - 8, base, "0", size=10, color=MUTED, anchor="end"))

    # ідеальна «цеглина» (ціль) — пунктир
    f.append(line(ax_x0, top, fc, top, color=IDEAL, sw=2.2, dash="6 4"))
    f.append(line(fc, top, fc, base, color=IDEAL, sw=2.2, dash="6 4"))
    f.append(line(fc, base, ax_x1, base, color=IDEAL, sw=2.2, dash="6 4"))
    f.append(text(220, top - 12, "ідеал-«цеглина»", size=10.5, color=IDEAL, italic=True))

    # реальна крива обрізаного sinc: брижі обабіч стрибка (Ґіббс)
    H1 = base - top      # повна висота
    pts = []
    N = 240
    for i in range(N + 1):
        px = ax_x0 + (ax_x1 - ax_x0) * i / N
        # нормована відстань від межі зрізу
        d = (px - fc) / 60.0
        if px < fc:
            # пропускання ~1 з затухаючими брижами вгору від краю
            ripple = 0.16 * math.cos(d * 3.0) * math.exp(-abs(d) * 0.5)
            val = 1.0 + ripple if abs(d) < 6 else 1.0
            if px < fc - 8:
                val = 1.0 + 0.16 * math.cos(d * 3.0) * math.exp(-abs(d) * 0.45)
        else:
            # затримання ~0 з затухаючими брижами
            val = 0.16 * math.cos(d * 3.0) * math.exp(-abs(d) * 0.45)
            if val < 0:
                val = abs(val) * 0.6
        py = base - val * H1
        py = max(top - 34, min(base + 4, py))
        pts.append("%.1f,%.1f" % (px, py))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>'
             % (" ".join(pts), REAL))

    # позначка перестрибу ~8.95%
    f.append(line(fc - 70, top - 24, fc - 18, top - 24, color=GOLD, sw=1.2, dash="3 3"))
    f.append(text(fc - 96, top - 20, "+8.95%", size=10.5, color=GOLD, anchor="end", bold=True))
    f.append(text(560, top - 8, "обрізаний sinc", size=10.5, color=REAL, italic=True))

    f.append(text(W / 2, 300,
                  "грубий обрив дає брижі (явище Ґіббса) ~8.95% — і вони НЕ меншають від довшого фільтра,",
                  size=10.5, color=MUTED, italic=True))
    f.append(text(W / 2, 320,
                  "лише вужчають; стеля придушення прямокутного «вікна» застрягає на ~21 дБ",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "truncation-gibbs.svg"), W, H, *f)


# ── 3. Вибір вікна: придушення проти ширини переходу ──────────────────────────
def fig_window_choice():
    W, H = 780, 330
    f = [text(W / 2, 26, "Вибір вікна — розмін придушення на крутість", size=15, bold=True)]

    cols = [
        ("Прямокутне", "~21 дБ", "найвужчий", "перехід, але", "сміття в смузі", REAL),
        ("Геммінга", "~53 дБ", "збалансоване —", "робочий", "стандарт", GOOD),
        ("Блекмана", "~74 дБ", "глибоке", "придушення,", "ширший перехід", IDEAL),
        ("Кайзера", "налаштовне", "один важіль β", "крутить компроміс", "під число As", GOLD),
    ]
    cw = 178
    x = 16
    for name, att, l1, l2, l3, col in cols:
        f.append(rect(x, 52, cw, 210, fill=FILL, stroke=col, sw=1.8))
        f.append(text(x + cw / 2, 78, name, size=13.5, color=col, bold=True))
        f.append(line(x + 14, 92, x + cw - 14, 92, color="#dddddd", sw=1.1))
        f.append(text(x + cw / 2, 122, att, size=15, color=col, bold=True))
        f.append(text(x + cw / 2, 142, "придушення", size=9.5, color=MUTED, italic=True))
        f.append(text(x + cw / 2, 184, l1, size=10.5, color=INK))
        f.append(text(x + cw / 2, 204, l2, size=10.5, color=INK))
        f.append(text(x + cw / 2, 224, l3, size=10.5, color=INK))
        x += cw + 12

    f.append(text(W / 2, 290,
                  "глибше придушення → ширший перехід при тій самій довжині; Кайзер дає крутити це числом",
                  size=10.5, color=MUTED, italic=True))
    f.append(text(W / 2, 312,
                  "за замовчуванням — Геммінга; треба тихіше — Блекмана; треба точно під As — Кайзера",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "window-choice.svg"), W, H, *f)


# ── 4. Драбина методів: вікно → частотна вибірка → Parks-McClellan ────────────
def fig_methods_ladder():
    W, H = 780, 300
    f = [text(W / 2, 26, "Три методи проєктування — за потужністю", size=15, bold=True)]

    steps = [
        (["Метод вікон", "ідеальний sinc × вікно", "просто, прозоро, надійно"],
         "робочий кінь — 90% задач", GOOD, 210),
        (["Частотна вибірка", "задаєш |H| на сітці частот", "будь-яка химерна форма"],
         "коли форма нестандартна", IDEAL, 150),
        (["Parks-McClellan", "рівнобрижий оптимум (Remez)", "найкоротший фільтр під маску"],
         "коли важить кожен відвід", GOLD, 90),
    ]
    x = 30
    bw = 226
    for lines, note, col, top in steps:
        h = 250 - top
        f.append(rect(x, top, bw, h, fill=FILL, stroke=col, sw=1.8))
        f.append(text(x + bw / 2, top + 28, lines[0], size=13.5, color=col, bold=True))
        f.append(text(x + bw / 2, top + 52, lines[1], size=10.5, color=INK, italic=True))
        f.append(text(x + bw / 2, top + 74, lines[2], size=10.5, color=MUTED))
        f.append(text(x + bw / 2, 240, note, size=10, color=col, italic=True))
        x += bw + 14

    # стрілка «складніше / потужніше»
    f.append(arrow(40, 268, 740, 268, color=MUTED, sw=1.6))
    f.append(text(W / 2, 286, "складніше й потужніше →  (але метод вікон покриває більшість потреб)",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "methods-ladder.svg"), W, H, *f)


# ── 5. Пара перетворення: «цеглина» у частоті ⇄ sinc у часі (math-вставка) ────
def fig_rect_sinc():
    W, H = 780, 330
    f = [text(W / 2, 26, "Обернене перетворення: цеглина → sinc", size=15, bold=True)]

    # ЛІВО: ідеальна частотна «цеглина» H(ω)
    lx0, lx1 = 60, 360
    lbase = 250        # рівень 0
    ltop = 90          # рівень 1
    cy = (lbase + ltop) / 2
    f.append(line(lx0, lbase, lx1, lbase, color=INK, sw=1.3))          # вісь ω
    f.append(line((lx0 + lx1) / 2, lbase + 6, (lx0 + lx1) / 2, ltop - 18, color="#cfcfcf", sw=1))  # ω=0
    # прямокутник 1 від −ωc до +ωc
    wcx = 70
    midx = (lx0 + lx1) / 2
    f.append(rect(midx - wcx, ltop, 2 * wcx, lbase - ltop, fill="#e9eefc", stroke=IDEAL, sw=2.0))
    f.append(text(midx, ltop - 8, "H(ω) = 1", size=11, color=IDEAL, bold=True))
    f.append(text(midx + wcx + 4, lbase + 16, "+ωc", size=9.5, color=MUTED, anchor="start"))
    f.append(text(midx - wcx - 4, lbase + 16, "−ωc", size=9.5, color=MUTED, anchor="end"))
    f.append(text(lx1, lbase + 16, "ω →", size=9.5, color=MUTED, anchor="end", italic=True))
    f.append(text(midx, lbase + 34, "частотна область", size=10, color=MUTED, italic=True))

    # стрілка-перехід із підписом інтегралу
    f.append(arrow(385, cy, 425, cy, color=INK, sw=2))
    f.append(text(405, cy - 30, "обернене", size=10, color=INK, italic=True))
    f.append(text(405, cy - 16, "Фур'є", size=10, color=INK, italic=True))
    f.append(text(405, cy + 22, "h[n]=", size=9, color=MUTED))
    f.append(text(405, cy + 34, "∫H·e dω", size=9, color=MUTED))

    # ПРАВО: sinc у часі h[n]
    rx0, rx1 = 440, 740
    rbase = 250
    rmid = (rx0 + rx1) / 2
    rtop = 96
    f.append(line(rx0, rbase, rx1, rbase, color=INK, sw=1.3))          # вісь n
    f.append(line(rmid, rbase + 6, rmid, rtop - 6, color=INK, sw=1.3)) # вісь h
    pts = []
    Npt = 200
    for i in range(Npt + 1):
        x = rx0 + (rx1 - rx0) * i / Npt
        u = (x - rmid) / 26.0       # масштаб по n
        v = 1.0 if abs(u) < 1e-6 else math.sin(u) / u
        y = rbase - v * (rbase - rtop) * 0.92
        pts.append("%.1f,%.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (" ".join(pts), REAL))
    f.append(text(rmid + 6, rtop + 2, "h[n] = sin(ωc·n)/(π·n)", size=10.5, color=REAL,
                  anchor="start", bold=True))
    f.append(text(rx1, rbase + 16, "n →", size=9.5, color=MUTED, anchor="end", italic=True))
    f.append(text(rmid, rbase + 34, "часова область (нескінченна)", size=10, color=MUTED, italic=True))

    f.append(text(W / 2, 304,
                  "ширша цеглина (більше ωc) ⇄ вужчий sinc; нескінченні хвости sinc — і є те, що доведеться обрізати",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "math-rect-sinc.svg"), W, H, *f)


# ── 6. Обрізання = згортка ідеалу зі спектром вікна (звідки брижі) ─────────────
def fig_convolution():
    W, H = 780, 340
    f = [text(W / 2, 26, "Обрізання у часі = згортка у частоті", size=15, bold=True)]

    base = 250
    top = 92
    x0, x1 = 70, 710
    fc = 300       # межа зрізу на екрані

    f.append(line(x0, base, x1, base, color=INK, sw=1.3))
    f.append(line(x0, base, x0, top - 6, color=INK, sw=1.3))
    f.append(text(x0 - 6, top, "1", size=9.5, color=MUTED, anchor="end"))
    f.append(text(x0 - 6, base, "0", size=9.5, color=MUTED, anchor="end"))
    f.append(text(x1, base + 16, "ω →", size=9.5, color=MUTED, anchor="end", italic=True))

    # ідеальна цеглина (ціль)
    f.append(line(x0, top, fc, top, color=IDEAL, sw=2.0, dash="6 4"))
    f.append(line(fc, top, fc, base, color=IDEAL, sw=2.0, dash="6 4"))
    f.append(line(fc, base, x1, base, color=IDEAL, sw=2.0, dash="6 4"))
    f.append(text(180, top - 10, "ідеал H(ω)", size=10, color=IDEAL, italic=True))

    # спектр вікна (вузький ядро Діріхле) — намалюємо як «розмазувач» біля стрибка
    kx = 480
    kpts = []
    Nk = 120
    for i in range(Nk + 1):
        x = kx - 70 + 140 * i / Nk
        u = (x - kx) / 11.0
        v = 1.0 if abs(u) < 1e-6 else math.sin(u) / u
        y = (base - 30) - abs(v) * 46 if v >= 0 else (base - 30) + abs(v) * 26
        # головна пелюстка вгору, бічні дрібні
        y = (base - 30) - v * 46
        kpts.append("%.1f,%.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8"/>'
             % (" ".join(kpts), GOOD))
    f.append(text(kx + 78, base - 64, "спектр вікна W(ω):", size=10, color=GOOD, anchor="start", italic=True))
    f.append(text(kx + 78, base - 50, "головна + бічні пелюстки", size=10, color=GOOD, anchor="start", italic=True))

    # реальна (зґорнута) крива: розмита стіна + брижі
    rpts = []
    Nr = 260
    for i in range(Nr + 1):
        x = x0 + (x1 - x0) * i / Nr
        d = (x - fc) / 52.0
        if x < fc:
            val = 1.0 + 0.15 * math.cos(d * 3.1) * math.exp(-abs(d) * 0.5)
        else:
            val = 0.15 * math.cos(d * 3.1) * math.exp(-abs(d) * 0.5)
            if val < 0:
                val = abs(val) * 0.55
        y = base - val * (base - top)
        y = max(top - 28, min(base + 4, y))
        rpts.append("%.1f,%.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.1"/>'
             % (" ".join(rpts), REAL))
    f.append(text(560, top - 4, "результат = H ∗ W", size=10.5, color=REAL, anchor="start", bold=True))

    # позначка першої бічної пелюстки −13 дБ
    f.append(text(fc + 96, base - 8, "перша бічна −13 дБ", size=9.5, color=GOLD, anchor="start", bold=True))

    f.append(text(W / 2, 300,
                  "множення sinc на вікно у часі ⇄ згортка ідеальної цеглини зі спектром вікна у частоті:",
                  size=10.5, color=MUTED, italic=True))
    f.append(text(W / 2, 320,
                  "гострий край «розмазується» головною пелюсткою, а бічні пелюстки сіють брижі обабіч",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "math-convolution.svg"), W, H, *f)


# ── 7. Анатомія спектра вікна: головна пелюстка ⇄ бічні (компроміс) ────────────
def fig_mainlobe_sidelobe():
    W, H = 780, 340
    f = [text(W / 2, 26, "Компроміс вікна: ширина головної ⇄ висота бічних", size=15, bold=True)]

    base = 250
    top = 80
    x0, x1 = 70, 710
    cx = (x0 + x1) / 2

    f.append(line(x0, base, x1, base, color=INK, sw=1.3))
    f.append(line(x0, base, x0, top - 6, color=INK, sw=1.3))
    f.append(text(x0 - 6, top, "0 дБ", size=9.5, color=MUTED, anchor="end"))
    f.append(text(x1, base + 16, "ω →", size=9.5, color=MUTED, anchor="end", italic=True))

    # лог-спектр вікна: висока головна пелюстка + затухаючі бічні
    pts = []
    Np = 320
    for i in range(Np + 1):
        x = x0 + (x1 - x0) * i / Np
        u = (x - cx) / 17.0
        v = 1.0 if abs(u) < 1e-6 else abs(math.sin(u) / u)
        db = 20.0 * math.log10(v + 1e-4)       # у дБ, з підлогою
        y = top - db * 1.9                      # 0 дБ зверху, нижче — глибше
        y = min(base, y)
        pts.append("%.1f,%.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>'
             % (" ".join(pts), IDEAL))

    # ширина головної пелюстки — двосторонній розмір біля вершини
    f.append(line(cx - 17, top + 6, cx + 17, top + 6, color=GOLD, sw=1.4))
    f.append(line(cx - 17, top + 2, cx - 17, top + 12, color=GOLD, sw=1.4))
    f.append(line(cx + 17, top + 2, cx + 17, top + 12, color=GOLD, sw=1.4))
    f.append(text(cx, top - 6, "головна пелюстка (ширина → крутість переходу)",
                  size=10, color=GOLD, bold=True))

    # рівень першої бічної пелюстки
    sb_y = top + 13 * 1.9
    f.append(line(cx + 53, sb_y, cx + 130, sb_y, color=REAL, sw=1.2, dash="3 3"))
    f.append(text(cx + 134, sb_y + 4, "перша бічна пелюстка", size=10, color=REAL, anchor="start", bold=True))
    f.append(text(cx + 134, sb_y + 18, "(рівень → стеля придушення)", size=9.5, color=REAL, anchor="start"))

    f.append(text(W / 2, 296,
                  "вузька головна пелюстка дає крутий перехід, АЛЕ тягне високі бічні (слабке придушення);",
                  size=10.5, color=MUTED, italic=True))
    f.append(text(W / 2, 316,
                  "придавити бічні (гладке вікно) можна лише ширшою головною — це і є нездоланний розмін",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "math-mainlobe-sidelobe.svg"), W, H, *f)


# ── 8. Густина сітки перевірки: чи ловить вона викид у затриманні (proj) ───────
def fig_grid_density():
    W, H = 760, 380
    f = [text(W / 2, 24, "Густина сітки перевірки вирішує все", size=15, bold=True)]

    ax_x0, ax_x1 = 80, 700

    # спільна форма характеристики в затриманні: «горби» між нулями, один пробиває стелю
    def stop_curve(px):
        d = (px - ax_x0) / (ax_x1 - ax_x0)         # 0..1 по екрану
        env = 22.0 * math.exp(-d * 1.1)            # огинаюча спадає вглиб
        hump = abs(math.sin(d * math.pi * 3.3))    # три горби
        return env * hump

    def draw_panel(cy_ceil, nodes_x, label, caught):
        out = []
        base = cy_ceil + 60     # «глибина» осі під стелею
        out.append(line(ax_x0, base, ax_x1, base, color=INK, sw=1.2))
        out.append(line(ax_x0, cy_ceil, ax_x1, cy_ceil, color=GOLD, sw=1.8, dash="6 4"))
        out.append(text(ax_x0 - 8, cy_ceil + 4, "−As", size=10, color=GOLD,
                        anchor="end", bold=True))
        out.append(text(ax_x1, base + 16, "частота →", size=9.5, color=MUTED,
                        anchor="end", italic=True))
        # справжня крива (сіра)
        pts = []
        N = 200
        for i in range(N + 1):
            px = ax_x0 + (ax_x1 - ax_x0) * i / N
            py = base - stop_curve(px)
            py = max(cy_ceil - 26, py)
            pts.append("%.1f,%.1f" % (px, py))
        out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8"/>'
                   % (" ".join(pts), MUTED))
        # вузли сітки: під стелею зелені, над стелею червоні
        for nx in nodes_x:
            ny = base - stop_curve(nx)
            col = GOOD if ny >= cy_ceil else REAL
            out.append(circle(nx, ny, 3.4, fill=col, stroke=col, sw=1))
        out.append(text(ax_x0, cy_ceil - 32, label, size=11,
                        color=(REAL if caught else GOOD), bold=True, anchor="start"))
        return out

    sparse = [ax_x0 + (ax_x1 - ax_x0) * i / 6.0 for i in range(7)]
    f += draw_panel(72, sparse,
                    "Рідка сітка: усі вузли під стелею → «вкладається» (а горб пробив!)",
                    caught=False)
    dense = [ax_x0 + (ax_x1 - ax_x0) * i / 30.0 for i in range(31)]
    f += draw_panel(252, dense,
                    "Густа сітка: вузол попав на горб → тест чесно червоніє",
                    caught=True)

    f.append(text(W / 2, 360,
                  "сіра — справжня крива; зелені вузли під стелею, червоні — над нею; "
                  "для КІХ |H| рахується точно й миттєво, тож густа сітка майже безкоштовна",
                  size=9.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "grid-density.svg"), W, H, *f)


if __name__ == "__main__":
    fig_from_spec()
    fig_truncation_gibbs()
    fig_window_choice()
    fig_methods_ladder()
    fig_rect_sinc()
    fig_convolution()
    fig_mainlobe_sidelobe()
    fig_grid_density()
    print("OK: 8 figures ->", IMG)
