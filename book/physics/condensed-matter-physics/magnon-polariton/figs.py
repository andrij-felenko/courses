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

def ellipse_custom(cx, cy, rx, ry, fill=FILL, stroke=LINE, sw=1.5, angle=0, dash=None):
    tr = ' transform="rotate(%.1f %.1f %.1f)"' % (angle, cx, cy) if angle != 0 else ''
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" stroke-width="%.1f"%s%s/>' % (cx, cy, rx, ry, fill, stroke, sw, tr, d_attr)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Гібридизація магнонів та фотонів у резонаторі
# ════════════════════════════════════════════════════════════════════════════
def fig_magnon_polariton_hybridization():
    W, H = 840, 440
    f = []

    # Розділювальна лінія
    f.append(line(420, 20, 420, 420, color=MUTED, sw=1.5, dash="4 4"))

    # ── Ліва панель: Схема мікрохвильової кавіті з YIG-сферою ──
    f.append(text(210, 32, "Спін-фотонна резонаторна система", size=14, bold=True, color=INK))
    f.append(text(210, 52, "YIG-сфера у стоячій НВЧ-хвилі b_rf(t)", size=12, color=MUTED))

    # Корпус резонатора (мідна кавіті)
    f.append(rect(40, 75, 340, 270, fill="#fef9e7", stroke="#d35400", sw=2.5, rx=10))
    f.append(text(210, 95, "Мікрохвильовий резонатор (добротність Q)", size=11, bold=True, color="#a04000"))

    # Стояча електромагнітна хвиля b_rf (зелена синусоїда)
    wave_pts = []
    for x_i in range(50, 370, 5):
        y_i = 210 + 45 * math.sin(2 * math.pi * (x_i - 50) / 160)
        wave_pts.append((x_i, y_i))
    wave_str = "M " + " L ".join("%.1f %.1f" % p for p in wave_pts)
    f.append(svg_path(wave_str, stroke=FIELD, sw=2.0, dash="5 3"))
    f.append(text(120, 150, "Поле b_rf", size=11, bold=True, color=FIELD))

    # Вхідний та вихідний зонди (порт 1 та порт 2)
    f.append(rect(15, 195, 25, 30, fill="#ebf5fb", stroke="#2980b9", sw=1.5, rx=3))
    f.append(line(40, 210, 80, 210, color="#2980b9", sw=2.0))
    f.append(text(27, 190, "Порт 1", size=10, bold=True, color="#1b4f72"))

    f.append(rect(380, 195, 25, 30, fill="#ebf5fb", stroke="#2980b9", sw=1.5, rx=3))
    f.append(line(340, 210, 380, 210, color="#2980b9", sw=2.0))
    f.append(text(393, 190, "Порт 2", size=10, bold=True, color="#1b4f72"))

    # Сфера YIG в пучності магнітного поля
    f.append(circle(210, 210, 28, fill="#fadbd8", stroke="#c0392b", sw=2.5))
    f.append(text(210, 206, "YIG", size=12, bold=True, color="#78281f"))
    f.append(text(210, 222, "m, ω_m", size=10, bold=True, color="#78281f"))

    # Зовнішнє поле H0 (вертикальні стрілки)
    for x_h in [100, 210, 320]:
        f.append(line(x_h, 325, x_h, 265, color="#8e44ad", sw=1.8))
        f.append(polygon([(x_h-4, 270), (x_h, 260), (x_h+4, 270)], fill="#8e44ad"))
    f.append(text(210, 342, "Зовнішнє статичне поле H₀", size=11, bold=True, color="#8e44ad"))

    # Формула зв'язку
    f.append(text(210, 395, "Колективна взаємодія: g_eff = g₀ · √N", size=13, bold=True, color=INK))

    # ── Права панель: Спектр антиперетину (Магнон-поляритони) ──
    f.append(text(630, 32, "Антиперетин та розщеплення Рабі", size=14, bold=True, color=INK))
    f.append(text(630, 52, "Гібридизація модальних віток LMP та UMP", size=12, color=MUTED))

    # Осі координат
    ox, oy = 480, 360
    w_w, w_h = 320, 270
    f.append(line(ox, oy, ox + w_w, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - w_h, color=INK, sw=1.8))
    f.append(polygon([(ox + w_w - 6, oy - 4), (ox + w_w + 4, oy), (ox + w_w - 6, oy + 4)], fill=INK))
    f.append(polygon([(ox - 4, oy - w_h + 6), (ox, oy - w_h - 4), (ox + 4, oy - w_h + 6)], fill=INK))
    f.append(text(ox + w_w, oy + 22, "Поле H₀", size=11, bold=True, color=INK))
    f.append(text(ox - 25, oy - w_h + 10, "Частота ω", size=11, bold=True, color=INK))

    # Незаряджені модові лінії (пунктир)
    # Фотона мода wa (горизонтальна)
    y_wa = oy - 135
    f.append(line(ox, y_wa, ox + w_w - 20, y_wa, color="#2980b9", sw=1.5, dash="4 4"))
    f.append(text(ox + 45, y_wa - 8, "Фотонна мода ω_a", size=11, bold=True, color="#2980b9"))

    # Магнонна мода wm(H0) (похила)
    f.append(line(ox + 20, oy - 25, ox + w_w - 40, oy - 245, color="#8e44ad", sw=1.5, dash="4 4"))
    f.append(text(ox + w_w - 110, oy - 225, "Магнонна мода ω_m(H₀)", size=11, bold=True, color="#8e44ad"))

    # Гібридизовані вітки магнон-поляритонів (LMP та UMP)
    g_val = 40.0
    pts_lmp = []
    pts_ump = []
    for step in range(0, 260, 5):
        x_p = ox + 20 + step
        delta = 0.9 * (step - 125)
        sq = math.sqrt((delta / 2.0)**2 + g_val**2)
        w_lmp = (oy - 135) + (delta / 2.0 - sq)
        w_ump = (oy - 135) + (delta / 2.0 + sq)
        pts_lmp.append((x_p, w_lmp))
        pts_ump.append((x_p, w_ump))

    str_lmp = "M " + " L ".join("%.1f %.1f" % p for p in pts_lmp)
    str_ump = "M " + " L ".join("%.1f %.1f" % p for p in pts_ump)

    f.append(svg_path(str_lmp, stroke=POS, sw=2.8))
    f.append(svg_path(str_ump, stroke=POS, sw=2.8))

    f.append(text(ox + 210, oy - 65, "LMP (нижня вітка)", size=11, bold=True, color=POS))
    f.append(text(ox + 70, oy - 200, "UMP (верхня вітка)", size=11, bold=True, color=POS))

    # Вакуумне розщеплення Рабі
    x_res = ox + 145
    y_u = (oy - 135) - g_val
    y_l = (oy - 135) + g_val
    f.append(line(x_res, y_u, x_res, y_l, color=DARK, sw=1.8))
    f.append(polygon([(x_res-4, y_u+6), (x_res, y_u), (x_res+4, y_u+6)], fill=DARK))
    f.append(polygon([(x_res-4, y_l-6), (x_res, y_l), (x_res+4, y_l-6)], fill=DARK))
    f.append(text(x_res + 14, oy - 148, "Ω_R = 2 g_eff", size=11, bold=True, color=DARK))

    render(os.path.join(OUT, "magnon-polariton-hybridization.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Спектроскопія коефіцієнта проходження S21 та розщеплення Рабі
# ════════════════════════════════════════════════════════════════════════════
def fig_rabi_splitting_spectrum():
    W, H = 840, 440
    f = []

    # Розділювальна лінія
    f.append(line(420, 20, 420, 420, color=MUTED, sw=1.5, dash="4 4"))

    # ── Ліва панель: 2D Карта проходження S21(ω, H0) ──
    f.append(text(210, 32, "Двовимірна карта проходження S₂₁(ω, H₀)", size=14, bold=True, color=INK))
    f.append(text(210, 52, "Зрізи спектра при різній розстройці Δ = ω_m - ω_a", size=12, color=MUTED))

    ox1, oy1 = 60, 360
    w1, h1 = 320, 270

    # Прямокутний фон карти
    f.append(rect(ox1, oy1 - h1, w1, h1, fill="#ebf5fb", stroke=LINE, sw=1.5))

    # Спектральні лінії антиперетину на карті
    g_val = 38.0
    pts1_lmp, pts1_ump = [], []
    for step in range(0, 310, 5):
        xp = ox1 + step
        delta = 0.8 * (step - 155)
        sq = math.sqrt((delta / 2.0)**2 + g_val**2)
        w_lmp = (oy1 - 135) + (delta / 2.0 - sq)
        w_ump = (oy1 - 135) + (delta / 2.0 + sq)
        pts1_lmp.append((xp, w_lmp))
        pts1_ump.append((xp, w_ump))

    f.append(svg_path("M " + " L ".join("%.1f %.1f" % p for p in pts1_lmp), stroke="#2457d6", sw=4.0))
    f.append(svg_path("M " + " L ".join("%.1f %.1f" % p for p in pts1_ump), stroke="#2457d6", sw=4.0))

    # Вертикальні пунктирні зрізи
    f.append(line(ox1 + 65, oy1 - h1, ox1 + 65, oy1, color="#e74c3c", sw=1.5, dash="3 3"))
    f.append(text(ox1 + 65, oy1 + 18, "Δ < 0", size=10, bold=True, color="#e74c3c"))

    f.append(line(ox1 + 155, oy1 - h1, ox1 + 155, oy1, color="#27ae60", sw=1.8, dash="3 3"))
    f.append(text(ox1 + 155, oy1 + 18, "Δ = 0", size=11, bold=True, color="#27ae60"))

    f.append(line(ox1 + 245, oy1 - h1, ox1 + 245, oy1, color="#8e44ad", sw=1.5, dash="3 3"))
    f.append(text(ox1 + 245, oy1 + 18, "Δ > 0", size=10, bold=True, color="#8e44ad"))

    # Осі для карти
    f.append(text(ox1 + w1 / 2, oy1 + 35, "Магнітне поле H₀", size=11, bold=True, color=INK))
    f.append(text(ox1 - 30, oy1 - h1 / 2, "Частота ω", size=11, bold=True, color=INK))

    # ── Права панель: Окремі зрізи проходження S21(ω) ──
    f.append(text(630, 32, "Спектри проходження S₂₁(ω) у 3 точках", size=14, bold=True, color=INK))
    f.append(text(630, 52, "Поява подвійного резонансного піка при Δ = 0", size=12, color=MUTED))

    # 1. Спектр при Δ = 0
    ox2, oy2 = 470, 240
    f.append(line(ox2, oy2, ox2 + 320, oy2, color=MUTED, sw=1.0))
    s21_res = []
    for step in range(0, 310, 4):
        xp = ox2 + step
        w_rel = (step - 150) / 15.0
        val = 1.0 - 0.45 / (1.0 + (w_rel - 2.5)**2) - 0.45 / (1.0 + (w_rel + 2.5)**2)
        yp = oy2 - val * 70
        s21_res.append((xp, yp))

    f.append(svg_path("M " + " L ".join("%.1f %.1f" % p for p in s21_res), stroke=FIELD, sw=2.5))
    f.append(text(ox2 + 150, oy2 - 82, "Δ = 0: Розщеплення 2 g_eff", size=11, bold=True, color=FIELD))

    # 2. Спектр при Δ < 0
    oy3 = 130
    f.append(line(ox2, oy3, ox2 + 320, oy3, color=MUTED, sw=1.0))
    s21_neg = []
    for step in range(0, 310, 4):
        xp = ox2 + step
        w_rel = (step - 150) / 15.0
        val = 1.0 - 0.7 / (1.0 + (w_rel - 3.5)**2) - 0.15 / (1.0 + (w_rel + 2.0)**2)
        yp = oy3 - val * 50
        s21_neg.append((xp, yp))

    f.append(svg_path("M " + " L ".join("%.1f %.1f" % p for p in s21_neg), stroke="#e74c3c", sw=2.0))
    f.append(text(ox2 + 40, oy3 - 58, "Δ < 0: Переважає фотонна мода", size=10, bold=True, color="#e74c3c"))

    # 3. Спектр при Δ > 0
    oy4 = 360
    f.append(line(ox2, oy4, ox2 + 320, oy4, color=MUTED, sw=1.0))
    s21_pos = []
    for step in range(0, 310, 4):
        xp = ox2 + step
        w_rel = (step - 150) / 15.0
        val = 1.0 - 0.15 / (1.0 + (w_rel - 2.0)**2) - 0.7 / (1.0 + (w_rel + 3.5)**2)
        yp = oy4 - val * 50
        s21_pos.append((xp, yp))

    f.append(svg_path("M " + " L ".join("%.1f %.1f" % p for p in s21_pos), stroke="#8e44ad", sw=2.0))
    f.append(text(ox2 + 220, oy4 - 58, "Δ > 0: Переважає магнонна мода", size=10, bold=True, color="#8e44ad"))

    f.append(text(ox2 + 160, oy4 + 22, "Частота НВЧ-поля ω", size=11, bold=True, color=INK))

    render(os.path.join(OUT, "rabi-splitting-spectrum.svg"), W, H, *f)


if __name__ == "__main__":
    fig_magnon_polariton_hybridization()
    fig_rabi_splitting_spectrum()
    print("Generated all figures for magnon-polariton successfully.")
