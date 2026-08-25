# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

TAU = math.pi


def _halfwave_pts(ox, oy, aw, amp, a0, a1, samples=120):
    """Точки полілінії sin θ на відрізку фази [a0,a1] (рад), у пікселях."""
    pts = []
    for i in range(samples + 1):
        th = a0 + (a1 - a0) * i / samples
        x = ox + (th / TAU) * aw
        y = oy - amp * math.sin(th)
        pts.append((x, y))
    return pts


def _poly(pts, stroke=INK, sw=2.2, fill="none"):
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="%s" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round"/>' % (s, fill, stroke, sw))


def _filled(pts, base_y, fill="#fde4e0", stroke="none"):
    if not pts:
        return ""
    s = "M %.1f %.1f " % (pts[0][0], base_y)
    s += " ".join("L %.1f %.1f" % (x, y) for x, y in pts)
    s += " L %.1f %.1f Z" % (pts[-1][0], base_y)
    return '<path d="%s" fill="%s" stroke="%s"/>' % (s, fill, stroke)


# ── firing-angle: одна півхвиля при трьох кутах відсікання ────────────────────
# Ідея: показати, що момент запуску α ріже початок півхвилі; залита частина —
# те, що реально дістається навантаженню. Малий α — майже все; великий — хвостик.

def fig_firing_angle():
    W, H = 720, 300
    panels = [("малий α — повна потужність", 0.18 * TAU),
              ("α = 90° — половина", 0.5 * TAU),
              ("великий α — тьмяно", 0.78 * TAU)]
    pw = W / 3
    amp = 78
    p = []
    for k, (lab, a) in enumerate(panels):
        ox = k * pw + 30
        oy = 168
        aw = pw - 56
        # вісь часу (одна півхвиля 0..π)
        p.append(line(ox, oy, ox + aw, oy, color=MUTED, sw=1.2))
        # повна синусоїда тонко (що було б без відсікання)
        p.append(_poly(_halfwave_pts(ox, oy, aw, amp, 0, TAU), stroke="#cbd3dc", sw=1.4))
        # провідна частина α..π — залита й жирна
        cond = _halfwave_pts(ox, oy, aw, amp, a, TAU)
        p.append(_filled(cond, oy))
        p.append(_poly(cond, stroke=POS, sw=2.6))
        # вертикаль у момент запуску
        ax = ox + (a / TAU) * aw
        p.append(line(ax, oy + 8, ax, oy - amp - 10, color=NEG, sw=1.6, dash="4,3"))
        p.append(text(ax, oy - amp - 16, "α", size=13, color=NEG, bold=True, italic=True))
        # підпис панелі
        p.append(text(ox + aw / 2, oy + 38, lab, size=11, color=INK))
        p.append(text(ox + aw / 2, oy + 56, "запуск → кінець півхвилі", size=9, color=MUTED))
    p.append(text(W / 2, H - 12,
                  "залита площа — те, що дісталося навантаженню; пунктир — момент запуску α",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "firing-angle.svg"), W, H, *p,
           title="Кут відсікання α: чим пізніший запуск, тим менший шматок півхвилі")


# ── power-vs-angle: S-подібна крива P/Pмакс(α) ────────────────────────────────
# Ідея: половина потужності рівно на 90°, але крива пологa біля країв і крута в
# середині — звідси нерівномірність дешевого димера з лінійною ручкою.

def _power_frac(alpha):  # alpha у радіанах
    return (1.0 / TAU) * ((TAU - alpha) + math.sin(2 * alpha) / 2.0)


def fig_power_vs_angle():
    W, H = 560, 420
    ox, oy = 90, 350          # початок осей (ліво-низ)
    aw, ah = 410, 280
    p = []
    # осі
    p.append(arrow(ox, oy, ox, oy - ah - 12, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw + 12, oy, color=INK, sw=1.6))
    p.append(text(ox + aw / 2, oy + 40, "кут відсікання α", size=12, color=INK, italic=True))
    p.append(text(ox - 56, oy - ah / 2, "P / Pмакс", size=12, color=INK, italic=True))
    # сітка/поділки по X (0,45,90,135,180) і Y (0..1)
    for deg in (0, 45, 90, 135, 180):
        gx = ox + (deg / 180.0) * aw
        p.append(line(gx, oy, gx, oy - ah, color="#eef1f4", sw=1.0))
        p.append(text(gx, oy + 18, "%d°" % deg, size=10, color=MUTED))
    for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
        gy = oy - frac * ah
        p.append(line(ox, gy, ox + aw, gy, color="#eef1f4", sw=1.0))
        p.append(text(ox - 12, gy + 4, "%.2f" % frac, size=10, color=MUTED, anchor="end"))
    # крива P(α)
    pts = []
    for i in range(0, 181):
        a = i * TAU / 180.0
        f = _power_frac(a)
        pts.append((ox + (i / 180.0) * aw, oy - f * ah))
    p.append(_poly(pts, stroke=POS, sw=3.0))
    # позначка половини на 90°
    mx, my = ox + 0.5 * aw, oy - 0.5 * ah
    p.append(line(ox, my, mx, my, color=NEG, sw=1.4, dash="5,3"))
    p.append(line(mx, oy, mx, my, color=NEG, sw=1.4, dash="5,3"))
    p.append(circle(mx, my, 4.5, fill=NEG, stroke=NEG, sw=1))
    p.append(text(mx + 10, my - 10, "90° → рівно ½", size=11, color=NEG, anchor="start"))
    # підписи нахилу
    p.append(text(ox + 0.12 * aw, oy - 0.93 * ah, "положисто", size=10, color=MUTED, anchor="start"))
    p.append(text(ox + 0.86 * aw, oy - 0.10 * ah, "положисто", size=10, color=MUTED, anchor="end"))
    p.append(text(mx + 8, my + 40, "круто", size=10, color=MUTED, anchor="start"))
    render(os.path.join(OUT, "power-vs-angle.svg"), W, H, *p,
           title="Частка потужності від кута: ½ рівно на 90°, краї положисті")


# ── lamp-vs-smps: чому лампа димерується, а імпульсний блок — ні ──────────────
# Ідея: резистивна лампа бере будь-який шматок синусоїди й рівно гріється;
# вхід SMPS качає струм голками біля піка — відсічена верхівка збиває його.

def fig_lamp_vs_smps():
    W, H = 720, 320
    amp = 64
    p = []
    # ── ліва панель: лампа розжарення ──
    ox, oy, aw = 40, 150, 280
    p.append(line(ox, oy, ox + aw, oy, color=MUTED, sw=1.2))
    p.append(_poly(_halfwave_pts(ox, oy, aw, amp, 0, TAU), stroke="#cbd3dc", sw=1.4))
    a = 0.42 * TAU
    cond = _halfwave_pts(ox, oy, aw, amp, a, TAU)
    p.append(_filled(cond, oy, fill="#fde4e0"))
    p.append(_poly(cond, stroke=POS, sw=2.4))
    ax = ox + (a / TAU) * aw
    p.append(line(ax, oy + 6, ax, oy - amp - 6, color=NEG, sw=1.4, dash="4,3"))
    b, bw, bh = textbox(ox + aw / 2, oy + 70,
                        "лампа розжарення\nбере будь-який шматок\n→ рівно гріється", size=11,
                        fill="#eafaf0", stroke=FIELD)
    p.append(b)
    p.append(text(ox + aw / 2, oy - amp - 18, "димерується", size=12, color=FIELD, bold=True))

    # ── права панель: імпульсний блок ──
    ox2 = 400
    p.append(line(ox2, oy, ox2 + aw, oy, color=MUTED, sw=1.2))
    # повна синусоїда (обидві полярності модулем — показуємо одну півхвилю)
    full = _halfwave_pts(ox2, oy, aw, amp, 0, TAU)
    p.append(_poly(full, stroke="#cbd3dc", sw=1.4))
    # рівень напруги на конденсаторі (трохи нижче піка) — горизонталь
    cap_y = oy - amp * 0.82
    p.append(line(ox2, cap_y, ox2 + aw, cap_y, color=MUTED, sw=1.3, dash="3,3"))
    p.append(text(ox2 + aw - 4, cap_y - 6, "напруга на C", size=9, color=MUTED, anchor="end"))
    # голки струму біля піка (де синус вище конденсатора)
    for frac in (0.40, 0.46, 0.52, 0.58):
        th = frac * TAU
        hx = ox2 + frac * aw
        hy = oy - amp * math.sin(th)
        p.append(line(hx, oy, hx, hy - 14, color=POS, sw=2.4))
    p.append(text(ox2 + 0.49 * aw, oy - amp - 6, "голки струму", size=10, color=POS, anchor="middle"))
    # відсічений шматок верхівки — заштрихований «зник»
    a2 = 0.62 * TAU
    cut = _halfwave_pts(ox2, oy, aw, amp, a2, TAU)
    p.append(_poly(cut, stroke=NEG, sw=2.0, fill="none"))
    bx2 = ox2 + (a2 / TAU) * aw
    p.append(line(bx2, oy + 6, bx2, oy - amp - 6, color=NEG, sw=1.4, dash="4,3"))
    b2, bw2, bh2 = textbox(ox2 + aw / 2, oy + 70,
                           "імпульсний блок (SMPS)\nживиться верхівкою\n→ мерехтить, гуде", size=11,
                           fill="#fdeeec", stroke=POS)
    p.append(b2)
    p.append(text(ox2 + aw / 2, oy - amp - 18, "НЕ димерується", size=12, color=POS, bold=True))

    render(os.path.join(OUT, "lamp-vs-smps.svg"), W, H, *p,
           title="Резистивне навантаження ріжеться легко, вхід SMPS — ні")


# ── halfwave-integral (math): півхвиля + площа під sin²θ ──────────────────────
# Ідея: потужність — це площа під КВАДРАТОМ напруги праворуч від α, поділена на
# повну. Дві панелі: зверху v(θ), знизу v²∝sin²θ із залитою провідною частиною.

def fig_halfwave_integral():
    W, H = 640, 420
    aw = 480
    a = 0.34 * TAU
    p = []
    # ── верхня панель: напруга ──
    ox, oy, amp = 100, 150, 86
    p.append(arrow(ox, oy, ox, oy - amp - 18, color=INK, sw=1.4))
    p.append(arrow(ox, oy, ox + aw + 14, oy, color=INK, sw=1.4))
    p.append(text(ox - 16, oy - amp - 6, "v", size=12, color=INK, bold=True, italic=True, anchor="end"))
    # закрита ділянка 0..α на нулі (синя жирна по осі)
    ax = ox + (a / TAU) * aw
    p.append(line(ox, oy, ax, oy, color=NEG, sw=3.2))
    # повна синусоїда тонко, провідна частина жирна червона
    p.append(_poly(_halfwave_pts(ox, oy, aw, amp, 0, TAU), stroke="#cbd3dc", sw=1.4))
    p.append(_poly(_halfwave_pts(ox, oy, aw, amp, a, TAU), stroke=POS, sw=2.6))
    p.append(line(ax, oy + 6, ax, oy - amp * math.sin(a), color=NEG, sw=1.4, dash="4,3"))
    p.append(text(ax, oy + 20, "α", size=13, color=NEG, bold=True, italic=True))
    p.append(text(ox + aw, oy + 20, "π", size=12, color=MUTED))
    p.append(text(ox + aw / 2, oy - amp - 4, "ключ закритий до α, далі пропускає синусоїду",
                  size=10, color=MUTED))

    # ── нижня панель: квадрат напруги ──
    oy2, amp2 = 360, 120
    p.append(arrow(ox, oy2, ox, oy2 - amp2 - 18, color=INK, sw=1.4))
    p.append(arrow(ox, oy2, ox + aw + 14, oy2, color=INK, sw=1.4))
    p.append(text(ox - 16, oy2 - amp2 - 6, "v²", size=12, color=INK, bold=True, italic=True, anchor="end"))
    # sin²θ повна крива
    sq = []
    sqc = []
    for i in range(0, 121):
        th = TAU * i / 120.0
        x = ox + (th / TAU) * aw
        y = oy2 - amp2 * (math.sin(th) ** 2)
        sq.append((x, y))
        if th >= a:
            sqc.append((x, y))
    p.append(_poly(sq, stroke="#cbd3dc", sw=1.4))
    p.append(_filled(sqc, oy2, fill="#fde4e0"))
    p.append(_poly(sqc, stroke=POS, sw=2.4))
    p.append(line(ax, oy2 + 6, ax, oy2 - amp2 * (math.sin(a) ** 2), color=NEG, sw=1.4, dash="4,3"))
    p.append(text(ax, oy2 + 20, "α", size=13, color=NEG, bold=True, italic=True))
    p.append(text(ox + aw / 2, oy2 - amp2 - 4,
                  "потужність ∝ sin²θ; до навантаження — лише залита площа праворуч від α",
                  size=10, color=POS))
    render(os.path.join(OUT, "halfwave-integral.svg"), W, H, *p,
           title="Потужність — площа під квадратом напруги праворуч від α")


# ── power-curve (math): та сама S-крива, акцент на симетрії 90° ───────────────
def fig_power_curve():
    W, H = 560, 420
    ox, oy = 90, 350
    aw, ah = 410, 280
    p = []
    p.append(arrow(ox, oy, ox, oy - ah - 12, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw + 12, oy, color=INK, sw=1.6))
    p.append(text(ox + aw / 2, oy + 40, "кут запуску α", size=12, color=INK, italic=True))
    p.append(text(ox - 56, oy - ah / 2, "P / Pповна", size=12, color=INK, italic=True))
    for deg in (0, 45, 90, 135, 180):
        gx = ox + (deg / 180.0) * aw
        p.append(line(gx, oy, gx, oy - ah, color="#eef1f4", sw=1.0))
        p.append(text(gx, oy + 18, "%d°" % deg, size=10, color=MUTED))
    for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
        gy = oy - frac * ah
        p.append(line(ox, gy, ox + aw, gy, color="#eef1f4", sw=1.0))
        p.append(text(ox - 12, gy + 4, "%.2f" % frac, size=10, color=MUTED, anchor="end"))
    pts = []
    for i in range(0, 181):
        a = i * TAU / 180.0
        pts.append((ox + (i / 180.0) * aw, oy - _power_frac(a) * ah))
    p.append(_poly(pts, stroke=POS, sw=3.0))
    # симетрична пара 45°/135° → 0.91 / 0.09
    for deg in (45, 135):
        a = deg * TAU / 180.0
        f = _power_frac(a)
        gx, gy = ox + (deg / 180.0) * aw, oy - f * ah
        p.append(circle(gx, gy, 4.0, fill=FIELD, stroke=FIELD, sw=1))
        p.append(text(gx + (8 if deg == 45 else -8), gy - 8, "%.2f" % f, size=10, color=FIELD,
                      anchor=("start" if deg == 45 else "end")))
    # центр (90°, 0.5)
    mx, my = ox + 0.5 * aw, oy - 0.5 * ah
    p.append(circle(mx, my, 4.5, fill=NEG, stroke=NEG, sw=1))
    p.append(text(mx + 10, my - 10, "центр (90°, ½)", size=11, color=NEG, anchor="start"))
    p.append(text(W / 2, H - 12, "симетрично: 45° і 135° дають разом 1.00",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "power-curve.svg"), W, H, *p,
           title="S-крива симетрична відносно центру (90°, ½)")


# ── timeline (proj): хронограма півперіоду ───────────────────────────────────
# Ідея: нуль запускає таймер на затримку d; по таймеру — короткий імпульс на
# затвор; симістор далі тримається сам до наступного нуля.

def fig_timeline():
    W, H = 720, 360
    ox, aw = 70, 600
    p = []
    # три доріжки
    rows = [("мережа", 70), ("zero-cross", 180), ("затвор", 270)]
    for lab, y in rows:
        p.append(text(ox - 8, y + 4, lab, size=11, color=INK, anchor="end", bold=True))
    # вісь часу з нулями 0,10,20 мс
    base = 140
    p.append(line(ox, base, ox + aw, base, color=MUTED, sw=1.2))
    amp = 56
    # дві півхвилі (модуль для наочності: + та −)
    pts = []
    for i in range(0, 241):
        th = 2 * TAU * i / 240.0      # два повних π = два півперіоди
        x = ox + (i / 240.0) * aw
        y = base - amp * math.sin(th)
        pts.append((x, y))
    p.append(_poly(pts, stroke="#cbd3dc", sw=1.6))
    # нулі
    for k in range(3):
        zx = ox + (k / 2.0) * aw
        p.append(line(zx, 60, zx, 300, color="#e3e8ee", sw=1.0, dash="3,4"))
        p.append(text(zx, 320, "%d мс" % (k * 10), size=10, color=MUTED))
    # імпульси zero-cross (зелені) у нулях
    for k in range(2):
        zx = ox + (k / 2.0) * aw
        p.append(line(zx, 200, zx, 165, color=FIELD, sw=2.6))
        p.append(text(zx + 4, 198, "нуль", size=9, color=FIELD, anchor="start"))
    # затримка d → імпульс на затвор + підсвічена провідна частина
    d_frac = 0.32     # частка півперіоду
    for k in range(2):
        z0 = (k / 2.0) * aw
        gx = ox + z0 + d_frac * (aw / 2.0)
        # стрілка затримки d
        zx = ox + z0
        p.append(line(zx, 245, gx, 245, color=NEG, sw=1.4, dash="4,3"))
        p.append(text((zx + gx) / 2, 240, "d", size=11, color=NEG, bold=True, italic=True))
        # імпульс на затвор
        p.append(line(gx, 290, gx, 255, color=POS, sw=2.8))
        p.append(text(gx + 4, 288, "імпульс ~100 мкс", size=9, color=POS, anchor="start"))
        # підсвічена провідна частина півхвилі на «мережі»
        a = d_frac * TAU
        sign = 1 if k == 0 else -1
        seg = []
        for i in range(0, 81):
            th = a + (TAU - a) * i / 80.0
            x = ox + z0 + (th / TAU) * (aw / 2.0)
            yy = base - sign * amp * math.sin(th)
            seg.append((x, yy))
        p.append(_poly(seg, stroke=POS, sw=2.6))
    p.append(text(W / 2, H - 10,
                  "кожен нуль — новий відлік; півперіоди обробляються однаково й незалежно",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="Хронограма: нуль → таймер на d → імпульс на затвор")


# ── mapping (proj): лінійна ручка → нелінійна затримка через таблицю ──────────
def fig_mapping():
    W, H = 720, 360
    p = []
    # ліва панель: крива частки потужності від затримки d (0..10 мс)
    ox, oy = 70, 290
    aw, ah = 250, 220
    p.append(arrow(ox, oy, ox, oy - ah - 12, color=INK, sw=1.5))
    p.append(arrow(ox, oy, ox + aw + 10, oy, color=INK, sw=1.5))
    p.append(text(ox + aw / 2, oy + 34, "затримка d, мс", size=11, color=INK, italic=True))
    p.append(text(ox - 44, oy - ah / 2, "яскравість", size=11, color=INK, italic=True))
    # яскравість(d): частка потужності, де α = (d/10)·π
    pts = []
    for i in range(0, 101):
        d = 10.0 * i / 100.0
        a = (d / 10.0) * TAU
        f = _power_frac(a)
        pts.append((ox + (d / 10.0) * aw, oy - f * ah))
    p.append(_poly(pts, stroke=POS, sw=2.8))
    # рівні кроки яскравості 25% → нерівні d
    levels = [(0.75, "6.3"), (0.50, "5.0"), (0.25, "3.7")]
    for frac, _ in levels:
        # знайти d, де _power_frac = frac
        lo, hi = 0.0, TAU
        for _ in range(40):
            mid = (lo + hi) / 2
            if _power_frac(mid) > frac:
                lo = mid
            else:
                hi = mid
        a = (lo + hi) / 2
        d = (a / TAU) * 10.0
        gx = ox + (d / 10.0) * aw
        gy = oy - frac * ah
        p.append(line(ox, gy, gx, gy, color=NEG, sw=1.0, dash="4,3"))
        p.append(line(gx, oy, gx, gy, color=NEG, sw=1.0, dash="4,3"))
        p.append(circle(gx, gy, 3.5, fill=NEG, stroke=NEG, sw=1))
        p.append(text(gx, oy + 16, "%.1f" % d, size=9, color=NEG))
    p.append(text(ox + aw / 2, oy - ah - 4, "рівні 25% → нерівні мс", size=10, color=MUTED))

    # права панель: перетворення «ручка → таблиця → мс»
    bx = 410
    knob_x = bx
    tab_x = bx + 150
    out_x = bx + 280
    ys = [90, 150, 210, 270]
    p.append(text(knob_x, 60, "ручка", size=11, color=INK, bold=True))
    p.append(text(tab_x, 60, "d[·]", size=11, color=INK, bold=True))
    p.append(text(out_x, 60, "мс", size=11, color=INK, bold=True))
    knob_lbl = ["100%", "75%", "50%", "25%"]
    ms_lbl = ["GUARD", "6.3", "5.0", "3.7"]
    # таблиця-коробка
    p.append(rect(tab_x - 28, 72, 56, 220, fill="#eef4ff", stroke="#c9d6f0", sw=1.4))
    for i, y in enumerate(ys):
        p.append(circle(knob_x, y, 12, fill=FILL, stroke=INK, sw=1.4))
        p.append(text(knob_x, y + 4, knob_lbl[i], size=9, color=INK))
        p.append(arrow(knob_x + 16, y, tab_x - 32, y, color=MUTED, sw=1.4))
        p.append(arrow(tab_x + 30, y, out_x - 18, y, color=MUTED, sw=1.4))
        p.append(text(out_x, y + 4, ms_lbl[i], size=10, color=POS, anchor="start"))
    p.append(text(bx + 130, H - 12, "рівні поділки ручки → нерівні мілісекунди",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "mapping.svg"), W, H, *p,
           title="Лінійна ручка → нелінійна затримка через таблицю")


if __name__ == "__main__":
    fig_firing_angle()
    fig_power_vs_angle()
    fig_lamp_vs_smps()
    fig_halfwave_integral()
    fig_power_curve()
    fig_timeline()
    fig_mapping()
    print("OK: figures written to", OUT)
