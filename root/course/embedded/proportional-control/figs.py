# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def polyline(pts, color=INK, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"%s/>'
            % (" ".join("%.1f,%.1f" % p for p in pts), color, sw, d))


# ── Спільна модель об'єкта з інерцією для відгуків ────────────────────────────
# Дискретна симуляція: інерційний об'єкт другого порядку (маса + загасання) під
# P-регулятором. Дає правдиві криві: малий Kp повзе й недотягує, великий —
# перестрілює й розгойдується. load — стале навантаження (дає сталий зсув).

def sim(Kp, load=0.0, n=600, dt=0.05, mass=1.0, damp=0.5, setpoint=1.0):
    y = 0.0; v = 0.0; out = []
    for _ in range(n):
        e = setpoint - y
        u = Kp * e
        a = (u - load - damp * v) / mass
        v += a * dt
        y += v * dt
        out.append(y)
    return out


# ── Фігура 1: пропорційний закон u = Kp·e ────────────────────────────────────

def fig_proportional_law():
    W, H = 720, 300
    p = []
    ox, oy = 360, 165          # центр (нуль)
    half = 250
    top = 60
    bot = 250

    # осі
    p.append(arrow(ox - half, oy, ox + half, oy, color=INK, sw=1.8))
    p.append(arrow(ox, bot, ox, top, color=INK, sw=1.8))
    p.append(text(ox + half - 4, oy + 20, "помилка e", size=12, color=INK, anchor="end"))
    p.append(text(ox + 44, top + 8, "вплив u", size=12, color=INK))

    # пряма u = Kp·e через нуль (нахил підібрано так, щоб лінія лишалася в полотні)
    run = half - 30                 # горизонтальний хід від центра
    rise = (oy - top - 12)          # вертикальний хід угору до стелі
    slope = rise / run
    p.append(line(ox - run, oy + run * slope,
                  ox + run, oy - run * slope, color=NEG, sw=3))
    p.append(text(ox + 150, oy - 96, "нахил = Kp", size=12, color=NEG, bold=True))

    # пунктир: велика помилка → велика дія
    ex, ey = ox + 150, oy - 150 * slope
    p.append(line(ex, oy, ex, ey, color=MUTED, sw=1.4, dash="4 3"))
    p.append(line(ox, ey, ex, ey, color=MUTED, sw=1.4, dash="4 3"))
    p.append(circle(ex, ey, 4, fill=POS, stroke=POS))
    p.append(text(ox + 130, oy + 36, "велика помилка → велика дія", size=10, color=INK))
    p.append(text(ox - 130, oy - 24, "помилка в один бік —", size=10, color=MUTED))
    p.append(text(ox - 130, oy - 10, "дія в той самий", size=10, color=MUTED))

    render(os.path.join(OUT, "proportional-law.svg"), W, H, *p,
           title="Пропорційний закон: u = Kp · e")


# ── Фігура 2: P як пружина ────────────────────────────────────────────────────

def fig_spring_analogy():
    W, H = 720, 260
    p = []

    def spring(x0, y, coils, length, color=INK):
        seg = length / (coils * 2)
        pts = [(x0, y)]
        for i in range(coils * 2):
            x = x0 + seg * (i + 1)
            yy = y - 14 if i % 2 == 0 else y + 14
            pts.append((x, yy))
        pts.append((x0 + length, y))
        return polyline(pts, color=color, sw=1.8)

    def row(y, length, label, force_label):
        q = []
        anchor_x = 130
        # стіна-ціль
        q.append(line(anchor_x, y - 22, anchor_x, y + 22, color=INK, sw=3))
        q.append(text(anchor_x, y - 30, "ціль", size=9.5, color=MUTED))
        # пружина
        q.append(spring(anchor_x, y, 9, length))
        # вантаж
        bx = anchor_x + length
        q.append(rect(bx, y - 16, 32, 32, fill="#dce4f2", stroke=INK, sw=1.6, rx=3))
        # сила тяги назад (червона) — довша за більшого розтягу
        far = length * 0.42
        q.append(line(bx, y, bx - far, y, color=POS, sw=3))
        q.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" stroke-width="3"/>'
                 % (bx - far + 9, y - 5, bx - far, y, bx - far + 9, y + 5, POS))
        q.append(text(bx + 60, y + 4, label, size=10, color=INK, anchor="start"))
        q.append(text(bx + 16, y - 24, force_label, size=9, color=POS, bold=True))
        return q

    p += row(96, 150, "велика помилка → сильна тяга", "F = Kp·e")
    p += row(190, 60, "мала помилка → слабка тяга", "F = Kp·e")

    render(os.path.join(OUT, "spring-analogy.svg"), W, H, *p,
           title="P — це «пружина» до завдання")


# ── Фігура 3: вплив Kp — повільно / баланс / розгойдування ────────────────────

def fig_kp_tradeoff():
    W, H = 720, 300
    p = []
    ox, oy = 80, 252
    top = 56
    Ax = 580
    # рівень завдання
    y_set = top + 55

    p.append(arrow(ox, oy, ox, top, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + Ax, oy, color=INK, sw=1.6))
    p.append(text(ox + Ax, oy + 18, "час", size=11, color=INK, anchor="end"))
    p.append(line(ox, y_set, ox + Ax, y_set, color=MUTED, sw=1.6, dash="6 4"))
    p.append(text(ox + Ax + 4, y_set + 4, "завдання", size=10, color=MUTED, anchor="start"))

    def curve(data, color):
        pts = []
        N = len(data)
        for i, yv in enumerate(data):
            x = ox + Ax * i / (N - 1)
            y = oy - (oy - y_set) * yv          # yv=1 → лінія завдання
            pts.append((x, y))
        return polyline(pts, color=color, sw=2.4)

    p.append(curve(sim(Kp=0.7, load=0.18), FIELD))    # малий — повзе, недотягує
    p.append(curve(sim(Kp=3.0, load=0.18), NEG))      # баланс
    p.append(curve(sim(Kp=10.0, load=0.18), POS))     # розгойдування

    # легенда
    lx = ox + 26
    for i, (c, t) in enumerate([(FIELD, "малий Kp"), (NEG, "середній Kp"), (POS, "великий Kp")]):
        ly = top + 6 + i * 16
        p.append(line(lx, ly, lx + 26, ly, color=c, sw=2.4))
        p.append(text(lx + 32, ly + 4, t, size=10, color=c, anchor="start", bold=True))

    render(os.path.join(OUT, "kp-tradeoff.svg"), W, H, *p,
           title="Вплив Kp: малий повзе, великий перестрілює й розгойдується")


# ── Фігура 4: сталий зсув — P завжди недотягує ────────────────────────────────

def fig_steady_state_offset():
    W, H = 720, 300
    p = []
    ox, oy = 80, 246
    top = 58
    Ax = 560
    y_set = top + 20

    p.append(arrow(ox, oy, ox, top, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + Ax, oy, color=INK, sw=1.6))
    p.append(text(ox + Ax, oy + 18, "час", size=11, color=INK, anchor="end"))
    p.append(line(ox, y_set, ox + Ax, y_set, color=MUTED, sw=1.8, dash="6 4"))
    p.append(text(ox + Ax + 4, y_set + 4, "завдання", size=10, color=MUTED, anchor="start"))

    def curve(data, color):
        pts = []
        N = len(data)
        for i, yv in enumerate(data):
            x = ox + Ax * i / (N - 1)
            y = oy - (oy - y_set) * yv
            pts.append((x, y))
        return pts

    d_lo = curve(sim(Kp=3.0, load=0.5), FIELD)
    d_hi = curve(sim(Kp=10.0, load=0.5), NEG)
    p.append(polyline(d_lo, color=FIELD, sw=2.4))
    p.append(polyline(d_hi, color=NEG, sw=2.4))

    # маркер сталого зсуву наприкінці кривих
    xend = ox + Ax - 6
    p.append(line(xend, y_set, xend, d_lo[-1][1], color=FIELD, sw=2.4))
    p.append(text(xend - 4, (y_set + d_lo[-1][1]) / 2, "e_ss (малий Kp)", size=9.5, color=FIELD, anchor="end", bold=True))
    p.append(line(xend - 130, y_set, xend - 130, d_hi[-1][1], color=NEG, sw=2.4))
    p.append(text(xend - 134, (y_set + d_hi[-1][1]) / 2 - 2, "e_ss (великий Kp)", size=9.5, color=NEG, anchor="end", bold=True))

    # підпис у межах полотна (не за viewBox!)
    p.append(text(ox + Ax * 0.5, top + 2, "більший Kp → менший зсув, та НІКОЛИ не нуль",
                  size=10.5, color=POS, bold=True))

    render(os.path.join(OUT, "steady-state-offset.svg"), W, H, *p,
           title="Сталий зсув: P завжди «недотягує» до завдання")


# ── Фігура 5: чому зсув неминучий ─────────────────────────────────────────────

def fig_why_offset():
    W, H = 720, 270
    p = []

    # об'єкт
    p.append(rect(166, 126, 68, 48, fill="#dce4f2", stroke=INK, sw=1.8, rx=4))
    p.append(text(200, 152, "об'єкт", size=10.5, color=INK, bold=True))
    # навантаження вниз
    p.append(arrow(200, 174, 200, 228, color=POS, sw=3))
    p.append(text(208, 220, "навантаження", size=10, color=POS, anchor="start", bold=True))
    p.append(text(208, 234, "(вага, тертя)", size=9, color=MUTED, anchor="start"))
    # вплив угору
    p.append(arrow(200, 126, 200, 72, color=FIELD, sw=3))
    p.append(text(208, 80, "вплив u₀", size=10, color=FIELD, anchor="start", bold=True))
    p.append(text(208, 94, "(щоб утримати)", size=9, color=MUTED, anchor="start"))
    # стрілка до рамки-висновку
    p.append(arrow(280, 150, 384, 150, color=INK, sw=2))
    # рамка-висновок
    p.append(fitbox(390, 96, 300, 108, "", fill="#f6f4ec", stroke=INK, sw=1.6))
    p.append(text(540, 124, "P дає вплив ТІЛЬКИ з помилки:", size=11, color=INK, bold=True))
    p.append(text(540, 150, "u = Kp · e", size=15, color=NEG, bold=True))
    p.append(text(540, 176, "щоб u = u₀  →  e_ss = u₀ / Kp ≠ 0", size=11.5, color=POS, bold=True))
    p.append(text(540, 195, "помилку не прибрати, лише зменшити", size=9.5, color=MUTED))

    render(os.path.join(OUT, "why-offset.svg"), W, H, *p,
           title="Чому зсув неминучий")


# ── Фігура 6: P лишає зсув — його прибирає інтегральна складова ────────────────

def fig_automatic_reset():
    W, H = 720, 280
    p = []
    ox, oy = 80, 240
    top = 56
    Ax = 560
    y_set = top + 20

    p.append(arrow(ox, oy, ox, top, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + Ax, oy, color=INK, sw=1.6))
    p.append(text(ox + Ax, oy + 18, "час", size=11, color=INK, anchor="end"))
    p.append(line(ox, y_set, ox + Ax, y_set, color=MUTED, sw=1.8, dash="6 4"))
    p.append(text(ox + Ax + 4, y_set + 4, "завдання", size=10, color=MUTED, anchor="start"))

    def curve(data, color):
        pts = []
        N = len(data)
        for i, yv in enumerate(data):
            x = ox + Ax * i / (N - 1)
            y = oy - (oy - y_set) * yv
            pts.append((x, y))
        return pts

    # лише P — застигає нижче (зсув)
    d_p = curve(sim(Kp=3.0, load=0.5), NEG)
    p.append(polyline(d_p, color=NEG, sw=2.6))
    # з інтегральною — повзе на завдання (схематично: P-крива, дотягнута до 1.0)
    d_pi = []
    N = len(d_p)
    for i, (x, y) in enumerate(d_p):
        frac = min(1.0, i / (N * 0.62))
        ytarget = oy - (oy - y_set) * 1.0
        yy = y + (ytarget - y) * frac
        d_pi.append((x, yy))
    p.append(polyline(d_pi, color=FIELD, sw=2.2, dash="6 4"))

    # маркер зсуву P
    xm = ox + Ax * 0.62
    im = int(N * 0.62)
    p.append(line(xm, y_set, xm, d_p[im][1], color=POS, sw=2.4))
    p.append(text(xm + 8, (y_set + d_p[im][1]) / 2, "сталий зсув (P)", size=10, color=POS, anchor="start", bold=True))

    # легенда
    p.append(line(ox + 22, top + 6, ox + 48, top + 6, color=NEG, sw=2.6))
    p.append(text(ox + 54, top + 10, "лише P", size=10, color=NEG, anchor="start", bold=True))
    p.append(line(ox + 22, top + 24, ox + 48, top + 24, color=FIELD, sw=2.2, dash="6 4"))
    p.append(text(ox + 54, top + 28, "P з інтегральною → зсув зникає", size=10, color=FIELD, anchor="start", bold=True))

    render(os.path.join(OUT, "automatic-reset.svg"), W, H, *p,
           title="P лишає зсув — його прибирає інтегральна складова")


# ══════════════════════════════════════════════════════════════════════════════
#  Фігури для історичної вставки hist-reset-and-band
# ══════════════════════════════════════════════════════════════════════════════

# ── Сопло-заслінка зі зворотним сильфоном: звідки взялося підсилення ───────────

def fig_nozzle_flapper():
    W, H = 720, 370
    p = []

    # подача повітря → жиклер → сопло
    supply_y = 150
    p.append(text(70, supply_y - 14, "живлення", size=10, color=MUTED, anchor="middle"))
    p.append(text(70, supply_y - 2, "повітря", size=10, color=MUTED, anchor="middle"))
    p.append(arrow(30, supply_y, 118, supply_y, color=FIELD, sw=3))
    # жиклер (звуження)
    p.append(rect(118, supply_y - 7, 18, 14, fill="#dce4f2", stroke=INK, sw=1.4, rx=2))
    p.append(text(127, supply_y + 26, "жиклер", size=9, color=MUTED, anchor="middle"))
    # трубка до сопла
    p.append(line(136, supply_y, 250, supply_y, color=INK, sw=3))
    # сопло (конус, дме праворуч)
    p.append('<polygon points="250,%.1f 250,%.1f 272,%.1f 272,%.1f" fill="#dce4f2" stroke="%s" stroke-width="1.4"/>'
             % (supply_y - 8, supply_y + 8, supply_y + 4, supply_y - 4, INK))
    p.append(text(250, supply_y - 16, "сопло", size=9.5, color=MUTED, anchor="middle"))

    # заслінка — вертикальна планка на важелі, ледь відхилена
    flap_x = 292
    p.append(line(flap_x, supply_y - 60, flap_x + 10, supply_y + 62, color=POS, sw=4))
    p.append(text(flap_x + 30, supply_y - 52, "заслінка", size=10, color=POS, anchor="start", bold=True))
    # мікрозазор
    p.append(line(272, supply_y, flap_x + 2, supply_y, color=MUTED, sw=1.2, dash="2 2"))
    p.append(text(300, supply_y + 82, "зазор ~ соті міліметра", size=9, color=MUTED, anchor="middle"))

    # важіль заслінки (вхід — помилка тисне зверху)
    piv_x, piv_y = flap_x + 6, supply_y - 60
    p.append(circle(piv_x, piv_y, 4, fill=INK, stroke=INK))
    p.append(arrow(piv_x + 70, piv_y - 40, piv_x + 20, piv_y - 6, color=INK, sw=2))
    p.append(text(piv_x + 74, piv_y - 44, "вхід (помилка)", size=10, color=INK, anchor="start", bold=True))

    # відбір тиску з-за жиклера → вихід + зворотний сильфон
    tap_x = 193
    p.append(line(tap_x, supply_y, tap_x, 250, color=NEG, sw=2.4))
    p.append(circle(tap_x, supply_y, 3.5, fill=NEG, stroke=NEG))
    # розгалуження: до виходу і до сильфона
    p.append(line(tap_x, 250, 470, 250, color=NEG, sw=2.4))
    p.append(arrow(470, 250, 560, 250, color=NEG, sw=3))
    p.append(text(566, 254, "вихід u", size=11, color=NEG, anchor="start", bold=True))
    # відгалуження вниз до сильфона
    sb_x = 360
    p.append(line(sb_x, 250, sb_x, 288, color=NEG, sw=2.4))

    # зворотний сильфон (гармошка) під важелем — тисне заслінку НАЗАД
    bx, by = sb_x, 292
    for i in range(5):
        yy = by + i * 8
        p.append(line(bx - 20, yy, bx + 20, yy + 4, color=INK, sw=1.6))
        p.append(line(bx + 20, yy + 4, bx - 20, yy + 8, color=INK, sw=1.6))
    p.append(text(bx, by + 62, "зворотний сильфон", size=10, color=NEG, anchor="middle", bold=True))
    p.append(arrow(bx, by - 6, flap_x + 8, supply_y + 60, color=NEG, sw=2))
    p.append(text(bx + 96, by + 10, "тисне заслінку назад", size=9.5, color=NEG, anchor="start"))

    render(os.path.join(OUT, "nozzle-flapper.svg"), W, H, *p,
           title="Сопло-заслінка: крихітний рух — величезний тиск")


# ── Смуга пропорційності як «вікно» входу, що жене вихід 0→100% ────────────────

def fig_proportional_band():
    W, H = 720, 340
    p = []
    ox, oy = 110, 268
    top = 70
    Ax = 520

    # осі: вхід (помилка, % шкали) → вихід (клапан, %)
    p.append(arrow(ox, oy, ox, top, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + Ax, oy, color=INK, sw=1.6))
    p.append(text(ox + Ax, oy + 20, "вимір (% шкали давача)", size=10.5, color=INK, anchor="end"))
    p.append(text(ox - 8, top - 4, "вихід, %", size=10.5, color=INK, anchor="end"))

    # рівні 0 і 100 %
    y0, y100 = oy, top + 20
    p.append(line(ox, y100, ox + Ax, y100, color=MUTED, sw=1.2, dash="4 3"))
    p.append(text(ox - 8, y100 + 4, "100", size=10, color=MUTED, anchor="end"))
    p.append(text(ox - 8, y0 + 4, "0", size=10, color=MUTED, anchor="end"))

    # похила ділянка = смуга пропорційності (тут ~40 %)
    band_frac = 0.40
    x_lo = ox + Ax * 0.30
    x_hi = x_lo + Ax * band_frac
    # поза смугою — насичення (плоскі 0 і 100)
    p.append(line(ox, y0, x_lo, y0, color=NEG, sw=3))
    p.append(line(x_hi, y100, ox + Ax, y100, color=NEG, sw=3))
    # похила лінія в межах смуги
    p.append(line(x_lo, y0, x_hi, y100, color=NEG, sw=3.2))

    # затінити смугу
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity="0.10"/>'
             % (x_lo, y100, x_hi - x_lo, y0 - y100, FIELD))
    p.append(line(x_lo, y0, x_lo, top + 4, color=FIELD, sw=1.2, dash="3 3"))
    p.append(line(x_hi, y0, x_hi, top + 4, color=FIELD, sw=1.2, dash="3 3"))
    # дужка смуги
    p.append(line(x_lo, top + 12, x_hi, top + 12, color=FIELD, sw=2))
    p.append(line(x_lo, top + 8, x_lo, top + 16, color=FIELD, sw=2))
    p.append(line(x_hi, top + 8, x_hi, top + 16, color=FIELD, sw=2))
    p.append(text((x_lo + x_hi) / 2, top + 4, "смуга пропорційності (тут 40 %)",
                  size=11, color=FIELD, anchor="middle", bold=True))

    # підписи насичення
    p.append(text((ox + x_lo) / 2, y0 - 10, "клапан закрито", size=9.5, color=MUTED, anchor="middle"))
    p.append(text((x_hi + ox + Ax) / 2, y100 - 10, "клапан відкрито", size=9.5, color=MUTED, anchor="middle"))

    # нижній підпис — суть формули
    p.append(fitbox(ox, oy + 34, Ax, 30,
                    "вузька смуга = крутий нахил = великий Kp   ·   PB (%) = 100 / Kp",
                    size=12, bold=True, fill="#f6f4ec", stroke=INK, sw=1.4, color=INK))

    render(os.path.join(OUT, "proportional-band.svg"), W, H, *p,
           title="Смуга пропорційності — «вікно» входу від 0 до 100 % виходу")


# ══════════════════════════════════════════════════════════════════════════════
#  Фігури для вставки math-closed-loop-dynamics.md (динаміка замкненого контуру)
# ══════════════════════════════════════════════════════════════════════════════

# ── math-фіг. 1: об'єкт 1-го порядку — контур лише пришвидшує, крива монотонна ──

def figm_first_order():
    W, H = 720, 320
    p = []
    ox, oy = 78, 250
    top = 58
    Ax = 566

    p.append(arrow(ox, oy, ox, top, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + Ax, oy, color=INK, sw=1.6))
    p.append(text(ox + Ax, oy + 18, "час", size=11, color=INK, anchor="end"))
    p.append(text(ox - 8, top + 4, "вихід y", size=11, color=INK, anchor="end"))

    # рівень завдання (нормований до 1 = стеля відкладання)
    y_set = top + 26
    p.append(line(ox, y_set, ox + Ax, y_set, color=MUTED, sw=1.6, dash="6 4"))
    p.append(text(ox + Ax + 4, y_set + 4, "завдання r", size=10, color=MUTED, anchor="start"))

    # три експоненти 1 − e^(−t/τ) із різними сталими часу; усі МОНОТОННІ.
    # τ_замкн = τ / (1 + K·Kp): що більший Kp, то менша стала, то крутіше до рівня.
    T = 3.0
    def expo(tau, color, dash=None, sw=2.6):
        pts = []
        N = 240
        for i in range(N + 1):
            t = T * i / N
            yv = 1.0 - math.exp(-t / tau)
            x = ox + Ax * t / T
            y = oy - (oy - y_set) * yv
            pts.append((x, y))
        return polyline(pts, color=color, sw=sw, dash=dash)

    p.append(expo(1.10, FIELD))     # розімкнено / малий Kp — мляво
    p.append(expo(0.45, NEG))       # більший Kp — швидше
    p.append(expo(0.18, POS))       # ще більший Kp — ще швидше

    # позначки сталої часу τ (де крива сягає ~63 % рівня) для двох кривих
    for tau, color in [(1.10, FIELD), (0.18, POS)]:
        xt = ox + Ax * tau / T
        yv = 1.0 - math.exp(-1.0)
        yt = oy - (oy - y_set) * yv
        p.append(line(xt, oy, xt, yt, color=color, sw=1.2, dash="3 3"))
        p.append(circle(xt, yt, 3.4, fill=color, stroke=color))

    # легенда
    lx = ox + Ax - 232
    for i, (c, t) in enumerate([(FIELD, "малий Kp: τ велика"),
                                 (NEG, "більший Kp: τ менша"),
                                 (POS, "ще більший Kp: τ ще менша")]):
        ly = top + 8 + i * 16
        p.append(line(lx, ly, lx + 24, ly, color=c, sw=2.6))
        p.append(text(lx + 30, ly + 4, t, size=10, color=c, anchor="start", bold=True))

    p.append(text(ox + 150, oy - 6, "усі криві монотонні — перельоту немає",
                  size=10.5, color=INK, anchor="middle"))

    render(os.path.join(OUT, "first-order-speedup.svg"), W, H, *p,
           title="Об'єкт 1-го порядку: P лише пришвидшує, крива не перестрілює")


# ── math-фіг. 2: корені 2-го порядку на s-площині повзуть із ростом Kp ─────────

def figm_root_locus():
    W, H = 720, 360
    p = []
    # осі: горизонталь — дійсна вісь (Re s), вертикаль — уявна (Im s). Нуль праворуч.
    ox, oy = 470, 190          # початок координат (0,0) на площині
    L = 300                    # довжина від'ємної дійсної півосі, що показуємо
    up = 148                   # піввисота уявної осі

    # легка заливка лівої (стійкої) півплощини
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#eafaf0" '
             'opacity="0.7"/>' % (ox - L - 6, oy - up, L + 6, 2 * up))

    # осі
    p.append(arrow(ox - L, oy, ox + 118, oy, color=INK, sw=1.6))
    p.append(arrow(ox, oy + up, ox, oy - up, color=INK, sw=1.6))
    p.append(text(ox + 114, oy + 18, "Re s", size=11, color=INK, anchor="end"))
    p.append(text(ox + 12, oy - up + 12, "Im s", size=11, color=INK, anchor="start"))

    # межа стійкості — уявна вісь (усе ліворуч від неї = згасання)
    p.append(text(ox + 10, oy - up + 30, "стійко ←", size=10, color=FIELD, anchor="start", bold=True))
    p.append(text(ox + 10, oy - up + 44, "→ рознос", size=10, color=POS, anchor="start", bold=True))

    # Модель: J·s² + b·s + Kp = 0  →  s = (−b ± √(b²−4·J·Kp)) / (2J).
    # Фіксуємо J=1, b=6. З ростом Kp корені: дійсні різні → злиття (Kp=b²/4J=9)
    #  → комплексна пара, що йде вгору/вниз уздовж вертикалі Re=−b/2J=−3.
    J, b = 1.0, 6.0
    kps = [1.0, 4.0, 9.0, 16.0, 25.0, 36.0]   # останній дає im = √(144−36)/2 ≈ 5.2
    # масштаби осей від фактичного розмаху коренів (щоб усі точки лишались у полотні)
    im_max = max(math.sqrt(4 * J * kp - b * b) / (2 * J)
                 for kp in kps if 4 * J * kp - b * b > 0)
    re_max = 9.0               # найлівіший дійсний корінь при малому Kp ≈ −6…−8
    sx = L / re_max            # масштаб дійсної осі (px на одиницю −Re)
    sy = (up - 22) / im_max    # масштаб уявної осі (із запасом під підписи)

    def plot_root(re_s, im_s, color, r=5.0, cross=False):
        x = ox + re_s * sx     # re_s від'ємне → ліворуч від нуля
        y = oy - im_s * sy
        if cross:
            d = 5.5
            return (line(x - d, y - d, x + d, y + d, color=color, sw=2.6) +
                    line(x - d, y + d, x + d, y - d, color=color, sw=2.6))
        return circle(x, y, r, fill=color, stroke=color)

    # для кожного значення Kp — обидва корені
    for Kp in kps:
        disc = b * b - 4 * J * Kp
        if disc > 1e-9:                       # надлишкове загасання: два дійсні корені
            r1 = (-b + math.sqrt(disc)) / (2 * J)
            r2 = (-b - math.sqrt(disc)) / (2 * J)
            p.append(plot_root(r1, 0, NEG))
            p.append(plot_root(r2, 0, NEG))
        elif disc < -1e-9:                    # недостатнє загасання: комплексна пара
            re_s = -b / (2 * J)
            im_s = math.sqrt(-disc) / (2 * J)
            p.append(plot_root(re_s, im_s, POS))
            p.append(plot_root(re_s, -im_s, POS))
        else:                                 # критичне: подвійний корінь
            p.append(plot_root(-b / (2 * J), 0, INK, r=6.5, cross=True))

    # вертикальна лінія Re = −b/2J, уздовж якої тікають комплексні корені
    xv = ox + (-b / (2 * J)) * sx
    p.append(line(xv, oy - up + 8, xv, oy + up - 20, color=POS, sw=1.2, dash="4 4"))
    p.append(text(xv, oy + up - 6, "Re = −b/2J", size=9.5, color=POS, anchor="middle"))

    # підписи режимів
    p.append(text(ox - L + 82, oy + 40, "малий Kp:", size=10, color=NEG, anchor="middle", bold=True))
    p.append(text(ox - L + 82, oy + 54, "два дійсні корені", size=9.5, color=NEG, anchor="middle"))
    p.append(text(ox - L + 82, oy + 68, "надлишкове загасання", size=9, color=MUTED, anchor="middle"))
    p.append(text(xv - 78, oy - up + 42, "великий Kp:", size=10, color=POS, anchor="middle", bold=True))
    p.append(text(xv - 78, oy - up + 56, "комплексна пара", size=9.5, color=POS, anchor="middle"))
    p.append(text(xv - 78, oy - up + 70, "недостатнє загасання", size=9, color=MUTED, anchor="middle"))
    # точка злиття
    p.append(text(xv + 70, oy + 30, "Kp = b²/4J:", size=9.5, color=INK, anchor="middle", bold=True))
    p.append(text(xv + 70, oy + 44, "злиття (критичне)", size=9, color=INK, anchor="middle"))

    render(os.path.join(OUT, "root-locus-2nd.svg"), W, H, *p,
           title="Корені 2-го порядку на s-площині: більший Kp зводить дійсні в пару")


# ── math-фіг. 3: три режими загасання (надлишкове загасання / критичне / недостатнє загасання) ───────────

def figm_damping_regimes():
    W, H = 720, 320
    p = []
    ox, oy = 78, 246
    top = 58
    Ax = 566

    p.append(arrow(ox, oy, ox, top, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + Ax, oy, color=INK, sw=1.6))
    p.append(text(ox + Ax, oy + 18, "час (у періодах ωₙ)", size=11, color=INK, anchor="end"))
    p.append(text(ox - 8, top + 4, "вихід y", size=11, color=INK, anchor="end"))

    y_set = top + 40
    p.append(line(ox, y_set, ox + Ax, y_set, color=MUTED, sw=1.6, dash="6 4"))
    p.append(text(ox + Ax + 4, y_set + 4, "завдання", size=10, color=MUTED, anchor="start"))

    # крокова відповідь стандартної ланки 2-го порядку для трьох ζ.
    wn = 1.0
    T = 12.0
    def step2(zeta, color, dash=None, sw=2.6):
        pts = []
        N = 320
        for i in range(N + 1):
            t = T * i / N
            if zeta < 1.0:                    # недостатнє загасання
                wd = wn * math.sqrt(1 - zeta * zeta)
                y = 1 - math.exp(-zeta * wn * t) * (math.cos(wd * t) +
                        (zeta * wn / wd) * math.sin(wd * t))
            elif abs(zeta - 1.0) < 1e-6:      # критичне
                y = 1 - math.exp(-wn * t) * (1 + wn * t)
            else:                             # надлишкове загасання
                s = math.sqrt(zeta * zeta - 1)
                r1 = -wn * (zeta - s)
                r2 = -wn * (zeta + s)
                y = 1 - (r1 * math.exp(r2 * t) - r2 * math.exp(r1 * t)) / (r1 - r2)
            x = ox + Ax * t / T
            yy = oy - (oy - y_set) * y
            pts.append((x, yy))
        return polyline(pts, color=color, sw=sw, dash=dash)

    p.append(step2(2.0, FIELD))                     # надлишкове загасання — повзе, без перельоту
    p.append(step2(1.0, INK, dash="2 3", sw=2.2))   # критичне — найшвидше без перельоту
    p.append(step2(0.3, POS))                       # недостатнє загасання — швидко, але перестрілює

    # легенда
    lx = ox + Ax - 250
    rows = [(FIELD, "ζ > 1 — надлишкове (повільно, без перельоту)"),
            (INK, "ζ = 1 — критичне (найшвидше без перельоту)"),
            (POS, "ζ < 1 — недостатнє (швидко, але перельоти)")]
    for i, (c, t) in enumerate(rows):
        ly = top + 8 + i * 16
        p.append(line(lx, ly, lx + 24, ly, color=c, sw=2.6))
        p.append(text(lx + 30, ly + 4, t, size=9.5, color=c, anchor="start", bold=True))

    render(os.path.join(OUT, "damping-regimes.svg"), W, H, *p,
           title="Три режими 2-го порядку за коефіцієнтом загасання ζ")


if __name__ == "__main__":
    fig_proportional_law()
    fig_spring_analogy()
    fig_kp_tradeoff()
    fig_steady_state_offset()
    fig_why_offset()
    fig_automatic_reset()
    fig_nozzle_flapper()
    fig_proportional_band()
    figm_first_order()
    figm_root_locus()
    figm_damping_regimes()
    print("OK: figures written to", OUT)
