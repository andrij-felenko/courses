# -*- coding: utf-8 -*-
"""Фігури до теми «Рядкова заслінка».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Рядкова проти глобальної: послідовно vs водночас ──────────────────────
def fig_rolling_vs_global():
    W, H = 820, 410
    f = [text(W / 2, 26, "Дві заслінки: коли пікселі ловлять світло", size=16, bold=True)]

    rows = 9
    rh = 26
    gx, gy = 70, 70          # глобальна — ліворуч
    rx, ry = 470, 70         # рядкова — праворуч
    panel_w = 230

    # ── ГЛОБАЛЬНА: усі рядки в одному вікні часу ──
    f.append(text(gx + panel_w / 2, gy - 14, "ГЛОБАЛЬНА (global)", size=12.5,
                  color=FIELD, bold=True))
    for i in range(rows):
        yy = gy + i * rh
        f.append(rect(gx, yy, panel_w, rh - 4, fill="#eafaef", stroke=FIELD, sw=1.4))
    f.append(text(gx + panel_w / 2, gy + rows * rh + 18,
                  "усі пікселі — в одну мить", size=10.5, color="#15803d"))
    f.append(text(gx + panel_w / 2, gy + rows * rh + 34,
                  "рух «заморожено», форма ціла", size=10, color=MUTED))

    # ── РЯДКОВА: вікно з'їжджає по рядках ──
    f.append(text(rx + panel_w / 2, ry - 14, "РЯДКОВА (rolling)", size=12.5,
                  color=POS, bold=True))
    for i in range(rows):
        yy = ry + i * rh
        f.append(rect(rx, yy, panel_w, rh - 4, fill="white", stroke="#e5e7eb", sw=1))
        off = i * (panel_w * 0.5 / rows)
        f.append(rect(rx + off, yy, panel_w * 0.5, rh - 4, fill="#fdecea",
                      stroke=POS, sw=1.4))
    f.append(arrow(rx - 22, ry + 4, rx - 22, ry + rows * rh - 6, color=INK, sw=2))
    f.append(text(rx - 32, ry + rows * rh / 2, "час", size=10, color=INK, anchor="end"))
    f.append(text(rx + panel_w / 2, ry + rows * rh + 18,
                  "рядок за рядком, згори вниз", size=10.5, color=POS))
    f.append(text(rx + panel_w / 2, ry + rows * rh + 34,
                  "верх і низ кадру — у різні миті", size=10, color=MUTED))

    f.append(text(W / 2, H - 12,
                  "Глобальна знімає весь кадр одночасно; рядкова веде вікно експозиції зверху вниз — звідси всі її артефакти.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "rolling-vs-global.svg"), W, H, *f)


# ── 2. Час зчитування → зсув між верхнім і нижнім рядком ─────────────────────
def fig_readout_shift():
    W, H = 800, 430
    f = [text(W / 2, 26, "Час зчитування кадру → зсув між першим і останнім рядком",
              size=15.5, bold=True)]

    # шкала часу зліва: рядки зчитуються один за одним
    ax, ay = 90, 80
    n = 10
    rh = 28
    for i in range(n):
        yy = ay + i * rh
        t = i * (30.0 / (n - 1))
        f.append(rect(ax, yy, 150, rh - 5, fill="white", stroke="#d1d5db", sw=1))
        f.append(text(ax + 75, yy + rh / 2, "рядок %d" % (i * 120),
                      size=9.5, color=MUTED))
        f.append(text(ax - 12, yy + rh / 2, "%.0f мс" % t, size=10,
                      color=INK, anchor="end"))
    f.append(text(ax + 75, ay - 14, "1080 рядків", size=11, bold=True))
    f.append(arrow(ax - 52, ay + 2, ax - 52, ay + n * rh - 8, color=POS, sw=2))
    f.append(text(ax - 64, ay + n * rh / 2, "час", size=10, color=POS, anchor="end"))

    # точки: рухомий об'єкт (червона цятка) у момент зчитування кожного рядка
    ox = 330
    f.append(text(ox + 170, ay - 14, "де була точка, коли цей рядок зчитувався",
                  size=10.5, bold=True))
    for i in range(n):
        yy = ay + i * rh + (rh - 5) / 2
        # точка зсувається вправо з часом (об'єкт летить)
        px = ox + 30 + i * 30
        f.append(circle(px, yy, 6, fill=POS, stroke="white", sw=1.4))
        if i == 0:
            f.append(text(px, yy - 12, "t=0", size=9, color=POS))
        if i == n - 1:
            f.append(text(px, yy - 12, "t=30 мс", size=9, color=POS))
    # пунктир, що з'єднує точки — нахилена «траєкторія в кадрі»
    pts = " ".join("%.0f,%.1f" % (ox + 30 + i * 30, ay + i * rh + (rh - 5) / 2)
                   for i in range(n))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6" '
             'stroke-dasharray="5,4"/>' % (pts, POS))

    # підсумкова формула
    f.append(rect(ax - 64, ay + n * rh + 18, 690, 56, fill="#f4f4f5",
                  stroke=INK, sw=1.4, rx=10))
    f.append(text(W / 2, ay + n * rh + 42,
                  "зсув низу = (швидкість у кадрі) × (час зчитування)",
                  size=12.5, bold=True))
    f.append(text(W / 2, ay + n * rh + 62,
                  "що довше зчитується кадр і що швидший рух — то більший перекіс",
                  size=10.5, color=MUTED))

    f.append(text(W / 2, H - 10,
                  "Перший рядок знято на 30 мс раніше за останній — за цей час швидка ціль встигає поїхати вбік.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "readout-shift.svg"), W, H, *f)


# ── 3. Геометричні спотворення: нахил, желе, гвинт ───────────────────────────
def fig_distortions():
    W, H = 840, 380
    f = [text(W / 2, 26, "Три обличчя рядкової заслінки на швидкому русі", size=16, bold=True)]

    cw, cy, ch = 250, 70, 230
    x0, gap = 30, 20

    # картка 1 — нахил вертикалі
    x = x0
    f.append(rect(x, cy, cw, ch, fill="white", stroke=POS, sw=1.8, rx=12))
    f.append(text(x + cw / 2, cy + 24, "НАХИЛ (skew)", size=12.5, color=POS, bold=True))
    # пряма щогла (примара) і нахилена (як знято)
    f.append(line(x + 70, cy + 50, x + 70, cy + 180, color="#cbd5e1", sw=6))
    f.append(text(x + 70, cy + 200, "насправді", size=9, color=MUTED))
    f.append('<polyline points="%d,%d %d,%d" fill="none" stroke="%s" stroke-width="6"/>'
             % (x + 150, cy + 50, x + 195, cy + 180, POS))
    f.append(text(x + 178, cy + 200, "у кадрі", size=9, color=POS))
    f.append(mtext(x + cw / 2, cy + ch - 20,
                   ["вертикаль «лягає» вбік:", "низ знято пізніше за верх"],
                   size=9.5, color=MUTED, lh=1.35))

    # картка 2 — желе (jello / wobble)
    x = x0 + cw + gap
    f.append(rect(x, cy, cw, ch, fill="white", stroke="#d98a00", sw=1.8, rx=12))
    f.append(text(x + cw / 2, cy + 24, "ЖЕЛЕ (jello)", size=12.5, color="#b06b00", bold=True))
    # хвиляста вертикаль — тремтіння камери міняє напрям зсуву по рядках
    import math
    pts = []
    for k in range(31):
        yy = cy + 48 + k * 4.2
        xx = x + cw / 2 + 22 * math.sin(k / 3.3)
        pts.append("%.1f,%.1f" % (xx, yy))
    f.append('<polyline points="%s" fill="none" stroke="#d98a00" stroke-width="5"/>'
             % " ".join(pts))
    f.append(mtext(x + cw / 2, cy + ch - 20,
                   ["вібрація хитає напрям зсуву —", "кадр «тремтить, як желе»"],
                   size=9.5, color=MUTED, lh=1.35))

    # картка 3 — гвинт/пропелер
    x = x0 + 2 * (cw + gap)
    f.append(rect(x, cy, cw, ch, fill="white", stroke=NEG, sw=1.8, rx=12))
    f.append(text(x + cw / 2, cy + 24, "ГВИНТ (propeller)", size=12.5, color=NEG, bold=True))
    ccx, ccy = x + cw / 2, cy + 120
    # вигнуті «банани» замість прямих лопатей
    for ang in (0, 120, 240):
        a = math.radians(ang)
        bpts = []
        for tt in range(11):
            r = 12 + tt * 6
            aa = a + tt * 0.10        # лопать «закручується»
            bpts.append("%.1f,%.1f" % (ccx + r * math.cos(aa), ccy + r * math.sin(aa)))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="5" '
                 'stroke-linecap="round"/>' % (" ".join(bpts), NEG))
    f.append(circle(ccx, ccy, 7, fill=INK, stroke="white", sw=1.5))
    f.append(mtext(x + cw / 2, cy + ch - 20,
                   ["лопать обертається швидше,", "ніж зчитується кадр — банани"],
                   size=9.5, color=MUTED, lh=1.35))

    f.append(text(W / 2, H - 10,
                  "Усе це — не дефект сенсора, а наслідок того, що рядки зняті в різні миті, поки об'єкт рухався.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "distortions.svg"), W, H, *f)


# ── 4. Часткова смуга: спалах / ШІМ-світло ───────────────────────────────────
def fig_partial_band():
    W, H = 800, 400
    f = [text(W / 2, 26, "Спалах і ШІМ-світло: чому лягає смуга", size=16, bold=True),
         text(W / 2, 46, "світло було коротким — його зловили лише ті рядки, що саме зчитувалися",
              size=11.5, color=MUTED)]

    # ЛІВОРУЧ: короткий спалах → яскрава смуга посередині
    px, py, pw, ph = 70, 86, 250, 230
    f.append(text(px + pw / 2, py - 12, "КОРОТКИЙ СПАЛАХ", size=12, color=POS, bold=True))
    rows = 14
    rh = ph / rows
    lit = {6, 7, 8}     # рядки, що «застали» спалах
    for i in range(rows):
        yy = py + i * rh
        col = "#fde68a" if i in lit else "#1f2937"
        f.append('<rect x="%d" y="%.1f" width="%d" height="%.1f" fill="%s"/>'
                 % (px, yy, pw, rh + 0.5, col))
    f.append(rect(px, py, pw, ph, fill="none", stroke=INK, sw=1.6))
    f.append(text(px + pw + 12, py + 7 * rh, "← світла смуга", size=10,
                  color="#b45309", anchor="start", bold=True))
    f.append(text(px + pw / 2, py + ph + 18, "решта кадру лишилась темною",
                  size=9.5, color=MUTED))

    # ПРАВОРУЧ: ШІМ-світло → кілька смуг (рядки чергуються ввімк/вимк)
    qx = 470
    f.append(text(qx + pw / 2, py - 12, "ШІМ-СВІТЛО (миготить)", size=12,
                  color="#b06b00", bold=True))
    for i in range(rows):
        yy = py + i * rh
        on = (i // 2) % 2 == 0       # смуги ввімк/вимк
        col = "#fde68a" if on else "#374151"
        f.append('<rect x="%d" y="%.1f" width="%d" height="%.1f" fill="%s"/>'
                 % (qx, yy, pw, rh + 0.5, col))
    f.append(rect(qx, py, pw, ph, fill="none", stroke=INK, sw=1.6))
    f.append(text(qx + pw / 2, py + ph + 18, "поки рядки зчитуються, світло то ввімк, то вимк",
                  size=9.5, color=MUTED))

    f.append(text(W / 2, H - 10,
                  "Глобальна заслінка зловила б цілий спалах усім кадром — у рядкової кожен рядок «бачить» світло у свою мить.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "partial-band.svg"), W, H, *f)


# ── 5. Чому CMOS зазвичай рядковий: піксель 4T vs 5T+ зі сховком ──────────────
def fig_pixel_cost():
    W, H = 820, 400
    f = [text(W / 2, 26, "Ціна глобальності: пам'ять у кожному пікселі", size=16, bold=True)]

    bw, by, bh = 320, 76, 230

    # ── РЯДКОВИЙ піксель: простий, без сховку ──
    x = 60
    f.append(rect(x, by, bw, bh, fill="#eafaef", stroke=FIELD, sw=1.8, rx=12))
    f.append(text(x + bw / 2, by + 26, "РЯДКОВИЙ піксель (≈4T)", size=12.5,
                  color="#15803d", bold=True))
    # фотодіод велике, трохи логіки
    f.append(circle(x + 80, by + 120, 42, fill="#bbf7d0", stroke=FIELD, sw=2))
    f.append(text(x + 80, by + 124, "фотодіод", size=10, color="#15803d"))
    f.append(text(x + 80, by + 168, "велика площа на світло", size=9, color=MUTED))
    f.append(rect(x + 175, by + 84, 120, 30, fill="white", stroke=MUTED, sw=1.2, rx=5))
    f.append(text(x + 235, by + 103, "трохи логіки", size=9.5, color=MUTED))
    f.append(mtext(x + 235, by + 138,
                   ["зчитали рядок —", "одразу віддали назовні.", "Сховку нема."],
                   size=9.5, color="#15803d", lh=1.4))
    f.append(text(x + bw / 2, by + bh - 12, "дешево, дрібний піксель, більше світла",
                  size=9.5, color="#15803d", bold=True))

    # ── ГЛОБАЛЬНИЙ піксель: + комірка пам'яті на КОЖЕН піксель ──
    x = 440
    f.append(rect(x, by, bw, bh, fill="#fff5e6", stroke="#d98a00", sw=1.8, rx=12))
    f.append(text(x + bw / 2, by + 26, "ГЛОБАЛЬНИЙ піксель (5T+ зі сховком)",
                  size=11.5, color="#b06b00", bold=True))
    # менший фотодіод
    f.append(circle(x + 72, by + 118, 30, fill="#fde68a", stroke="#d98a00", sw=2))
    f.append(text(x + 72, by + 122, "фотодіод", size=9.5, color="#b06b00"))
    f.append(text(x + 72, by + 162, "менший", size=9, color=MUTED))
    f.append(text(x + 72, by + 176, "(місце з'їла пам'ять)", size=9, color=MUTED))
    # комірка пам'яті
    f.append(rect(x + 140, by + 86, 150, 40, fill="#fef3c7", stroke=POS, sw=1.8, rx=6))
    f.append(text(x + 215, by + 110, "комірка пам'яті", size=10, color=POS, bold=True))
    f.append(mtext(x + 215, by + 144,
                   ["тримає заряд, поки", "кадр зчитується рядок", "за рядком назовні"],
                   size=9.5, color="#b06b00", lh=1.4))
    f.append(text(x + bw / 2, by + bh - 12, "дорожче, складніший піксель, менше світла",
                  size=9.5, color="#b06b00", bold=True))

    f.append(text(W / 2, H - 26,
                  "Рядковому пікселю сховок не потрібен — він віддає заряд одразу, тож виходить простішим і дешевшим.",
                  size=11, color=MUTED, italic=True))
    f.append(text(W / 2, H - 10,
                  "Глобальному треба «запам'ятати» весь кадр в одну мить — а пам'ять на кожен піксель коштує площі й грошей.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "pixel-cost.svg"), W, H, *f)


if __name__ == "__main__":
    fig_rolling_vs_global()
    fig_readout_shift()
    fig_distortions()
    fig_partial_band()
    fig_pixel_cost()
    print("OK: rolling-vs-global, readout-shift, distortions, partial-band, pixel-cost")
