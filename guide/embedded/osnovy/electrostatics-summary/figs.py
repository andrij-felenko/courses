# -*- coding: utf-8 -*-
"""Фігури до детальної статті «Зведення електростатики»
(guide/embedded/osnovy/electrostatics-summary — версія -d).

Ця стаття — синтез: зводить заряд, силу, поле, потенціал, вольт, енергію
в одну виведену картину. Тож фігури несуть саме синтез, а не окремі поняття.

Фігури:
  ladder.svg    — драбина виведень: від заряду до енергії, з формулою на кожному щаблі
  slopes.svg    — 1/r² проти 1/r: справжні профілі поля й потенціалу над віссю r
  flux.svg      — Гаусс: потік крізь будь-яку оболонку рахує лише заряд усередині
  workpath.svg  — робота полем не залежить від шляху (консервативність) → потенціал
  radial-work.svg — вставка math-conservative-field: будь-який крок = радіальний
                    (робота ≠ 0) + поперечний по дузі (робота = 0)
  action-vs-field.svg — вставка hist-field-idea: дія на відстані проти поля
  field-timeline.svg  — вставка hist-field-idea: Ньютон→Фарадей→Томсон→Максвелл
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Драбина виведень ──────────────────────────────────────────────────────
def fig_ladder():
    W, H = 780, 500
    els = []
    # щаблі: (підпис-поняття, формула, коротке «звідки»)
    steps = [
        ("Заряд Q",            "Кл — джерело всього",                "первинна властивість"),
        ("Сила між зарядами",  "F = k·Q₁Q₂ / r²",                   "«наскільки сильно?»"),
        ("Поле",               "E = F / q   →   E = k·Q / r²",       "«що передає силу?»"),
        ("Потенціал",          "V = W / q   →   V = k·Q / r",        "«скільки енергії?»"),
        ("Вольт",              "1 В = 1 Дж / 1 Кл",                  "одиниця V"),
        ("Енергія й сила",     "F = qE ,  W = qV",                   "назад на заряд"),
    ]
    n = len(steps)
    x0, y0 = 60, 70
    bw, bh = 300, 46
    gap = (H - y0 - bh - 30) / (n - 1)
    cx_form = x0 + bw + 190
    for i, (name, form, why) in enumerate(steps):
        y = y0 + i * gap
        # блок-поняття ліворуч
        els.append(fitbox(x0, y, bw, bh, name, size=16, bold=True,
                          fill="#eef3ff", stroke=NEG))
        # формула праворуч
        els.append(fitbox(cx_form - 170, y, 340, bh, form, size=15,
                          fill=FILL, stroke=LINE))
        # «звідки» — курсивом під стрілкою переходу
        if i < n - 1:
            ax = x0 + bw / 2
            els.append(arrow(ax, y + bh, ax, y + gap - 2, color=FIELD, sw=2.2))
            els.append(text(ax + 8, y + bh + gap / 2 + 4, why, size=11,
                           color=MUTED, anchor="start", italic=True))
        # тонка звʼязка поняття→формула
        els.append(line(x0 + bw, y + bh / 2, cx_form - 170, y + bh / 2,
                        color=MUTED, sw=1, dash="3 3"))
    return render(os.path.join(IMG, 'ladder.svg'), W, H, *els,
                  title="Драбина виведень: одне поняття породжує наступне")


# ── 2. 1/r² проти 1/r ────────────────────────────────────────────────────────
def fig_slopes():
    W, H = 760, 440
    els = []
    # спільна вісь r; дві криві в одній системі, нормовані до однакового старту
    ox, oy = 90, H - 70          # початок координат
    axw, axh = W - 160, H - 140
    els.append(line(ox, oy, ox + axw, oy, color=INK, sw=2))          # r
    els.append(line(ox, oy, ox, oy - axh, color=INK, sw=2))          # значення
    els.append(text(ox + axw, oy + 24, "відстань r →", size=13, anchor="end"))
    els.append(text(ox - 12, oy - axh + 4, "значення", size=13, anchor="end"))

    r0 = 0.5     # старт (щоб не ділити на 0)
    rmax = 5.0
    def px(r): return ox + (r - 0) / rmax * axw
    top = oy - axh + 10
    # нормуємо так, щоб при r0 обидві криві були біля верху
    def v_field(r): return 1.0 / (r * r)
    def v_pot(r):    return 1.0 / r
    f0, p0 = v_field(r0), v_pot(r0)
    scale = (axh - 20)
    def yF(r): return oy - (v_field(r) / f0) * scale
    def yP(r): return oy - (v_pot(r) / p0) * scale

    def poly(fn, color, sw):
        pts = []
        r = r0
        while r <= rmax + 1e-6:
            pts.append("%.1f,%.1f" % (px(r), fn(r)))
            r += 0.05
        return ('<polyline points="%s" fill="none" stroke="%s" '
                'stroke-width="%.1f"/>' % (" ".join(pts), color, sw))

    els.append(poly(yF, POS, 2.6))   # поле — крутіше падає
    els.append(poly(yP, FIELD, 2.6)) # потенціал — пологіше

    # підписи кривих біля їхніх «хвостів»
    els.append(text(px(2.1), yF(2.1) - 12, "E ~ 1/r²  (крутіше)", size=14,
                    color=POS, anchor="start", bold=True))
    els.append(text(px(3.0), yP(3.0) - 12, "V ~ 1/r  (пологіше)", size=14,
                    color=FIELD, anchor="start", bold=True))

    # маркери: удвічі далі
    for r in (1.0, 2.0):
        els.append(line(px(r), oy, px(r), oy + 6, color=INK, sw=1.5))
        els.append(text(px(r), oy + 22, ("r" if r == 1 else "2r"), size=12))
    # показати падіння E у 4 рази, V у 2 рази між r і 2r
    els.append(text(px(3.35), top + 40,
                    "від r до 2r:", size=12, color=MUTED, anchor="start"))
    els.append(text(px(3.35), top + 58,
                    "E падає ×4,  V падає ×2", size=12, color=MUTED, anchor="start"))
    els.append(text(px(3.35), top + 80,
                    "бо E — це нахил V", size=12, color=INK, anchor="start", italic=True))
    return render(os.path.join(IMG, 'slopes.svg'), W, H, *els,
                  title="Крутість і висота: чому E спадає як 1/r², а V — як 1/r")


# ── 3. Гаусс: потік крізь оболонку ───────────────────────────────────────────
def fig_flux():
    W, H = 760, 420
    els = []
    cx, cy = 250, H / 2 + 10
    # заряд у центрі
    els.append(plus(cx, cy, r=14))
    # промені поля назовні
    for k in range(12):
        a = k * math.pi / 6
        x2 = cx + 150 * math.cos(a)
        y2 = cy + 150 * math.sin(a)
        els.append(arrow(cx + 18 * math.cos(a), cy + 18 * math.sin(a),
                         x2, y2, color=FIELD, sw=1.6))
    # дві РІЗНІ замкнені оболонки навколо того самого заряду
    els.append(circle(cx, cy, 70, fill="none", stroke=NEG, sw=2.2))
    # друга — неправильна (пунктир), більша
    import io
    blob = ('<path d="M %.0f %.0f Q %.0f %.0f %.0f %.0f Q %.0f %.0f %.0f %.0f '
            'Q %.0f %.0f %.0f %.0f Q %.0f %.0f %.0f %.0f Z" fill="none" '
            'stroke="%s" stroke-width="2.2" stroke-dasharray="7 5"/>' % (
            cx+120, cy, cx+130,cy-90, cx+20,cy-115, cx-110,cy-95, cx-135,cy,
            cx-120,cy+100, cx+10,cy+120, cx+130,cy+85, cx+120,cy, NEG))
    els.append(blob)
    els.append(text(cx, cy - 100, "гладка сфера", size=12, color=NEG))
    els.append(text(cx - 120, cy + 135, "будь-яка інша оболонка", size=12, color=NEG))
    # висновок праворуч
    els.append(fitbox(500, cy - 90, 230, 180,
                      "Потік Φ = Q / ε₀\n\nоднаковий крізь ОБИДВІ\nоболонки — важить лише\nзаряд усередині, а не\nформа й розмір.\n\nСкільки ліній вийшло —\nстільки й перетнуло межу.",
                      size=13, fill=FILL, stroke=LINE))
    return render(os.path.join(IMG, 'flux.svg'), W, H, *els,
                  title="Закон Гаусса: потік рахує лише заряд усередині")


# ── 4. Робота полем не залежить від шляху ────────────────────────────────────
def fig_workpath():
    W, H = 760, 420
    els = []
    ax, ay = 120, H - 90     # точка A
    bx, by = W - 150, 110    # точка B
    els.append(circle(ax, ay, 10, fill="#eef3ff", stroke=NEG, sw=2))
    els.append(text(ax - 18, ay + 5, "A", size=15, bold=True, anchor="end"))
    els.append(circle(bx, by, 10, fill="#eef3ff", stroke=NEG, sw=2))
    els.append(text(bx + 18, by + 5, "B", size=15, bold=True, anchor="start"))
    # шлях 1 — пряма
    els.append(arrow(ax + 10, ay - 6, bx - 10, by + 8, color=POS, sw=2.2))
    els.append(text((ax+bx)/2 + 10, (ay+by)/2 - 6, "шлях 1", size=13,
                    color=POS, anchor="start"))
    # шлях 2 — гак угору-праворуч (крива через контрольні точки)
    p = ('<path d="M %.0f %.0f C %.0f %.0f %.0f %.0f %.0f %.0f" fill="none" '
         'stroke="%s" stroke-width="2.2" marker-end="url(#arrow)"/>' % (
         ax + 8, ay - 8, ax + 40, ay - 200, bx - 260, by - 40, bx - 12, by + 6, FIELD))
    els.append(p)
    els.append(text(ax + 120, ay - 165, "шлях 2 (звивистий)", size=13,
                    color=FIELD, anchor="start"))
    # висновок
    els.append(fitbox(ax - 5, 150, 250, 120,
                      "Робота поля\nW = q·(V_A − V_B)\n\nоднакова обома шляхами.\nПоле консервативне —\nтож і зʼявляється\nпотенціал: число на\nточку, а не на шлях.",
                      size=13, fill=FILL, stroke=LINE))
    return render(os.path.join(IMG, 'workpath.svg'), W, H, *els,
                  title="Робота не залежить від шляху → існує потенціал")


# ── 5. Радіальний + поперечний крок (для вставки math-conservative-field) ─────
def fig_radial_work():
    """Ядро доведення консервативності: розкладаємо будь-який крок на
    радіальний (уздовж E → робота ≠ 0) і поперечний по дузі кола
    (E ⊥ шлях → робота = 0). Дуги — еквіпотенціалі."""
    W, H = 780, 470
    cx, cy = 150, 380          # заряд-джерело (лівий нижній кут)
    els = []
    # заряд-джерело
    els.append(plus(cx, cy, r=12))
    els.append(text(cx - 22, cy + 5, "Q", size=15, bold=True, anchor="end"))

    # дві еквіпотенціальні дуги (кола радіусів r1, r2)
    r1, r2 = 210, 320
    def arc(r, a0, a1, color, sw, dash=None):
        import math as m
        x0, y0 = cx + r * m.cos(a0), cy - r * m.sin(a0)
        x1, y1 = cx + r * m.cos(a1), cy - r * m.sin(a1)
        large = 1 if (a1 - a0) > m.pi else 0
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<path d="M %.1f %.1f A %.1f %.1f 0 %d 0 %.1f %.1f" '
                'fill="none" stroke="%s" stroke-width="%.1f"%s/>' %
                (x0, y0, r, r, large, x1, y1, color, sw, d))
    import math as m
    a_lo, a_hi = m.radians(8), m.radians(70)
    els.append(arc(r1, a_lo, a_hi, NEG, 2.0, dash="5 4"))
    els.append(arc(r2, a_lo, a_hi, NEG, 2.0, dash="5 4"))
    # підписи еквіпотенціалей
    els.append(text(cx + r1 * m.cos(a_lo) + 8, cy - r1 * m.sin(a_lo) + 4,
                    "V = V₁", size=13, color=NEG, anchor="start"))
    els.append(text(cx + r2 * m.cos(a_lo) + 8, cy - r2 * m.sin(a_lo) + 4,
                    "V = V₂", size=13, color=NEG, anchor="start"))

    # робоча точка A на внутрішній дузі, під кутом aA
    aA = m.radians(40)
    Ax, Ay = cx + r1 * m.cos(aA), cy - r1 * m.sin(aA)
    # радіальний крок A → C: уздовж радіуса до зовнішньої дуги (той самий кут)
    Cx, Cy = cx + r2 * m.cos(aA), cy - r2 * m.sin(aA)
    # поперечний крок C → B: по зовнішній дузі до кута aB
    aB = m.radians(58)
    Bx, By = cx + r2 * m.cos(aB), cy - r2 * m.sin(aB)

    # вектор поля E у точці A (уздовж радіуса, ВІД заряду) — зелений
    Ex, Ey = cx + (r1 + 55) * m.cos(aA), cy - (r1 + 55) * m.sin(aA)
    els.append(arrow(Ax, Ay, Ex, Ey, color=FIELD, sw=2.4))
    els.append(text(Ex + 6, Ey - 6, "E", size=15, color=FIELD, bold=True, anchor="start"))

    # радіальний крок (робота ≠ 0) — червоний, уздовж E
    els.append(arrow(Ax, Ay, Cx, Cy, color=POS, sw=2.6))
    # поперечний крок по дузі (робота = 0) — синій пунктир уздовж еквіпотенціалі
    els.append(arc(r2, aA, aB, "#2457d6", 2.6))
    # стрілочка-наконечник поперечного кроку
    els.append(arrow(cx + r2 * m.cos(aB - m.radians(2)), cy - r2 * m.sin(aB - m.radians(2)),
                     Bx, By, color="#2457d6", sw=2.6))

    # позначки точок
    for (px, py, lab, off) in [(Ax, Ay, "A", (-16, 5)), (Cx, Cy, "C", (14, -6)),
                               (Bx, By, "B", (14, -4))]:
        els.append(circle(px, py, 5, fill=BG, stroke=INK, sw=1.6))
        els.append(text(px + off[0], py + off[1], lab, size=14, bold=True,
                        anchor="middle"))

    # підписи-ярлики біля кроків
    els.append(text((Ax + Cx) / 2 + 30, (Ay + Cy) / 2, "радіальний крок",
                    size=13, color=POS, anchor="start"))
    els.append(text((Ax + Cx) / 2 + 30, (Ay + Cy) / 2 + 17, "робота = qE·Δr ≠ 0",
                    size=12, color=POS, anchor="start"))
    midx = cx + (r2 + 14) * m.cos((aA + aB) / 2)
    midy = cy - (r2 + 14) * m.sin((aA + aB) / 2)
    els.append(text(midx + 6, midy - 2, "поперечний крок (по дузі)",
                    size=13, color="#2457d6", anchor="start"))
    els.append(text(midx + 6, midy + 16, "E ⊥ шлях → робота = 0",
                    size=12, color="#2457d6", anchor="start"))

    # пояснювальна рамка
    els.append(fitbox(430, 300, 320, 132,
                      "Будь-який крок розкладається на два:\n"
                      "• уздовж r — поле штовхає, робота є;\n"
                      "• упоперек (по колу) — E ⊥ шлях, нуль.\n"
                      "Тож уся робота залежить лише від того,\n"
                      "як змінився r — а не від звивин шляху.",
                      size=13, fill=FILL, stroke=LINE))
    return render(os.path.join(IMG, 'radial-work.svg'), W, H, *els,
                  title="Робота = радіальна частина; упоперек поля — нуль")


# ── 6. Дія на відстані ПРОТИ поля (вставка hist-field-idea) ──────────────────
def fig_action_vs_field():
    """Дві картини світу поряд: порожнеча + стрибок сили  vs  простір із лініями."""
    W, H = 820, 430
    els = []
    midx = W / 2
    els.append(line(midx, 60, midx, H - 30, color=MUTED, sw=1.2, dash="6 6"))

    # ── ліва панель: дія на відстані ──
    lx = W * 0.25
    els.append(text(lx, 56, "Дія на відстані (Ньютон)", size=15, bold=True))
    ay, by = 150, 300
    q1x, q2x = lx - 95, lx + 95
    els.append(plus(q1x, ay + 40, r=15))
    els.append(plus(q2x, by, r=15))
    # «стрибок» сили крізь порожнечу — ламана з питальником
    els.append(line(q1x + 16, ay + 46, q2x - 14, by - 6, color=POS, sw=2.4, dash="4 5"))
    els.append(text((q1x + q2x) / 2 + 6, (ay + by) / 2 + 34, "F = ?",
                    size=15, color=POS, bold=True, anchor="start"))
    els.append(text(lx, H - 62, "простір між ними — порожній", size=12, color=MUTED))
    els.append(text(lx, H - 44, "сила «стрибає» крізь ніщо", size=12, color=MUTED))

    # ── права панель: поле ──
    rx = W * 0.75
    els.append(text(rx, 56, "Поле-посередник (Фарадей)", size=15, bold=True))
    src = (rx - 70, 220)
    tst = (rx + 95, 150)
    # радіальні лінії сили від джерела (заповнюють простір)
    for k in range(12):
        a = k * math.pi / 6
        els.append(line(src[0] + 17 * math.cos(a), src[1] + 17 * math.sin(a),
                        src[0] + 120 * math.cos(a), src[1] + 120 * math.sin(a),
                        color=FIELD, sw=1.4))
    els.append(plus(src[0], src[1], r=15))
    els.append(plus(tst[0], tst[1], r=13))
    # локальна стрілка сили на пробний заряд — уздовж лінії поля в його точці
    dx, dy = tst[0] - src[0], tst[1] - src[1]
    d = math.hypot(dx, dy)
    els.append(arrow(tst[0], tst[1], tst[0] + 38 * dx / d, tst[1] + 38 * dy / d,
                     color=POS, sw=2.4))
    els.append(text(rx, H - 62, "простір заповнений лініями сили", size=12, color=MUTED))
    els.append(text(rx, H - 44, "заряд відчуває стан ПОРЯД із собою", size=12, color=MUTED))

    return render(os.path.join(IMG, 'action-vs-field.svg'), W, H, *els,
                  title="Дві картини світу: порожнеча проти поля")


# ── 7. Часова лінія народження поняття поля (вставка hist-field-idea) ─────────
def fig_field_timeline():
    """Понад півтора століття: Ньютон → Фарадей → Томсон → Максвелл."""
    W, H = 880, 400
    els = []
    axy = 205
    x0, x1 = 60, W - 50
    els.append(line(x0, axy, x1, axy, color=INK, sw=2.5))
    els.append(arrow(x1 - 2, axy, x1 + 1, axy, color=INK, sw=2.5))

    # події (СОРТОВАНО за роком). Вісь — рівними слотами, а не лінійно за роком:
    # між Ньютоном і Фарадеєм ~140 років, далі чотири події за 30 — лінійна
    # шкала звела б їх у нечитабельну купу. Довгу паузу показуємо підписом.
    events = [
        (1693, "Ньютон", "дія на відстані —\n«безглуздя», але як?", "чесно лишив питання"),
        (1835, "Фарадей", "лінії сили:\nспершу образ", "здогад, не доведення"),
        (1845, "Томсон", "перше число:\nмова тепла", "образ → математика"),
        (1852, "Фарадей", "лінії сили —\nфізично реальні", "тепер переконання"),
        (1865, "Максвелл", "повні рівняння;\nсвітло = поле", "доведено"),
    ]
    events.sort(key=lambda e: e[0])
    n = len(events)
    def xp(i): return x0 + (i + 0.5) / n * (x1 - x0 - 14)

    bw, bh = 168, 66
    def clampx(cx):  # тримати рамку в межах полотна
        return max(6, min(W - 6 - bw, cx - bw / 2))

    # позначка «~140 років паузи» між Ньютоном і Фарадеєм
    xn, xf = xp(0), xp(1)
    els.append(text((xn + xf) / 2, axy - 6, "≈ 140 років", size=11,
                    color=MUTED, italic=True))
    els.append(text((xn + xf) / 2, axy + 16, "скалка муляє", size=11,
                    color=MUTED, italic=True))

    for i, (yr, who, what, status) in enumerate(events):
        x = xp(i)
        up = (i % 2 == 0)
        els.append(circle(x, axy, 7,
                          fill=(MUTED if who == "Ньютон" else FIELD),
                          stroke=INK, sw=1.6))
        els.append(text(x, axy + (30 if not up else -16), str(yr),
                        size=13, bold=True, color=INK))
        by = axy - 44 - bh if up else axy + 44
        bx = clampx(x)
        els.append(fitbox(bx, by, bw, bh, who + "\n" + what,
                          size=12, fill="#eef3ff", stroke=NEG))
        # ніжка від осі до рамки (до її центра по x)
        stem_top, stem_bot = (by + bh, axy - 16) if up else (axy + 16, by)
        els.append(line(bx + bw / 2, stem_top, bx + bw / 2, stem_bot,
                        color=MUTED, sw=1, dash="3 3"))
        els.append(text(bx + bw / 2, (by - 6) if up else (by + bh + 14),
                        status, size=10, color=MUTED, italic=True))

    els.append(text(W / 2, H - 14,
                    "півтора століття · чотири людини · одне поняття",
                    size=12, color=INK, italic=True))
    return render(os.path.join(IMG, 'field-timeline.svg'), W, H, *els,
                  title="Народження поняття поля")


if __name__ == '__main__':
    fig_ladder()
    fig_slopes()
    fig_flux()
    fig_workpath()
    fig_radial_work()
    fig_action_vs_field()
    fig_field_timeline()
    print("OK:", os.listdir(IMG))
