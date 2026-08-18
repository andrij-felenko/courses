# -*- coding: utf-8 -*-
import sys, os
import math
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

def ellipse(cx, cy, rx, ry, fill=FILL, stroke=LINE, sw=1.5, angle=0):
    tr = ' transform="rotate(%.1f %.1f %.1f)"' % (angle, cx, cy) if angle != 0 else ''
    return '<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" stroke-width="%.1f"%s/>' % (cx, cy, rx, ry, fill, stroke, sw, tr)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Зсув долин зони провідності n-Si та перерозподіл електронів
# ════════════════════════════════════════════════════════════════════════════
def fig_valley_splitting():
    W, H = 840, 420
    f = []

    # Розділювальна лінія між станом без деформації та під деформацією
    f.append(line(420, 25, 420, 395, color=MUTED, sw=1.5, dash="4 4"))

    # ── Ліва панель: Рівноважний стан без деформації (σ = 0) ──
    f.append(text(210, 35, "Рівноважний кристал n-Si (σ = 0)", size=14, bold=True, color=INK))
    f.append(text(210, 55, "6 долин вироджені за енергією: E₁ = E₂ = E₃", size=11.5, color=MUTED))

    # Енергетична вісь E
    f.append(line(50, 340, 50, 80, color=DARK, sw=1.5))
    f.append(polygon([(46, 80), (50, 70), (54, 80)], fill=DARK))
    f.append(text(20, 75, "Енергія E", size=11, bold=True, color=DARK))

    # Спільний рівень долин E_0
    y_e0 = 240
    f.append(line(70, y_e0, 390, y_e0, color=MUTED, sw=1.2, dash="3 3"))
    f.append(text(80, y_e0 - 8, "Енергетичний мінімум E₀", size=10.5, color=MUTED))

    # 3 пари еквівалентних долин (креслення парабол)
    valleys_left = [
        (130, "Долини [100], [̄100]", "#2980b9"),
        (230, "Долини [010], [0̄10]", "#2980b9"),
        (330, "Долини [001], [00̄1]", "#2980b9")
    ]

    for vx, vname, color in valleys_left:
        pts = []
        for dx in range(-35, 36, 2):
            px = vx + dx
            py = y_e0 - int(0.08 * (dx**2))
            pts.append((px, py))
        path_d = "M " + " L ".join("%d %d" % p for p in pts)
        f.append(svg_path(path_d, stroke=color, sw=2.0, fill="none"))

        # Заповнення електронами (крапки однакового рівня)
        for ex in [-18, -6, 6, 18]:
            ey = y_e0 - int(0.08 * (ex**2)) - 4
            f.append(circle(vx + ex, ey, 3.5, fill="#e74c3c", stroke="#c0392b", sw=1.0))

        f.append(text(vx, y_e0 + 25, vname, size=10, bold=True, color=color))
        f.append(text(vx, y_e0 + 42, "nᵢ = n₀ / 6", size=10, color=DARK))

    f.append(text(210, 375, "Рівномірна провідність σ₀ (анізотропія відсутня)", size=11.5, bold=True, color=DARK))

    # ── Права панель: Одноосьове розтягнення вздовж [100] (σ > 0) ──
    f.append(text(630, 35, "Розтягнення вздовж осі [100] (σ > 0)", size=14, bold=True, color=INK))
    f.append(text(630, 55, "Зняття виродження: зсув долин на ΔE", size=11.5, color=MUTED))

    # Енергетична вісь E
    f.append(line(460, 340, 460, 80, color=DARK, sw=1.5))
    f.append(polygon([(456, 80), (460, 70), (464, 80)], fill=DARK))

    # Зсунуті рівні долин
    y_v1 = 280 # поздовжні долини (опустилися за енергією)
    y_v2 = 190 # поперечні долини (піднялися за енергією)

    f.append(line(480, y_v1, 800, y_v1, color="#27ae60", sw=1.0, dash="2 2"))
    f.append(line(480, y_v2, 800, y_v2, color="#c0392b", sw=1.0, dash="2 2"))

    # Стрілка расщеплення ΔE
    f.append(line(500, y_v1, 500, y_v2, color="#8e44ad", sw=1.5))
    f.append(polygon([(496, y_v2+6), (500, y_v2), (504, y_v2+6)], fill="#8e44ad"))
    f.append(polygon([(496, y_v1-6), (500, y_v1), (504, y_v1-6)], fill="#8e44ad"))
    f.append(text(510, (y_v1 + y_v2)//2 + 4, "ΔE", size=11, bold=True, color="#8e44ad"))

    # 1) Поздовжні долини [100] (нижча енергія, більше електронів)
    vx1 = 560
    pts1 = []
    for dx in range(-45, 46, 2):
        px = vx1 + dx
        py = y_v1 - int(0.06 * (dx**2))
        pts1.append((px, py))
    f.append(svg_path("M " + " L ".join("%d %d" % p for p in pts1), stroke="#27ae60", sw=2.2, fill="none"))

    # Багато електронів у низькій долині
    for ex in [-28, -20, -12, -4, 4, 12, 20, 28]:
        ey = y_v1 - int(0.06 * (ex**2)) - 4
        f.append(circle(vx1 + ex, ey, 3.5, fill="#e74c3c", stroke="#c0392b", sw=1.0))

    f.append(text(vx1, y_v1 + 25, "Поздовжня [100]", size=10.5, bold=True, color="#27ae60"))
    f.append(text(vx1, y_v1 + 42, "n ∥ ↑ (наплив носіїв)", size=10, bold=True, color="#27ae60"))

    # 2) Поперечні долини [010], [001] (вища енергія, мало електронів)
    vx2 = 720
    pts2 = []
    for dx in range(-35, 36, 2):
        px = vx2 + dx
        py = y_v2 - int(0.08 * (dx**2))
        pts2.append((px, py))
    f.append(svg_path("M " + " L ".join("%d %d" % p for p in pts2), stroke="#c0392b", sw=2.2, fill="none"))

    # Мало електронів у високій долині
    for ex in [-8, 8]:
        ey = y_v2 - int(0.08 * (ex**2)) - 4
        f.append(circle(vx2 + ex, ey, 3.5, fill="#e74c3c", stroke="#c0392b", sw=1.0))

    f.append(text(vx2, y_v2 + 25, "Поперечні [010], [001]", size=10.5, bold=True, color="#c0392b"))
    f.append(text(vx2, y_v2 + 42, "n ⊥ ↓ (спустошення)", size=10, bold=True, color="#c0392b"))

    f.append(text(630, 375, "Перекачка носіїв ⇒ Зміна питомого опору Δρ / ρ₀", size=11.5, bold=True, color="#8e44ad"))

    render(os.path.join(OUT, "valley-splitting.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Деформація валентної зони p-Si та зняття виродження дірок
# ════════════════════════════════════════════════════════════════════════════
def fig_valence_band_distortion():
    W, H = 840, 420
    f = []

    # Розділювальна пунктирна лінія
    f.append(line(420, 25, 420, 395, color=MUTED, sw=1.5, dash="4 4"))

    # ── Ліва панель: Недеформований кристал p-Si ──
    f.append(text(210, 35, "Недеформований кристал p-Si", size=14, bold=True, color=INK))
    f.append(text(210, 55, "Виродження важких (HH) та легких (LH) дірок", size=11.5, color=MUTED))

    cx1, cy1 = 210, 140

    # Осі k та E
    f.append(line(70, cy1, 350, cy1, color=MUTED, sw=1.2)) # k
    f.append(line(cx1, 330, cx1, 80, color=DARK, sw=1.5)) # E
    f.append(polygon([(cx1-4, 80), (cx1, 70), (cx1+4, 80)], fill=DARK))
    f.append(text(cx1 + 10, 75, "Енергія E", size=10.5, bold=True, color=DARK))
    f.append(text(340, cy1 - 10, "Хвильовий вектор k", size=10, color=MUTED))

    # Важка дірка HH (широка парабола)
    pts_hh = []
    for dx in range(-110, 111, 3):
        px = cx1 + dx
        py = cy1 + int(0.012 * (dx**2))
        pts_hh.append((px, py))
    f.append(svg_path("M " + " L ".join("%d %d" % p for p in pts_hh), stroke="#2980b9", sw=2.2, fill="none"))

    # Легка дірка LH (вузька парабола)
    pts_lh = []
    for dx in range(-65, 66, 3):
        px = cx1 + dx
        py = cy1 + int(0.035 * (dx**2))
        pts_lh.append((px, py))
    f.append(svg_path("M " + " L ".join("%d %d" % p for p in pts_lh), stroke="#e67e22", sw=2.2, fill="none"))

    # Точка виродження Γ
    f.append(circle(cx1, cy1, 4.5, fill="#c0392b", stroke="#7b241c", sw=1.2))
    f.append(text(cx1 + 12, cy1 + 4, "Точка Γ (k=0)", size=10.5, bold=True, color="#c0392b"))

    f.append(text(120, 270, "Важкі дірки HH (m* велика)", size=10.5, bold=True, color="#2980b9"))
    f.append(text(120, 290, "Легкі дірки LH (m* мала)", size=10.5, bold=True, color="#e67e22"))

    f.append(text(210, 375, "Сферична симетрія ізоенергетичних поверхонь", size=11, bold=True, color=DARK))

    # ── Права панель: Зняття виродження та деформація ──
    f.append(text(630, 35, "Деформований кристал (σ ≠ 0)", size=14, bold=True, color=INK))
    f.append(text(630, 55, "Розщеплення підзон ΔE_v та анізотропія m*(k)", size=11.5, color=MUTED))

    cx2 = 630
    cy_lh = 120
    cy_hh = 170

    f.append(line(490, 145, 770, 145, color=MUTED, sw=1.2)) # k
    f.append(line(cx2, 330, cx2, 80, color=DARK, sw=1.5)) # E
    f.append(polygon([(cx2-4, 80), (cx2, 70), (cx2+4, 80)], fill=DARK))

    # Верхня розщеплена зона
    pts_v1 = []
    for dx in range(-100, 101, 3):
        px = cx2 + dx
        py = cy_lh + int(0.018 * (dx**2))
        pts_v1.append((px, py))
    f.append(svg_path("M " + " L ".join("%d %d" % p for p in pts_v1), stroke="#27ae60", sw=2.2, fill="none"))

    # Нижня розщеплена зона
    pts_v2 = []
    for dx in range(-80, 81, 3):
        px = cx2 + dx
        py = cy_hh + int(0.022 * (dx**2))
        pts_v2.append((px, py))
    f.append(svg_path("M " + " L ".join("%d %d" % p for p in pts_v2), stroke="#8e44ad", sw=2.2, fill="none"))

    # Стрілка розщеплення ΔE_v
    f.append(line(cx2 - 40, cy_lh, cx2 - 40, cy_hh, color="#c0392b", sw=1.5))
    f.append(polygon([(cx2-44, cy_lh+5), (cx2-40, cy_lh), (cx2-36, cy_lh+5)], fill="#c0392b"))
    f.append(polygon([(cx2-44, cy_hh-5), (cx2-40, cy_hh), (cx2-36, cy_hh-5)], fill="#c0392b"))
    f.append(text(cx2 - 80, (cy_lh + cy_hh)//2 + 4, "ΔE_v", size=11, bold=True, color="#c0392b"))

    f.append(text(540, 260, "Верхня зона v₁ (легка маса вздовж [111])", size=10, bold=True, color="#27ae60"))
    f.append(text(540, 280, "Нижня зона v₂ (важка маса)", size=10, bold=True, color="#8e44ad"))

    f.append(text(630, 375, "Гігантська п'єзорезистивність p-Si (π₄₄ ≈ +138×10⁻¹¹ Pa⁻¹)", size=11, bold=True, color="#27ae60"))

    render(os.path.join(OUT, "valence-band-distortion.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — MEMS топологія кремнієвої мембрани та мостова схема Вітстона
# ════════════════════════════════════════════════════════════════════════════
def fig_piezoresistive_wheatstone_bridge():
    W, H = 840, 440
    f = []

    # Розділювальна лінія
    f.append(line(420, 25, 420, 415, color=MUTED, sw=1.5, dash="4 4"))

    # ── Ліва панель: Топологія кремнієвої мембрани MEMS ──
    f.append(text(210, 35, "MEMS мембрана датчика тиску", size=14, bold=True, color=INK))
    f.append(text(210, 55, "Розміщення п'єзорезисторів R₁..R₄ у зонах деформації", size=11, color=MUTED))

    # Квадратна мембрана
    mx, my, ms = 70, 90, 280
    f.append(rect(mx, my, ms, ms, fill="#ecf0f1", stroke="#7f8c8d", sw=2.0))
    # Зона потоншеної мембрани (внутрішній квадрат)
    f.append(rect(mx + 40, my + 40, ms - 80, ms - 80, fill="#e8f8f5", stroke="#16a085", sw=1.5))
    f.append(text(210, 230, "Гнучка мембрана (Si)", size=11, bold=True, color="#16a085"))

    # П'єзорезистори на краях мембрани
    # R1 - поздовжній (верхній край)
    f.append(rect(210 - 25, my + 15, 50, 14, fill="#e74c3c", stroke="#c0392b", sw=1.2))
    f.append(text(210, my + 26, "R₁ (R+ΔR)", size=9.5, bold=True, color="#ffffff"))

    # R3 - поздовжній (нижній край)
    f.append(rect(210 - 25, my + ms - 29, 50, 14, fill="#e74c3c", stroke="#c0392b", sw=1.2))
    f.append(text(210, my + ms - 18, "R₃ (R+ΔR)", size=9.5, bold=True, color="#ffffff"))

    # R2 - поперечний (лівий край)
    f.append(rect(mx + 15, 230 - 25, 14, 50, fill="#3498db", stroke="#2980b9", sw=1.2))
    f.append(text(mx + 22, 230, "R₂", size=9.5, bold=True, color="#ffffff"))

    # R4 - поперечний (правий край)
    f.append(rect(mx + ms - 29, 230 - 25, 14, 50, fill="#3498db", stroke="#2980b9", sw=1.2))
    f.append(text(mx + ms - 22, 230, "R₄", size=9.5, bold=True, color="#ffffff"))

    f.append(text(210, 395, "Ось [110] на пластині Si (100)", size=11, bold=True, color=DARK))

    # ── Права панель: Електрична мостова схема Вітстона ──
    f.append(text(630, 35, "Мостова вимірювальна схема", size=14, bold=True, color=INK))
    f.append(text(630, 55, "Диференціальна вихідна напруга V_out(P)", size=11, color=MUTED))

    # Вузли моста Вітстона
    bx_top, by_top = 630, 100
    bx_bot, by_bot = 630, 320
    bx_left, by_left = 520, 210
    bx_right, by_right = 740, 210

    # Лінії з'єднання
    f.append(line(bx_top, by_top, bx_left, by_left, color=DARK, sw=2.0))
    f.append(line(bx_top, by_top, bx_right, by_right, color=DARK, sw=2.0))
    f.append(line(bx_left, by_left, bx_bot, by_bot, color=DARK, sw=2.0))
    f.append(line(bx_right, by_right, bx_bot, by_bot, color=DARK, sw=2.0))

    # Позначення резисторів прямокутниками у гілках
    # Верхня ліва гілка: R1
    f.append(rect(560, 140, 30, 16, fill="#e74c3c", stroke="#c0392b", sw=1.2))
    f.append(text(575, 130, "R₁ (R+ΔR)", size=9.5, bold=True, color="#c0392b"))

    # Верхня права гілка: R2
    f.append(rect(670, 140, 30, 16, fill="#3498db", stroke="#2980b9", sw=1.2))
    f.append(text(685, 130, "R₂ (R-ΔR)", size=9.5, bold=True, color="#2980b9"))

    # Нижня ліва гілка: R4
    f.append(rect(560, 250, 30, 16, fill="#3498db", stroke="#2980b9", sw=1.2))
    f.append(text(575, 280, "R₄ (R-ΔR)", size=9.5, bold=True, color="#2980b9"))

    # Нижня права гілка: R3
    f.append(rect(670, 250, 30, 16, fill="#e74c3c", stroke="#c0392b", sw=1.2))
    f.append(text(685, 280, "R₃ (R+ΔR)", size=9.5, bold=True, color="#c0392b"))

    # Точки вузлів
    for nx, ny in [(bx_top, by_top), (bx_bot, by_bot), (bx_left, by_left), (bx_right, by_right)]:
        f.append(circle(nx, ny, 4, fill=DARK))

    # Джерело живлення V_in
    f.append(line(bx_top, by_top, bx_top, by_top - 25, color=DARK, sw=1.5))
    f.append(line(bx_bot, by_bot, bx_bot, by_bot + 25, color=DARK, sw=1.5))
    f.append(text(bx_top + 10, by_top - 15, "V_in (+)", size=11, bold=True, color="#27ae60"))
    f.append(text(bx_bot + 10, by_bot + 20, "GND (0V)", size=11, bold=True, color=DARK))

    # Вихід V_out
    f.append(line(bx_left, by_left, bx_left - 30, by_left, color="#8e44ad", sw=1.5))
    f.append(line(bx_right, by_right, bx_right + 30, by_right, color="#8e44ad", sw=1.5))
    f.append(circle(bx_left - 30, by_left, 3, fill="#8e44ad"))
    f.append(circle(bx_right + 30, by_right, 3, fill="#8e44ad"))
    f.append(text(bx_left - 50, by_left - 8, "V_out⁻", size=11, bold=True, color="#8e44ad"))
    f.append(text(bx_right + 15, by_right - 8, "V_out⁺", size=11, bold=True, color="#8e44ad"))

    # Формула виходу
    f.append(text(630, 395, "V_out = V_in · (ΔR / R₀) = V_in · π_L · σ_L", size=11.5, bold=True, color="#8e44ad"))

    render(os.path.join(OUT, "piezoresistive-wheatstone-bridge.svg"), W, H, *f)


if __name__ == '__main__':
    fig_valley_splitting()
    fig_valence_band_distortion()
    fig_piezoresistive_wheatstone_bridge()
    print("All figures generated successfully.")
