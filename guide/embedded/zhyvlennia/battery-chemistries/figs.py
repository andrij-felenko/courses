# -*- coding: utf-8 -*-
"""Фігури до теми «Хімії батарей» та її історичної вставки.
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# Сталі кольори чотирьох хімій (узгоджено між фігурами теми)
C_PB  = NEG       # свинець — синій
C_NI  = FIELD     # нікель (NiMH) — зелений
C_LI  = POS       # Li-ion — червоний/гарячий
C_LFP = "#caa24a" # LiFePO4 — золотавий


# ── 1. Напруга елемента за хімією ────────────────────────────────────────────
def fig_voltage():
    """Стовпчики номінальної напруги одного елемента з робочим діапазоном.
    Видно головний наслідок: що вища напруга, то менше комірок послідовно."""
    W, H = 760, 420
    f = [text(W / 2, 30, "Напруга елемента: скільки комірок на потрібні вольти", size=16, bold=True)]
    bx, by = 110, 320          # початок осей
    top = 70
    vmax = 4.5
    sc = (by - top) / vmax     # px на вольт
    # вісь Y
    f.append(line(bx, by, bx, top, color=INK, sw=1.6))
    for v in range(0, 5):
        yy = by - v * sc
        f.append(line(bx - 5, yy, bx, yy, color=INK, sw=1))
        f.append(text(bx - 10, yy + 4, str(v), size=10, color=MUTED, anchor="end"))
    f.append(text(bx - 10, top - 6, "В", size=11, bold=True, anchor="end"))
    # стовпчики: (назва, номінал, low, high, колір, діапазон-підпис)
    cells = [("Свинець", 2.0, 1.75, 2.4, C_PB, "1.75–2.4 В"),
             ("NiMH",    1.2, 1.0,  1.4, C_NI, "1.0–1.4 В"),
             ("Li-ion",  3.7, 3.0,  4.2, C_LI, "3.0–4.2 В"),
             ("LiFePO4", 3.2, 2.5,  3.65, C_LFP, "2.5–3.65 В")]
    n = len(cells)
    span = W - bx - 60
    step = span / n
    bw = 52
    for i, (nm, nom, lo, hi, col, rng) in enumerate(cells):
        cx = bx + step * (i + 0.5)
        yhi, ylo = by - hi * sc, by - lo * sc
        # робочий діапазон — світла рамка
        f.append(rect(cx - bw / 2, yhi, bw, ylo - yhi, fill=col, stroke=col, sw=1.6))
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" fill="%s" fill-opacity="0.15"/>'
                 % (cx - bw / 2, yhi, bw, ylo - yhi, col))
        # лінія номіналу
        ynom = by - nom * sc
        f.append(line(cx - bw / 2, ynom, cx + bw / 2, ynom, color=col, sw=2.6))
        f.append(text(cx + bw / 2 + 8, ynom + 4, "%.1f В" % nom, size=10, color=col, bold=True, anchor="start"))
        f.append(text(cx, by + 22, nm, size=11, color=col, bold=True))
        f.append(text(cx, by + 38, rng, size=9, color=MUTED))
    # підсумкова смуга
    f.append(fitbox(bx - 40, by + 56, span + 80, 26,
                    "12 В — це 6 свинцевих елементів, 3–4 літієвих чи 10 NiMH послідовно.",
                    size=10, fill="#eafaf0", stroke=FIELD, sw=1.3))
    render(os.path.join(IMG, "voltage.svg"), W, H, *f)


# ── 2. Питома енергія за хімією ──────────────────────────────────────────────
def fig_energy():
    """Горизонтальні смуги Вт·год/кг. Розкид уп'ятеро — літій проти свинцю."""
    W, H = 760, 360
    f = [text(W / 2, 30, "Питома енергія: ват-години на кілограм", size=16, bold=True)]
    bx = 150
    top = 70
    emax = 230
    span = W - bx - 130
    sc = span / emax
    rows = [("Свинець", 40, C_PB),
            ("NiMH", 90, C_NI),
            ("LiFePO4", 120, C_LFP),
            ("Li-ion/LiPo", 200, C_LI)]
    rh = 44
    for i, (nm, e, col) in enumerate(rows):
        cy = top + i * rh + 16
        f.append(text(bx - 12, cy + 6, nm, size=11, color=col, bold=True, anchor="end"))
        f.append(rect(bx, cy - 8, e * sc, 28, fill=col, stroke=col, sw=1.4))
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="28" rx="6" fill="%s" fill-opacity="0.18"/>'
                 % (bx, cy - 8, e * sc, col))
        f.append(text(bx + e * sc + 10, cy + 6, "%d Вт·год/кг" % e, size=11, color=col, bold=True, anchor="start"))
    f.append(line(bx, top + 4, bx, top + len(rows) * rh + 6, color=INK, sw=1.4))
    f.append(fitbox(bx - 110, top + len(rows) * rh + 22, span + 240, 26,
                    "Та сама енергія важить уп'ятеро менше на літії, ніж на свинці.",
                    size=10, fill="#eafaf0", stroke=FIELD, sw=1.3))
    render(os.path.join(IMG, "energy.svg"), W, H, *f)


# ── 3. Криві розряду ─────────────────────────────────────────────────────────
def fig_discharge():
    """Похила (Li-ion, свинець) проти пласкої (LiFePO4, NiMH).
    Пласке плато «бреше» про залишок: 80% і 20% по напрузі майже однакові."""
    W, H = 760, 400
    f = [text(W / 2, 30, "Форма кривої розряду: чи видно заряд по напрузі", size=16, bold=True)]
    ox, oy = 90, 320          # початок координат
    pw, ph = W - ox - 40, oy - 70
    f.append(line(ox, oy, ox + pw, oy, color=INK, sw=1.5))   # X
    f.append(line(ox, oy, ox, oy - ph, color=INK, sw=1.5))   # Y
    f.append(text(ox + pw / 2, oy + 34, "віддано заряду →", size=10, color=MUTED))
    f.append(text(ox - 14, oy - ph - 6, "В", size=10, color=MUTED, anchor="end"))
    f.append(text(ox - 14, oy - ph + 8, "100%", size=9, color=MUTED, anchor="end"))
    f.append(text(ox - 14, oy - 2, "0", size=9, color=MUTED, anchor="end"))

    def poly(pts, col, dash=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        p = " ".join("%.1f,%.1f" % (ox + px * pw, oy - py * ph) for px, py in pts)
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
                'stroke-linejoin="round" stroke-linecap="round"%s/>' % (p, col, d))

    # похила: Li-ion (плавне сповзання), свинець (схоже, нижче масштабом — те саме сімейство)
    f.append(poly([(0, 0.96), (0.15, 0.86), (0.5, 0.66), (0.8, 0.5), (0.95, 0.34), (1.0, 0.12)], C_LI))
    f.append(poly([(0, 0.86), (0.2, 0.74), (0.6, 0.54), (0.85, 0.4), (0.97, 0.22), (1.0, 0.06)], C_PB, dash="6 4"))
    # пласка: LiFePO4 і NiMH — довге плато, різкий обвал у кінці
    f.append(poly([(0, 0.74), (0.08, 0.66), (0.85, 0.62), (0.93, 0.5), (0.98, 0.2), (1.0, 0.05)], C_LFP))
    f.append(poly([(0, 0.62), (0.08, 0.55), (0.85, 0.52), (0.92, 0.42), (0.98, 0.16), (1.0, 0.04)], C_NI, dash="6 4"))

    leg = [("Li-ion (похила)", C_LI, False), ("свинець (похила)", C_PB, True),
           ("LiFePO4 (плато)", C_LFP, False), ("NiMH (плато)", C_NI, True)]
    lx, ly = ox + pw - 188, oy - ph + 6
    for i, (nm, col, dash) in enumerate(leg):
        yy = ly + i * 18
        f.append(line(lx, yy, lx + 26, yy, color=col, sw=2.6, dash="5 3" if dash else None))
        f.append(text(lx + 32, yy + 4, nm, size=10, color=col, bold=True, anchor="start"))
    f.append(fitbox(ox, oy + 44, pw, 24,
                    "Пласке плато «бреше» про заряд: 80% і 20% залишку по напрузі майже однакові.",
                    size=9.5, fill="#eafaf0", stroke=FIELD, sw=1.3))
    render(os.path.join(IMG, "discharge.svg"), W, H, *f)


# ── 4. Ресурс циклів ─────────────────────────────────────────────────────────
def fig_cycles():
    """Скільки циклів до 80% ємності. LFP живе у рази довше — тому дешевший «за цикл»."""
    W, H = 760, 360
    f = [text(W / 2, 30, "Ресурс циклів до 80% ємності", size=16, bold=True)]
    bx = 150
    top = 70
    cmax = 3000
    span = W - bx - 150
    sc = span / cmax
    rows = [("Свинець", 300, C_PB),
            ("NiMH", 500, C_NI),
            ("Li-ion", 800, C_LI),
            ("LiFePO4", 3000, C_LFP)]
    rh = 44
    for i, (nm, c, col) in enumerate(rows):
        cy = top + i * rh + 16
        f.append(text(bx - 12, cy + 6, nm, size=11, color=col, bold=True, anchor="end"))
        f.append(rect(bx, cy - 8, c * sc, 28, fill=col, stroke=col, sw=1.4))
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="28" rx="6" fill="%s" fill-opacity="0.18"/>'
                 % (bx, cy - 8, c * sc, col))
        lbl = "%d+ циклів" % c if c >= 3000 else "%d циклів" % c
        f.append(text(bx + c * sc + 10, cy + 6, lbl, size=11, color=col, bold=True, anchor="start"))
    f.append(line(bx, top + 4, bx, top + len(rows) * rh + 6, color=INK, sw=1.4))
    f.append(fitbox(bx - 110, top + len(rows) * rh + 22, span + 260, 26,
                    "Дорожчий за штуку LFP часто найдешевший у перерахунку на один цикл.",
                    size=10, fill="#eafaf0", stroke=FIELD, sw=1.3))
    render(os.path.join(IMG, "cycles.svg"), W, H, *f)


# ── 5. Температурні вікна заряду й розряду ───────────────────────────────────
def fig_temp():
    """Вузьке вікно ЗАРЯДУ проти ширшого вікна розряду.
    Головне: літій не заряджати нижче 0°C."""
    W, H = 760, 380
    f = [text(W / 2, 30, "Температура: вікно заряду вужче за вікно розряду", size=16, bold=True)]
    ax = 150
    tmin, tmax = -40, 60
    span = W - ax - 70
    sc = span / (tmax - tmin)

    def tx(t):
        return ax + (t - tmin) * sc
    # шкала
    base = 300
    f.append(line(ax, base + 16, ax + span, base + 16, color=INK, sw=1.4))
    for t in range(-40, 61, 20):
        f.append(line(tx(t), base + 12, tx(t), base + 20, color=MUTED, sw=1))
        f.append(text(tx(t), base + 34, "%d" % t, size=9, color=MUTED))
    f.append(text(ax + span / 2, base + 50, "°C", size=10, color=MUTED))
    f.append(line(tx(0), top_y := 64, tx(0), base + 16, color=C_LI, sw=1.2, dash="4 4"))
    f.append(text(tx(0) + 4, 76, "0°C — нижче літій не заряджати", size=9.5, color=C_LI, bold=True, anchor="start"))

    # (назва, заряд lo, заряд hi, розряд lo, розряд hi, колір)
    rows = [("Li-ion/LiFePO4", 0, 45, -20, 60, C_LI),
            ("NiMH", -10, 45, -20, 50, C_NI),
            ("Свинець", -15, 45, -30, 50, C_PB)]
    top = 96
    rh = 60
    for i, (nm, clo, chi, dlo, dhi, col) in enumerate(rows):
        cy = top + i * rh
        f.append(text(ax - 12, cy + 14, nm, size=10.5, color=col, bold=True, anchor="end"))
        # розряд — ширша сіра смуга
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="16" rx="5" fill="%s" fill-opacity="0.25"/>'
                 % (tx(dlo), cy, (dhi - dlo) * sc, MUTED))
        f.append(text(tx(dhi) + 6, cy + 13, "розряд", size=9, color=MUTED, anchor="start"))
        # заряд — вузька кольорова
        f.append(rect(tx(clo), cy + 20, (chi - clo) * sc, 14, fill=col, stroke=col, sw=1.2))
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="14" rx="5" fill="%s" fill-opacity="0.25"/>'
                 % (tx(clo), cy + 20, (chi - clo) * sc, col))
        f.append(text(tx(chi) + 6, cy + 31, "заряд", size=9, color=col, bold=True, anchor="start"))
    render(os.path.join(IMG, "temp.svg"), W, H, *f)


# ── 6. Карта вибору хімії під задачу ─────────────────────────────────────────
def fig_decision():
    """Чотири квадранти: під яку задачу яка хімія й чим платить."""
    W, H = 760, 420
    f = [text(W / 2, 30, "Карта вибору: яка хімія під яку роботу", size=16, bold=True)]
    cards = [
        (C_LI,  "Li-ion / LiPo", "вага — усе:\nносимий, дрон, мобільний", "ціна: обов'язковий захист"),
        (C_LFP, "LiFePO4", "роки служби й спокій:\nсонячна, стаціонарна", "ціна: пласка крива, оцінка заряду"),
        (C_NI,  "NiMH", "дешево й просто,\nготові «пальчики»", "ціна: мало енергії"),
        (C_PB,  "Свинець", "об'ємна енергія за гроші,\nпусковий струм", "ціна: важко, боїться розряду"),
    ]
    cw, ch = 320, 140
    gx, gy = 30, 30
    x0, y0 = (W - 2 * cw - gx) / 2, 56
    for i, (col, title, use, cost) in enumerate(cards):
        cx = x0 + (i % 2) * (cw + gx)
        cy = y0 + (i // 2) * (ch + gy)
        f.append(rect(cx, cy, cw, ch, fill="#fff", stroke=col, sw=2))
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="34" rx="6" fill="%s" fill-opacity="0.15"/>'
                 % (cx, cy, cw, col))
        f.append(text(cx + cw / 2, cy + 23, title, size=14, color=col, bold=True))
        f.append(mtext(cx + cw / 2, cy + 58, use, size=11, color=INK))
        f.append(line(cx + 16, cy + ch - 30, cx + cw - 16, cy + ch - 30, color=col, sw=0.8, dash="3 3"))
        f.append(text(cx + cw / 2, cy + ch - 12, cost, size=9.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "decision.svg"), W, H, *f)


# ── 7. Хронологія перезаряджуваних батарей (вставка) ─────────────────────────
def fig_timeline():
    """Від первинного стовпа Вольти (1800) до доледієвих акумуляторів.
    Жодна хімія — не витвір однієї руки."""
    W, H = 820, 320
    f = [text(W / 2, 30, "Два століття перезаряджуваних батарей", size=16, bold=True)]
    ax, ay = 60, 170
    span = W - 2 * ax
    f.append(line(ax, ay, ax + span, ay, color=INK, sw=2))
    f.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>'
             % (ax + span, ay, ax + span + 14, ay, INK))
    events = [
        (1800, "Стовп Вольти", "первинний, одноразовий", C_PB, -1),
        (1859, "Свинець Планте", "уперше «оживає»", C_PB, 1),
        (1881, "Пластини Фора", "придатний до серії", C_PB, -1),
        (1899, "Юнгнер", "лужні: NiCd, NiFe", C_NI, 1),
        (1901, "Едісон (NiFe)", "запатентував пізніше", C_NI, -1),
    ]
    t0, t1 = 1790, 1915
    for yr, nm, note, col, side in events:
        x = ax + (yr - t0) / (t1 - t0) * span
        f.append(circle(x, ay, 6, fill=col, stroke=col, sw=1.5))
        f.append(text(x, ay + (28 if side > 0 else -34), str(yr), size=11, color=INK, bold=True))
        yb = ay + (46 if side > 0 else -76)
        f.append(fitbox(x - 78, yb, 156, 40, nm + "\n" + note, size=9.5,
                        fill="#fff", stroke=col, sw=1.4))
        f.append(line(x, ay, x, yb + (0 if side > 0 else 40), color=col, sw=0.9, dash="3 3"))
    render(os.path.join(IMG, "timeline.svg"), W, H, *f)


# ── 8. Пріоритет: Юнгнер проти Едісона (вставка) ─────────────────────────────
def fig_priority():
    """NiFe запатентував першим Юнгнер (1899); суд виграв грошима Едісон (1901).
    Першість — за датою в реєстрі; «винайшов Едісон» — міф."""
    W, H = 760, 340
    f = [text(W / 2, 30, "Хто винайшов нікель-залізний акумулятор", size=16, bold=True)]
    # дві колонки
    jx, ex = 200, 560
    cy = 110
    f.append(rect(jx - 150, cy - 26, 300, 150, fill="#fff", stroke=C_NI, sw=2))
    f.append(text(jx, cy, "Вальдемар Юнгнер", size=14, color=C_NI, bold=True))
    f.append(text(jx, cy + 24, "патент NiFe — 1899", size=12, color=INK))
    f.append(text(jx, cy + 46, "першість за датою", size=11, color=FIELD, bold=True))
    f.append(mtext(jx, cy + 74, "мала шведська фірма,\nхронічний брак коштів", size=10, color=MUTED))

    f.append(rect(ex - 150, cy - 26, 300, 150, fill="#fff", stroke=C_LI, sw=2))
    f.append(text(ex, cy, "Томас Едісон", size=14, color=C_LI, bold=True))
    f.append(text(ex, cy + 24, "патент NiFe — 1901", size=12, color=INK))
    f.append(text(ex, cy + 46, "на ~2 роки пізніше", size=11, color=POS, bold=True))
    f.append(mtext(ex, cy + 74, "капітал, юристи, слава —\nвиграв суд грошима", size=10, color=MUTED))

    f.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>'
             % (jx + 152, cy + 40, ex - 152, cy + 40, MUTED))
    f.append(fitbox(W / 2 - 280, 270, 560, 44,
                    "У світ пішла назва «батарея Едісона». Едісон реально вдосконалив NiFe,\nале «винайшов першим» — історичний міф.",
                    size=10.5, fill="#fdf3f2", stroke=POS, sw=1.4))
    render(os.path.join(IMG, "priority.svg"), W, H, *f)


# ── 9. Три доледієві хімії — і що з них вийшло (вставка) ──────────────────────
def fig_chemistries():
    """Три старі хімії, кожна у своїй ніші донині."""
    W, H = 820, 320
    f = [text(W / 2, 30, "Три доледієві хімії та їхні ніші", size=16, bold=True)]
    cards = [
        (C_PB, "Свинцево-кислотний", "Планте, 1859", "важкий, дешевий,\nвеликий струм", "автостартери, ДБЖ"),
        (C_NI, "Нікель-кадмій", "Юнгнер", "міцний, морозостійкий;\nкадмій + «ефект пам'яті»", "фірма дожила як Saft"),
        (C_LFP, "Нікель-залізний", "Юнгнер; впр. Едісон", "майже «вічний», грубий,\nнизький ККД", "нішевий резерв"),
    ]
    cw = 244
    gx = 18
    x0 = (W - 3 * cw - 2 * gx) / 2
    cy = 60
    ch = 210
    for i, (col, title, who, body, niche) in enumerate(cards):
        cx = x0 + i * (cw + gx)
        f.append(rect(cx, cy, cw, ch, fill="#fff", stroke=col, sw=2))
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="50" rx="6" fill="%s" fill-opacity="0.15"/>'
                 % (cx, cy, cw, col))
        f.append(text(cx + cw / 2, cy + 22, title, size=12.5, color=col, bold=True))
        f.append(text(cx + cw / 2, cy + 41, who, size=10, color=MUTED, italic=True))
        f.append(mtext(cx + cw / 2, cy + 84, body, size=10.5, color=INK))
        f.append(line(cx + 16, cy + ch - 40, cx + cw - 16, cy + ch - 40, color=col, sw=0.8, dash="3 3"))
        f.append(mtext(cx + cw / 2, cy + ch - 22, niche, size=10, color=col, bold=True))
    render(os.path.join(IMG, "chemistries.svg"), W, H, *f)


# ── 10. Форма кривої: твердий розчин проти двофазного переходу (детальна) ─────
def fig_phase_plateau():
    """Мікроскопічна причина похилої проти пласкої кривої.
    Ліворуч — solid solution (плавна зміна складу → похила напруга за Нернстом);
    праворуч — двофазний перехід (склади фаз сталі, рухається межа → плато)."""
    W, H = 820, 400
    f = [text(W / 2, 28, "Чому одні криві похилі, а інші — пласке плато", size=16, bold=True)]

    # ── ліва панель: твердий розчин ──
    def panel( x0, title, sub, col):
        pw, ph = 320, 150
        oy = 210
        out = [text(x0 + pw / 2, 58, title, size=13, color=col, bold=True),
               text(x0 + pw / 2, 76, sub, size=10, color=MUTED, italic=True)]
        # осі невеликого графіка напруги
        gx, gy, gw, gh = x0 + 40, oy, pw - 70, 100
        out.append(line(gx, gy, gx + gw, gy, color=INK, sw=1.3))
        out.append(line(gx, gy, gx, gy - gh, color=INK, sw=1.3))
        out.append(text(gx - 8, gy - gh + 4, "В", size=9, color=MUTED, anchor="end"))
        out.append(text(gx + gw / 2, gy + 18, "віддано →", size=9, color=MUTED))
        return out, gx, gy, gw, gh

    lp, lgx, lgy, lgw, lgh = panel(30, "Твердий розчин (Li-ion)",
                                   "одна фаза, склад плавно біднішає", C_LI)
    f += lp
    # похила крива
    pts = [(0.0, 0.92), (0.3, 0.74), (0.6, 0.58), (0.85, 0.42), (1.0, 0.16)]
    p = " ".join("%.1f,%.1f" % (lgx + a * lgw, lgy - b * lgh) for a, b in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round"/>' % (p, C_LI))
    # схематичний кристал: точки літію рідшають
    cxk, cyk = 30 + 165, 130
    for r in range(2):
        for c in range(6):
            filled = (r * 6 + c) < 8
            xx, yy = cxk - 60 + c * 22, cyk + r * 20
            f.append(circle(xx, yy, 5, fill=(C_LI if filled else "#fff"), stroke=C_LI, sw=1.3))
    f.append(text(cxk, cyk + 56, "склад міняється → напруга сповзає", size=9.5, color=C_LI))

    rp, rgx, rgy, rgw, rgh = panel(470, "Двофазний перехід (LiFePO4)",
                                   "дві фази сталого складу, рух межі", C_LFP)
    f += rp
    # пласке плато + різкий обвал
    pts2 = [(0.0, 0.78), (0.08, 0.70), (0.85, 0.68), (0.93, 0.5), (0.98, 0.2), (1.0, 0.05)]
    p2 = " ".join("%.1f,%.1f" % (rgx + a * rgw, rgy - b * rgh) for a, b in pts2)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round"/>' % (p2, C_LFP))
    # дві фази з рухомою межею
    bx0, by0, bw0, bh0 = 470 + 40, 108, 230, 40
    f.append(rect(bx0, by0, bw0, bh0, fill="#fff", stroke=C_LFP, sw=1.4))
    boundary = bx0 + bw0 * 0.55
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="4" fill="%s" fill-opacity="0.18"/>'
             % (bx0, by0, boundary - bx0, bh0, C_LFP))
    f.append(line(boundary, by0, boundary, by0 + bh0, color=C_LFP, sw=2.2))
    f.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>'
             % (boundary + 4, by0 + bh0 / 2, boundary + 34, by0 + bh0 / 2, MUTED))
    f.append(text(bx0 + (boundary - bx0) / 2, by0 + bh0 / 2 + 4, "багата", size=9, color=C_LFP, bold=True))
    f.append(text(boundary + (bx0 + bw0 - boundary) / 2 + 8, by0 + bh0 / 2 + 4, "бідна", size=9, color=MUTED))
    f.append(text(470 + 165, by0 + bh0 + 16, "склад фаз сталий → напруга стоїть", size=9.5, color=C_LFP))

    f.append(fitbox(30, 340, 760, 30,
                    "Напруга за Нернстом залежить від складу фази: плавна зміна → похила крива; "
                    "стала (рух межі) → пласке плато.",
                    size=10, fill="#eafaf0", stroke=FIELD, sw=1.3))
    render(os.path.join(IMG, "phase-plateau.svg"), W, H, *f)


# ── 11. Холодний заряд літію: осадження дендритів (детальна) ──────────────────
def fig_cold_plating():
    """Чому заряд літію заборонено нижче 0°C: на морозі дифузія вглиб гальмується
    сильніше за прибуття іонів → метал осідає дендритами до сепаратора."""
    W, H = 820, 380
    f = [text(W / 2, 28, "Чому холодний заряд літію руйнує комірку", size=16, bold=True)]

    def anode(x0, title, col, cold):
        aw, ah = 300, 210
        ay = 70
        out = [text(x0 + aw / 2, 56, title, size=13, color=col, bold=True)]
        # анод (сірий брусок ліворуч) + сепаратор (пунктир праворуч)
        ex, ew = x0 + 20, 70
        out.append(rect(ex, ay, ew, ah, fill="#eceff3", stroke=MUTED, sw=1.4))
        out.append(text(ex + ew / 2, ay + ah + 16, "анод (графіт)", size=9, color=MUTED))
        sep = x0 + aw - 40
        out.append(line(sep, ay, sep, ay + ah, color=NEG, sw=2, dash="5 4"))
        out.append(text(sep, ay - 6, "сепаратор", size=9, color=NEG))
        # іони летять зліва направо (з електроліту в анод)
        for k in range(4):
            yy = ay + 30 + k * 45
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.6" marker-end="url(#arrow)"/>'
                       % (sep - 20, yy, ex + ew + 14, yy, C_LI))
            out.append(text(sep - 8, yy - 4, "Li⁺", size=9, color=C_LI, anchor="start"))
        return out, ex, ew, ay, ah, sep

    # ── тепло: іон заходить углиб ──
    wp, wex, wew, way, wah, wsep = anode(20, "Тепло: іон заходить углиб", FIELD, False)
    f += wp
    # стрілки вглиб анода (інтеркаляція) — усередину бруска
    for k in range(3):
        yy = way + 45 + k * 55
        f.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.6" marker-end="url(#arrow)"/>'
                 % (wex + wew - 6, yy, wex + 14, yy, FIELD))
    f.append(fitbox(20 + 20, way + wah + 26, 260, 26,
                    "дифузія встигає: літій у ґратці",
                    size=9.5, fill="#eafaf0", stroke=FIELD, sw=1.2))

    # ── холод: метал осідає дендритами ──
    cp, cex, cew, cay, cah, csep = anode(500, "Мороз: метал осідає на поверхні", POS, True)
    f += cp
    # дендрити ростуть від поверхні анода праворуч до сепаратора
    surf = cex + cew
    import math
    for k in range(3):
        y0 = cay + 40 + k * 60
        x = surf
        y = y0
        pts = [(x, y)]
        for step in range(6):
            x += 18
            y += (12 if step % 2 else -10)
            pts.append((x, y))
        pth = " ".join("%.1f,%.1f" % (px, py) for px, py in pts)
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
                 'stroke-linejoin="round"/>' % (pth, POS))
        f.append(circle(pts[-1][0], pts[-1][1], 3.5, fill=POS, stroke=POS, sw=1))
    f.append(text(surf + 60, cay + 8, "дендрити → до сепаратора", size=9.5, color=POS, bold=True))
    f.append(fitbox(500 + 20, cay + cah + 26, 260, 26,
                    "дифузія відстає: незворотна втрата + ризик КЗ",
                    size=9.5, fill="#fdf3f2", stroke=POS, sw=1.2))
    render(os.path.join(IMG, "cold-plating.svg"), W, H, *f)


# ══════════════════════════════════════════════════════════════════════════════
# Фігури до математичної вставки «Нернст і вільна енергія Гіббса» (math-nernst-gibbs)
# ══════════════════════════════════════════════════════════════════════════════

# ── M1. Ланцюг виведення: ΔG → E = −ΔG/nF → Нернст ───────────────────────────
def fig_nernst_chain():
    """Три сходинки думки: рушій реакції (ΔG) → напруга (заряд, що падає з висоти)
    → плавання напруги за концентрацією (член RT/nF·lnQ). Видно, ЗВІДКИ береться
    рівняння Нернста, а не як його постулат."""
    W, H = 780, 470
    f = [text(W / 2, 30, "Звідки береться рівняння Нернста: три сходинки", size=16, bold=True)]

    # три вертикальні картки-сходинки
    bx, top, bw, bh, gap = 40, 60, 226, 300, 22
    cols = [FIELD, C_LI, NEG]
    titles = ["1. Рушій реакції", "2. Напруга = рушій / заряд", "3. Рушій пливе з умовами"]
    for i in range(3):
        x = bx + i * (bw + gap)
        f.append(rect(x, top, bw, bh, fill="#fbfcfd", stroke=cols[i], sw=1.8, rx=10))
        f.append(fitbox(x + 10, top + 10, bw - 20, 26, titles[i], size=12,
                        fill=cols[i], stroke=cols[i], sw=0, color="#ffffff", bold=True))

    # картка 1: ΔG — вільна енергія
    x0 = bx
    f.append(text(x0 + bw / 2, top + 74, "Скільки корисної роботи", size=10.5, color=MUTED))
    f.append(text(x0 + bw / 2, top + 90, "віддасть реакція?", size=10.5, color=MUTED))
    f.append(fitbox(x0 + 18, top + 108, bw - 36, 34, "ΔG < 0 → реакція йде\nсама, віддає роботу",
                    size=10.5, fill="#eafaf0", stroke=FIELD, sw=1.2))
    f.append(text(x0 + bw / 2, top + 172, "ΔG = ΔH − T·ΔS", size=13, color=INK, bold=True))
    f.append(fitbox(x0 + 18, top + 190, bw - 36, 46,
                    "тепло реакції ΔH\nмінус T × безлад ΔS\n(звідси температура!)",
                    size=9.5, fill=FILL, stroke=MUTED, sw=1))
    f.append(text(x0 + bw / 2, top + 262, "енергія на моль", size=9.5, color=MUTED, italic=True))
    f.append(text(x0 + bw / 2, top + 278, "(Дж/моль)", size=9.5, color=MUTED, italic=True))

    # стрілка 1→2
    f.append(arrow(bx + bw + 3, top + bh / 2, bx + bw + gap - 3, top + bh / 2, color=INK, sw=2))
    # картка 2: E = −ΔG/nF
    x1 = bx + bw + gap
    f.append(text(x1 + bw / 2, top + 74, "Ту роботу несуть", size=10.5, color=MUTED))
    f.append(text(x1 + bw / 2, top + 90, "n електронів заряду nF", size=10.5, color=MUTED))
    f.append(text(x1 + bw / 2, top + 138, "E = − ΔG / (n·F)", size=15, color=C_LI, bold=True))
    f.append(fitbox(x1 + 18, top + 158, bw - 36, 44,
                    "робота / заряд = напруга\n(як висота, з якої\nпадає заряд)",
                    size=9.5, fill="#fdecea", stroke=C_LI, sw=1.1))
    f.append(text(x1 + bw / 2, top + 232, "n — електронів на реакцію", size=9.5, color=MUTED))
    f.append(text(x1 + bw / 2, top + 248, "F = 96485 Кл/моль", size=9.5, color=MUTED))
    f.append(text(x1 + bw / 2, top + 278, "вольти (В)", size=9.5, color=MUTED, italic=True))

    # стрілка 2→3
    f.append(arrow(x1 + bw + 3, top + bh / 2, x1 + bw + gap - 3, top + bh / 2, color=INK, sw=2))
    # картка 3: Нернст
    x2 = x1 + bw + gap
    f.append(text(x2 + bw / 2, top + 74, "ΔG залежить від того,", size=10.5, color=MUTED))
    f.append(text(x2 + bw / 2, top + 90, "скільки вже віддано:", size=10.5, color=MUTED))
    f.append(fitbox(x2 + 16, top + 106, bw - 32, 26, "ΔG = ΔG° + RT·ln Q",
                    size=11, fill=FILL, stroke=MUTED, sw=1))
    f.append(text(x2 + bw / 2, top + 156, "поділили на −nF:", size=9.5, color=MUTED, italic=True))
    f.append(fitbox(x2 + 14, top + 172, bw - 28, 30, "E = E° − (RT/nF)·ln Q",
                    size=11.5, fill="#eaf0fd", stroke=NEG, sw=1.4, color=NEG, bold=True))
    f.append(text(x2 + bw / 2, top + 234, "Q = [продукти]/[реагенти]", size=9.5, color=MUTED))
    f.append(text(x2 + bw / 2, top + 250, "розряд → Q росте → E падає", size=9.5, color=NEG))
    f.append(text(x2 + bw / 2, top + 278, "рівняння Нернста", size=9.5, color=NEG, italic=True, bold=True))

    f.append(fitbox(bx, top + bh + 20, 3 * bw + 2 * gap, 28,
                    "Напруга — не задане число, а вільна енергія реакції на одиницю перенесеного заряду.",
                    size=10.5, fill="#eafaf0", stroke=FIELD, sw=1.3))
    render(os.path.join(IMG, "nernst-chain.svg"), W, H, *f)


# ── M2. Нахил Нернста: ~59 мВ на декаду, звідки 2.303·RT/F ────────────────────
def fig_nernst_slope():
    """Пряма E проти log10(Q): кожна декада Q зсуває напругу рівно на 2.303·RT/nF.
    Показано, ЗВІДКИ 25.7 мВ (RT/F) і як множник ln10=2.303 робить із нього ~59 мВ."""
    W, H = 780, 430
    f = [text(W / 2, 30, "Нахил Нернста: 59 мВ на кожну декаду Q", size=16, bold=True)]

    ox, oy = 300, 330
    pw, ph = 430, 250
    # осі
    f.append(line(ox, oy, ox + pw, oy, color=INK, sw=1.6))
    f.append(line(ox, oy, ox, oy - ph, color=INK, sw=1.6))
    f.append(text(ox + pw / 2, oy + 40, "log₁₀ Q  (кожен крок — ×10 у складі)", size=10.5, color=MUTED))
    # вертикальний підпис осі Y
    f.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="10.5" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">E − E° (мВ)</text>'
             % (ox - 46, oy - ph / 2, FONT, MUTED, ox - 46, oy - ph / 2))

    # пряма з нахилом −59 мВ/декаду: беремо log10 Q від −2 до +2, E від +2·59 до −2·59
    slope_px = ph / 4.0            # 4 декади по всій висоті (від −2 до +2)
    step_x = pw / 4.0
    def px(logq): return ox + (logq + 2) * step_x
    def py(mv):   return oy - ph / 2 - mv * (slope_px / 59.0)
    # лінія
    f.append(line(px(-2), py(2 * 59), px(2), py(-2 * 59), color=NEG, sw=2.8))
    # горизонтальна нульова лінія E=E°
    f.append(line(ox, oy - ph / 2, ox + pw, oy - ph / 2, color=MUTED, sw=1, dash="4,4"))
    f.append(text(ox + pw + 4, oy - ph / 2 + 4, "E°", size=10, color=MUTED, anchor="start"))
    # мітки по X (декади)
    for lq in range(-2, 3):
        f.append(line(px(lq), oy, px(lq), oy + 5, color=INK, sw=1))
        f.append(text(px(lq), oy + 20, "%+d" % lq if lq else "0", size=9.5, color=MUTED))
    # сходинка: одна декада → −59 мВ (ступінчаста ілюстрація на прямій)
    x_a, x_b = px(0), px(1)
    y_a, y_b = py(0), py(-59)
    f.append(line(x_a, y_a, x_b, y_a, color=POS, sw=1.6, dash="3,3"))
    f.append(line(x_b, y_a, x_b, y_b, color=POS, sw=1.6, dash="3,3"))
    f.append(circle(x_a, y_a, 4, fill=NEG, stroke=NEG, sw=1))
    f.append(circle(x_b, y_b, 4, fill=NEG, stroke=NEG, sw=1))
    f.append(text((x_a + x_b) / 2, y_a - 8, "Q ×10", size=10, color=POS, bold=True))
    f.append(text(x_b + 10, (y_a + y_b) / 2 + 4, "−59 мВ", size=11, color=POS, bold=True, anchor="start"))

    # ліворуч — звідки береться 59
    lx, ly = 30, 78
    f.append(fitbox(lx, ly, 236, 26, "Звідки береться 59 мВ", size=11.5,
                    fill=NEG, stroke=NEG, sw=0, color="#ffffff", bold=True))
    steps = [
        ("RT/F при 25°C:", "8.314 · 298.15 / 96485"),
        ("=", "0.0257 В = 25.7 мВ"),
        ("ln 10 = 2.303 (перехід", "натуральний → десятковий лог)"),
        ("2.303 · 25.7 мВ", "= 59.2 мВ на декаду"),
        ("для n електронів:", "нахил = 59 / n мВ"),
    ]
    yy = ly + 40
    for a, b in steps:
        f.append(text(lx + 6, yy, a, size=10, color=INK, anchor="start", bold=True))
        f.append(text(lx + 6, yy + 15, b, size=10, color=MUTED, anchor="start"))
        yy += 40
    f.append(fitbox(lx, yy + 2, 236, 40,
                    "n=1 → 59 мВ/декаду\nn=2 → лише 29 мВ/декаду",
                    size=10, fill="#eaf0fd", stroke=NEG, sw=1.2))
    render(os.path.join(IMG, "nernst-slope.svg"), W, H, *f)


# ── M3. Температурний коефіцієнт напруги: dE/dT через ентропію ────────────────
def fig_temp_coeff():
    """Чому номінал зсувається на морозі й у спеку: dE/dT = ΔS/nF.
    Мала, але реальна нахилена пряма E(T); числа для трьох катодів."""
    W, H = 780, 420
    f = [text(W / 2, 30, "Температурний зсув напруги: dE/dT = ΔS/(nF)", size=16, bold=True)]

    ox, oy = 90, 300
    pw, ph = 400, 210
    f.append(line(ox, oy, ox + pw, oy, color=INK, sw=1.6))
    f.append(line(ox, oy, ox, oy - ph, color=INK, sw=1.6))
    f.append(text(ox + pw / 2, oy + 36, "температура T (°C)", size=10.5, color=MUTED))
    f.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="10.5" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">напруга комірки E</text>'
             % (ox - 50, oy - ph / 2, FONT, MUTED, ox - 50, oy - ph / 2))

    # температурна вісь від −20 до +60
    def tx(t): return ox + (t + 20) / 80.0 * pw
    for t in (-20, 0, 25, 60):
        f.append(line(tx(t), oy, tx(t), oy + 5, color=INK, sw=1))
        f.append(text(tx(t), oy + 20, str(t), size=9.5, color=MUTED))
    # мітка 25°C — опорна
    f.append(line(tx(25), oy, tx(25), oy - ph, color=MUTED, sw=1, dash="4,4"))
    f.append(text(tx(25), oy - ph - 4, "стандарт 25°C", size=9.5, color=MUTED))

    # спадна пряма (від'ємний dE/dT: холод → трохи вища, спека → трохи нижча)
    y25 = oy - ph / 2
    slope = 0.9    # px напруги на градус (перебільшено для видимості)
    def ty(t): return y25 + (t - 25) * slope
    f.append(line(tx(-20), ty(-20), tx(60), ty(60), color=C_LI, sw=2.8))
    f.append(circle(tx(25), y25, 4.5, fill=C_LI, stroke=C_LI, sw=1))
    f.append(text(tx(25) + 8, y25 - 8, "E° (тут)", size=9.5, color=C_LI, anchor="start"))
    # холодний і теплий маркери
    f.append(circle(tx(-20), ty(-20), 4, fill=NEG, stroke=NEG, sw=1))
    f.append(text(tx(-20) + 6, ty(-20) - 6, "мороз:", size=9.5, color=NEG, anchor="start", bold=True))
    f.append(text(tx(-20) + 6, ty(-20) + 8, "трохи вища", size=9.5, color=NEG, anchor="start"))
    f.append(circle(tx(60), ty(60), 4, fill=POS, stroke=POS, sw=1))
    f.append(text(tx(60) - 6, ty(60) + 4, "спека: трохи нижча", size=9.5, color=POS, anchor="end"))
    f.append(text(ox + pw / 2, oy - ph + 16,
                  "нахил малий: одиниці десятих мВ на градус", size=10, color=MUTED, italic=True))

    # праворуч — формула й реальні числа
    rx, ryy = 520, 76
    f.append(fitbox(rx, ryy, 236, 26, "Нахил = ентропія реакції", size=11,
                    fill=C_LI, stroke=C_LI, sw=0, color="#ffffff", bold=True))
    f.append(text(rx + 118, ryy + 54, "dE/dT = ΔS / (n·F)", size=13.5, color=INK, bold=True))
    f.append(fitbox(rx, ryy + 68, 236, 44,
                    "ΔS — зміна безладу реакції\n(+ безлад → напруга росте з T,\n− безлад → падає)",
                    size=9.5, fill=FILL, stroke=MUTED, sw=1))
    f.append(text(rx + 6, ryy + 138, "Реальні катоди (dE/dT):", size=10, color=INK, anchor="start", bold=True))
    rows = [("LiFePO4", "−0.08 мВ/К", C_LFP),
            ("LiMn2O4", "−0.20 мВ/К", C_NI),
            ("LiCoO2",  "−0.25 мВ/К", C_LI)]
    yy = ryy + 158
    for nm, val, col in rows:
        f.append(text(rx + 10, yy, nm, size=10, color=col, anchor="start", bold=True))
        f.append(text(rx + 226, yy, val, size=10, color=col, anchor="end"))
        yy += 20
    f.append(fitbox(rx, yy + 4, 236, 30,
                    "малий, але не нуль — тому\nномінал «гуляє» з температурою",
                    size=9.5, fill="#fdecea", stroke=C_LI, sw=1.1))
    render(os.path.join(IMG, "temp-coeff.svg"), W, H, *f)


if __name__ == "__main__":
    fig_voltage()
    fig_energy()
    fig_discharge()
    fig_cycles()
    fig_temp()
    fig_decision()
    fig_timeline()
    fig_priority()
    fig_chemistries()
    fig_phase_plateau()
    fig_cold_plating()
    fig_nernst_chain()
    fig_nernst_slope()
    fig_temp_coeff()
    print("OK: 14 figures ->", IMG)
