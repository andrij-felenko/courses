import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

os.makedirs("img", exist_ok=True)

# ── Фігура: projection ───────────────────────────────────────────────────────
# Скалярний добуток як проєкція: вектор b відкидає тінь |b|·cos θ на напрям a.
# Показуємо a (червоний, уздовж осі x), b (синій, під кутом), кут θ між ними,
# перпендикуляр від кінця b на лінію a і саму проєкцію (зелений відрізок).

def fig_projection():
    W, H = 880, 440
    parts = []

    ox, oy = 130, 330  # спільний початок обох векторів

    # Вектор a — довгий, уздовж осі x (напрям, на який проєктуємо)
    La = 560
    ax_end = ox + La
    ay_end = oy

    # Вектор b — коротший, під кутом theta до a
    theta = math.radians(40)
    Lb = 300
    bx = Lb * math.cos(theta)
    by = Lb * math.sin(theta)
    bex = ox + bx
    bey = oy - by  # SVG: y вниз

    # Проєкція b на a: довжина |b|·cos θ уздовж осі x
    proj_len = Lb * math.cos(theta)
    px = ox + proj_len   # точка-основа перпендикуляра на лінії a
    py = oy

    # --- допоміжна лінія напряму a (тонка, на повну довжину) ---
    parts.append(line(ox, oy, ax_end + 10, oy, color=MUTED, sw=1.0, dash="2,4"))

    # --- проєкція (зелений товстий відрізок на осі a) ---
    parts.append(line(ox, oy, px, py, color=FIELD, sw=5.0))

    # --- перпендикуляр від кінця b на лінію a (пунктир) ---
    parts.append(line(bex, bey, px, py, color=MUTED, sw=1.3, dash="6,4"))

    # значок прямого кута біля основи перпендикуляра
    sq = 11
    parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                 'fill="none" stroke="%s" stroke-width="1.2"/>'
                 % (px - sq, py - sq, sq, sq, MUTED))

    # --- вектор a (червоний) ---
    parts.append(arrow(ox, oy, ax_end, ay_end, color=POS, sw=2.8))
    parts.append(text(ax_end - 16, oy + 26, "a", size=18, color=POS, bold=True))

    # --- вектор b (синій) ---
    parts.append(arrow(ox, oy, bex, bey, color=NEG, sw=2.8))
    parts.append(text(ox + bx / 2 - 22, oy - by / 2 - 10, "b", size=18, color=NEG, bold=True))

    # --- кут θ (дуга між a і b) ---
    arc_r = 64
    sx = ox + arc_r
    sy = oy
    aex = ox + arc_r * math.cos(theta)
    aey = oy - arc_r * math.sin(theta)
    parts.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 0 %.1f %.1f" '
                 'fill="none" stroke="%s" stroke-width="1.6"/>'
                 % (sx, sy, arc_r, arc_r, aex, aey, INK))
    parts.append(text(ox + arc_r + 16, oy - 18, "θ", size=16, color=INK, italic=True))

    # --- підпис проєкції під зеленим відрізком ---
    parts.append(text((ox + px) / 2, oy + 30, "|b| · cos θ", size=15, color=FIELD,
                      bold=True, anchor="middle"))
    parts.append(text((ox + px) / 2, oy + 50, "(проєкція b на a)", size=12, color=MUTED,
                      anchor="middle"))

    # --- формула скалярного добутку в рамці ---
    box_cx, box_cy = 660, 120
    b, bw, bh = textbox(box_cx, box_cy, "a · b = |a| · (|b| · cos θ)",
                        size=15, bold=True, fill="#fef9ec", stroke="#c8a000",
                        sw=1.8, pad=14)
    parts.append(b)
    parts.append(text(box_cx, box_cy + bh / 2 + 22,
                      "довжина a × тінь b на a", size=12, color=MUTED, anchor="middle"))

    # --- точки ---
    parts.append(circle(ox, oy, 4, fill=INK, stroke=INK, sw=0))
    parts.append(text(ox - 14, oy + 18, "O", size=14, color=INK))
    parts.append(circle(bex, bey, 4.5, fill=NEG, stroke=NEG, sw=0))
    parts.append(circle(px, py, 4.5, fill=FIELD, stroke=FIELD, sw=0))

    # --- заголовок ---
    parts.append(text(W / 2, 30, "Скалярний добуток = довжина a × проєкція b на a",
                      size=16, bold=True))

    render("img/projection.svg", W, H, *parts)

fig_projection()
print("projection.svg OK")
