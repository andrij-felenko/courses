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
    print("OK: 9 figures ->", IMG)
