# -*- coding: utf-8 -*-
"""Фігури до теми «Кінетична енергія».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

KE  = "#c0392b"   # кінетична / рух — гаряче червоне
PE  = "#27ae60"   # потенціальна / висота — зелене
COL = "#2457d6"   # допоміжне холодне


# ── Фігура 1: чому квадрат — непарні прирости роботи → квадрати енергії ────────
def fig_why_square():
    W, H = 900, 604
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Чому квадрат: рівні прирости швидкості коштують непарних порцій роботи",
                  size=15.5, bold=True))
    f.append(text(W / 2, 52, "а їхні суми — точні квадрати", size=13, color=MUTED))

    y0 = 438            # база стовпчиків
    unit = 20.0         # px на одиницю енергії (у частках ½mu²)
    axL = 150           # ліва вісь
    axR = 806

    # осі
    f.append(line(axL, y0, axR, y0, color=LINE, sw=1.6))
    f.append(line(axL, y0, axL, y0 - 16.5 * unit, color=LINE, sw=1.6))
    f.append(text(axL - 8, y0 - 16.5 * unit + 4, "енергія", size=12, color=INK, anchor="end"))
    f.append(text(axL - 8, y0 - 16.5 * unit + 20, "(у частках ½mu²)", size=11, color=MUTED, anchor="end"))

    # горизонтальні лінії-квадрати 1,4,9,16
    for e in (1, 4, 9, 16):
        yy = y0 - e * unit
        f.append(line(axL, yy, axR, yy, color="#e6e9ee", sw=1, dash="5,5"))
        f.append(text(axL - 8, yy + 4, str(e), size=11.5, color=MUTED, anchor="end", bold=True))

    bw, gap = 92, 44
    left0 = 210
    vlabs = ("u", "2u", "3u", "4u")
    for k in range(1, 5):
        left = left0 + (k - 1) * (bw + gap)
        cx = left + bw / 2.0
        tot = k * k
        prev = (k - 1) * (k - 1)
        topY = y0 - tot * unit
        # повний стовпчик (накопичена енергія)
        f.append(rect(left, topY, bw, tot * unit, fill="#eef1f4", stroke=LINE, sw=1.3, rx=4))
        # верхня скибка — новий приріст (2k-1), червона
        sliceH = (tot - prev) * unit
        f.append(rect(left, topY, bw, sliceH, fill="#fdecea", stroke=KE, sw=1.6, rx=4))
        # підпис приросту в скибці
        odd = 2 * k - 1
        f.append(text(cx, topY + sliceH / 2.0 + 5, "+%d" % odd, size=14, bold=True, color=KE))
        # накопичений квадрат над стовпчиком
        f.append(text(cx, topY - 12, "= %d" % tot, size=15, bold=True, color=INK))
        # підпис швидкості під віссю
        f.append(text(cx, y0 + 22, vlabs[k - 1], size=13.5, bold=True, color=COL))
        f.append(text(cx, y0 + 40, "крок %d" % k, size=11, color=MUTED))

    f.append(text((210 + 806) / 2.0, y0 + 62, "швидкість (рівними приростами u)", size=12, color=INK))

    # тотожність «сума непарних = квадрат» — у вільному полі над низькими стовпчиками
    f.append(text(238, 96, "сума непарних чисел = квадрат:", size=12, color=MUTED, anchor="start"))
    f.append(mtext(238, 118, ["1 = 1", "1 + 3 = 4", "1 + 3 + 5 = 9", "1 + 3 + 5 + 7 = 16"],
                   size=13, color=INK, anchor="start", lh=1.55, bold=True))

    b, bw2, bh = textbox(W / 2, 558,
                         ["Рівні прирости швидкості коштують дедалі більшої роботи — 1, 3, 5, 7 (непарні числа):",
                          "тіло вже мчить швидше й за однаковий час проходить довший шлях.",
                          "Суми непарних — точні квадрати 1, 4, 9, 16. Тому енергія росте як v², а не як v."],
                         size=12, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "why-square.svg"), W, H, *f)


# ── мала піктограма чашки ─────────────────────────────────────────────────────
def _mug(cx, base, col=INK):
    s = []
    tw, bwd, h = 17, 14, 34            # верх/низ/висота
    poly = [(cx - tw, base - h), (cx + tw, base - h), (cx + bwd, base), (cx - bwd, base)]
    pts = " ".join("%.1f,%.1f" % p for p in poly)
    s.append('<polygon points="%s" fill="#ffffff" stroke="%s" stroke-width="2"/>' % (pts, col))
    s.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="4" fill="#f1f4f8" stroke="%s" stroke-width="1.6"/>'
             % (cx, base - h, tw, col))
    # ручка праворуч
    s.append('<path d="M %.1f %.1f q 20 5 20 13 q 0 8 -20 12" fill="none" stroke="%s" stroke-width="3"/>'
             % (cx + tw - 2, base - h + 7, col))
    # пара
    s.append('<path d="M %.1f %.1f q 6 -8 0 -16" fill="none" stroke="%s" stroke-width="1.6"/>'
             % (cx - 6, base - h - 4, MUTED))
    s.append('<path d="M %.1f %.1f q 6 -8 0 -16" fill="none" stroke="%s" stroke-width="1.6"/>'
             % (cx + 6, base - h - 4, MUTED))
    return "".join(s)


# ── Фігура 2: кінетична енергія відносна — одна чашка, дві системи ─────────────
def fig_frame_relative():
    W, H = 880, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Кінетична енергія залежить від системи відліку: одна чашка — два різні значення",
                  size=15, bold=True))
    f.append(line(W / 2, 62, W / 2, 392, color="#dfe4ea", sw=1.2, dash="4,6"))

    # ── ЛІВОРУЧ: система салону ──
    f.append(text(222, 88, "У системі салону літака", size=13.5, bold=True, color=COL))
    # столик
    tbl_y = 250
    f.append(rect(150, tbl_y, 150, 10, fill="#e9edf2", stroke=LINE, sw=1.3, rx=3))
    f.append(line(168, tbl_y + 10, 168, tbl_y + 40, color=LINE, sw=2))
    f.append(line(282, tbl_y + 10, 282, tbl_y + 40, color=LINE, sw=2))
    f.append(_mug(222, tbl_y))
    # v = 0
    f.append(circle(222, 300, 3.5, fill=INK, stroke=INK, sw=1))
    f.append(text(222, 322, "чашка нерухома:  v = 0", size=12.5, color=INK))
    b1, w1, h1 = textbox(222, 360, "E_к = ½·m·0² = 0", size=15, pad=10,
                         fill="#eef2f9", stroke=COL, sw=1.6, color=COL, bold=True)
    f.append(b1)

    # ── ПРАВОРУЧ: система землі ──
    f.append(text(650, 88, "У системі землі", size=13.5, bold=True, color=KE))
    # чашка з великою стрілкою руху
    mug_y = 200
    f.append(_mug(560, mug_y))
    f.append(arrow(585, mug_y - 17, 748, mug_y - 17, color=KE, sw=3.4))
    f.append(text(668, mug_y - 26, "v = 250 м/с", size=13, bold=True, color=KE))
    # штрихи швидкості
    for dy in (-6, 2, 10):
        f.append(line(540, mug_y - 17 + dy, 556, mug_y - 17 + dy, color="#e0a59c", sw=1.6))
    # земля з маленьким спостерігачем
    gy = 300
    f.append(line(470, gy, 800, gy, color=LINE, sw=2))
    for hx in range(486, 800, 26):
        f.append(line(hx, gy, hx - 8, gy + 9, color=MUTED, sw=1))
    f.append(circle(556, gy - 26, 7, fill="#fef6e7", stroke=INK, sw=1.6))       # голова
    f.append(line(556, gy - 19, 556, gy - 4, color=INK, sw=2))                  # тулуб
    f.append(line(556, gy - 4, 550, gy, color=INK, sw=1.8))
    f.append(line(556, gy - 4, 562, gy, color=INK, sw=1.8))
    f.append(text(556, gy + 18, "спостерігач на землі", size=11, color=MUTED))
    b2, w2, h2 = textbox(650, 360, "E_к = ½·m·(250 м/с)²  — велика", size=14.5, pad=10,
                         fill="#fdecea", stroke=KE, sw=1.6, color=KE, bold=True)
    f.append(b2)

    b, bw2, bh = textbox(W / 2, 440,
                         ["Те саме тіло, дві системи відліку, два різні значення кінетичної енергії — і жодне не «правильніше».",
                          "Кінетична енергія існує лише відносно обраного спостерігача, бо будується на швидкості, а швидкість завжди відносна."],
                         size=12, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "frame-relative.svg"), W, H, *f)


# ── Фігура 3: обмін КЕ ⇄ ПЕ на гірках, сума стала ─────────────────────────────
def _track_y(x):
    """Профіль гірок: спуск у долину (x 90→430), підйом на пагорб (430→700), спад (700→790)."""
    if x <= 430:
        t = (x - 90) / (430 - 90.0)
        return 150 + (360 - 150) * (1 - math.cos(math.pi * t)) / 2.0
    elif x <= 700:
        t = (x - 430) / (700 - 430.0)
        return 360 + (250 - 360) * (1 - math.cos(math.pi * t)) / 2.0
    else:
        t = (x - 700) / (790 - 700.0)
        return 250 + (300 - 250) * (1 - math.cos(math.pi * t)) / 2.0


def fig_energy_exchange():
    W, H = 880, 590
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Американські гірки: кінетична й потенціальна енергія міняються місцями, а сума стала",
                  size=15, bold=True))

    # ── ВЕРХ: колія ──
    y_low = 360.0
    pts = []
    x = 90
    while x <= 790:
        pts.append("%.1f,%.1f" % (x, _track_y(x)))
        x += 4
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(pts), MUTED))
    f.append(line(90, y_low + 2, 790, y_low + 2, color="#e6e9ee", sw=1, dash="4,6"))
    f.append(text(96, y_low - 4, "нижній рівень (h = 0)", size=10.5, color=MUTED, anchor="start"))

    marks = [(150, "A", "вершина"), (430, "B", "низ"), (700, "C", "пагорб")]
    total = 10.0
    data = {}
    for mx, lab, name in marks:
        my = _track_y(mx)
        pe = (y_low - my) / 22.0            # 22 px/одиницю — узгоджено з профілем
        pe = max(0.0, min(total, pe))
        ke = total - pe
        data[lab] = (ke, pe, name)
        # візок
        f.append(rect(mx - 13, my - 15, 26, 14, fill="#fff4e6", stroke=KE, sw=1.8, rx=3))
        f.append(circle(mx - 7, my - 1, 3.4, fill="#444", stroke=INK, sw=1))
        f.append(circle(mx + 7, my - 1, 3.4, fill="#444", stroke=INK, sw=1))
        f.append(text(mx, my - 24, lab, size=14, bold=True, color=INK))
        f.append(line(mx, my + 2, mx, 452, color="#cfd6df", sw=1, dash="3,5"))

    # легенда
    lx, ly = 622, 96
    f.append(rect(lx - 12, ly - 20, 232, 66, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    f.append(rect(lx, ly - 10, 20, 14, fill="#fdecea", stroke=KE, sw=1.5, rx=2))
    f.append(text(lx + 30, ly + 2, "кінетична (рух)", size=12, color=INK, anchor="start"))
    f.append(rect(lx, ly + 14, 20, 14, fill="#e7f6ee", stroke=PE, sw=1.5, rx=2))
    f.append(text(lx + 30, ly + 26, "потенціальна (висота)", size=12, color=INK, anchor="start"))

    # ── НИЗ: стовпчики енергії ──
    yb = 556.0
    u = 10.0                                # px на одиницю
    topline = yb - total * u
    f.append(line(110, topline, 770, topline, color=INK, sw=1.4, dash="7,5"))
    f.append(text(778, topline + 4, "повна енергія — стала", size=11.5, bold=True, color=INK, anchor="start"))

    barw = 60
    for mx, lab, name in marks:
        ke, pe, nm = data[lab]
        left = mx - barw / 2.0
        # кінетична (низ, червона)
        hk = ke * u
        f.append(rect(left, yb - hk, barw, hk, fill="#fdecea", stroke=KE, sw=1.6, rx=3))
        # потенціальна (верх, зелена)
        hp = pe * u
        f.append(rect(left, yb - hk - hp, barw, hp, fill="#e7f6ee", stroke=PE, sw=1.6, rx=3))
        # підписи всередині, якщо влазить
        if hk > 20:
            f.append(text(mx, yb - hk / 2.0 + 4, "%.0f" % round(ke), size=12.5, bold=True, color=KE))
        if hp > 20:
            f.append(text(mx, yb - hk - hp / 2.0 + 4, "%.0f" % round(pe), size=12.5, bold=True, color=PE))
        f.append(text(mx, yb + 18, "%s — %s" % (lab, nm), size=12, bold=True, color=INK))

    return render(os.path.join(IMG, "energy-exchange.svg"), W, H, *f)


# ══════════════════════════════════════════════════════════════════════════════
#  Фігури до математичної вставки «Теорема про кінетичну енергію»
# ══════════════════════════════════════════════════════════════════════════════

# ── Фігура M1: робота змінної сили = площа під кривою F(x) ─────────────────────
def _Fcurve(t):
    """Гладкий позитивний профіль сили F у частках максимуму, t ∈ [0,1]."""
    return 0.34 + 0.42 * math.sin(math.pi * (0.14 + 0.82 * t))


def fig_work_integral():
    W, H = 960, 566
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Робота змінної сили — це площа під кривою F(x), тобто інтеграл ∫F dx",
                  size=15.5, bold=True))
    f.append(text(W / 2, 51, "а заміна змінної під інтегралом віддає рівно ½mv²", size=12.5, color=MUTED))

    # система координат
    x0, x1 = 96, 566
    yb, ytop = 440, 150
    f.append(line(x0, yb, x1 + 18, yb, color=LINE, sw=1.7))
    f.append(line(x0, yb, x0, ytop - 6, color=LINE, sw=1.7))
    f.append(text(x0 - 10, ytop + 2, "сила", size=12, color=INK, anchor="end"))
    f.append(text(x0 - 10, ytop + 18, "F", size=12, color=INK, anchor="end", italic=True))
    f.append(text(x1 + 20, yb + 20, "переміщення x", size=12, color=INK, anchor="end"))

    span = x1 - x0
    amp = yb - ytop            # px на повну (одиничну) силу

    # рімановi смужки ΣF·Δx
    N = 11
    for i in range(N):
        t = (i + 0.5) / N
        h = _Fcurve(t) * amp
        left = x0 + (x1 - x0) * i / N
        wdt = span / N
        f.append(rect(left, yb - h, wdt, h, fill="#fdecea", stroke="#e7a49b", sw=1.0, rx=0))

    # гладка крива F(x) поверх смужок
    pts = []
    steps = 90
    for k in range(steps + 1):
        t = k / steps
        px = x0 + span * t
        py = yb - _Fcurve(t) * amp
        pts.append("%.1f,%.1f" % (px, py))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(pts), KE))

    # виділити одну смужку як «F·Δx»
    j = 6
    t = (j + 0.5) / N
    h = _Fcurve(t) * amp
    left = x0 + span * j / N
    wdt = span / N
    f.append(rect(left, yb - h, wdt, h, fill="none", stroke=INK, sw=1.6, rx=0))
    f.append(line(left, yb + 4, left + wdt, yb + 4, color=INK, sw=1.4))
    f.append(text(left + wdt / 2, yb + 20, "Δx", size=11.5, color=INK))
    f.append(text(left + wdt / 2, yb - h - 8, "F", size=11.5, italic=True, color=INK))

    # підпис площі
    f.append(text(x0 + span * 0.34, yb - 74, "W = ∫ F dx", size=17, bold=True, color=KE))
    f.append(text(x0 + span * 0.34, yb - 52, "= площа під кривою", size=12, color=MUTED))

    # права колонка — ланцюжок підстановок
    box, bw, bh = textbox(770, 250,
                          ["F dx  =  m (dv/dt) dx",
                           "         =  m (dx/dt) dv  =  m·v dv",
                           "∫ m·v dv  =  m · ½v²",
                           "  =  ½mv²кінц − ½mv²поч"],
                          size=13.5, pad=13, fill="#f7f9fc", stroke=COL, sw=1.5,
                          color=INK, bold=True)
    f.append(box)
    f.append(text(770, 250 - bh / 2 - 10, "ключ — заміна змінної:", size=12, color=MUTED))
    f.append(text(770, 250 + bh / 2 + 22, "∫v dv = ½v²  дає і ½, і квадрат", size=12.5, bold=True, color=KE))

    b, bw2, bh2 = textbox(W / 2, 520,
                          ["Стала сила: робота = F·d (прямокутник). Змінна: січемо шлях на кроки Δx, на кожному F майже стала,",
                           "сумуємо F·Δx і згущуємо крок — сума стає інтегралом ∫F dx, тобто площею під кривою F(x)."],
                          size=12, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "work-integral.svg"), W, H, *f)


# ── Фігура M2: роботу виконує лише поздовжня складова сили ─────────────────────
def fig_dot_work():
    W, H = 960, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Роботу виконує лише складова сили вздовж руху; поперечна — нуль",
                  size=15.5, bold=True))
    f.append(line(540, 66, 540, 520, color="#dfe4ea", sw=1.2, dash="4,6"))

    # ── ЛІВОРУЧ: розклад F на F∥ і F⊥ ──
    Ox, Oy = 150, 300
    dx = 330                       # довжина переміщення
    f.append(arrow(Ox, Oy, Ox + dx, Oy, color=INK, sw=2.6))
    f.append(text(Ox + dx - 18, Oy + 24, "dr  (переміщення)", size=12.5, color=INK, anchor="end"))

    # сила під кутом
    ang = math.radians(34)
    FL = 250
    Fx = Ox + FL * math.cos(ang)
    Fy = Oy - FL * math.sin(ang)
    f.append(arrow(Ox, Oy, Fx, Fy, color=KE, sw=3.2))
    f.append(text(Fx + 6, Fy - 8, "F", size=15, bold=True, italic=True, color=KE))

    # поздовжня складова (проєкція на dr)
    projx = Ox + FL * math.cos(ang)
    f.append(arrow(Ox, Oy, projx, Oy, color="#1f7a3d", sw=3.0))
    f.append(text((Ox + projx) / 2, Oy + 40, "F∥ = F·cosθ  (виконує роботу)",
                  size=12.5, bold=True, color="#1f7a3d"))
    # поперечна складова (пунктир вгору від кінця проєкції до вершини F)
    f.append(line(projx, Oy, projx, Fy, color=COL, sw=2.2, dash="5,4"))
    f.append(text(projx + 10, (Oy + Fy) / 2, "F⊥", size=13, bold=True, color=COL, anchor="start"))
    f.append(text(projx + 10, (Oy + Fy) / 2 + 18, "роботи 0", size=11, color=COL, anchor="start"))
    # прямий кут
    f.append('<path d="M %.1f %.1f h -12 v -12" fill="none" stroke="%s" stroke-width="1.4"/>'
             % (projx, Oy, MUTED))
    # дуга кута θ
    f.append('<path d="M %.1f %.1f A 44 44 0 0 0 %.1f %.1f" fill="none" stroke="%s" stroke-width="1.6"/>'
             % (Ox + 44, Oy, Ox + 44 * math.cos(ang), Oy - 44 * math.sin(ang), MUTED))
    f.append(text(Ox + 60, Oy - 20, "θ", size=13, italic=True, color=MUTED))

    fb, fbw, fbh = textbox(300, 430,
                           ["W = F · dr = F·d·cosθ = F∥·d"],
                           size=13.5, pad=11, fill="#eef2f9", stroke=COL, sw=1.5, color=INK, bold=True)
    f.append(fb)

    # ── ПРАВОРУЧ: три випадки нульової роботи поперечної сили ──
    f.append(text(750, 88, "Поперечна сила → нуль роботи → стала швидкість", size=12.5, bold=True, color=COL))

    # 1) камінь на мотузці
    cx, cy, R = 660, 170, 46
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="4,5"/>'
             % (cx, cy, R, MUTED))
    f.append(circle(cx, cy, 3.5, fill=INK, stroke=INK, sw=1))
    px, py = cx, cy - R
    f.append(circle(px, py, 6, fill="#fdecea", stroke=KE, sw=1.8))
    f.append(arrow(px, py, cx, cy, color=COL, sw=2.2))            # натяг до центра
    f.append(arrow(px, py, px + 40, py, color=KE, sw=2.4))         # швидкість дотична
    f.append(text(px + 44, py - 6, "v", size=12, italic=True, bold=True, color=KE, anchor="start"))
    f.append(text(cx + 8, cy - 18, "натяг", size=11, color=COL, anchor="start"))
    f.append(text(760, 150, "камінь на мотузці:", size=12, bold=True, color=INK, anchor="start"))
    f.append(text(760, 168, "натяг ⊥ v  →  W = 0", size=11.5, color=MUTED, anchor="start"))
    f.append(text(760, 184, "модуль швидкості сталий", size=11.5, color=MUTED, anchor="start"))

    # 2) супутник на орбіті
    cx2, cy2, R2 = 660, 300, 42
    f.append(circle(cx2, cy2, 13, fill="#eef2f9", stroke=COL, sw=1.6))
    f.append(text(cx2, cy2 + 4, "M", size=11, bold=True, color=COL))
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="4,5"/>'
             % (cx2, cy2, R2, MUTED))
    sx, sy = cx2 + R2, cy2
    f.append(circle(sx, sy, 5.5, fill="#fdecea", stroke=KE, sw=1.8))
    f.append(arrow(sx, sy, cx2 + 12, cy2, color=COL, sw=2.2))       # тяжіння до центра
    f.append(arrow(sx, sy, sx, sy - 38, color=KE, sw=2.4))          # швидкість дотична
    f.append(text(760, 286, "супутник на орбіті:", size=12, bold=True, color=INK, anchor="start"))
    f.append(text(760, 304, "тяжіння (доцентрове) ⊥ v", size=11.5, color=MUTED, anchor="start"))
    f.append(text(760, 320, "стала орбітальна швидкість", size=11.5, color=MUTED, anchor="start"))

    # 3) тяжіння на горизонтальному русі
    bx, by = 620, 430
    f.append(arrow(bx, by, bx + 70, by, color=KE, sw=2.6))          # рух горизонтальний
    f.append(text(bx + 30, by - 8, "рух", size=11, color=KE))
    f.append(arrow(bx + 35, by, bx + 35, by + 40, color=COL, sw=2.4))  # mg вниз
    f.append(text(bx + 42, by + 30, "mg", size=11.5, color=COL, anchor="start"))
    f.append(text(760, 420, "горизонтальний рух:", size=12, bold=True, color=INK, anchor="start"))
    f.append(text(760, 438, "тяжіння mg ⊥ переміщенню", size=11.5, color=MUTED, anchor="start"))
    f.append(text(760, 454, "W = 0 (висота не міняється)", size=11.5, color=MUTED, anchor="start"))

    f.append(text(750, 494, "також: нормальна реакція опори, сила Лоренца qv×B", size=11, color=MUTED, italic=True))

    b, bw, bh = textbox(W / 2, 534,
                        ["Скалярний добуток F·dr вибирає лише проєкцію сили на напрям руху: сила поперек переміщення руху не пришвидшує."],
                        size=12, pad=10, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "dot-work.svg"), W, H, *f)


# ── Фігура M3: ½Iω² зі суми ½Σmᵢvᵢ² ───────────────────────────────────────────
def fig_rotational_ke():
    W, H = 960, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Обертальна ½Iω² — це сума ½mᵢvᵢ² усіх частинок, де vᵢ = ω·rᵢ",
                  size=15.5, bold=True))

    # диск
    cx, cy, Rd = 250, 285, 155
    f.append(circle(cx, cy, Rd, fill="#f4f6f8", stroke=LINE, sw=1.8))
    f.append(circle(cx, cy, 4, fill=INK, stroke=INK, sw=1))
    f.append(text(cx, cy + 22, "вісь", size=11.5, color=MUTED))

    # дуга кутової швидкості ω
    f.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" fill="none" stroke="%s" stroke-width="2.4" marker-end="url(#arrow)"/>'
             % (cx + Rd + 20, cy - 26, Rd + 20, Rd + 20, cx + Rd + 4, cy + 34, COL))
    f.append(text(cx + Rd + 40, cy - 4, "ω", size=16, bold=True, italic=True, color=COL))

    # частинки на спиці вправо, швидкість ∝ r
    radii = [46, 92, 132]
    for r in radii:
        ex, ey = cx + r, cy
        f.append(line(cx, cy, ex, ey, color="#cfd6df", sw=1))
        f.append(circle(ex, ey, 6.5, fill="#fdecea", stroke=KE, sw=1.8))
        vlen = r * 0.52
        f.append(arrow(ex, ey, ex, ey - vlen, color=KE, sw=2.4))
    # підписи для зовнішньої частинки
    ex, ey = cx + radii[-1], cy
    f.append(text(ex + 10, ey - radii[-1] * 0.52 + 6, "vᵢ = ω·rᵢ", size=12.5, bold=True, color=KE, anchor="start"))
    f.append(text(cx + radii[-1] / 2, cy + 18, "rᵢ", size=12, italic=True, color=INK))
    f.append(text(cx + radii[0] - 4, cy - 12, "mᵢ", size=11.5, color=INK, anchor="end"))

    # права колонка — виведення
    box, bw, bh = textbox(690, 250,
                          ["E = Σ ½ mᵢ vᵢ²",
                           "vᵢ = ω·rᵢ   (кутова швидкість × плече)",
                           "= Σ ½ mᵢ (ω rᵢ)²",
                           "= ½ (Σ mᵢ rᵢ²) ω²",
                           "= ½ I ω²"],
                          size=14, pad=14, fill="#f7f9fc", stroke=COL, sw=1.5, color=INK, bold=True)
    f.append(box)
    f.append(text(690, 250 + bh / 2 + 24,
                  "I = Σ mᵢ rᵢ² — момент інерції;  ω спільна для всіх (тверде тіло) — виноситься",
                  size=11.5, color=MUTED))

    b, bw2, bh2 = textbox(W / 2, 464,
                         ["Та сама будова, що й ½mv²: половина · «інертність» · квадрат «швидкості» — тільки інертність тепер обертальна (I), а швидкість кутова (ω)."],
                         size=12, pad=10, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "rotational-ke.svg"), W, H, *f)


# ══════════════════════════════════════════════════════════════════════════════
#  Фігури до вставки «Зіткнення двох тіл» (proj-collision-energy)
# ══════════════════════════════════════════════════════════════════════════════

def _cball(cx, cy, r, col, lab):
    """Куля-тіло: коло з легкою заливкою + позначка маси всередині."""
    lf = "#fdecea" if col == KE else ("#eaf0fd" if col == COL else "#e7f6ee")
    s = circle(cx, cy, r, fill=lf, stroke=col, sw=2.3)
    s += text(cx, cy + 5, lab, size=13, bold=True, color=col)
    return s


def _vel(cx, cy, val, vscale, col, label):
    """Горизонтальна стрілка швидкості з підписом (val знаковий; ~0 → тільки підпис)."""
    if abs(val) < 0.2:
        return text(cx, cy, label if label else "0", size=11.5, color=MUTED, bold=True)
    L = abs(val) * vscale
    x2 = cx + L if val > 0 else cx - L
    s = arrow(cx, cy, x2, cy, color=col, sw=2.6)
    s += text((cx + x2) / 2, cy - 8, label, size=11.5, bold=True, color=col)
    return s


# ── Фігура C1: три режими пружного удару за відношенням мас ────────────────────
def fig_elastic_regimes():
    W, H = 930, 600
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Пружний удар у нерухому ціль: результат вирішує відношення мас",
                  size=15.5, bold=True))
    f.append(text(W / 2, 49, "маси й швидкість налітача ті самі — а розліт щоразу інший", size=12.5, color=MUTED))

    Bx, Ax = 300, 700       # центри сцен «до» / «після»
    vs = 20.0               # px на одиницю швидкості
    bands = [
        ("Рівні маси   m₁ = m₂", "m", "m", 20, 20, 0.0, 2.0, None, "v = u",
         "швидкості міняються місцями: налітач спиняється, ціль зривається з тією ж швидкістю"),
        ("Важке б'є легке   m₁ ≫ m₂", "M", "m", 30, 13, 2.0, 4.0, "≈ u", "≈ 2u",
         "важке майже не гальмує, а легке відлітає вдвічі прудкіше за налітача"),
        ("Легке б'є важке   m₁ ≪ m₂", "m", "M", 13, 30, -2.0, 0.0, "≈ −u", "≈ 0",
         "легке відскакує назад, важке ледь зрушується — як м'яч від стіни"),
    ]
    cys = [140, 300, 458]
    for (name, l1, l2, r1, r2, v1, v2, a1, a2, desc), cy in zip(bands, cys):
        f.append(text(38, cy - 4, name, size=12.5, bold=True, color=INK, anchor="start"))
        # «до»
        f.append(text(Bx, cy - 66, "до", size=12, color=MUTED))
        b1x, b2x = Bx - 44, Bx + 44
        f.append(_cball(b1x, cy, r1, KE, l1))
        f.append(_cball(b2x, cy, r2, COL, l2))
        f.append(_vel(b1x, cy - r1 - 16, 2.0, vs, KE, "u"))
        f.append(text(b2x, cy - r2 - 14, "0", size=11.5, color=MUTED, bold=True))
        # перехід
        f.append(arrow(Bx + 120, cy, Ax - 150, cy, color=INK, sw=2.0))
        f.append(text((Bx + 120 + Ax - 150) / 2, cy - 12, "пружний", size=11, color=MUTED))
        # «після»
        f.append(text(Ax, cy - 66, "після", size=12, color=MUTED))
        a1x, a2x = Ax - 54, Ax + 62
        f.append(_cball(a1x, cy, r1, KE, l1))
        f.append(_cball(a2x, cy, r2, COL, l2))
        f.append(_vel(a1x, cy - r1 - 16, v1, vs, KE, a1))
        f.append(_vel(a2x, cy - r2 - 16, v2, vs, COL, a2))
        # опис
        f.append(text(W / 2, cy + max(r1, r2) + 30, desc, size=11.5, color=INK))

    b, bw, bh = textbox(W / 2, 566,
                        ["Той самий налітач, той самий пружний удар — а розліт диктує лише відношення мас:",
                         "рівні маси міняються швидкостями; важке пробиває крізь; легке відскакує, майже не зрушивши ціль."],
                        size=12, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "collision-elastic-regimes.svg"), W, H, *f)


# ── Фігура C2: імпульс сталий; КЕ = зафіксована + e²·відносна ──────────────────
def fig_collision_ledger():
    W, H = 900, 606
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Імпульс той самий при будь-якому e; губиться лише «відносна» частка енергії, і то в e² разів",
                  size=14, bold=True))
    f.append(text(W / 2, 49, "приклад:  m₁ = 2 кг, u₁ = 3 м/с   б'є нерухоме   m₂ = 1 кг", size=12.5, color=MUTED))

    base = 440
    KEcm, KErel, P = 6.0, 3.0, 6.0
    ue, up = 25.0, 24.0
    es = [(1.0, "e = 1", "9 Дж", "пружний", None),
          (0.5, "e = ½", "6.75 Дж", "", "−2.25"),
          (0.0, "e = 0", "6 Дж", "злипання", "−3")]

    # ── ЛІВОРУЧ: імпульс — три однакові стовпчики ──
    f.append(text(178, 96, "ІМПУЛЬС", size=13, bold=True, color=INK))
    f.append(text(178, 113, "p = m₁u₁ + m₂u₂", size=11.5, color=MUTED))
    mx0 = 100
    for i, (e, elab, _, _, _) in enumerate(es):
        x = mx0 + i * 58
        h = P * up
        f.append(rect(x, base - h, 40, h, fill="#eaf0fd", stroke=COL, sw=1.7, rx=3))
        f.append(text(x + 20, base - h - 8, "6", size=12.5, bold=True, color=COL))
        f.append(text(x + 20, base + 16, elab, size=11, color=INK))
    f.append(text(178, base + 40, "не залежить від e", size=11.5, italic=True, color=COL))

    f.append(line(342, 74, 342, 470, color="#dfe4ea", sw=1.2, dash="4,6"))

    # ── ПРАВОРУЧ: кінетична енергія — складені стовпчики ──
    f.append(text(628, 96, "КІНЕТИЧНА ЕНЕРГІЯ", size=13, bold=True, color=INK))
    yb9 = base - (KEcm + KErel) * ue
    f.append(line(402, yb9, 852, yb9, color=INK, sw=1.3, dash="7,5"))
    f.append(text(850, yb9 - 7, "КЕ до = 9 Дж", size=11, bold=True, color=INK, anchor="end"))

    ex0 = 432
    for i, (e, elab, keaf, note, lostlab) in enumerate(es):
        x = ex0 + i * 138
        w = 92
        hc = KEcm * ue
        hk = e * e * KErel * ue
        hl = (1 - e * e) * KErel * ue
        # зафіксована (рух центра мас) — зелена, недоторка
        f.append(rect(x, base - hc, w, hc, fill="#e7f6ee", stroke=FIELD, sw=1.7, rx=3))
        if i == 0:
            f.append(text(x + w / 2, base - hc / 2 + 4, "6 Дж", size=12, bold=True, color="#1f7a3d"))
        # збережена відносна — червона
        if hk > 3:
            f.append(rect(x, base - hc - hk, w, hk, fill="#fdecea", stroke=KE, sw=1.7, rx=3))
            if hk > 34:
                f.append(text(x + w / 2, base - hc - hk / 2 + 4, "3 Дж", size=12, bold=True, color=KE))
        # втрачена на тепло — сіра, пунктирна рамка
        if hl > 3:
            yl = base - hc - hk - hl
            f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="#f2f3f5" '
                     'stroke="%s" stroke-width="1.5" stroke-dasharray="5,4"/>' % (x, yl, w, hl, POS))
            f.append(text(x + w / 2, yl + hl / 2 + 4, lostlab, size=12, bold=True, color=POS))
        # підписи під стовпчиком
        f.append(text(x + w / 2, base + 16, elab, size=12, bold=True, color=INK))
        f.append(text(x + w / 2, base + 31, "КЕ = " + keaf, size=10.5, color=MUTED))
        if note:
            f.append(text(x + w / 2, base + 46, note, size=10.5, italic=True, color=INK))

    # ── легенда ──
    ly = 512
    f.append(rect(96, ly - 11, 18, 14, fill="#e7f6ee", stroke=FIELD, sw=1.5, rx=2))
    f.append(text(120, ly + 1, "зафіксована рухом центра мас (6 Дж) — недоторка", size=11, color=INK, anchor="start"))
    f.append(rect(96, ly + 13, 18, 14, fill="#fdecea", stroke=KE, sw=1.5, rx=2))
    f.append(text(120, ly + 25, "збережена відносна = e²·3 Дж", size=11, color=INK, anchor="start"))
    f.append('<rect x="516" y="%.1f" width="18" height="14" rx="2" fill="#f2f3f5" stroke="%s" '
             'stroke-width="1.5" stroke-dasharray="5,4"/>' % (ly - 11, POS))
    f.append(text(540, ly + 1, "втрачена на тепло = (1−e²)·3 Дж", size=11, color=INK, anchor="start"))

    b, bw, bh = textbox(W / 2, 574,
                        ["Рух центра мас (6 Дж) заморожено збереженням імпульсу — його не спалити нічим.",
                         "Спалити можна лише відносний рух (3 Дж); e = 0 палить його весь — це й є максимум утрати."],
                        size=12, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "collision-energy-ledger.svg"), W, H, *f)


# ══════════════════════════════════════════════════════════════════════════════
#  Фігури до історичної вставки «Жива сила» (hist-vis-viva)
# ══════════════════════════════════════════════════════════════════════════════

CLAY  = "#e7d7b8"   # глина
CLAYD = "#b79b6b"   # темніша глина / контур
BRASS = "#c9a24b"   # латунна кулька


def _down_arrow(cx, y1, y2, col, sw=3.4):
    """Стрілка вниз власним трикутником (щоб вістря було потрібного кольору)."""
    s = [line(cx, y1, cx, y2 - 6, color=col, sw=sw)]
    s.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
             % (cx - 6, y2 - 8, cx + 6, y2 - 8, cx, y2, col))
    return "".join(s)


def _clay_column(cx, y_surf, depth, rw, num, vlab):
    """Стовпчик досліду: кулька зі стрілкою швидкості + брусок глини з дентом ∝ v²."""
    s = []
    by = 104
    L = {1: 30, 2: 58, 3: 86}[num]
    # штрихи руху за кулькою
    for dx in (26, 34, 42):
        s.append(line(cx - dx, by - 6, cx - dx + 10, by - 6, color="#e6b7ae", sw=2))
        s.append(line(cx - dx, by + 4, cx - dx + 10, by + 4, color="#e6b7ae", sw=2))
    s.append(circle(cx, by, 14, fill=BRASS, stroke=CLAYD, sw=1.6))
    s.append(_down_arrow(cx, by + 20, by + 20 + L, KE))
    s.append(text(cx + 22, by + 20 + L / 2.0 + 5, vlab, size=15, bold=True, color=KE, anchor="start"))

    # брусок глини
    bx, bw, bh = cx - 88, 176, 196
    s.append(rect(bx, y_surf, bw, bh, fill=CLAY, stroke=CLAYD, sw=1.4, rx=4))
    s.append(line(bx, y_surf, bx + bw, y_surf, color=CLAYD, sw=1.8))
    # дент — біла парабола вглиб (глибина depth у центрі)
    s.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f Z" fill="%s" stroke="none"/>'
             % (cx - rw, y_surf, cx, y_surf + 2 * depth, cx + rw, y_surf, BG))
    s.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="1.8"/>'
             % (cx - rw, y_surf, cx, y_surf + 2 * depth, cx + rw, y_surf, CLAYD))
    # кулька, що засіла на дні дента
    s.append(circle(cx, y_surf + depth - 7, 12, fill=BRASS, stroke=CLAYD, sw=1.6))
    # мірка глибини праворуч від бруска
    mx = cx + 88 + 14
    s.append(line(mx, y_surf, mx, y_surf + depth, color=COL, sw=1.4, dash="3,4"))
    s.append(line(mx - 5, y_surf, mx + 5, y_surf, color=COL, sw=1.4))
    s.append(line(mx - 5, y_surf + depth, mx + 5, y_surf + depth, color=COL, sw=1.4))
    # велике число глибини (v²) під бруском
    s.append(text(cx, y_surf + bh + 34, str(num * num), size=23, bold=True, color=KE))
    return "".join(s)


def fig_gravesande():
    W, H = 900, 604
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Дослід 'с Гравезанде: глибина сліду в глині росте як квадрат швидкості",
                  size=15, bold=True))

    y_surf = 250.0
    for cx, depth, rw, num, vlab in [(200, 15.0, 30, 1, "v"),
                                     (460, 60.0, 40, 2, "2v"),
                                     (720, 135.0, 50, 3, "3v")]:
        f.append(_clay_column(cx, y_surf, depth, rw, num, vlab))

    f.append(text(W / 2, 524, "глибина сліду росте як v²   (1 : 4 : 9)", size=13.5, bold=True, color=KE))

    b, bw2, bh2 = textbox(W / 2, 574,
                          ["Виміряно (слід у глині):  1 : 4 : 9  =  v²   →  міра руху ∝ mv²   ✓",
                           "Якби мірою руху було mv, сліди відносилися б як 1 : 2 : 3   ✗"],
                          size=12, pad=10, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "hist-gravesande.svg"), W, H, *f)


def fig_timeline():
    W, H = 940, 742
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Народження поняття: майже двісті років від «живої сили» до «кінетичної енергії»",
                  size=15, bold=True))

    spine = 190
    y0, step = 106, 96
    f.append(line(spine, y0 - 30, spine, y0 + 6 * step + 30, color="#cfd6df", sw=2.6))

    rows = [
        ("1686", "Ляйбніц — «Коротка демонстрація помилки Декарта»",
         ["Сила руху тіла йде як mv², а не як «кількість руху» mv.",
          "Спалах майже столітньої суперечки з картезіанцями."], KE),
        ("1695", "Ляйбніц — «Зразок динаміки»",
         ["Величина mv² дістає ім'я vis viva — «жива сила»,",
          "на противагу «мертвій силі» спокою."], KE),
        ("1722", "'с Гравезанде — кульки в глину (Лейден)",
         ["Глибина сліду росте як v²: удвічі швидша куля —",
          "вчетверо глибший слід. Дослід стає на бік mv²."], COL),
        ("1740", "Емілі дю Шатле — «Начала фізики»",
         ["Синтез Ляйбніца й Ньютона; енергію («живу силу»)",
          "вперше чітко відділено від імпульсу («кількості руху»)."], FIELD),
        ("1829", "Коріоліс — «Про обчислення дії машин»",
         ["Додає множник ½ і слово travail — «робота».",
          "Виходить сучасне ½mv²."], INK),
        ("1849–51", "Вільям Томсон (лорд Кельвін)",
         ["Дає англійську назву kinetic energy —",
          "«кінетична енергія»."], INK),
        ("1853", "Вільям Ренкін",
         ["Парна назва potential energy —",
          "«потенціальна енергія»."], INK),
    ]

    cx0 = spine + 24
    cw = W - cx0 - 24
    for i, (yr, head, desc, col) in enumerate(rows):
        yc = y0 + i * step
        ch = 22 + len(desc) * 17 + 16
        cy0 = yc - ch / 2.0
        f.append(rect(cx0, cy0, cw, ch, fill=FILL, stroke=LINE, sw=1.1, rx=6))
        f.append(rect(cx0 + 3, cy0 + 4, 4, ch - 8, fill=col, stroke='none', sw=0, rx=2))
        f.append(text(cx0 + 18, cy0 + 22, head, size=13.5, bold=True, color=col, anchor="start"))
        f.append(mtext(cx0 + 18, cy0 + 41, desc, size=12, color=MUTED, anchor="start", lh=1.42))
        f.append(circle(spine, yc, 7.5, fill=BG, stroke=col, sw=2.6))
        f.append(circle(spine, yc, 2.8, fill=col, stroke=col, sw=1))
        f.append(text(spine - 20, yc + 5, yr, size=14, bold=True, color=col, anchor="end"))

    return render(os.path.join(IMG, "hist-vis-viva-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_why_square()
    fig_frame_relative()
    fig_energy_exchange()
    fig_work_integral()
    fig_dot_work()
    fig_rotational_ke()
    fig_elastic_regimes()
    fig_collision_ledger()
    fig_gravesande()
    fig_timeline()
    print("OK: фігури у", IMG)
