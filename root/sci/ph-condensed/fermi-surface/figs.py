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

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Ідеальна сфера Фермі проти деформованої поверхні у кристалі
# ════════════════════════════════════════════════════════════════════════════
def fig_fermi_sphere_vs_lattice():
    W, H = 840, 420
    f = []

    # Розділювальна пунктирна лінія
    f.append(line(420, 25, 420, 395, color=MUTED, sw=1.5, dash="4 4"))

    # ── Ліва панель: Модель вільних електронів (Сфера Фермі) ──
    f.append(text(210, 35, "Модель вільних електронів (Зоммерфельд)", size=14, bold=True, color=INK))
    f.append(text(210, 55, "Ізотропний k-простір, ідеальна сфера", size=12, color=MUTED))

    # Вісі kx, ky
    f.append(arrow(60, 230, 360, 230, color=MUTED, sw=1.5))
    f.append(text(370, 234, "k_x", size=12, bold=True, color=INK))
    f.append(arrow(210, 360, 210, 90, color=MUTED, sw=1.5))
    f.append(text(210, 80, "k_y", size=12, bold=True, color=INK))

    # Сфера Фермі
    cx, cy, r = 210, 230, 110
    f.append(circle(cx, cy, r, fill="#e8f4f8", stroke="#2980b9", sw=2.5))
    f.append(text(cx, cy - 20, "Заповнені стани", size=13, bold=True, color="#2980b9"))
    f.append(text(cx, cy + 5, "E(k) ≤ E_F", size=12, color="#2980b9"))

    # Радіус k_F
    rx, ry = cx + r * math.cos(math.pi/4), cy - r * math.sin(math.pi/4)
    f.append(arrow(cx, cy, rx, ry, color="#c0392b", sw=2.0))
    f.append(text(cx + 45, cy - 45, "k_F", size=13, bold=True, color="#c0392b"))

    f.append(text(210, 385, "E(k) = ℏ² k² / (2m*) — кульова симетрія", size=12, bold=True, color=INK))

    # ── Права панель: Вплив кристалічної ґратки (Перетяжки) ──
    f.append(text(630, 35, "Періодичний ґратковий потенціал (Мідь, Cu)", size=14, bold=True, color=INK))
    f.append(text(630, 55, "Межа зони Бріллюена та ортогональний перетин", size=12, color=MUTED))

    # Вісі kx, ky
    f.append(arrow(480, 230, 780, 230, color=MUTED, sw=1.5))
    f.append(text(790, 234, "k_x", size=12, bold=True, color=INK))
    f.append(arrow(630, 360, 630, 90, color=MUTED, sw=1.5))
    f.append(text(630, 80, "k_y", size=12, bold=True, color=INK))

    # Квадрат першої зони Бріллюена
    bx1, by1, bw, bh = 520, 120, 220, 220
    f.append(rect(bx1, by1, bw, bh, fill="none", stroke="#7f8c8d", sw=1.5, rx=0))
    f.append(text(bx1 + bw - 5, by1 + 18, "Зона Бріллюена", size=11, color=MUTED, anchor="end"))

    # Поверхня Фермі з перетяжками ("шиями"), що підходять перпендикулярно до межі
    pts_right = []
    rcx, rcy = 630, 230
    for a_deg in range(0, 360, 2):
        rad = math.radians(a_deg)
        dr = 12 * math.cos(4 * rad)
        r_val = 98 + dr
        px = rcx + r_val * math.cos(rad)
        py = rcy - r_val * math.sin(rad)
        pts_right.append((px, py))
    path_cu = "M " + " L ".join("%.1f %.1f" % p for p in pts_right) + " Z"
    f.append(svg_path(path_cu, stroke="#d35400", sw=2.5, fill="#fdebd0"))

    f.append(text(rcx, rcy - 15, "Деформоване ядро", size=12, bold=True, color="#d35400"))
    f.append(text(rcx, rcy + 10, "Поверхня Фермі", size=12, color="#d35400"))

    f.append(circle(630 + 110, 230, 5, fill="#c0392b", stroke="none"))
    f.append(text(630 + 75, 215, "Контакт під 90°", size=10, bold=True, color="#c0392b"))

    f.append(text(630, 385, "∇_k E · n̂ = 0 на межі зони Бріллюена", size=12, bold=True, color=INK))

    render(os.path.join(OUT, "fermi-sphere-vs-lattice.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Траєкторії електронів у k-просторі у магнітному полі
# ════════════════════════════════════════════════════════════════════════════
def fig_cyclotron_orbits_kspace():
    W, H = 840, 420
    f = []

    f.append(line(280, 25, 280, 395, color=MUTED, sw=1.5, dash="4 4"))
    f.append(line(560, 25, 560, 395, color=MUTED, sw=1.5, dash="4 4"))

    # Панель 1: Замкнена електронна орбіта
    f.append(text(140, 35, "Електронна орбіта", size=14, bold=True, color="#2980b9"))
    f.append(text(140, 55, "Обхід проти годинникової", size=12, color=MUTED))
    f.append(circle(140, 210, 75, fill="#e8f4f8", stroke="#2980b9", sw=2.5))
    f.append(arrow(140 + 75, 210, 140 + 75, 190, color="#2980b9", sw=2.2))
    f.append(text(140, 205, "Заповнені", size=12, bold=True, color="#2980b9"))
    f.append(text(140, 225, "стани всередині", size=11, color="#2980b9"))
    f.append(text(140, 375, "S_e (електронна кишеня)", size=12, bold=True, color=INK))

    # Панель 2: Замкнена діркова орбіта
    f.append(text(420, 35, "Діркова орбіта", size=14, bold=True, color="#c0392b"))
    f.append(text(420, 55, "Обхід за годинниковою стрілкою", size=12, color=MUTED))
    f.append(rect(310, 120, 220, 180, fill="#fdedec", stroke="none", rx=6))
    f.append(circle(420, 210, 65, fill="#ffffff", stroke="#c0392b", sw=2.5))
    f.append(arrow(420 + 65, 210, 420 + 65, 230, color="#c0392b", sw=2.2))
    f.append(text(420, 205, "Порожні стани", size=12, bold=True, color="#c0392b"))
    f.append(text(420, 225, "(вакансії / дірки)", size=11, color="#c0392b"))
    f.append(text(420, 375, "S_h (діркова кишеня)", size=12, bold=True, color=INK))

    # Панель 3: Відкрита орбіта
    f.append(text(700, 35, "Відкрита орбіта", size=14, bold=True, color="#8e44ad"))
    f.append(text(700, 55, "Нескінченний рух через ґратку", size=12, color=MUTED))

    for x_b in [610, 790]:
        f.append(line(x_b, 100, x_b, 320, color=MUTED, sw=1.2, dash="3 3"))

    pts_open = []
    for y_val in range(100, 330, 4):
        x_val = 700 + 45 * math.sin((y_val - 100) * 0.05)
        pts_open.append((x_val, y_val))
    path_op = "M " + " L ".join("%.1f %.1f" % p for p in pts_open)
    f.append(svg_path(path_op, stroke="#8e44ad", sw=2.8, fill="none"))
    f.append(arrow(pts_open[20][0], pts_open[20][1], pts_open[25][0], pts_open[25][1], color="#8e44ad", sw=2.5))
    f.append(arrow(pts_open[50][0], pts_open[50][1], pts_open[55][0], pts_open[55][1], color="#8e44ad", sw=2.5))

    f.append(text(700, 210, "Беззамкнена", size=12, bold=True, color="#8e44ad"))
    f.append(text(700, 230, "траєкторія в k-просторі", size=11, color="#8e44ad"))
    f.append(text(700, 375, "Гігантський магнітоопір", size=12, bold=True, color=INK))

    render(os.path.join(OUT, "cyclotron-orbits-kspace.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Топологічні переходи Ліфшиця
# ════════════════════════════════════════════════════════════════════════════
def fig_lifshitz_transitions():
    W, H = 840, 420
    f = []

    f.append(line(420, 25, 420, 395, color=MUTED, sw=1.5, dash="4 4"))

    # ── Ліва панель: Перехід типу "поява/зникнення порожнини" ──
    f.append(text(210, 35, "Тип 1: Поява / зникнення кишені", size=14, bold=True, color=INK))
    f.append(text(210, 55, "Зміна зв'язності (утворення нової порожнини)", size=12, color=MUTED))

    # Стан 1: E < Ec
    f.append(rect(40, 110, 100, 160, fill="#f4f6f8", stroke="#bdc3c7", sw=1.5, rx=6))
    f.append(circle(90, 190, 3, fill="#7f8c8d", stroke="none"))
    f.append(text(90, 140, "E < E_c", size=12, bold=True, color=MUTED))
    f.append(text(90, 245, "Немає порожнини", size=10, color=MUTED))

    f.append(arrow(150, 190, 180, 190, color="#27ae60", sw=2.0))

    # Стан 2: E = Ec
    f.append(rect(190, 110, 100, 160, fill="#f4f6f8", stroke="#27ae60", sw=1.8, rx=6))
    f.append(circle(240, 190, 6, fill="#27ae60", stroke="none"))
    f.append(text(240, 140, "E = E_c", size=12, bold=True, color="#27ae60"))
    f.append(text(240, 245, "Зародження", size=10, bold=True, color="#27ae60"))

    f.append(arrow(300, 190, 330, 190, color="#27ae60", sw=2.0))

    # Стан 3: E > Ec
    f.append(rect(340, 110, 65, 160, fill="#e8f8f5", stroke="#27ae60", sw=2.0, rx=6))
    f.append(circle(372, 190, 24, fill="#27ae60", stroke="#1e8449", sw=1.5))
    f.append(text(372, 140, "E > E_c", size=12, bold=True, color="#1e8449"))
    f.append(text(372, 245, "Нова кишеня", size=10, bold=True, color="#1e8449"))

    f.append(text(210, 375, "Сингулярність густини станів δg(E) ∝ √(E - E_c)", size=12, bold=True, color=INK))

    # ── Права панель: Перехід типу "утворення/розрив перетяжки" ──
    f.append(text(630, 35, "Тип 2: Утворення / розрив перетяжки", size=14, bold=True, color=INK))
    f.append(text(630, 55, "Зміна топологічного роду (перебудова шиї)", size=12, color=MUTED))

    # До переходу: дві роз'єднані поверхні
    f.append(rect(450, 110, 100, 160, fill="#f4f6f8", stroke="#bdc3c7", sw=1.5, rx=6))
    f.append(circle(480, 190, 22, fill="#e74c3c", stroke="none"))
    f.append(circle(520, 190, 22, fill="#e74c3c", stroke="none"))
    f.append(text(500, 140, "E < E_c", size=12, bold=True, color=MUTED))
    f.append(text(500, 245, "Два листочки", size=10, color=MUTED))

    f.append(arrow(560, 190, 580, 190, color="#d35400", sw=2.0))

    # Після переходу: з'єднаний гантелеподібний міст
    f.append(rect(590, 110, 210, 160, fill="#fdedec", stroke="#d35400", sw=2.0, rx=6))
    path_bridge = "M 610 170 Q 695 185 780 170 L 780 210 Q 695 195 610 210 Z"
    f.append(svg_path(path_bridge, stroke="#c0392b", sw=2.0, fill="#e74c3c"))
    f.append(text(695, 140, "E > E_c (Міст / Перетяжка)", size=12, bold=True, color="#c0392b"))
    f.append(text(695, 245, "Безперервний канал для електронів", size=10, bold=True, color="#c0392b"))

    f.append(text(630, 375, "Стрибок термоЕДС та аномалії стисливості", size=12, bold=True, color=INK))

    render(os.path.join(OUT, "lifshitz-transitions.svg"), W, H, *f)

if __name__ == "__main__":
    fig_fermi_sphere_vs_lattice()
    fig_cyclotron_orbits_kspace()
    fig_lifshitz_transitions()
    print("SVG figures successfully generated!")
