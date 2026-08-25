# -*- coding: utf-8 -*-
"""Фігури до теми «Розв'язка IMU від вібрації».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Звідки біда: рама тремтить → дві поломки в IMU ────────────────────────
def fig_why_vibration():
    W, H = 780, 392
    f = [text(W / 2, 28, "Чому вібрація рами псує IMU — два механізми поломки", size=16, bold=True)]

    # джерело: мотори / гвинти
    src, sw_, sh_ = textbox(150, 92, ["Мотори й гвинти", "сотні обертів/с"],
                            size=13, fill="#fdecea", stroke=POS, bold=True)
    f.append(src)
    f.append(text(150, 134, "→ рама дрібно тремтить", size=12, color=MUTED))

    # стрілка вниз до IMU
    f.append(arrow(150, 152, 150, 200, color=POS, sw=2.2))

    # IMU на рамі
    imu, iw, ih = textbox(150, 224, "MEMS-IMU\nжорстко на рамі", size=12, bold=True)
    f.append(imu)

    # дві гілки поломки
    f.append(arrow(215, 222, 318, 150, color=LINE, sw=2))
    f.append(arrow(215, 234, 318, 300, color=LINE, sw=2))

    b1 = fitbox(322, 104, 430, 92,
                ["1. НАСИЧЕННЯ", "пік вібрації перевищує діапазон ±g —",
                 "показ упирається в стелю й обрізається."],
                size=13)
    f.append(b1)

    b2 = fitbox(322, 270, 430, 96,
                ["2. АЛІАСИНГ", "швидке тремтіння при рідкій вибірці",
                 "складається в ХИБНИЙ повільний сигнал", "просто в смузі корисних даних."],
                size=13)
    f.append(b2)

    f.append(text(W / 2, 380, "Обидві поломки стаються ДО того, як дані дійдуть до програми.",
                  size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, "why-vibration.svg"), W, H, *f)


# ── 2. Аліасинг: швидка вібрація → хибна повільна хвиля в смузі даних ─────────
def fig_aliasing():
    W, H = 760, 380
    f = [text(W / 2, 28, "Аліасинг: швидка вібрація прикидається повільним рухом", size=16, bold=True)]

    x0, x1 = 70, 700
    yc = 150
    amp = 52

    # справжня швидка вібрація (багато періодів)
    pts = []
    n = 400
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        ph = (x - x0) / (x1 - x0)
        y = yc - amp * math.sin(ph * 2 * math.pi * 11)   # 11 періодів = висока частота
        pts.append("%.1f,%.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6" opacity="0.55"/>'
             % (" ".join(pts), MUTED))
    f.append(text(x1 + 4, yc - amp - 6, "справжня вібрація (висока f)", size=11,
                  color=MUTED, anchor="end"))

    # рідкі моменти вибірки (точки) — частота трохи нижча за вібрацію → биття
    samp_n = 12
    sx, sy = [], []
    for k in range(samp_n + 1):
        x = x0 + (x1 - x0) * k / samp_n
        ph = (x - x0) / (x1 - x0)
        y = yc - amp * math.sin(ph * 2 * math.pi * 11)
        sx.append(x); sy.append(y)
        f.append(line(x, yc + amp + 14, x, y, color=NEG, sw=1, dash="3 3"))
        f.append(circle(x, y, 5, fill=NEG, stroke=BG, sw=1.5))
        f.append(text(x, yc + amp + 28, "↑", size=12, color=NEG))

    # ХИБНА повільна хвиля, що з'єднує точки вибірки
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join("%.1f,%.1f" % (sx[i], sy[i]) for i in range(len(sx))), POS))
    f.append(text(x0 + 6, yc + amp + 52, "сині стрілки — рідкі моменти вибірки",
                  size=11, color=NEG, anchor="start"))
    f.append(text(W / 2, yc + amp + 78,
                  "червоне — те, що «бачить» давач: повільна хвиля, якої НАСПРАВДІ НЕМАЄ",
                  size=12.5, color=POS, bold=True))

    f.append(text(W / 2, H - 14,
                  "Підробка лягає прямо в смугу корисних даних — фільтр уже не відрізнить її від руху.",
                  size=12, italic=True, color=INK))
    render(os.path.join(IMG, "aliasing.svg"), W, H, *f)


# ── 3. М'яке кріплення = механічний ФНЧ; власна частота підвісу ──────────────
def fig_softmount():
    W, H = 760, 400
    f = [text(W / 2, 28, "М'яке кріплення — механічний фільтр; усе вирішує власна частота", size=15.5, bold=True)]

    # ліворуч: фізична картинка — маса на пружинах
    cx = 150
    # рама внизу
    f.append(rect(cx - 95, 300, 190, 18, fill="#dfe6ee", stroke=LINE, sw=2))
    f.append(text(cx, 336, "рама (тремтить)", size=12, color=POS, bold=True))
    # маса (IMU + тягарець) угорі
    mb, mw, mh = textbox(cx, 110, "IMU\n+ маса", size=12, bold=True, fill="#eaf7ef", stroke=FIELD)
    f.append(mb)
    # чотири «пружини» (демпфери) між масою і рамою
    for dx in (-60, -20, 20, 60):
        x = cx + dx
        zig = ["%.1f,%.1f" % (x, 140)]
        steps = 7
        for s in range(1, steps + 1):
            yy = 140 + (300 - 140) * s / steps
            xx = x + (8 if s % 2 else -8)
            zig.append("%.1f,%.1f" % (xx, yy))
        zig.append("%.1f,%.1f" % (x, 300))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>'
                 % (" ".join(zig), NEG))
    f.append(text(cx, 168, "м'які демпфери", size=11, color=NEG))
    f.append(text(cx, 360, "ƒₙ = (1/2π)·√(k/m)", size=12.5, bold=True, color=INK))

    # праворуч: передавання vs частота (механічний ФНЧ із піком на резонансі)
    gx0, gx1 = 360, 720
    gy0, gy1 = 70, 300
    f.append(line(gx0, gy1, gx1, gy1, color=INK, sw=1.6))      # вісь X (частота)
    f.append(line(gx0, gy0, gx0, gy1, color=INK, sw=1.6))      # вісь Y (передавання)
    f.append(text(gx1, gy1 + 22, "частота →", size=12, color=INK, anchor="end"))
    f.append(text(gx0 - 6, gy0 + 4, "передавання", size=11, color=INK, anchor="end"))
    f.append(line(gx0 - 5, (gy0 + gy1) / 2, gx0 + 5, (gy0 + gy1) / 2, color=MUTED, sw=1))
    f.append(text(gx0 - 8, (gy0 + gy1) / 2 + 4, "1", size=11, color=MUTED, anchor="end"))

    # лінія передавання: ≈1 до fn, пік на fn, спад після
    fn_x = gx0 + (gx1 - gx0) * 0.30
    one_y = (gy0 + gy1) / 2
    pts = []
    n = 240
    for i in range(n + 1):
        x = gx0 + (gx1 - gx0) * i / n
        r = (x - gx0) / (fn_x - gx0) if fn_x > gx0 else 0  # частота / fn
        Q = 2.2
        denom = math.sqrt((1 - r * r) ** 2 + (r / Q) ** 2)
        T = 1.0 / denom if denom > 1e-6 else 8
        T = min(T, 3.0)
        y = one_y - (T - 1) * 55
        y = max(gy0 + 6, min(gy1 - 2, y))
        pts.append("%.1f,%.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts), INK))

    # позначка fn і зони
    f.append(line(fn_x, gy0, fn_x, gy1, color=POS, sw=1.4, dash="4 4"))
    f.append(text(fn_x, gy1 + 22, "ƒₙ (резонанс!)", size=11.5, color=POS, bold=True))
    f.append(text(gx0 + (fn_x - gx0) / 2, gy1 - 8, "проходить", size=11, color=MUTED))
    pass_lbl = fitbox(fn_x + 8, gy0 + 6, gx1 - fn_x - 12, 34,
                      "тут вібрація гаситься (спад)", size=10.5, fill="#eaf7ef", stroke=FIELD)
    f.append(pass_lbl)

    f.append(text(W / 2, H - 16,
                  "Хитрість: посади ƒₙ НИЖЧЕ за вібрацію (м'якше/важче), але ВИЩЕ за корисний рух апарата.",
                  size=12, italic=True, color=INK))
    render(os.path.join(IMG, "soft-mount.svg"), W, H, *f)


# ── 4. Чому фільтр сам не рятує: порядок дій вирішує все ─────────────────────
def fig_filter_too_late():
    W, H = 800, 360
    f = [text(W / 2, 28, "Чому цифровий фільтр сам не рятує: аліасинг стається ДО вибірки", size=15, bold=True)]

    yb = 96
    bh = 46
    boxes = [
        ("вібрація", "висока f", "#fdecea", POS),
        ("АЦП: вибірка", "рідкі відліки", "#eaf0fd", NEG),
        ("цифр. фільтр", "у програмі", "#eef2f6", LINE),
    ]
    bw, gap = 150, 40
    x = 56
    centers = []
    for title, sub, fill, stroke in boxes:
        f.append(fitbox(x, yb, bw, bh, title, size=13, fill=fill, stroke=stroke))
        f.append(text(x + bw / 2, yb + bh + 18, sub, size=11.5, color=MUTED))
        centers.append(x + bw / 2)
        f.append(arrow(x + bw, yb + bh / 2, x + bw + gap, yb + bh / 2, color=LINE, sw=2))
        x += bw + gap

    # вердикт-блок
    bad = fitbox(x, yb, 170, bh, "ПІЗНО!", size=14, fill="#fdecea", stroke=POS, bold=True)
    f.append(bad)
    f.append(text(x + 85, yb + bh + 18, "фільтр ріже й правду, і аліас", size=11.5, color=POS))

    # підпис над стрілкою вибірки: тут і народжується аліас
    mid = (centers[0] + centers[1]) / 2
    f.append(text(mid, yb - 12, "↑ тут народжується аліас", size=12, color=POS, bold=True))
    f.append(line(mid, yb - 4, mid, yb, color=POS, sw=1.4))

    f.append(text(W / 2, 224,
                  "Цифровий фільтр живе ПІСЛЯ вибірки — він не прибере того, що змішалося ДО неї.",
                  size=12.5, bold=True, color=INK))
    f.append(text(W / 2, 262,
                  "Зупинити вібрацію треба РАНІШЕ: механічним демпфером (або аналоговим ФНЧ до АЦП).",
                  size=12.5, color=INK))
    f.append(text(W / 2, 300,
                  "Демпфер — це і є той «фільтр до вибірки», якого цифрі бракує.",
                  size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, "filter-too-late.svg"), W, H, *f)


if __name__ == "__main__":
    fig_why_vibration()
    fig_aliasing()
    fig_softmount()
    fig_filter_too_late()
    print("OK: figures written to", IMG)
