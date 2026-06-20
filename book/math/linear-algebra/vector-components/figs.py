import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)

# ── Фігура 1: vector-projection ──────────────────────────────────────────────
# Показуємо вектор a у першій чверті, кут theta, складові aₓ і a_y як катети.

def fig_vector_projection():
    W, H = 880, 420
    parts = []

    # Осі координат — oy нижче, щоб вісь y не виходила за межі
    ox, oy = 120, 310  # початок координат

    # Вектор: довжина 220, кут 50° від осі x
    import math
    theta = math.radians(50)
    L = 220
    vx = L * math.cos(theta)
    vy = L * math.sin(theta)

    ex = ox + vx
    ey = oy - vy  # SVG: y вниз, тому мінус

    # --- Осі ---
    axis_len = 350
    parts.append(arrow(ox - 20, oy, ox + axis_len, oy, color=INK, sw=1.8))
    parts.append(arrow(ox, oy + 20, ox, oy - 270, color=INK, sw=1.8))

    # Підписи осей
    parts.append(text(ox + axis_len + 16, oy + 5, "x", size=16, bold=True, color=INK))
    parts.append(text(ox + 5, oy - 278, "y", size=16, bold=True, color=INK))

    # --- Прямокутний трикутник ---
    # Горизонтальна пунктирна лінія від початку до (ex, oy)
    parts.append(line(ox, oy, ex, oy, color=MUTED, sw=1.2, dash="6,4"))
    # Вертикальна пунктирна лінія від (ex, oy) до (ex, ey)
    parts.append(line(ex, oy, ex, ey, color=MUTED, sw=1.2, dash="6,4"))

    # Значок прямого кута
    sq = 10
    parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                 'fill="none" stroke="%s" stroke-width="1.2"/>' % (ex - sq, oy - sq, sq, sq, MUTED))

    # --- Сам вектор a (POS = червоний) ---
    parts.append(arrow(ox, oy, ex, ey, color=POS, sw=2.5))

    # --- Підписи складових ---
    # aₓ під горизонтальним катетом
    parts.append(text((ox + ex) / 2, oy + 28, "aₓ = |a| · cos θ", size=14, color=NEG, anchor="middle"))
    # a_y збоку від вертикального катету
    parts.append(text(ex + 64, (oy + ey) / 2, "a_y = |a| · sin θ", size=14, color=FIELD, anchor="middle"))

    # --- Підпис вектора a ---
    mid_x = ox + vx / 2 - 24
    mid_y = oy - vy / 2 - 14
    parts.append(text(mid_x, mid_y, "a", size=17, color=POS, bold=True))

    # --- Кут θ (дуга) ---
    arc_r = 52
    # SVG arc: від 0° до -theta (у SVG y вниз, тому кут іде у від'ємному напрямку y)
    start_x = ox + arc_r
    start_y = oy
    end_x = ox + arc_r * math.cos(theta)
    end_y = oy - arc_r * math.sin(theta)
    parts.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 0 %.1f %.1f" '
                 'fill="none" stroke="%s" stroke-width="1.5"/>' % (
                     start_x, start_y, arc_r, arc_r, end_x, end_y, MUTED))
    parts.append(text(ox + arc_r + 14, oy - 16, "θ", size=15, color=MUTED, italic=True))

    # --- Крапки і мітки ---
    # Кінець вектора
    parts.append(circle(ex, ey, 4, fill=POS, stroke=POS, sw=0))

    # Початок координат
    parts.append(circle(ox, oy, 4, fill=INK, stroke=INK, sw=0))
    parts.append(text(ox - 12, oy + 18, "O", size=14, color=INK))

    # Проєкція на x
    parts.append(circle(ex, oy, 4, fill=NEG, stroke=NEG, sw=0))
    # Проєкція на y
    parts.append(circle(ox, ey, 4, fill=FIELD, stroke=FIELD, sw=0))
    parts.append(line(ox - 6, ey, ox + 6, ey, color=FIELD, sw=1.5))

    # Довжина |a|
    parts.append(text(ex + 18, ey - 12, "кінець вектора a", size=13, color=POS, anchor="start"))

    # Заголовок-підпис
    parts.append(text(W / 2, 30, "Вектор як трикутник: складові = катети", size=16, bold=True))

    render("img/vector-projection.svg", W, H, *parts)

fig_vector_projection()
print("vector-projection.svg OK")


# ── Фігура 2: basis-decomposition ────────────────────────────────────────────
# Показуємо a = aₓ·î + a_y·ĵ: стрілки î і ĵ, зважені копії, та підсумковий вектор a.

def fig_basis_decomposition():
    W, H = 900, 400
    parts = []

    import math
    ox, oy = 140, 290  # початок координат

    # Вектор a: (aₓ = 3, a_y = 2) у масштабі 70px на одиницю
    scale = 70
    ax_v, ay_v = 3, 2  # компоненти
    vx = ax_v * scale
    vy = ay_v * scale

    ex = ox + vx
    ey = oy - vy

    # --- Осі ---
    parts.append(arrow(ox - 20, oy, ox + 310, oy, color=INK, sw=1.8))
    parts.append(arrow(ox, oy + 20, ox, oy - 220, color=INK, sw=1.8))
    parts.append(text(ox + 320, oy + 4, "x", size=16, bold=True))
    parts.append(text(ox + 6, oy - 228, "y", size=16, bold=True))

    # --- Базисні вектори î і ĵ (малі) ---
    # î вздовж x
    parts.append(arrow(ox, oy, ox + scale, oy, color=NEG, sw=2.0))
    parts.append(text(ox + scale / 2, oy + 22, "î", size=15, color=NEG, bold=True, italic=True))

    # ĵ вздовж y
    parts.append(arrow(ox, oy, ox, oy - scale, color=FIELD, sw=2.0))
    parts.append(text(ox - 22, oy - scale / 2, "ĵ", size=15, color=FIELD, bold=True, italic=True))

    # --- Пунктирний "ланцюжок": aₓ кроків î, потім a_y кроків ĵ ---
    # Горизонтальна складова (aₓ · î) — товстіша, NEG
    parts.append(arrow(ox, oy, ex, oy, color=NEG, sw=2.5))
    # Вертикальна складова (a_y · ĵ) від кінця горизонталі
    parts.append(arrow(ex, oy, ex, ey, color=FIELD, sw=2.5))

    # Пунктири до проєкцій
    parts.append(line(ox, ey, ex, ey, color=MUTED, sw=1.0, dash="5,4"))
    parts.append(line(ex, oy, ex, ey, color=MUTED, sw=0.8, dash="5,4"))

    # --- Вектор a (підсумковий) ---
    parts.append(arrow(ox, oy, ex, ey, color=POS, sw=2.8))
    parts.append(text((ox + ex) / 2 - 20, (oy + ey) / 2 - 12, "a", size=18, color=POS, bold=True))

    # --- Підписи складових ---
    parts.append(text((ox + ex) / 2, oy + 28, "aₓ · î", size=14, color=NEG, anchor="middle"))
    parts.append(text(ex + 46, (oy + ey) / 2, "a_y · ĵ", size=14, color=FIELD, anchor="middle"))

    # --- Розгорнута формула ---
    box_cx = 660
    box_cy = 180
    b, bw, bh = textbox(box_cx, box_cy, "a = aₓ · î + a_y · ĵ", size=15, bold=True,
                         fill="#fef9ec", stroke="#c8a000", sw=1.8, pad=14)
    parts.append(b)

    # Приклад з числами
    parts.append(text(box_cx, box_cy + bh / 2 + 24,
                       "Тут: a = 3·î + 2·ĵ", size=13, color=MUTED, anchor="middle"))

    # Початок координат
    parts.append(circle(ox, oy, 4, fill=INK, stroke=INK, sw=0))
    parts.append(text(ox - 14, oy + 18, "O", size=14, color=INK))

    # Кінець вектора
    parts.append(circle(ex, ey, 5, fill=POS, stroke=POS, sw=0))

    # Заголовок
    parts.append(text(W / 2, 30, "Розклад за базисом: вектор = зважена сума î і ĵ", size=16, bold=True))

    render("img/basis-decomposition.svg", W, H, *parts)

fig_basis_decomposition()
print("basis-decomposition.svg OK")
