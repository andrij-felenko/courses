# -*- coding: utf-8 -*-
"""Фігури до теми «Діелектрики конденсаторів».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Чому все вирішує діелектрик: стабільна vs «гумова» ε ──────────────────
def fig_why_dielectric():
    W, H = 720, 360
    f = [text(W / 2, 28, "Той самий заряд — різний діелектрик → різна поведінка", size=16, bold=True)]

    def cell(x0, label, eps, fill, note1, note2):
        # дві обкладки
        f.append(rect(x0 + 40, 70, 16, 150, fill="#dfe6ee", stroke=LINE, sw=2))
        f.append(rect(x0 + 230, 70, 16, 150, fill="#dfe6ee", stroke=LINE, sw=2))
        # діелектрик між ними
        f.append(rect(x0 + 56, 70, 174, 150, fill=fill, stroke=MUTED, sw=1.4, rx=3))
        f.append(text(x0 + 143, 150, eps, size=15, bold=True, color=INK))
        # заряди на обкладках (однакові)
        for k in range(3):
            f.append(plus(x0 + 48, 92 + k * 50, 9))
            f.append(minus(x0 + 238, 92 + k * 50, 9))
        f.append(text(x0 + 143, 58, label, size=13, bold=True, color=INK))
        b, _, _ = textbox(x0 + 143, 252, note1, size=12, fill="#eef6ef", stroke=FIELD)
        f.append(b)
        f.append(text(x0 + 143, 300, note2, size=11, color=MUTED))

    cell(20, "Стабільна ε", "εᵣ ≈ 2  (плівка)", "#f4f6f8",
         "ємність скромна,\nале незмінна", "температура, напруга — байдуже")
    f.append(line(W / 2, 70, W / 2, 285, color="#d6dde6", sw=1.2, dash="4,5"))
    cell(380, "Велика «гумова» ε", "εᵣ ~ 1000 (кераміка кл.2)", "#fbeee6",
         "ємності багато,\nале вона провисає", "гуляє з t° і напругою")
    render(os.path.join(IMG, "why-dielectric.svg"), W, H, *f)


# ── 2. Код EIA класу 2: три позиції ─────────────────────────────────────────
def fig_eia_code():
    W, H = 720, 380
    f = [text(W / 2, 28, "Код кераміки класу 2 читається по три позиції", size=16, bold=True)]

    # великі символи X 7 R
    chars = [("X", "#fdecea", POS), ("7", "#eef6ef", FIELD), ("R", "#eaf0fd", NEG)]
    cx0 = 150
    for i, (ch, fl, st) in enumerate(chars):
        cx = cx0 + i * 140
        f.append(rect(cx - 42, 50, 84, 84, fill=fl, stroke=st, sw=2.2, rx=10))
        f.append(text(cx, 108, ch, size=46, bold=True, color=st))

    # підписи-пояснення під кожним символом
    notes = [
        ("нижня t°", "X = −55 °C\nY = −30 °C\nZ = +10 °C"),
        ("верхня t°", "5 = +85 °C\n6 = +105 °C\n7 = +125 °C"),
        ("розкид ємності", "R = ±15%\nV = +22/−82%"),
    ]
    for i, (cap, body) in enumerate(notes):
        cx = cx0 + i * 140
        f.append(line(cx, 134, cx, 158, color=MUTED, sw=1.4))
        f.append(text(cx, 174, cap, size=12, bold=True, color=INK))
        b, _, _ = textbox(cx, 222, body, size=12, fill=FILL, stroke=LINE)
        f.append(b)

    # підсумкові приклади
    b1, w1, _ = textbox(220, 320, "X7R  =  −55…+125 °C,  ±15%", size=13,
                        fill="#eef6ef", stroke=FIELD, bold=True)
    f.append(b1)
    b2, w2, _ = textbox(510, 320, "Y5V  =  −30…+85 °C,  +22/−82%", size=13,
                        fill="#fbeee6", stroke=POS, bold=True)
    f.append(b2)
    render(os.path.join(IMG, "eia-code.svg"), W, H, *f)


# ── 3. DC-bias: падіння ємності під напругою ────────────────────────────────
def fig_dc_bias():
    W, H = 720, 400
    f = [text(W / 2, 28, "Реальна ємність класу 2 тане під постійною напругою", size=16, bold=True)]

    # осі
    ox, oy = 90, 320          # початок координат
    ax_w, ax_h = 540, 240
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))          # X
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))          # Y
    f.append(text(ox + ax_w / 2, oy + 42, "постійна напруга на конденсаторі  (частка від номінальної)",
                  size=12, color=INK))
    f.append(text(ox - 60, oy - ax_h / 2, "ємність", size=12, color=INK, anchor="middle"))
    f.append(text(ox - 60, oy - ax_h / 2 + 16, "(% номіналу)", size=11, color=MUTED, anchor="middle"))

    # позначки по осях
    for frac, lab in [(0.0, "0"), (0.25, "¼"), (0.5, "½"), (0.75, "¾"), (1.0, "1")]:
        x = ox + frac * ax_w
        f.append(line(x, oy, x, oy + 5, color=INK, sw=1.4))
        f.append(text(x, oy + 20, lab, size=11, color=MUTED))
    for pv, lab in [(0, "0"), (50, "50"), (100, "100")]:
        y = oy - pv / 100.0 * ax_h
        f.append(line(ox - 5, y, ox, y, color=INK, sw=1.4))
        f.append(text(ox - 20, y + 4, lab, size=11, color=MUTED))

    def curve(points, color, sw=2.6, dash=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        pts = " ".join("%.1f,%.1f" % (ox + fx * ax_w, oy - fy / 100.0 * ax_h) for fx, fy in points)
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (pts, color, sw, d))

    # C0G / плівка — рівно 100%
    curve([(0, 100), (1.0, 100)], FIELD, sw=2.4, dash="6,5")
    # X7R великий корпус — м'яке провисання
    curve([(0, 100), (0.25, 92), (0.5, 78), (0.75, 62), (1.0, 50)], NEG)
    # X5R дрібний корпус — різке провисання
    curve([(0, 100), (0.25, 80), (0.5, 55), (0.75, 38), (1.0, 25)], POS)

    # підписи кривих
    f.append(text(ox + ax_w - 6, oy - 100 / 100.0 * ax_h - 8, "C0G / плівка", size=12,
                  color=FIELD, anchor="end", bold=True))
    f.append(text(ox + ax_w - 6, oy - 50 / 100.0 * ax_h + 16, "X7R (більший корпус)", size=12,
                  color=NEG, anchor="end", bold=True))
    f.append(text(ox + ax_w - 6, oy - 25 / 100.0 * ax_h + 16, "X5R (дрібний корпус)", size=12,
                  color=POS, anchor="end", bold=True))
    render(os.path.join(IMG, "dc-bias.svg"), W, H, *f)


# ── 4. Плівкові: рулон, поліестер vs поліпропілен ───────────────────────────
def fig_film():
    W, H = 720, 360
    f = [text(W / 2, 28, "Плівковий конденсатор: рулон плівки-діелектрика з обкладками", size=16, bold=True)]

    # рулон — концентричні «витки»
    cx, cy = 175, 195
    for i, r in enumerate(range(78, 14, -12)):
        col = "#dfe6ee" if i % 2 == 0 else "#f4d9c4"
        f.append(circle(cx, cy, r, fill=col, stroke=MUTED, sw=1.2))
    f.append(circle(cx, cy, 12, fill=BG, stroke=LINE, sw=1.4))
    # виводи
    f.append(line(cx - 30, cy + 78, cx - 30, cy + 120, color=LINE, sw=2.4))
    f.append(line(cx + 30, cy + 78, cx + 30, cy + 120, color=LINE, sw=2.4))
    f.append(text(cx, cy + 138, "шари: плівка-діелектрик + метал-обкладка", size=11, color=MUTED))

    # дві колонки порівняння
    bx = 380
    b1, _, _ = textbox(bx + 150, 110,
                       "Поліестер (ПЕТ)\nдешевший, дрібніший\nпомірні втрати",
                       size=12.5, fill="#eef2f8", stroke=NEG)
    f.append(b1)
    b2, _, _ = textbox(bx + 150, 235,
                       "Поліпропілен (PP)\nнайменші втрати (tan δ<0.001)\nстабільний, тримає імпульси",
                       size=12.5, fill="#eef6ef", stroke=FIELD)
    f.append(b2)
    b3, _, _ = textbox(bx + 150, 320,
                       "обидва: неполярні · малий витік · добре тримають напругу",
                       size=11.5, fill=FILL, stroke=LINE)
    f.append(b3)
    render(os.path.join(IMG, "film.svg"), W, H, *f)


# ── 5. Алюмінієвий електроліт: тонкий оксид на травленій фользі ──────────────
def fig_electrolytic():
    W, H = 720, 360
    f = [text(W / 2, 28, "Алюмінієвий електроліт: нанометровий оксид як діелектрик", size=16, bold=True)]

    # ліворуч — розріз фольги з зубцями (травлення) і тонким оксидом
    fx, fy = 60, 80
    f.append(text(fx + 160, 64, "розріз: травлена фольга + оксид", size=12, bold=True))
    # тіло фольги
    f.append(rect(fx, fy, 320, 70, fill="#cfd8e2", stroke=LINE, sw=1.6))
    # зубці травлення (велика площа)
    teeth = []
    n = 16
    for i in range(n):
        x = fx + 6 + i * (308.0 / n)
        teeth.append("%.1f,%.1f" % (x, fy + 70))
        teeth.append("%.1f,%.1f" % (x + 308.0 / n / 2, fy + 70 + 26))
    pts = "%.1f,%.1f " % (fx, fy + 70) + " ".join(teeth) + " %.1f,%.1f" % (fx + 320, fy + 70)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (pts, FIELD))
    f.append(text(fx + 160, fy + 128, "травлення → величезна площа в малому об'ємі", size=11, color=MUTED))
    # винесена тонка лінія оксиду
    f.append(line(fx + 320, fy + 35, fx + 360, fy + 35, color=POS, sw=1.4, dash="3,3"))
    b, _, _ = textbox(fx + 250, fy + 178, "оксид — діелектрик завтовшки нанометри → велика ємність",
                      size=11.5, fill="#fbeee6", stroke=POS)
    f.append(b)

    # праворуч — «банка» з полярністю
    bx, by = 470, 92
    f.append(rect(bx, by, 120, 150, fill="#e9edf2", stroke=LINE, sw=2, rx=10))
    f.append(rect(bx + 16, by, 22, 150, fill="#c9d2dc", stroke=MUTED, sw=1.2))   # смуга «−»
    f.append(text(bx + 27, by + 84, "−", size=26, bold=True, color=NEG))
    f.append(text(bx + 84, by + 40, "+", size=22, bold=True, color=POS))
    f.append(line(bx + 40, by + 150, bx + 40, by + 184, color=LINE, sw=2.4))
    f.append(line(bx + 90, by + 150, bx + 90, by + 184, color=LINE, sw=2.4))
    b2, _, _ = textbox(bx + 60, by + 214, "полярний:\nсмуга «−» обов'язкова", size=11.5,
                       fill=FILL, stroke=LINE)
    f.append(b2)
    render(os.path.join(IMG, "electrolytic.svg"), W, H, *f)


# ── 6. Дрібний шрифт: втрати, старіння, допуск ──────────────────────────────
def fig_loss_aging():
    W, H = 720, 330
    f = [text(W / 2, 28, "Заховане за номіналом: втрати · старіння · допуск", size=16, bold=True)]
    col_w, x0, top = 216, 18, 56

    # колонка 1 — втрати (стовпчики tan δ)
    c1 = x0 + col_w / 2
    f.append(text(c1, top, "Втрати (tan δ)", size=13, bold=True))
    bars = [("PP/кл.1", 18, FIELD), ("кл.2", 70, "#e08a3c"), ("електроліт", 120, POS)]
    bx = x0 + 16
    base = 250
    for lab, hh, col in bars:
        f.append(rect(bx, base - hh, 44, hh, fill=col, stroke=LINE, sw=1.2))
        f.append(text(bx + 22, base + 16, lab, size=10, color=MUTED))
        bx += 64
    f.append(text(c1, base + 40, "частина енергії → тепло", size=10.5, color=MUTED))

    # колонка 2 — старіння (спадна крива)
    c2 = x0 + col_w + col_w / 2
    f.append(text(c2, top, "Старіння кл.2", size=13, bold=True))
    axx, axy = x0 + col_w + 28, 240
    f.append(line(axx, axy, axx + 150, axy, color=INK, sw=1.5))
    f.append(line(axx, axy, axx, axy - 110, color=INK, sw=1.5))
    pts = " ".join("%.1f,%.1f" % (axx + t, axy - 95 + (95 * t / 150.0) * 0.62)
                   for t in range(0, 151, 10))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (pts, "#e08a3c"))
    f.append(text(axx - 6, axy - 100, "C", size=11, color=MUTED, anchor="end"))
    f.append(text(axx + 150, axy + 16, "час (роки)", size=10, color=MUTED, anchor="end"))
    f.append(text(c2, axy + 40, "ємність повзе вниз; нагрів скидає", size=10, color=MUTED))

    # колонка 3 — допуск (смуги розкиду)
    c3 = x0 + 2 * col_w + col_w / 2
    f.append(text(c3, top, "Допуск", size=13, bold=True))
    rows = [("кл.1 / плівка", 14, FIELD), ("кл.2", 40, "#e08a3c"), ("електроліт", 78, POS)]
    ry = 96
    cxr = c3
    for lab, half, col in rows:
        f.append(line(cxr - half, ry, cxr + half, ry, color=col, sw=6))
        f.append(circle(cxr, ry, 3.5, fill=BG, stroke=INK, sw=1.4))
        f.append(text(cxr, ry - 12, lab, size=10.5, color=INK))
        ry += 58
    f.append(text(c3, 250, "справжня ємність гуляє\nнавколо напису", size=10.5, color=MUTED))
    f.append(mtext(c3, 250, ["справжня ємність гуляє", "навколо напису"], size=10.5, color=MUTED))
    render(os.path.join(IMG, "loss-aging.svg"), W, H, *f)


# ── 7. Який діелектрик під яку задачу ───────────────────────────────────────
def fig_choose_dielectric():
    W, H = 720, 370
    f = [text(W / 2, 28, "Задача тягне наперед свою властивість діелектрика", size=16, bold=True)]

    cards = [
        ("Розв'язка живлення", "багато ємності в малому корпусі;\nточність байдужа",
         "кераміка кл.2\n(X7R / X5R)", NEG, "#eef2f8"),
        ("Фільтр / зріз частоти", "потрібна точна, стала ємність",
         "C0G/NP0\nабо плівка", FIELD, "#eef6ef"),
        ("Таймінг / частота", "максимальна сталість у часі й t°",
         "клас 1 (C0G)\nабо плівка", FIELD, "#eef6ef"),
        ("Накопичення енергії", "багато мкФ дешево;\nкомпактно й стабільно",
         "електроліт\nабо тантал", POS, "#fbeee6"),
    ]
    cw, gap = 160, 16
    x = (W - (4 * cw + 3 * gap)) / 2
    top = 56
    for title, need, pick, col, fl in cards:
        f.append(rect(x, top, cw, 250, fill=fl, stroke=col, sw=1.8, rx=10))
        f.append(text(x + cw / 2, top + 26, title, size=12.5, bold=True, color=INK))
        f.append(line(x + 14, top + 38, x + cw - 14, top + 38, color=col, sw=1.2))
        f.append(mtext(x + cw / 2, top + 66, need, size=11, color=MUTED, lh=1.25))
        f.append(text(x + cw / 2, top + 150, "→", size=22, bold=True, color=col))
        b, _, _ = textbox(x + cw / 2, top + 205, pick, size=12, fill=BG, stroke=col, bold=True)
        f.append(b)
        x += cw + gap
    f.append(text(W / 2, top + 286,
                  "один номінал «10 мкФ» на різних діелектриках — придатний до різних задач",
                  size=12, color=INK, italic=True))
    render(os.path.join(IMG, "choose-dielectric.svg"), W, H, *f)


if __name__ == "__main__":
    fig_why_dielectric()
    fig_eia_code()
    fig_dc_bias()
    fig_film()
    fig_electrolytic()
    fig_loss_aging()
    fig_choose_dielectric()
    print("OK: 7 figures ->", IMG)
