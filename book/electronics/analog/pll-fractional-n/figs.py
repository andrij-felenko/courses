# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Дробова петля: дільник чергує N/N+1 за командою акумулятора ────────────
def fig_frac_loop():
    W, H = 820, 360
    f = []
    y = 120
    bx = [60, 285, 510]
    bw = 150
    labels = [
        ("Фазовий\nдетектор", NEG),
        ("Фільтр\nпетлі", FIELD),
        ("Генератор\n(ГКН)", POS),
    ]
    for i, (lab, col) in enumerate(labels):
        f.append(fitbox(bx[i], y - 30, bw, 60, lab, size=15, bold=True,
                        stroke=col, sw=2.2, fill="#ffffff"))
    # вхід опори
    f.append(text(36, y - 4, "f_оп", size=13, color=INK, anchor="end"))
    f.append(arrow(40, y, bx[0], y, color=INK, sw=2.2))
    f.append(arrow(bx[0] + bw, y, bx[1], y, color=INK, sw=2.2))
    f.append(arrow(bx[1] + bw, y, bx[2], y, color=INK, sw=2.2))
    # вихід
    outx = bx[2] + bw
    f.append(arrow(outx, y, outx + 78, y, color=INK, sw=2.2))
    f.append(text(outx + 84, y - 4, "f_вих = (N+K/F)·f_оп", size=13,
                  color=INK, anchor="start", bold=True))

    # дільник N/N+1 у зворотному зв'язку
    fy = y + 130
    dx = (bx[0] + bw / 2 + outx + 35) / 2
    f.append(line(outx + 35, y, outx + 35, fy, color=POS, sw=2.2))
    f.append(line(outx + 35, fy, dx + 62, fy, color=POS, sw=2.2))
    db, dw, dh = textbox(dx, fy, "Дільник ÷N / ÷(N+1)", size=14, bold=True,
                         stroke=POS, sw=2.2, fill="#fdecea")
    f.append(db)
    f.append(line(dx - 62, fy, bx[0] + bw / 2, fy, color=POS, sw=2.2))
    f.append(arrow(bx[0] + bw / 2, fy, bx[0] + bw / 2, y + 30, color=POS, sw=2.2))

    # акумулятор керує дільником
    accx = dx
    accy = fy + 78
    ab, aw, ah = textbox(accx, accy, "Акумулятор:  acc += K, переповнення → +1",
                         size=12.5, bold=True, stroke=NEG, sw=2.0, fill="#eaf0fd")
    f.append(ab)
    f.append(arrow(accx, accy - ah / 2, accx, fy + dh / 2, color=NEG, sw=2.0))
    f.append(text(accx + aw / 2 + 8, accy + 4,
                  "задає, коли ділити на N+1", size=11.5, color=MUTED,
                  anchor="start", italic=True))

    render(os.path.join(IMG, "frac-loop.svg"), W, H, *f,
           title="Дробова петля: дільник чергує два цілих, у середньому — дріб")


# ── 2. Пилкоподібна помилка фази: накопичення + скидання при переповненні ─────
def fig_sawtooth():
    W, H = 760, 340
    f = []
    ox, oy, w, h = 70, 70, 600, 200
    # осі
    f.append(arrow(ox, oy + h, ox + w + 14, oy + h, color=INK, sw=1.6))
    f.append(arrow(ox, oy + h, ox, oy - 10, color=INK, sw=1.6))
    f.append(text(ox + w, oy + h + 24, "опорні періоди", size=13, color=INK, anchor="end"))
    f.append(text(ox - 8, oy - 4, "помилка фази", size=13, color=INK, anchor="end"))
    # нульова лінія
    base = oy + h
    f.append(line(ox, base, ox + w, base, color=MUTED, sw=1.0, dash="2 4"))

    # пилка: лінійне накопичення до порога, скидання вниз
    period = 92.0     # умовний крок пилки в пікселях
    top = oy + 16     # вершина пилки
    amp = base - top
    x = ox
    pts = []
    # будуємо кілька зубців
    while x < ox + w:
        seg = min(period, ox + w - x)
        # від base до top по похилій
        for k in range(0, int(seg) + 1, 2):
            xx = x + k
            yy = base - amp * (k / period)
            pts.append("%.1f,%.1f" % (xx, yy))
        x += period
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts), POS))
    # вертикальні скидання (пунктир) на кожному переповненні
    x = ox + period
    first = True
    while x < ox + w + 1:
        f.append(line(x, top, x, base, color=POS, sw=1.4, dash="4 3"))
        if first:
            f.append(text(x + 6, top + 14, "переповнення → ділимо на N+1",
                          size=11.5, color=POS, anchor="start", italic=True))
            first = False
        x += period

    # підпис до похилої ділянки
    f.append(text(ox + period * 0.45, base - amp * 0.32,
                  "ділимо на N: фаза забігає → помилка повзе вгору",
                  size=11.5, color=MUTED, anchor="start", italic=True))

    render(os.path.join(IMG, "sawtooth-error.svg"), W, H, *f,
           title="Пилка фазової помилки — джерело дробових спурів")


# ── 3. Формування шуму: спури → розмазаний шум, виштовхнутий угору ────────────
def fig_noise_shaping():
    W, H = 770, 360
    f = []
    ox, oy, w, h = 70, 80, 620, 210
    # осі
    f.append(arrow(ox, oy + h, ox + w + 14, oy + h, color=INK, sw=1.6))
    f.append(arrow(ox, oy + h, ox, oy - 10, color=INK, sw=1.6))
    f.append(text(ox + w, oy + h + 24, "відступ від несучої →", size=13, color=INK, anchor="end"))
    f.append(text(ox - 8, oy - 4, "шум", size=13, color=INK, anchor="end"))
    f.append(text(ox + 4, oy + h + 24, "несуча", size=12, color=INK, anchor="start"))
    base = oy + h

    # смуга фільтра петлі (зелена зона зрізання) — праворуч
    fcut = ox + w * 0.5
    f.append(rect(fcut, oy - 6, ox + w - fcut, h + 6, fill="#eafaf0",
                  stroke="none", sw=0, rx=0))
    f.append(line(fcut, oy - 6, fcut, base, color=FIELD, sw=1.6, dash="6 5"))
    f.append(text(fcut + (ox + w - fcut) / 2, oy + 6,
                  "смуга фільтра петлі", size=12, color=FIELD))
    f.append(text(fcut + (ox + w - fcut) / 2, oy + 22,
                  "тут шум зрізається", size=11, color=FIELD))

    # простий акумулятор: гострі спури близько до несучої (червоні піки)
    spur_x = [ox + 60, ox + 150, ox + 240]
    spur_h = [110, 78, 56]
    for sx, sh in zip(spur_x, spur_h):
        f.append(line(sx, base, sx, base - sh, color=POS, sw=3.0))
        f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
                 % (sx - 4, base - sh + 8, sx + 4, base - sh + 8, sx, base - sh, POS))
    f.append(mtext(ox + 150, base - 132, ["простий акумулятор:", "гострі спури"],
                   size=12, color=POS))

    # дельта-сигма: шум розмазаний і задертий угору (синій схил)
    pts = []
    for k in range(0, w + 1, 3):
        xfrac = k / w
        # низько біля несучої, круто росте з частотою (формування шуму ~ f^2)
        val = 0.10 + 0.85 * xfrac ** 2
        yy = base - val * (h - 30)
        pts.append("%.1f,%.1f" % (ox + k, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join(pts), NEG))
    f.append(text(ox + w * 0.30, base - 0.10 * (h - 30) - 10,
                  "дельта-сигма: шум виштовхнутий угору →", size=12,
                  color=NEG, anchor="start"))

    render(os.path.join(IMG, "noise-shaping.svg"), W, H, *f,
           title="Формування шуму: спури розмазують і відсувають під ніж фільтра")


# ── 4. Модуль NTF 1-го порядку: |1−z⁻¹| = 2·sin(πf/f_оп) ─────────────────────
def fig_ntf_magnitude():
    W, H = 760, 350
    f = []
    ox, oy, w, h = 80, 70, 600, 210
    base = oy + h
    # осі
    f.append(arrow(ox, base, ox + w + 14, base, color=INK, sw=1.6))
    f.append(arrow(ox, base, ox, oy - 12, color=INK, sw=1.6))
    f.append(text(ox + w, base + 24, "відступ від несучої →  (0 … f_оп/2)",
                  size=13, color=INK, anchor="end"))
    f.append(text(ox - 8, oy - 2, "|NTF|", size=13, color=INK, anchor="end"))
    f.append(text(ox + 2, base + 24, "несуча", size=11.5, color=INK, anchor="start"))
    # рівень |NTF| = 2 (горизонтальний орієнтир)
    y2 = base - (2.0 / 2.2) * h
    f.append(line(ox, y2, ox + w, y2, color=MUTED, sw=1.0, dash="3 4"))
    f.append(text(ox - 8, y2 + 4, "2", size=12, color=MUTED, anchor="end"))
    f.append(text(ox - 8, base + 4, "0", size=12, color=MUTED, anchor="end"))
    # крива 2·sin(π·x/1), x від 0 до 0.5 (нормовано до f_оп)
    pts = []
    for k in range(0, w + 1, 3):
        xfrac = 0.5 * k / w           # 0 … 0.5
        val = 2.0 * math.sin(math.pi * xfrac)
        yy = base - (val / 2.2) * h
        pts.append("%.1f,%.1f" % (ox + k, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join(pts), NEG))
    # підписи країв
    f.append(text(ox + 70, base - 18, "падає до 0 коло несучої:",
                  size=12, color=FIELD, anchor="start"))
    f.append(text(ox + 70, base - 3, "шум душиться",
                  size=12, color=FIELD, anchor="start"))
    f.append(text(ox + w - 8, y2 - 12, "росте до 2 вгорі:",
                  size=12, color=POS, anchor="end"))
    f.append(text(ox + w - 8, y2 + 3, "сюди шум переселяється",
                  size=12, color=POS, anchor="end"))
    render(os.path.join(IMG, "ntf-magnitude.svg"), W, H, *f,
           title="Передавальна функція шуму 1-го порядку: гасне внизу, росте вгору")


# ── 5. Нахили фазового шуму за порядком ΔΣ: 0 / 20 / 40 дБ/декаду ─────────────
def fig_order_slopes():
    W, H = 780, 380
    f = []
    ox, oy, w, h = 80, 80, 600, 230
    base = oy + h
    # осі (лог-частота умовна, лог-шум умовний)
    f.append(arrow(ox, base, ox + w + 14, base, color=INK, sw=1.6))
    f.append(arrow(ox, base, ox, oy - 12, color=INK, sw=1.6))
    f.append(text(ox + w, base + 24, "відступ від несучої (лог) →",
                  size=13, color=INK, anchor="end"))
    f.append(text(ox - 8, oy - 2, "фазовий шум (дБн/Гц)", size=12.5, color=INK, anchor="end"))

    # смуга фільтра петлі: зелена зона праворуч
    fcut = ox + w * 0.62
    f.append(rect(fcut, oy - 6, ox + w - fcut, h + 6, fill="#eafaf0",
                  stroke="none", sw=0, rx=0))
    f.append(line(fcut, oy - 6, fcut, base, color=FIELD, sw=1.6, dash="6 5"))
    f.append(text(fcut + (ox + w - fcut) / 2, oy + 8,
                  "смуга фільтра петлі", size=12, color=FIELD))
    f.append(text(fcut + (ox + w - fcut) / 2, oy + 24,
                  "тут хвіст зрізається", size=11, color=FIELD))

    # три прямі через СПІЛЬНУ точку перетину: нахили 0, 1, 2 (×20 дБ/дек).
    # Масштаб підібрано так, щоб жодна пряма не впиралась у рамку (без обрізів).
    xc = 0.50                      # пивот по горизонталі (центр)
    yc = base - 0.46 * h           # пивот по вертикалі
    pivot_y = yc
    span = 0.40 * h                # піврозмах найкрутішої прямої від пивота
    f.append(circle(ox + xc * w, yc, 3.2, fill=INK, stroke=INK, sw=1))
    def lineplot(slope_units, col, lab, laby):
        # slope_units: 0,1,2 — кратність 20 дБ/декаду; нормуємо до найкрутішої (=2)
        pts = []
        for k in range(0, w + 1, 4):
            xf = k / w
            val = (slope_units / 2.0) * span * (xf - xc) / xc
            yy = yc - val
            pts.append("%.1f,%.1f" % (ox + k, yy))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(pts), col))
        f.append(text(ox + w - 8, laby, lab, size=12, color=col, anchor="end", bold=True))
    # L=1 плаский, L=2 +20, L=3 +40 (масштаб умовний — показати відносну крутість)
    lineplot(0.0, MUTED, "L=1: 0 дБ/дек (плаский)", yc - 8)
    lineplot(1.0, NEG,   "L=2: +20 дБ/дек",          yc - span * 0.52 - 6)
    lineplot(2.0, POS,   "L=3: +40 дБ/дек",          yc - span - 6)
    f.append(text(ox + xc * w + 8, yc - 6, "спільна точка", size=10.5,
                  color=MUTED, anchor="start", italic=True))
    # підпис коло несучої
    f.append(text(ox + 6, base - 8, "коло несучої вищий порядок ТИХІШИЙ →",
                  size=11.5, color=INK, anchor="start", italic=True))

    render(os.path.join(IMG, "order-slopes.svg"), W, H, *f,
           title="Порядок ΔΣ обертає спектр: тихіше внизу — крутіше вгору")


# ── 6. Естафета способів проти спура: 1969 → 1976 → 1983 → 1990 (для hist) ────
def fig_history_timeline():
    W, H = 900, 380
    f = []
    ax = 70                    # ліва межа осі
    axr = W - 40               # права межа осі
    ty = 96                    # рівень осі часу
    f.append(line(ax, ty, axr, ty, color=INK, sw=2.2))
    f.append(arrow(axr - 2, ty, axr + 2, ty, color=INK, sw=2.2))
    f.append(text(ax - 6, ty + 5, "рік", size=12, color=MUTED, anchor="end"))

    # чотири віхи: (рік, x-частка, верхній підпис-хто, нижній блок-що, колір блоку, fill)
    cols = [
        ("1969", 0.06, "Джиллетт", ["ДИФАЗА", "спур ВІДНІМАЮТЬ", "аналогово (ЦАП)"], FIELD, "#eafaf0"),
        ("1976", 0.34, "Таніс",    ["цифровий дільник", "(зглитування тактів)", "без аналог. милиці"], MUTED, FILL),
        ("1983", 0.62, "Вітлі / Rockwell", ["ДРОЖ", "спур РОЗМАЗУЮТЬ", "випадковістю"], POS, "#fdecea"),
        ("1990", 0.90, "Міллер і Конлі", ["ДЕЛЬТА-СИГМА", "шум ВИШТОВХУЮТЬ", "угору, під фільтр"], NEG, "#eaf0fd"),
    ]
    span = axr - ax
    for yr, xf, who, what, col, fill in cols:
        x = ax + 30 + xf * (span - 60)
        # вузол на осі + рік
        f.append(circle(x, ty, 6, fill=col, stroke=INK, sw=1.6))
        f.append(text(x, ty - 16, yr, size=15, color=INK, anchor="middle", bold=True))
        # хто (над блоком)
        f.append(text(x, ty + 34, who, size=12.5, color=col, anchor="middle", bold=True))
        # що (рамка під написи — fitbox у задану ширину, текст не вилазить)
        bw, bh = 188, 78
        f.append(fitbox(x - bw / 2, ty + 44, bw, bh, "\n".join(what),
                        size=13, stroke=col, sw=2.0, fill=fill, bold=False))

    # нижня смужка-мораль
    f.append(fitbox(ax, H - 52, axr - ax, 38,
                    "спур — це форма: відняти · розмазати · зсунути; найрозумніше — зсунути туди, де не чути",
                    size=12.5, stroke=INK, sw=1.4, fill="#f7f7f7", bold=True))

    render(os.path.join(IMG, "history-timeline.svg"), W, H, *f,
           title="Естафета проти спура: чотири кроки дробового синтезу")


if __name__ == "__main__":
    fig_frac_loop()
    fig_sawtooth()
    fig_noise_shaping()
    fig_ntf_magnitude()
    fig_order_slopes()
    fig_history_timeline()
    print("OK figs ->", IMG)
