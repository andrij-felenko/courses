# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

DARK = INK

def svg_path(d_str, stroke="#c0392b", sw=2.5, fill="none", dash=None):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d_str, stroke, sw, fill, d_attr)

def polygon(points, fill=DARK, stroke="none", sw=1.0):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    st = ' stroke="%s" stroke-width="%.1f"' % (stroke, sw) if stroke != "none" else ''
    return '<polygon points="%s" fill="%s"%s/>' % (pts_str, fill, st)

def ellipse(cx, cy, rx, ry, fill="none", stroke=LINE, sw=1.5, dash=None):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" stroke-width="%.1f"%s/>' % (cx, cy, rx, ry, fill, stroke, sw, d_attr)



# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Принцип Z-пінчу та Тета-пінчу
# ════════════════════════════════════════════════════════════════════════════
def fig_pinches():
    W, H = 840, 420
    f = []

    # Розділювач панелей
    f.append(line(420, 25, 420, 395, color=MUTED, sw=1.5, dash="4 4"))

    # ── Ліва панель: Z-пінч ──
    f.append(text(210, 40, "Z-пінч (аксіальний струм)", size=14, bold=True, color=INK))
    f.append(text(210, 60, "Струм вздовж вісі Z → азимутальне поле B_φ", size=11.5, color=MUTED))

    # Колона плазми Z-пінчу (циліндр)
    f.append(rect(140, 100, 140, 240, fill="#fadbd8", stroke="#e74c3c", sw=2, rx=10))
    f.append(ellipse(210, 100, 70, 18, fill="#f5b7b1", stroke="#e74c3c", sw=2))

    # Вісь Z і струм I_z
    f.append(line(210, 75, 210, 365, color="#c0392b", sw=2.5, dash="6 3"))
    f.append(polygon([(205, 360), (210, 372), (215, 360)], fill="#c0392b"))
    f.append(text(225, 365, "I_z (струм)", size=12, bold=True, color="#c0392b"))

    # Магнітні лінії B_φ (азимутальні кільця)
    f.append(ellipse(210, 170, 95, 26, fill="none", stroke="#2980b9", sw=2, dash="5 3"))
    f.append(polygon([(303, 172), (307, 164), (300, 166)], fill="#2980b9"))
    f.append(ellipse(210, 250, 95, 26, fill="none", stroke="#2980b9", sw=2, dash="5 3"))
    f.append(polygon([(303, 252), (307, 244), (300, 246)], fill="#2980b9"))
    f.append(text(315, 170, "B_φ", size=12, bold=True, color="#2980b9"))

    # Радіальні сили Лоренца F_L (спрямовані всередину)
    # Ліва сторона
    f.append(line(110, 220, 165, 220, color="#d35400", sw=2.5))
    f.append(polygon([(160, 215), (170, 220), (160, 225)], fill="#d35400"))
    # Права сторона
    f.append(line(310, 220, 255, 220, color="#d35400", sw=2.5))
    f.append(polygon([(260, 215), (250, 220), (260, 225)], fill="#d35400"))
    f.append(text(210, 215, "F_r = j_z × B_φ", size=11.5, bold=True, color="#d35400"))

    # ── Права панель: Тета-пінч (Θ-пінч) ──
    f.append(text(630, 40, "Тета-пінч (азимутальний струм)", size=14, bold=True, color=INK))
    f.append(text(630, 60, "Змінне аксіальне поле B_z → індукований струм j_φ", size=11.5, color=MUTED))

    # Змійовик соленоїда (зовнішній — переріз витків ліворуч і праворуч від трубки)
    for y_coil in range(110, 330, 40):
        f.append(rect(520, y_coil, 40, 16, fill="#ebf5fb", stroke="#2980b9", sw=1.5, rx=4))
        f.append(rect(700, y_coil, 40, 16, fill="#ebf5fb", stroke="#2980b9", sw=1.5, rx=4))

    # Плазмовий шнур всередині
    f.append(rect(580, 100, 100, 240, fill="#d5f5e3", stroke="#27ae60", sw=2, rx=8))
    f.append(ellipse(630, 100, 50, 14, fill="#abebc6", stroke="#27ae60", sw=2))


    # Магнітне поле B_z вздовж осі
    f.append(line(630, 75, 630, 365, color="#8e44ad", sw=2.5, dash="6 3"))
    f.append(polygon([(625, 360), (630, 372), (635, 360)], fill="#8e44ad"))
    f.append(text(645, 365, "B_z (аксіальне)", size=12, bold=True, color="#8e44ad"))

    # Індукований струм j_φ (кільцеве вращення)
    f.append(ellipse(630, 210, 42, 14, fill="none", stroke="#27ae60", sw=2.5))
    f.append(polygon([(670, 212), (674, 204), (666, 206)], fill="#27ae60"))
    f.append(text(630, 195, "j_φ", size=12, bold=True, color="#27ae60"))

    # Радіальне стискання F_L у Тета-пінчі
    f.append(line(550, 220, 590, 220, color="#d35400", sw=2.5))
    f.append(polygon([(585, 215), (595, 220), (585, 225)], fill="#d35400"))
    f.append(line(710, 220, 670, 220, color="#d35400", sw=2.5))
    f.append(polygon([(675, 215), (665, 220), (675, 225)], fill="#d35400"))

    render(os.path.join(OUT, "z-pinch-principle.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Гідродінамічні нестійкості Z-пінчу (Сосисочна та Змійоподібна)
# ════════════════════════════════════════════════════════════════════════════
def fig_instabilities():
    W, H = 840, 400
    f = []

    # Розділювач
    f.append(line(420, 25, 420, 375, color=MUTED, sw=1.5, dash="4 4"))

    # ── Ліва панель: Перетяжкова нестійкість m = 0 (Sausage instability) ──
    f.append(text(210, 40, "Нестійкість m = 0 (перетяжкова / sausage)", size=14, bold=True, color=INK))
    f.append(text(210, 60, "Звуження r → зростання B_φ ∝ 1/r → катастрофічне стискання", size=11, color=MUTED))

    # Контур перетяжки (вузька шийка по центру)
    path_sausage = "M 150 90 L 270 90 C 270 150 220 180 220 200 C 220 220 270 250 270 310 L 150 310 C 150 250 200 220 200 200 C 200 180 150 150 150 90 Z"
    f.append(svg_path(path_sausage, stroke="#c0392b", sw=2, fill="#fadbd8"))

    # Стрілки посиленої магнітної сили у шийці
    f.append(line(140, 200, 190, 200, color="#900c3f", sw=3))
    f.append(polygon([(185, 194), (198, 200), (185, 206)], fill="#900c3f"))
    f.append(line(280, 200, 230, 200, color="#900c3f", sw=3))
    f.append(polygon([(235, 194), (222, 200), (235, 206)], fill="#900c3f"))

    f.append(text(210, 200, "B_φ ↑↑", size=12, bold=True, color="#900c3f"))
    f.append(text(210, 340, "Утворення пучностей і розрив шнура", size=11.5, color=DARK))

    # ── Права панель: Змійоподібна нестійкість m = 1 (Kink instability) ──
    f.append(text(630, 40, "Нестійкість m = 1 (змійоподібна / kink)", size=14, bold=True, color=INK))
    f.append(text(630, 60, "Вигин шнура → згущення ліній B_φ з внутрішнього боку", size=11, color=MUTED))

    # Зігнутий шнур плазми (S-подібний або вигнутий дугою)
    path_kink = "M 570 90 C 660 150 670 250 570 310 L 610 310 C 710 250 700 150 610 90 Z"
    f.append(svg_path(path_kink, stroke="#27ae60", sw=2, fill="#d5f5e3"))

    # Магнітні лінії, згущені у внутрішньому згині (виштовхують вигин далі)
    f.append(svg_path("M 550 150 C 590 180 600 220 550 250", stroke="#2980b9", sw=2, fill="none"))
    f.append(svg_path("M 535 140 C 585 180 595 220 535 260", stroke="#2980b9", sw=2, fill="none"))
    f.append(svg_path("M 520 130 C 580 180 590 220 520 270", stroke="#2980b9", sw=2, fill="none"))

    # Сила F_kink, що виштовхує дугу назовні
    f.append(line(620, 200, 680, 200, color="#d35400", sw=3))
    f.append(polygon([(675, 194), (688, 200), (675, 206)], fill="#d35400"))
    f.append(text(700, 200, "F_kink", size=12, bold=True, color="#d35400"))

    f.append(text(630, 340, "Зростання амплітуди вигину та викид на стінку", size=11.5, color=DARK))

    render(os.path.join(OUT, "pinch-instabilities.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Радіальний розподіл величин у рівновазі Беннетта
# ════════════════════════════════════════════════════════════════════════════
def fig_bennett_profiles():
    W, H = 780, 420
    f = []

    cx, cy = 400, 340
    rw, rh = 320, 280

    # Осі координат
    f.append(line(cx - rw - 20, cy, cx + rw + 20, cy, color=DARK, sw=1.5)) # r (радіус)
    f.append(line(cx, cy, cx, cy - rh - 20, color=DARK, sw=1.5))           # Величина

    f.append(polygon([(cx + rw + 20, cy - 4), (cx + rw + 30, cy), (cx + rw + 20, cy + 4)], fill=DARK))
    f.append(polygon([(cx - 4, cy - rh - 20), (cx, cy - rh - 30), (cx + 4, cy - rh - 20)], fill=DARK))

    f.append(text(cx + rw + 10, cy + 22, "Радіус r (від осі)", size=11.5, bold=True, color=DARK))
    f.append(text(cx - 90, cy - rh - 25, "Густина струму / Магнітне поле / Тиск", size=11.5, bold=True, color=DARK))

    # Позначка радіуса шнура a (Bennett radius)
    f.append(line(cx + 90, cy - 5, cx + 90, cy + 5, color=DARK, sw=1.5))
    f.append(text(cx + 90, cy + 22, "+a", size=11, bold=True, color=DARK))
    f.append(line(cx - 90, cy - 5, cx - 90, cy + 5, color=DARK, sw=1.5))
    f.append(text(cx - 90, cy + 22, "-a", size=11, bold=True, color=DARK))

    # 1. Профіль тиску p(r) або n(r) — червона крива (максимум на осі r=0)
    # p(r) = p0 / (1 + (r/a)^2)^2
    path_p = "M 80 335 C 250 330 310 100 400 100 C 490 100 550 330 720 335"
    f.append(svg_path(path_p, stroke="#c0392b", sw=2.5, fill="none"))
    f.append(text(410, 90, "p(r), n(r) — газовий тиск / концентрація", size=11.5, bold=True, color="#c0392b"))

    # 2. Профіль густини струму j_z(r) — оранжева пунктирна крива
    path_j = "M 80 337 C 260 334 320 120 400 120 C 480 120 540 334 720 337"
    f.append(svg_path(path_j, stroke="#d35400", sw=2, fill="none", dash="5 3"))
    f.append(text(410, 135, "j_z(r) — густина аксіального струму", size=11, color="#d35400"))

    # 3. Профіль азимутального магнітного поля B_φ(r) — синя крива (0 на осі, максимум при r=a)
    # B_φ(r) = (μ0 I / 2π) * r / (r^2 + a^2)
    path_b = "M 80 338 C 220 335 280 200 310 200 C 350 200 380 330 400 340 C 420 330 450 200 490 200 C 520 200 580 335 720 338"
    f.append(svg_path(path_b, stroke="#2980b9", sw=2.5, fill="none"))
    f.append(text(580, 170, "B_φ(r) — магнітне поле", size=11.5, bold=True, color="#2980b9"))

    # Стрілка рівноваги ∇p = j × B
    f.append(line(490, 270, 440, 270, color="#8e44ad", sw=2))
    f.append(polygon([(445, 265), (435, 270), (445, 275)], fill="#8e44ad"))
    f.append(text(540, 280, "∇p = j_z × B_φ (Магнітний стиск)", size=11, bold=True, color="#8e44ad"))


    render(os.path.join(OUT, "bennett-equilibrium.svg"), W, H, *f)


if __name__ == '__main__':
    fig_pinches()
    fig_instabilities()
    fig_bennett_profiles()
    print("Pinch effect figures generated successfully.")
