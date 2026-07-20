# -*- coding: utf-8 -*-
"""Фігури до теми «Подібність і масштабування».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── дрібні помічники ────────────────────────────────────────────────────────
def polyline(pts, color=INK, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for (x, y) in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, color, sw, d))


def polygon(pts, fill=FILL, stroke=LINE, sw=1.6):
    p = " ".join("%.1f,%.1f" % (x, y) for (x, y) in pts)
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>'
            % (p, fill, stroke, sw))


def head_at(x, y, dx, dy, color=INK, size=10):
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    bx, by = x - ux * size, y - uy * size
    nx, ny = -uy, ux
    return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
            % (x, y, bx + nx * size * 0.5, by + ny * size * 0.5,
               bx - nx * size * 0.5, by - ny * size * 0.5, color))


def varrow(x1, y1, x2, y2, color=LINE, sw=2.4, head=11):
    return line(x1, y1, x2, y2, color=color, sw=sw) + head_at(x2, y2, x2 - x1, y2 - y1, color, head)


# ── Фігура 1: квадратно-кубічний закон ──────────────────────────────────────
def fig_square_cube():
    W, H = 780, 450
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Подвоїв розмір — поверхня ×4, об'єм ×8", size=18, bold=True))

    def cube(x, y, s, label, tag):
        # ізометричний куб: передня грань + верх + правий бік
        dx, dy = s * 0.42, -s * 0.30
        front = rect(x, y, s, s, fill="#eef2f7", stroke=INK, sw=1.8)
        top = polygon([(x, y), (x + dx, y + dy), (x + s + dx, y + dy), (x + s, y)],
                      fill="#f7fafd", stroke=INK, sw=1.8)
        side = polygon([(x + s, y), (x + s + dx, y + dy),
                        (x + s + dx, y + s + dy), (x + s, y + s)],
                       fill="#dde5ee", stroke=INK, sw=1.8)
        out = top + side + front
        out += text(x + s / 2, y + s + 30, label, size=15, bold=True)
        out += text(x + s / 2, y + s + 50, tag, size=12, color=MUTED)
        return out

    # малий і великий куби, нижні грані на одному рівні (y+s = 300)
    f.append(cube(120, 240, 60, "L", "×1"))
    f.append(cube(320, 180, 120, "2L", "×2 сторона"))
    # стрілка росту між кубами
    f.append(varrow(210, 275, 300, 245, color=MUTED, sw=2.2, head=10))

    # права колонка — арифметика степенів
    px, pw = 520, 236
    f.append(fitbox(px, 78, pw, 58, "довжина:  L → 2L\n× 2",
                    size=13, pad=9, fill=FILL, stroke=INK, sw=1.4, bold=True))
    f.append(fitbox(px, 150, pw, 58, "поверхня:  6L² → 24L²\n× 4  (як квадрат)",
                    size=13, pad=9, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True))
    f.append(fitbox(px, 222, pw, 58, "об'єм:  L³ → 8L³\n× 8  (як куб)",
                    size=13, pad=9, fill="#fdecea", stroke=POS, sw=1.4, bold=True))

    # нижня плашка-підсумок
    b, w, h = textbox(W / 2, H - 34,
                      "міцність ∝ площа (×4), а вага ∝ об'єм (×8)  →  напруження ×2",
                      size=14, pad=11, fill="#eef1fb", stroke=NEG, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "square-cube.svg"), W, H, *f)


# ── Фігура 2: S/V ∝ 1/L (лог-лог: степінь -1 → пряма) ───────────────────────
def fig_surface_volume():
    W, H = 780, 460
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Менше тіло — більше поверхні на кожен грам (S/V ∝ 1/L)",
                  size=18, bold=True))

    # плоскі осі (логарифмічні)
    ox, oy = 100, 350     # початок координат (лівий-нижній)
    xr, yt = 650, 92      # права межа x, верхня межа y
    f.append(varrow(ox, oy, xr + 22, oy, color=INK, sw=1.8, head=11))   # вісь X
    f.append(varrow(ox, oy, ox, yt - 6, color=INK, sw=1.8, head=11))    # вісь Y
    f.append(text(xr + 18, oy - 12, "розмір L →", size=12, color=MUTED, anchor="end"))
    f.append(text(ox - 10, yt + 2, "S/V", size=13, bold=True, italic=True, anchor="end"))
    f.append(text(ox + 4, yt - 6, "(логарифмічні осі)", size=11, color=MUTED, anchor="start"))

    # лог-мапи: L у декадах [-1..4], S/V = 60/L
    def px_of(L):
        return ox + (math.log10(L) + 1) / 5.0 * (xr - ox)

    def py_of(sv):
        return oy - (math.log10(sv) + 3) / 6.0 * (oy - yt)   # S/V у [10⁻³..10³]

    # пряма лінія степеневого закону
    p0 = (px_of(0.1), py_of(60.0 / 0.1))
    p1 = (px_of(1e4), py_of(60.0 / 1e4))
    f.append(polyline([p0, p1], color=INK, sw=2.8))

    # позначки істот — рівномірно рознесені по лог-осі
    creatures = [(3.0, "комаха"), (60.0, "миша"), (500.0, "людина"), (8000.0, "кит")]
    for L, name in creatures:
        cx, cy = px_of(L), py_of(60.0 / L)
        f.append(circle(cx, cy, 5.5, fill=INK, stroke=INK, sw=1))
        f.append(text(cx, oy + 22, name, size=12, color=MUTED))

    # анотація малих (зелена) — унизу ліворуч, у вільній зоні під лінією
    f.append(fitbox(150, 285, 250, 60,
                    "малі: панують\nповерхневі сили\n(в'язкість, натяг, опір)",
                    size=12, pad=8, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True))
    f.append(line(240, 285, px_of(3.0) - 6, py_of(60.0 / 3.0) + 8, color=FIELD, sw=1.2, dash="4 3"))

    # анотація великих (синя) — угорі праворуч, у вільній зоні над лінією
    f.append(fitbox(430, 108, 262, 60,
                    "великі: панують\nоб'ємні сили\n(вага, інерція)",
                    size=12, pad=8, fill="#eef1fb", stroke=NEG, sw=1.3, bold=True))
    f.append(line(560, 168, px_of(8000.0) - 6, py_of(60.0 / 8000.0) - 8, color=NEG, sw=1.2, dash="4 3"))
    return render(os.path.join(IMG, "surface-volume.svg"), W, H, *f)


# ── Фігура 3: динамічна подібність (однакове Re → однакова картина) ──────────
def fig_dynamic_similarity():
    W, H = 780, 450
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Рівні числа Рейнольдса — однакова картина потоку",
                  size=18, bold=True))

    def flow(cx, cy, R, span, label, sub):
        out = []
        # тіло — овал
        rx, ry = R, R * 1.35
        # обтічні лінії, що вигинаються повз тіло
        offs = [1.0, 2.1, 3.4]      # у частках R
        for k in offs:
            for sgn in (+1, -1):
                base = cy + sgn * k * R
                pts = []
                for i in range(41):
                    t = i / 40.0
                    x = cx - span + 2 * span * t
                    bump = R * 1.25 / k * math.exp(-((x - cx) / (span * 0.42)) ** 2)
                    y = base + sgn * bump
                    pts.append((x, y))
                out.append(polyline(pts, color=NEG, sw=1.8))
        # стрілка напряму потоку (згори)
        out.append(varrow(cx - span, cy - 4.0 * R, cx - span + 46, cy - 4.0 * R,
                          color=MUTED, sw=2.0, head=9))
        out.append(text(cx - span + 54, cy - 4.0 * R + 4, "потік", size=11,
                        color=MUTED, anchor="start"))
        # тіло
        out.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="#dde5ee" '
                   'stroke="%s" stroke-width="1.8"/>' % (cx, cy, rx, ry, INK))
        # вихори в сліді
        for sgn in (+1, -1):
            vx = cx + span * 0.52
            vy = cy + sgn * R * 0.7
            out.append(circle(vx, vy, R * 0.34, fill="none", stroke=POS, sw=1.6))
        # підписи
        out.append(text(cx, cy + 4.7 * R + 6, label, size=14, bold=True))
        out.append(text(cx, cy + 4.7 * R + 26, sub, size=12, color=MUTED))
        return "".join(out)

    f.append(flow(210, 175, 34, 150, "оригінал", "розмір L, швидкість v"))
    f.append(flow(560, 175, 17, 75, "модель 1:5", "розмір L/5, швидкість 5v"))

    # середня плашка — однакове Re
    b, w, h = textbox(W / 2, 330, "Re = ρ·v·L / μ  —  однакове  →  той самий візерунок вихорів",
                      size=14, pad=10, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True)
    f.append(b)
    # нижня плашка — пастка
    b2, w2, h2 = textbox(W / 2, H - 30,
                         "пастка: щоб зрівняти Re, швидкість × масштаб → наскок на стисливість (Мах)",
                         size=13, pad=10, fill="#fdecea", stroke=POS, sw=1.3, bold=True)
    f.append(b2)
    return render(os.path.join(IMG, "dynamic-similarity.svg"), W, H, *f)


# ── Фігура 4: роздування швидкості обдуву для дрібних моделей ────────────────
def fig_speed_blowup():
    W, H = 840, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Дрібніша модель — швидша труба, аж до абсурду",
                  size=18, bold=True))

    ox, oy = 122, 418            # лівий-нижній кут поля
    xr, yt = 700, 96             # права й верхня межі
    nmax = 60.0
    vmin, vmax = 20.0, 2000.0
    lognmax = math.log10(nmax)
    logv0, logv1 = math.log10(vmin), math.log10(vmax)

    def px(n):
        return ox + math.log10(n) / lognmax * (xr - ox)

    def py(v):
        return oy - (math.log10(v) - logv0) / (logv1 - logv0) * (oy - yt)

    v_m1, v_m03 = 340.3, 102.1    # Мах 1 і Мах 0.3

    # зони (тло): надзвук / стисливість / надійна
    f.append(rect(ox, yt, xr - ox, py(v_m1) - yt, fill="#fbe4e0", stroke='none', sw=0, rx=0))
    f.append(rect(ox, py(v_m1), xr - ox, py(v_m03) - py(v_m1), fill="#fdf0e4", stroke='none', sw=0, rx=0))
    f.append(rect(ox, py(v_m03), xr - ox, oy - py(v_m03), fill="#edf6ee", stroke='none', sw=0, rx=0))

    # осі
    f.append(varrow(ox, oy, xr + 22, oy, color=INK, sw=1.8, head=11))
    f.append(varrow(ox, oy, ox, yt - 8, color=INK, sw=1.8, head=11))
    f.append(text((ox + xr) / 2, oy + 40, "масштаб моделі (лог)", size=12, color=MUTED))
    f.append(text(ox - 14, yt - 14, "швидкість обдуву, м/с (лог)", size=12, color=MUTED, anchor="start"))

    # позначки осей
    for n in (1, 2, 5, 10, 20, 50):
        x = px(n)
        f.append(line(x, oy, x, oy + 6, color=INK, sw=1.4))
        f.append(text(x, oy + 22, "1:%d" % n, size=12, color=MUTED))
    for v in (20, 50, 100, 200, 500, 1000, 2000):
        y = py(v)
        f.append(line(ox - 6, y, ox, y, color=INK, sw=1.4))
        f.append(text(ox - 12, y + 4, str(v), size=11, color=MUTED, anchor="end"))

    # горизонталі Маха
    f.append(line(ox, py(v_m1), xr, py(v_m1), color=POS, sw=1.8, dash="7 4"))
    f.append(line(ox, py(v_m03), xr, py(v_m03), color="#c47a1a", sw=1.8, dash="7 4"))

    # крива v = 30·n (лог-лог → пряма)
    pts = [(px(n), py(30.0 * n)) for n in (1, 2, 5, 10, 20, 40, 60)]
    f.append(polyline(pts, color=INK, sw=3.0))

    # приклади-точки з числом Маха (підпис праворуч-нижче, у вільному боці)
    for n, mach, col in ((5, "Мах 0.44", "#c47a1a"), (10, "Мах 0.88", "#c47a1a"), (20, "Мах 1.76", POS)):
        cx, cy = px(n), py(30.0 * n)
        f.append(circle(cx, cy, 6.0, fill=INK, stroke=BG, sw=1.5))
        f.append(text(cx + 12, cy + 16, "1:%d  %s" % (n, mach), size=11, color=col, anchor="start", bold=True))

    # підписи зон — зліва, де крива низько й місце вільне
    f.append(text(px(1.12), py(760), "надзвук — фізичний абсурд", size=12, color=POS, anchor="start", bold=True))
    f.append(text(px(1.12), py(175), "стисливість — Re і Мах уже не зрівняти", size=12, color="#b5651d", anchor="start", bold=True))
    f.append(text(px(6.0), oy - 16, "надійна зона обдуву", size=12, color=FIELD, anchor="middle", bold=True))

    # підписи горизонталей Маха (правий край)
    f.append(text(xr - 6, py(v_m1) - 8, "Мах 1  (340 м/с)", size=11, color=POS, anchor="end", bold=True))
    f.append(text(xr - 6, py(v_m03) - 8, "Мах 0.3  (102 м/с)", size=11, color="#b5651d", anchor="end", bold=True))

    # формула у вільному нижньому-правому трикутнику
    f.append(fitbox(px(24), py(47), 168, 52, "у тому самому повітрі\nv_моделі = v · масштаб",
                    size=12, pad=8, fill=FILL, stroke=INK, sw=1.3, bold=True))
    return render(os.path.join(IMG, "speed-blowup.svg"), W, H, *f)


# ── Фігура 5 (вставка hist): хронологія масштабного мислення ─────────────────
def fig_scaling_timeline():
    W, H = 880, 650
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Один хід думки крізь три століття", size=18, bold=True))
    f.append(text(W / 2, 52, "закони знають лише відношення, не абсолютний розмір",
                  size=12, color=MUTED))

    sx = 190                    # x спини часу
    f.append(line(sx, 78, sx, 606, color=MUTED, sw=2.6))

    # (рік, підпис, тип-тінт)
    rows = [
        ("1638", "Ґалілей: велетень завалиться під власною вагою —\nсуходільний розмір має межу", "plain"),
        ("1872", "Фруд: мала модель корабля передбачає велетня,\nякщо швидкості як √(довжина)", "plain"),
        ("1883", "Рейнольдс: одне безрозмірне число вирішує —\nплавна течія чи зрив у вихор", "plain"),
        ("1892", "Ваші (Франція): Π-теорема сформульована вперше — і забута", "prio"),
        ("1911", "Федерман · Рябушинський (Росія): незалежно виводять те саме", "prio"),
        ("1914", "Бекінгем (США): додає лише символ π і назву — вона й прилипла", "name"),
        ("1945–50", "Тейлор: вага атомної бомби з фотографій вогняної кулі —\nсамим розмірним аналізом", "peak"),
    ]
    tint = {
        "plain": (FILL, LINE),
        "prio":  ("#eef6ef", FIELD),
        "name":  ("#fdecea", POS),
        "peak":  ("#eef1fb", NEG),
    }
    cys = [118, 194, 270, 346, 422, 498, 574]
    bx, bw, bh = sx + 30, W - (sx + 30) - 26, 60
    for (yr, lab, kind), cy in zip(rows, cys):
        fill, stroke = tint[kind]
        dotc = stroke if kind != "plain" else INK
        f.append(line(sx, cy, bx, cy, color=MUTED, sw=1.6))          # відросток
        f.append(circle(sx, cy, 6.5, fill=dotc, stroke=dotc, sw=1))  # вузол на спині
        f.append(text(sx - 18, cy + 5, yr, size=15, bold=True, anchor="end"))
        f.append(fitbox(bx, cy - bh / 2, bw, bh, lab,
                        size=14, pad=10, fill=fill, stroke=stroke, sw=1.5, bold=False))
    return render(os.path.join(IMG, "scaling-timeline.svg"), W, H, *f)


# ── Фігура 6 (вставка hist): Тейлор — log R vs log t, нахил 2/5 → енергія ─────
def fig_taylor_loglog():
    W, H = 820, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Як фотографія важить бомбу: нахил 2/5 → енергія",
                  size=18, bold=True))

    ox, oy = 120, 372          # початок осей (лівий-нижній)
    xr, yt = 700, 96
    f.append(varrow(ox, oy, xr + 22, oy, color=INK, sw=1.8, head=11))   # вісь X
    f.append(varrow(ox, oy, ox, yt - 6, color=INK, sw=1.8, head=11))    # вісь Y
    f.append(text(xr + 14, oy + 26, "log t  (час після спалаху)", size=12,
                  color=MUTED, anchor="end"))
    f.append(text(ox - 8, yt + 4, "log R", size=13, bold=True, italic=True, anchor="end"))
    f.append(text(ox + 6, yt - 4, "(радіус кулі)", size=11, color=MUTED, anchor="start"))

    # пряма нахилу 2/5 у пікселях + точки-«фотографії» на ній
    p0 = (ox + 60, oy - 44)
    p1 = (xr - 40, yt + 118)
    f.append(polyline([p0, p1], color=INK, sw=3.0))
    for t in (0.06, 0.28, 0.5, 0.72, 0.94):
        cx = p0[0] + (p1[0] - p0[0]) * t
        cy = p0[1] + (p1[1] - p0[1]) * t
        f.append(circle(cx, cy, 6.0, fill=POS, stroke=BG, sw=1.6))
    # маленький трикутник нахилу біля середини лінії
    mx = p0[0] + (p1[0] - p0[0]) * 0.5
    my = p0[1] + (p1[1] - p0[1]) * 0.5
    f.append(line(mx, my, mx + 70, my, color=MUTED, sw=1.6, dash="4 3"))
    f.append(line(mx + 70, my, mx + 70, my - 28, color=MUTED, sw=1.6, dash="4 3"))
    f.append(text(mx + 34, my + 16, "5", size=12, color=MUTED))
    f.append(text(mx + 82, my - 12, "2", size=12, color=MUTED))

    # анотація над лінією (вільна зона — угорі ліворуч)
    f.append(fitbox(150, 96, 250, 52,
                    "точки з фото лягають\nна нахил 2/5  →  R ∝ t^(2/5)",
                    size=12, pad=8, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True))
    # анотація під лінією (вільна зона — унизу праворуч)
    f.append(fitbox(452, 300, 252, 52,
                    "висота лінії задає E:\nE ≈ ρ·R⁵ / t²",
                    size=12, pad=8, fill="#eef1fb", stroke=NEG, sw=1.3, bold=True))
    # плашка-результат
    b, w, h = textbox(W / 2, H - 28,
                      "E ≈ 17 кілотонів   —   офіційне ~20 кт було ще таємне",
                      size=14, pad=11, fill="#fdecea", stroke=POS, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "taylor-loglog.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_square_cube(), fig_surface_volume(), fig_dynamic_similarity(),
          fig_speed_blowup(), fig_scaling_timeline(), fig_taylor_loglog()]
    print("written:")
    for p in ps:
        print("  ", p)
