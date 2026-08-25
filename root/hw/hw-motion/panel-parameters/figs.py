# -*- coding: utf-8 -*-
"""Фігури до теми «Параметри панелі».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

import math

# Локальні відтінки понад палітру svgkit
AMBER = "#b9770e"   # світло / відблиск (тепле, читабельне)
GLASS = "#a9c8dd"   # скло панелі
GLASSL = "#5d7e93"  # обведення скла


# ── 1. Роздільність, PPI і кутовий розмір пікселя проти межі ока ──────────────
def fig_ppi():
    W, H = 760, 380
    f = [text(W / 2, 26, "PPI і кутовий розмір пікселя на оці", size=16, bold=True),
         text(W / 2, 47, "важить не кількість пікселів, а їхній кутовий розмір",
              size=11.5, color=MUTED, italic=True)]

    # око
    f.append('<ellipse cx="90" cy="190" rx="16" ry="9" fill="%s" stroke="%s" stroke-width="2"/>' % (BG, INK))
    f.append(circle(90, 190, 4.5, fill=INK, stroke=INK, sw=1))
    f.append(text(90, 224, "око", size=11, color=MUTED))

    # сітка пікселів екрана (5×4)
    gx, gy, cell = 500, 142, 18
    for r in range(4):
        for c in range(5):
            fill = "#dff0e2" if (r == 0 and c == 0) else BG
            f.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="%s" stroke-width="1"/>'
                     % (gx + c * cell, gy + r * cell, cell, cell, fill, MUTED))
    f.append(text(gx + 2.5 * cell, gy + 4 * cell + 18, "сітка пікселів екрана", size=11, color=MUTED))

    # відстань d
    f.append(line(110, 190, gx, 190, color=MUTED, sw=1.4, dash="5 4"))
    f.append(text((110 + gx) / 2, 182, "відстань d", size=12))

    # кут α на верхній піксель
    f.append(line(110, 190, gx, gy, color=INK, sw=1.6))
    f.append(line(110, 190, gx, gy + cell, color=INK, sw=1.6))
    f.append(text(gx - 24, gy + cell - 3, "α", size=14, bold=True, anchor="end"))
    f.append(text(gx + 5.5 * cell + 6, gy + cell, "1 піксель", size=11, anchor="start"))

    # формули внизу
    f.append(text(W / 2, 300, "PPI = (пікселів по діагоналі) ÷ (діагональ панелі, дюйми)", size=12.5))
    f.append(text(W / 2, 324, "кутовий розмір пікселя:  α = крок пікселя ÷ d", size=12.5))
    f.append(text(W / 2, 348, "око розрізняє ≈ 1′ = 1/60°", size=12.5))
    f.append(text(W / 2, 372, "α < 1′ — окремих пікселів не видно (ефект «retina»)",
                  size=12.5, color=FIELD, bold=True))
    render(os.path.join(IMG, "ppi.svg"), W, H, *f)


# ── 2. Шкала яскравості в нітах для різних середовищ ──────────────────────────
def fig_nits():
    W, H = 760, 260
    f = [text(W / 2, 26, "Скільки нітів треба для середовища", size=16, bold=True),
         text(W / 2, 47, "цифра «нітів» нічого не варта без середовища, де екран читатимуть",
              size=11.5, color=MUTED, italic=True)]

    x0, x1, y = 70, 700, 150           # вісь
    lo_log, hi_log = 0.0, 4.0          # 1 .. 10000 (log10)

    def X(nit):
        return x0 + (math.log10(nit) - lo_log) / (hi_log - lo_log) * (x1 - x0)

    # смуги-середовища
    bands = [(1, 30, "#dfe7ef", "ніч"), (30, 300, "#cfe6d3", "кімната / офіс"),
             (300, 700, "#fff0c2", "день"), (700, 10000, "#f7d7c0", "пряме сонце")]
    for a, b, col, lab in bands:
        xa, xb = X(a), X(b)
        f.append('<rect x="%.1f" y="%d" width="%.1f" height="30" fill="%s" stroke="%s" stroke-width="1"/>'
                 % (xa, y - 41, xb - xa, col, MUTED))
        f.append(text((xa + xb) / 2, y - 21, lab, size=11.5))

    # вісь і поділки
    f.append(line(x0, y, x1, y, color=INK, sw=2))
    for nit in (1, 10, 100, 1000, 10000):
        xx = X(nit)
        f.append(line(xx, y - 6, xx, y + 6, color=INK, sw=1.4))
        f.append(text(xx, y + 22, str(nit), size=11))

    # маркери реальних точок
    for nit, lab in ((250, "типовий TFT"), (500, "вулиця"), (1200, "для сонця")):
        xx = X(nit)
        f.append(circle(xx, y, 5, fill=FIELD, stroke=FIELD, sw=1))
        f.append(text(xx, y - 12, lab, size=10.5, color=FIELD, bold=True))

    f.append(text(W / 2, 222, "шкала логарифмічна: «вуличний» екран яскравіший за кімнатний у рази, не на відсотки",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "nits.svg"), W, H, *f)


# ── 3. Контраст і рівень чорного: LCD проти OLED, і вплив відблиску ───────────
def fig_contrast():
    W, H = 760, 320
    f = [text(W / 2, 26, "Контраст = білий ÷ чорний; на світлі він падає", size=16, bold=True)]

    def panel(cx, head, black_fill, black_lab, ratio):
        bx = cx - 75
        f.append(text(cx, 78, head, size=13, bold=True))
        f.append('<rect x="%d" y="86" width="150" height="72" fill="%s" stroke="%s" stroke-width="1.5"/>'
                 % (bx, BG, INK))
        f.append('<rect x="%d" y="158" width="150" height="72" fill="%s" stroke="%s" stroke-width="1.5"/>'
                 % (bx, black_fill, INK))
        f.append(text(cx, 126, "білий ≈ 300", size=11))
        f.append(text(cx, 198, black_lab, size=11, color=BG))
        f.append(text(cx, 256, ratio, size=13, color=FIELD, bold=True))

    panel(225, "LCD (заслінка протікає)", "#3b3f44", "чорний ≈ 0.3", "контраст ≈ 1000 : 1")
    panel(560, "OLED (піксель вимкнено)", "#0b0b0b", "чорний = 0", "контраст ≈ ∞")

    # сонце посередині, що додає світла чорному
    f.append(circle(392, 96, 11, fill="#fff4c2", stroke=AMBER, sw=2))
    for k in range(8):
        a = k * math.pi / 4
        f.append(line(392 + 13 * math.cos(a), 96 + 13 * math.sin(a),
                      392 + 19 * math.cos(a), 96 + 19 * math.sin(a), color=AMBER, sw=1.5))
    f.append(arrow(384, 110, 250, 200, color=AMBER, sw=1.8))
    f.append(arrow(400, 110, 545, 200, color=AMBER, sw=1.8))

    f.append(text(W / 2, 296, "відблиск додає світла ЧОРНОМУ — реальний контраст просідає, надто в LCD",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "contrast.svg"), W, H, *f)


# ── 4. Чому TN блякне збоку, а IPS — ні: орієнтація молекул ───────────────────
def fig_angles_mech():
    W, H = 760, 340
    f = [text(W / 2, 26, "Кути огляду: чому TN блякне збоку, а IPS — майже ні", size=16, bold=True)]

    def stack(cx, head, note):
        sx = cx - 92
        f.append(text(cx, 116, head, size=13, bold=True))
        f.append('<rect x="%d" y="136" width="184" height="9" rx="2" fill="%s" stroke="%s" stroke-width="1.4"/>'
                 % (sx, GLASS, GLASSL))
        f.append('<rect x="%d" y="238" width="184" height="9" rx="2" fill="%s" stroke="%s" stroke-width="1.4"/>'
                 % (sx, GLASS, GLASSL))
        f.append(text(cx, 268, note, size=10.5, color=MUTED))
        # око прямо
        f.append('<ellipse cx="%d" cy="102" rx="16" ry="9" fill="%s" stroke="%s" stroke-width="2"/>' % (cx, BG, INK))
        f.append(circle(cx, 104, 4.5, fill=INK, stroke=INK, sw=1))
        f.append(text(cx, 92, "прямо", size=10, color=MUTED))
        # око збоку
        f.append('<ellipse cx="%d" cy="192" rx="16" ry="9" fill="%s" stroke="%s" stroke-width="2"/>' % (cx + 140, BG, INK))
        f.append(circle(cx + 140, 192, 4.5, fill=INK, stroke=INK, sw=1))
        f.append(line(cx + 134, 192, cx + 100, 184, color=INK, sw=1.5))
        f.append(text(cx + 140, 214, "збоку", size=10, color=MUTED))

    # TN: молекули нахилені з площини (косі риски)
    stack(230, "TN — вузький кут", "молекули нахилені з площини")
    for c in range(5):
        bx = 166 + c * 32
        f.append(line(bx, 179.6, bx + 8, 204.4, color=INK, sw=4.6))
    # IPS: молекули лежать у площині (горизонтальні риски)
    stack(580, "IPS — широкий кут (~178°)", "молекули лежать У площині")
    for c in range(5):
        bx = 507 + c * 32
        f.append(line(bx, 192, bx + 26, 192, color=INK, sw=4.6))

    f.append(text(W / 2, 312, "збоку видно іншу «товщину» кристала: у TN це сильно міняє яскравість і колір, в IPS майже ні",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "angles-mech.svg"), W, H, *f)


# ── 5. Як падає контраст із кутом для різних типів панелей ────────────────────
def fig_angle_curve():
    W, H = 720, 380
    f = [text(W / 2, 26, "Відносний контраст проти кута огляду", size=16, bold=True)]

    ox, oy = 86, 300          # початок осей
    ax, ay = 686, 70          # кінці осей
    f.append(line(ox, oy, ax, oy, color=INK, sw=2))
    f.append(line(ox, oy, ox, ay, color=INK, sw=2))

    # вісь X: 0..80°
    for deg in (0, 20, 40, 60, 80):
        xx = ox + deg / 80 * (ax - 16 - ox)
        f.append(line(xx, oy, xx, oy + 6, color=INK, sw=1.4))
        f.append(text(xx, oy + 22, "%d°" % deg, size=11))
    f.append(text(ax - 14, oy + 22, "кут огляду", size=12, anchor="end"))

    # вісь Y: 0..100 %
    for pct in (0, 50, 100):
        yy = oy - pct / 100 * (oy - (ay + 6))
        f.append(line(ox - 6, yy, ox, yy, color=INK, sw=1.4))
        f.append(text(ox - 10, yy + 4, str(pct), size=11, anchor="end"))
    f.append(text(ox - 10, ay + 4, "контраст, %", size=12, anchor="start"))

    def X(deg):
        return ox + deg / 80 * (ax - 16 - ox)

    def Y(pct):
        return oy - pct / 100 * (oy - (ay + 6))

    # криві (відносний контраст у % на 0,20,40,60,80°)
    curves = [
        ("TN", POS, None, [100, 68, 34, 15, 6]),
        ("VA", AMBER, "6 4", [100, 85, 60, 35, 18]),
        ("IPS", NEG, None, [100, 97, 92, 80, 65]),
        ("OLED", FIELD, None, [100, 98, 94, 86, 75]),
    ]
    degs = [0, 20, 40, 60, 80]
    ly = 92
    for name, col, dash, pts in curves:
        prev = None
        for d, p in zip(degs, pts):
            cur = (X(d), Y(p))
            if prev:
                f.append(line(prev[0], prev[1], cur[0], cur[1], color=col, sw=2.6, dash=dash))
            prev = cur
        # легенда
        f.append(line(548, ly, 578, ly, color=col, sw=2.6, dash=dash))
        f.append(text(584, ly + 4, name, size=12, color=col, bold=True, anchor="start"))
        ly += 22

    f.append(text(W / 2, 360, "TN падає швидко; IPS і OLED тримають контраст майже до краю — це й вирішує, з якого боку дивитимуться",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "angle-curve.svg"), W, H, *f)


# ── 6. ШІМ-димінг: однакова яскравість, різна частота — різний результат ──────
def _pwm_wave(f, x0, x1, base, top, period, duty, color):
    """Прямокутна хвиля зліва направо."""
    on = period * duty
    x = x0
    pts = [(x, base)]
    while x < x1 - 1:
        x_end_on = min(x + on, x1)
        pts.append((x, top)); pts.append((x_end_on, top))
        x_next = x + period
        x_end_off = min(x_next, x1)
        pts.append((x_end_on, base)); pts.append((x_end_off, base))
        x = x_next
    poly = " ".join("%.1f,%.1f" % p for p in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-linecap="round" stroke-linejoin="round"/>' % (poly, color))


def fig_pwm():
    W, H = 760, 380
    f = [text(W / 2, 28, "ШІМ-димінг: шпаруватість задає яскравість, частота — мерехтіння", size=15, bold=True),
         text(W / 2, 49, "однакова яскравість (duty ≈ 35%), різна частота — різний результат для ока",
              size=11.5, color=MUTED, italic=True)]

    x0, x1 = 90, 700
    # низька частота
    _pwm_wave(f, x0, x1, 168, 120, period=90, duty=0.35, color=POS)
    f.append(text(x0, 102, "низька частота (сотні Гц)", size=12, color=POS, bold=True, anchor="start"))
    f.append(text(W / 2, 188, "→ око бачить мерехтіння, болять очі", size=11.5, color=POS))

    # висока частота
    _pwm_wave(f, x0, x1, 300, 252, period=21, duty=0.35, color=FIELD)
    f.append(text(x0, 234, "висока частота (>2 кГц)", size=12, color=FIELD, bold=True, anchor="start"))
    f.append(text(W / 2, 320, "→ око бачить рівне світло", size=11.5, color=FIELD))

    f.append(text(W / 2, 352, "найгірше: низька частота + низька яскравість (короткі рідкі спалахи)", size=11.5))
    f.append(text(W / 2, 373, "лікування: ШІМ понад кілька кГц або аналоговий (струмовий) димінг без миготіння",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "pwm.svg"), W, H, *f)


# ── 7. Час відгуку проти частоти оновлення ───────────────────────────────────
def fig_motion():
    W, H = 760, 330
    f = [text(W / 2, 26, "Дві різні лінійки руху: кадр і піксель", size=16, bold=True),
         text(W / 2, 47, "частота оновлення — як часто; час відгуку — як швидко піксель переходить",
              size=11.5, color=MUTED, italic=True)]

    # верх: частота оновлення — рамки кадрів на часовій осі
    y1 = 96
    f.append(text(40, y1 - 14, "частота оновлення (Гц): нові кадри щосекунди",
                  size=12, bold=True, anchor="start"))
    fx0 = 60
    for i in range(6):
        x = fx0 + i * 108
        f.append('<rect x="%d" y="%d" width="96" height="44" fill="%s" stroke="%s" stroke-width="1.5"/>'
                 % (x, y1, FILL, NEG))
        f.append(text(x + 48, y1 + 28, "кадр %d" % (i + 1), size=11, color=NEG))
    f.append(line(60, y1 + 60, 700, y1 + 60, color=INK, sw=1.6))
    f.append('<text x="700" y="%d" font-family="%s" font-size="11" fill="%s" text-anchor="end">'
             '1/60 с між кадрами при 60 Гц</text>' % (y1 + 76, FONT, MUTED))

    # низ: час відгуку — перехід пікселя від темного до світлого
    y2 = 230
    f.append(text(40, y2 - 14, "час відгуку (мс): як швидко піксель змінює колір",
                  size=12, bold=True, anchor="start"))
    px0, px1 = 60, 460
    f.append(line(px0, y2 + 40, px1, y2 + 40, color=MUTED, sw=1.2))   # рівень «темний»
    f.append(line(px0, y2, px1, y2, color=MUTED, sw=1.2))            # рівень «світлий»
    f.append(text(px0 - 8, y2 + 44, "темний", size=10, color=MUTED, anchor="end"))
    f.append(text(px0 - 8, y2 + 4, "світлий", size=10, color=MUTED, anchor="end"))
    # плавна крива переходу (повільний піксель)
    pts = []
    for k in range(41):
        t = k / 40.0
        x = px0 + t * (px1 - px0)
        val = 1 - math.exp(-3.2 * t)         # 0..~1
        yy = (y2 + 40) - val * 40
        pts.append((x, yy))
    poly = " ".join("%.1f,%.1f" % p for p in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linecap="round"/>' % (poly, POS))
    f.append(text(px1 + 10, y2 + 22, "повільний перехід", size=11, color=POS, anchor="start"))
    f.append(text(px1 + 10, y2 + 40, "→ хвіст-привид за рухом", size=10.5, color=MUTED, anchor="start", ))

    f.append(text(W / 2, 318, "не плутати: за 60 Гц на кадр є 1/60 с; якщо піксель не встигає — лишається змаз",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "motion.svg"), W, H, *f)


if __name__ == "__main__":
    fig_ppi()
    fig_nits()
    fig_contrast()
    fig_angles_mech()
    fig_angle_curve()
    fig_pwm()
    fig_motion()
    print("OK: 7 figures ->", IMG)
