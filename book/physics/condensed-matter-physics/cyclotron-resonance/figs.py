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
# Фігура 1 — Механізм ґірації та резонансного прискорення електрона
# ════════════════════════════════════════════════════════════════════════════
def fig_cyclotron_motion():
    W, H = 820, 420
    f = []

    # Розділювальна пунктирна лінія
    f.append(line(410, 25, 410, 395, color=MUTED, sw=1.5, dash="4 4"))

    # ── Ліва панель: Власна ґірація у магнітному полі B ──
    f.append(text(205, 40, "Циклотронна ґірація у полі B", size=14, bold=True, color=INK))
    f.append(text(205, 60, "Сила Лоренца F = q(v × B) утворює коло", size=12, color=MUTED))

    # Напрямок векторів магнітного поля B (вгору / z)
    for x in [80, 160, 240, 320]:
        f.append(line(x, 340, x, 100, color="#2980b9", sw=1.5, dash="4 3"))
        f.append(polygon([(x-4, 105), (x, 95), (x+4, 105)], fill="#2980b9"))
    f.append(text(340, 95, "B (магнітне поле)", size=11, bold=True, color="#2980b9"))

    # Орбіта ґірації (коло)
    cx, cy, r = 200, 230, 80
    f.append(circle(cx, cy, r, stroke="#7f8c8d", sw=1.5, fill="none"))

    # Електрон на орбіті
    ex, ey = cx + r * math.cos(math.pi/4), cy - r * math.sin(math.pi/4)
    f.append(circle(ex, ey, 7, fill="#c0392b", stroke="#7b241c", sw=1.5))
    f.append(text(ex + 12, ey - 5, "e⁻", size=12, bold=True, color="#c0392b"))

    # Вектор швидкості v (дотична)
    vx, vy = ex - 40 * math.sin(math.pi/4), ey - 40 * math.cos(math.pi/4)
    f.append(line(ex, ey, vx, vy, color="#27ae60", sw=2.2))
    f.append(polygon([(vx-3, vy+4), (vx-8, vy-4), (vx+4, vy-2)], fill="#27ae60"))
    f.append(text(vx - 20, vy - 8, "v (швидкість)", size=11, bold=True, color="#27ae60"))

    # Вектор сили Лоренца F (до центру)
    fx, fy = ex - 45 * math.cos(math.pi/4), ey + 45 * math.sin(math.pi/4)
    f.append(line(ex, ey, fx, fy, color="#d35400", sw=2.2))
    f.append(polygon([(fx+4, fy-4), (fx-2, fy+6), (fx-6, fy-2)], fill="#d35400"))
    f.append(text(fx - 5, fy + 16, "F_L (сила Лоренца)", size=11, bold=True, color="#d35400"))

    # Формула частоти
    f.append(text(205, 375, "ω_c = q · B / m*", size=13, bold=True, color=INK))

    # ── Права панель: Резонансне розгортання спіралі ──
    f.append(text(615, 40, "Резонансне поглинання (ω = ω_c)", size=14, bold=True, color=INK))
    f.append(text(615, 60, "Електричне поле E_RF сумісне за фазою", size=12, color=MUTED))

    # Спіральна траєкторія розгортання
    scx, scy = 615, 230
    pts = []
    for t_deg in range(0, 1080, 5):
        t_rad = math.radians(t_deg)
        r_t = 12 + 0.085 * t_deg
        px = scx + r_t * math.cos(t_rad)
        py = scy - r_t * math.sin(t_rad)
        pts.append((px, py))
    path_d = "M " + " L ".join("%.1f %.1f" % p for p in pts)
    f.append(svg_path(path_d, stroke="#8e44ad", sw=2.2, fill="none"))

    # Електрон на зовнішньому витку
    lex, ley = pts[-1]
    f.append(circle(lex, ley, 7, fill="#c0392b", stroke="#7b241c", sw=1.5))
    f.append(text(lex + 10, ley + 12, "e⁻ (розгін)", size=11, bold=True, color="#c0392b"))

    # Вектор обертального електричного поля E_RF
    f.append(line(lex, ley, lex + 45, ley, color="#e67e22", sw=2.5))
    f.append(polygon([(lex + 45, ley - 4), (lex + 55, ley), (lex + 45, ley + 4)], fill="#e67e22"))
    f.append(text(lex + 15, ley - 10, "E_RF(t)", size=11, bold=True, color="#e67e22"))

    # Позначка збільшення радіуса r_c
    f.append(line(scx, scy, lex, ley, color=MUTED, sw=1, dash="2 2"))
    f.append(text(scx - 35, scy + 15, "Центр", size=10, color=MUTED))
    f.append(text(615, 375, "Радіус r_c зростає  ⇒  E_k = m* v² / 2 ↑", size=12, bold=True, color="#8e44ad"))

    render(os.path.join(OUT, "cyclotron-motion.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Спектр резонансного поглинання потужності P(ω/ω_c)
# ════════════════════════════════════════════════════════════════════════════
def fig_resonance_curves():
    W, H = 780, 420
    f = []

    # Координатні осі
    ox, oy = 90, 340
    f.append(line(ox, oy, 720, oy, color=DARK, sw=1.5)) # ось ω / ω_c
    f.append(line(ox, oy, ox, 50, color=DARK, sw=1.5))  # ось P(ω)

    f.append(polygon([(720, oy-4), (730, oy), (720, oy+4)], fill=DARK))
    f.append(polygon([(ox-4, 50), (ox, 40), (ox+4, 50)], fill=DARK))

    f.append(text(710, oy + 25, "Відносна частота ω / ω_c", size=12, bold=True, color=DARK))
    f.append(text(25, 42, "Поглинута потужність P(ω)", size=12, bold=True, color=DARK))

    # Лінія резонансу (ω / ω_c = 1)
    rx = ox + 300
    f.append(line(rx, oy, rx, 65, color=MUTED, sw=1.2, dash="3 3"))
    f.append(text(rx - 15, oy + 20, "1.0", size=11, bold=True, color=DARK))
    f.append(text(rx - 30, 52, "Резонанс ω = ω_c", size=11, bold=True, color="#c0392b"))

    # Позначки на осі X (0.5, 1.5, 2.0)
    for ratio, label in [(0.5, "0.5"), (1.5, "1.5"), (2.0, "2.0")]:
        px = ox + int(ratio * 300)
        f.append(line(px, oy - 4, px, oy + 4, color=DARK, sw=1.5))
        f.append(text(px - 10, oy + 20, label, size=11, color=MUTED))

    # Спектральні криві для різних ω_c * τ
    curves_data = [
        (10.0, "#c0392b", "ω_c · τ = 10 (гострий резонанс, чистий кристал)"),
        (3.0,  "#d35400", "ω_c · τ = 3 (виразний пік)"),
        (1.0,  "#2980b9", "ω_c · τ = 1 (уширений поріг)"),
        (0.5,  "#7f8c8d", "ω_c · τ = 0.5 (без резонансу, сильне розсіювання)")
    ]

    for wt, color, label in curves_data:
        pts = []
        for x_pixel in range(ox, 700, 3):
            ratio = (x_pixel - ox) / 300.0
            val = 1.0 / (1.0 + ((ratio - 1.0) * wt)**2)
            y_pixel = oy - int(val * 250)
            pts.append((x_pixel, y_pixel))
        path_d = "M " + " L ".join("%d %d" % p for p in pts)
        f.append(svg_path(path_d, stroke=color, sw=2.2, fill="none"))

    # Легенда
    lx, ly = 430, 80
    f.append(rect(lx - 10, ly - 15, 290, 115, fill="#f8f9f9", stroke="#bdc3c7", sw=1.0))
    for i, (wt, color, label) in enumerate(curves_data):
        f.append(line(lx, ly + i*25, lx + 25, ly + i*25, color=color, sw=2.5))
        f.append(text(lx + 32, ly + i*25 + 4, label, size=10.5, bold=(i==0), color=DARK))

    # Ширина піку Δω = 1/τ
    f.append(line(rx - 30, oy - 125, rx + 30, oy - 125, color="#c0392b", sw=1.5))
    f.append(line(rx - 30, oy - 120, rx - 30, oy - 130, color="#c0392b", sw=1.5))
    f.append(line(rx + 30, oy - 120, rx + 30, oy - 130, color="#c0392b", sw=1.5))
    f.append(text(rx + 40, oy - 122, "Ширина Δω ≈ 1/τ", size=10.5, bold=True, color="#c0392b"))

    render(os.path.join(OUT, "resonance-curves.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Зонна анізотропія та розщеплення піків у кремнії/германії
# ════════════════════════════════════════════════════════════════════════════
def fig_semiconductor_anisotropy():
    W, H = 840, 440
    f = []

    # Розділювальна пунктирна лінія
    f.append(line(400, 25, 400, 415, color=MUTED, sw=1.5, dash="4 4"))

    # ── Ліва панель: Еліпсоїди енергії E(k) у k-просторі ──
    f.append(text(200, 40, "Зонні еліпсоїди германію (Ge)", size=14, bold=True, color=INK))
    f.append(text(200, 60, "Анізотропні долини вздовж напрямків <111>", size=12, color=MUTED))

    # Осі kx, ky, kz
    kcx, kcy = 200, 230
    f.append(line(kcx - 130, kcy, kcx + 130, kcy, color=MUTED, sw=1.2)) # kx
    f.append(line(kcx, kcy + 120, kcx, kcy - 120, color=MUTED, sw=1.2)) # ky
    f.append(line(kcx - 90, kcy + 90, kcx + 90, kcy - 90, color=MUTED, sw=1.2)) # kz (перспектива)

    f.append(text(kcx + 135, kcy + 4, "k_x [100]", size=10.5, color=MUTED))
    f.append(text(kcx + 5, kcy - 125, "k_y [010]", size=10.5, color=MUTED))
    f.append(text(kcx + 95, kcy - 90, "k_z [001]", size=10.5, color=MUTED))

    # Еліпсоїди
    f.append(ellipse(kcx + 40, kcy - 40, 55, 22, fill="#e74c3c", stroke="#c0392b", sw=1.5, angle=-35))
    f.append(ellipse(kcx - 40, kcy - 40, 55, 22, fill="#3498db", stroke="#2980b9", sw=1.5, angle=35))
    f.append(ellipse(kcx + 40, kcy + 40, 55, 22, fill="#2ecc71", stroke="#27ae60", sw=1.5, angle=35))
    f.append(ellipse(kcx - 40, kcy + 40, 55, 22, fill="#f1c40f", stroke="#d35400", sw=1.5, angle=-35))

    f.append(text(kcx - 150, kcy - 80, "Поздовжня маса m_l*", size=11, bold=True, color="#c0392b"))
    f.append(text(kcx - 150, kcy + 105, "Поперечна маса m_t*", size=11, bold=True, color="#2980b9"))

    # ── Права панель: Спектр розщеплення резонансних піків ──
    f.append(text(620, 40, "Експериментальний спектр (T = 4.2 K)", size=14, bold=True, color=INK))
    f.append(text(620, 60, "Розщеплення піків залежно від орієнтації B", size=12, color=MUTED))

    # Вісь магнітного поля B
    ox, oy = 440, 350
    f.append(line(ox, oy, 800, oy, color=DARK, sw=1.5))
    f.append(polygon([(800, oy-4), (810, oy), (800, oy+4)], fill=DARK))
    f.append(text(730, oy + 25, "Магнітне поле B (Тесла)", size=11.5, bold=True, color=DARK))

    # Спектральна крива з кількома піками поглинання
    pts_spec = []
    for x in range(ox, 790, 2):
        b_val = (x - ox) / 350.0
        p1 = 0.45 / (1.0 + ((b_val - 0.12) * 45)**2)  # light hole
        p2 = 0.70 / (1.0 + ((b_val - 0.28) * 35)**2)  # electron valley A
        p3 = 0.55 / (1.0 + ((b_val - 0.45) * 30)**2)  # heavy hole
        p4 = 0.85 / (1.0 + ((b_val - 0.65) * 30)**2)  # electron valley B
        total = p1 + p2 + p3 + p4 + 0.05
        y = oy - int(total * 220)
        pts_spec.append((x, y))

    path_spec = "M " + " L ".join("%d %d" % p for p in pts_spec)
    f.append(svg_path(path_spec, stroke="#8e44ad", sw=2.2, fill="none"))

    # Підписи до піків
    f.append(text(ox + int(0.12*350) - 25, oy - int(0.45*220) - 15, "Легкі дірки (lh)", size=10, bold=True, color="#8e44ad"))
    f.append(circle(ox + int(0.12*350), oy - int(0.45*220) - 5, 3, fill="#8e44ad"))

    f.append(text(ox + int(0.28*350) - 30, oy - int(0.70*220) - 15, "Електрони (долина 1)", size=10, bold=True, color="#2980b9"))
    f.append(circle(ox + int(0.28*350), oy - int(0.70*220) - 5, 3, fill="#2980b9"))

    f.append(text(ox + int(0.45*350) - 25, oy - int(0.55*220) - 15, "Важкі дірки (hh)", size=10, bold=True, color="#27ae60"))
    f.append(circle(ox + int(0.45*350), oy - int(0.55*220) - 5, 3, fill="#27ae60"))

    f.append(text(ox + int(0.65*350) - 30, oy - int(0.85*220) - 15, "Електрони (долина 2)", size=10, bold=True, color="#c0392b"))
    f.append(circle(ox + int(0.65*350), oy - int(0.85*220) - 5, 3, fill="#c0392b"))

    f.append(text(615, 395, "Поворот кристала змінює m_c* кожної долини", size=11, bold=True, color=DARK))

    render(os.path.join(OUT, "semiconductor-anisotropy.svg"), W, H, *f)


if __name__ == '__main__':
    fig_cyclotron_motion()
    fig_resonance_curves()
    fig_semiconductor_anisotropy()
    print("Figures generated successfully.")
