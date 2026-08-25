# -*- coding: utf-8 -*-
"""figs.py — генератор SVG-ілюстрацій до статті «Втрати в обмотках трансформатора».
Використовує svgkit зі scripts/ (імпорт, без копіювання).
Вивід у ./img/.
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Скін-ефект проти ефекту близькості ──────────────────────────────
def fig_skin_proximity():
    W, H = 840, 460
    p = []
    p.append(text(W / 2, 28, "Скін-ефект та ефект близькості у провідниках обмотки", size=17, bold=True))
    p.append(text(W / 2, 48, "Розподіл густини змінного струму під дією власного та зовнішнього магнітних полів",
                  size=12, color=MUTED, italic=True))

    # ── ЛІВОРУЧ: Скін-ефект (Skin Effect) ─────────────────────────────────────
    lx = 210
    p.append(rect(20, 65, 380, 375, fill="#f8fafc", stroke="#cbd5e1", sw=1.2))
    p.append(text(lx, 88, "Скін-ефект (одиночний провідник)", size=14, bold=True, color=INK))

    # Круглий провідник із градієнтом густини струму (концентричні кільця)
    cy = 200
    r_outer = 75
    # Зовнішнє кільце (висока густина)
    p.append(circle(lx, cy, r_outer, fill="#fee2e2", stroke=POS, sw=2.5))
    p.append(circle(lx, cy, r_outer - 15, fill="#ffedd5", stroke="#f97316", sw=1.5))
    p.append(circle(lx, cy, r_outer - 32, fill="#fef9c3", stroke="#eab308", sw=1.2))
    p.append(circle(lx, cy, r_outer - 50, fill="#f1f5f9", stroke="#94a3b8", sw=1.0))

    # Стрілка глибини скін-шару delta
    p.append(line(lx, cy - r_outer, lx, cy - r_outer + 20, color=POS, sw=2))
    p.append(arrow(lx + 28, cy - r_outer + 10, lx + 2, cy - r_outer + 5, color=POS, sw=1.5))
    p.append(text(lx + 34, cy - r_outer + 14, "δ (скін-шар)", size=11, color=POS, anchor="start", bold=True))

    # Напрямок струму та поле
    p.append(text(lx, cy, "J ≈ 0", size=13, color=MUTED, bold=True))
    p.append(text(lx, cy + 48, "J_max на поверхні", size=11.5, color=POS, bold=True))

    # Власне магнітне поле (пунктирне кільце)
    p.append('<circle cx="%.1f" cy="%.1f" r="92" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="4,4"/>' % (lx, cy, FIELD))
    p.append(arrow(lx + 92, cy - 2, lx + 92, cy + 8, color=FIELD, sw=1.6))
    p.append(text(lx, 312, "Власне змінне магнітне поле H_int", size=11, color=FIELD, bold=True))
    p.append(text(lx, 328, "витісняє струм до поверхні провідника", size=10.5, color=MUTED))

    # Опис внизу лівої панелі
    p.append(text(lx, 362, "Струм витісняється до країв", size=12, color=INK, bold=True))
    p.append(text(lx, 380, "Центральна частина міді не працює,", size=11, color=MUTED))
    p.append(text(lx, 398, "ефективний опір R_ac зростає як √f", size=11, color=MUTED))

    # ── ПРАВОРУЧ: Ефект близькості (Proximity Effect) ──────────────────────────
    rx = 630
    p.append(rect(440, 65, 380, 375, fill="#f8fafc", stroke="#cbd5e1", sw=1.2))
    p.append(text(rx, 88, "Ефект близькості (сусідні шари)", size=14, bold=True, color=INK))

    # Зовнішнє поле розсіювання від сусідніх шарів
    for dy in (-35, 0, 35):
        p.append(arrow(rx - 155, 200 + dy, rx + 155, 200 + dy, color=FIELD, sw=1.8))
    p.append(text(rx + 140, 155, "Поле H_ext", size=11, color=FIELD, anchor="end", bold=True))

    # Два сусідні провідники шару
    for offset_x in (-65, 65):
        cx_w = rx + offset_x
        # Тіло провідника
        p.append(circle(cx_w, cy, 42, fill="#f1f5f9", stroke="#64748b", sw=1.8))
        # Зміщена концентрація струму (один бік перевантажений через вихрові струми)
        if offset_x < 0:
            # На лівому витку струм витіснено вгору/вниз або на край
            p.append('<path d="M %d,%d A 42 42 0 0 1 %d,%d L %d,%d A 28 28 0 0 0 %d,%d Z" fill="#fee2e2" stroke="%s" stroke-width="1.5"/>' %
                     (cx_w - 42, cy, cx_w, cy - 42, cx_w, cy - 28, cx_w - 28, cy, POS))
            p.append(text(cx_w - 12, cy - 14, "J_max", size=10, color=POS, bold=True))
            p.append(text(cx_w + 14, cy + 12, "J_зворотний", size=9.5, color=NEG))
        else:
            p.append('<path d="M %d,%d A 42 42 0 0 1 %d,%d L %d,%d A 28 28 0 0 0 %d,%d Z" fill="#fee2e2" stroke="%s" stroke-width="1.5"/>' %
                     (cx_w, cy - 42, cx_w + 42, cy, cx_w + 28, cy, cx_w, cy - 28, POS))
            p.append(text(cx_w + 12, cy - 14, "J_max", size=10, color=POS, bold=True))
            p.append(text(cx_w - 14, cy + 12, "J_зворотний", size=9.5, color=NEG))

    p.append(text(rx, 312, "Поперечне поле H наводить вихрові контури", size=11, color=FIELD, bold=True))
    p.append(text(rx, 328, "Струми додаються з одного боку і віднімаються з іншого", size=10.5, color=MUTED))

    # Опис внизу правої панелі
    p.append(text(rx, 362, "Вихрові струми циркулюють у товщі", size=12, color=INK, bold=True))
    p.append(text(rx, 380, "Втрати ростуть із квадратом числа шарів m²", size=11, color=POS, bold=True))
    p.append(text(rx, 398, "Ефект близькості домінує над скін-ефектом!", size=11, color=POS))

    render(os.path.join(IMG, "skin-proximity.svg"), W, H, *p)


# ── Фігура 2: Розподіл МРС та чергування (Interleaving) ───────────────────────
def fig_mmf_interleaving():
    W, H = 840, 480
    p = []
    p.append(text(W / 2, 26, "Розподіл магніторушійної сили (МРС) у вікні осердя", size=17, bold=True))
    p.append(text(W / 2, 46, "Зниження напруженості поля розсіювання H(x) за допомогою секціонування (Interleaving)",
                  size=12, color=MUTED, italic=True))

    # ── ЛІВОРУЧ: Без чергування (P - S) ───────────────────────────────────────
    lx = 210
    p.append(rect(20, 65, 380, 395, fill="#f8fafc", stroke="#cbd5e1", sw=1.2))
    p.append(text(lx, 88, "Без чергування: P — S (4 шари + 4 шари)", size=13.5, bold=True, color=INK))

    # Схема шарів обмотки у вікні
    wy = 110
    # Первинна обмотка P (4 шари синього)
    for i in range(4):
        p.append(rect(50 + i * 36, wy, 32, 55, fill="#dbeafe", stroke=NEG, sw=1.2))
        p.append(text(66 + i * 36, wy + 32, "P%d" % (i + 1), size=11, color=NEG, bold=True))

    # Вторинна обмотка S (4 шари червоного)
    for i in range(4):
        p.append(rect(200 + i * 36, wy, 32, 55, fill="#fee2e2", stroke=POS, sw=1.2))
        p.append(text(216 + i * 36, wy + 32, "S%d" % (i + 1), size=11, color=POS, bold=True))

    # Графік МРС / H(x)
    gy = 310
    # Вісь X та Y
    p.append(line(45, gy, 355, gy, color=LINE, sw=1.5))
    p.append(line(45, gy + 15, 45, gy - 120, color=LINE, sw=1.5))
    p.append(text(40, gy - 125, "H(x), МРС", size=11, color=INK, anchor="end", bold=True))
    p.append(text(355, gy + 16, "x (вікно)", size=11, color=INK, anchor="end"))

    # Крива МРС: підйом від 0 до N*I на межі P/S, потім спад до 0
    p.append('<polygon points="45,%d 197,%d 344,%d 344,%d 45,%d" fill="#fee2e2" fill-opacity="0.6"/>' %
             (gy, gy - 100, gy, gy, gy))
    p.append(line(45, gy, 197, gy - 100, color=POS, sw=2.5))
    p.append(line(197, gy - 100, 344, gy, color=POS, sw=2.5))

    # Пікова точка
    p.append(circle(197, gy - 100, 4, fill=POS, stroke="#ffffff", sw=1.5))
    p.append(text(197, gy - 110, "Пік H_max = N·I", size=11.5, color=POS, bold=True))

    # Рівні шарів на графіку (пунктири)
    for i in range(1, 4):
        p.append(line(45 + i * 38, gy, 45 + i * 38, gy - i * 25, color="#94a3b8", sw=1.0, dash="3,3"))
        p.append(line(197 + i * 37, gy - 100 + i * 25, 197 + i * 37, gy, color="#94a3b8", sw=1.0, dash="3,3"))

    p.append(text(lx, 360, "Енергія магнітного поля розсіювання ∝ ∫H² dx", size=11.5, color=INK, bold=True))
    p.append(text(lx, 380, "Максимальне поле в зовнішніх шарах", size=11, color=MUTED))
    p.append(text(lx, 400, "Втрати близькості: F_R ∝ m² = 4² = 16", size=11.5, color=POS, bold=True))

    # ── ПРАВОРУЧ: Із чергуванням (P/2 - S - P/2) ──────────────────────────────
    rx = 630
    p.append(rect(440, 65, 380, 395, fill="#f8fafc", stroke="#cbd5e1", sw=1.2))
    p.append(text(rx, 88, "Секціонування: P/2 — S — P/2 (Interleaving)", size=13.5, bold=True, color=INK))

    # Схема шарів обмотки: P1, P2 (синій), S1..S4 (червоний), P3, P4 (синій)
    # P/2 (2 шари)
    for i in range(2):
        p.append(rect(465 + i * 34, wy, 30, 55, fill="#dbeafe", stroke=NEG, sw=1.2))
        p.append(text(480 + i * 34, wy + 32, "P%d" % (i + 1), size=10.5, color=NEG, bold=True))
    # S (4 шари)
    for i in range(4):
        p.append(rect(538 + i * 34, wy, 30, 55, fill="#fee2e2", stroke=POS, sw=1.2))
        p.append(text(553 + i * 34, wy + 32, "S%d" % (i + 1), size=10.5, color=POS, bold=True))
    # P/2 (2 шари)
    for i in range(2):
        p.append(rect(679 + i * 34, wy, 30, 55, fill="#dbeafe", stroke=NEG, sw=1.2))
        p.append(text(694 + i * 34, wy + 32, "P%d" % (i + 3), size=10.5, color=NEG, bold=True))

    # Графік МРС: підйом до (N*I)/2, перетин нуля в середині S, підйом до -(N*I)/2, спад до 0
    p.append(line(460, gy, 770, gy, color=LINE, sw=1.5))
    p.append(line(460, gy + 55, 460, gy - 75, color=LINE, sw=1.5))
    p.append(text(455, gy - 78, "H(x)", size=11, color=INK, anchor="end", bold=True))
    p.append(text(770, gy + 16, "x (вікно)", size=11, color=INK, anchor="end"))

    # Полігони площі під графіком (значно менша площа!)
    p.append('<polygon points="465,%d 534,%d 605,%d 465,%d" fill="#dcfce7" fill-opacity="0.7"/>' %
             (gy, gy - 50, gy, gy))
    p.append('<polygon points="605,%d 676,%d 748,%d 605,%d" fill="#dcfce7" fill-opacity="0.7"/>' %
             (gy, gy + 50, gy, gy))

    p.append(line(465, gy, 534, gy - 50, color=FIELD, sw=2.5))
    p.append(line(534, gy - 50, 676, gy + 50, color=FIELD, sw=2.5))
    p.append(line(676, gy + 50, 748, gy, color=FIELD, sw=2.5))

    p.append(circle(534, gy - 50, 4, fill=FIELD, stroke="#ffffff", sw=1.5))
    p.append(text(534, gy - 58, "H_max = N·I / 2", size=11, color=FIELD, bold=True))

    p.append(text(rx, 360, "Пікове поле впало вдвічі, площа ∫H²dx впала в 4 рази", size=11.5, color=FIELD, bold=True))
    p.append(text(rx, 380, "Ефективне число шарів у секції m_eff = 2 замість 4", size=11, color=MUTED))
    p.append(text(rx, 400, "Втрати близькості знижено у 4–5 разів!", size=11.5, color=FIELD, bold=True))

    render(os.path.join(IMG, "mmf-interleaving.svg"), W, H, *p)


# ── Фігура 3: Криві Доуелла (F_R vs xi) ───────────────────────────────────────
def fig_dowell_curves():
    W, H = 840, 480
    p = []
    p.append(text(W / 2, 26, "Криві Доуелла: коефіцієнт зростання опору F_R = R_ac / R_dc", size=17, bold=True))
    p.append(text(W / 2, 46, "Залежність коефіцієнта опору від відносної товщини шару ξ = h/δ для різного числа шарів m",
                  size=12, color=MUTED, italic=True))

    # Координатна сітка
    ox, oy = 90, 410
    gw, gh = 480, 330

    # Осі координат
    p.append(rect(ox, oy - gh, gw, gh, fill="#ffffff", stroke="#cbd5e1", sw=1.2))

    # Горизонтальні лінії (логарифмічна шкала F_R: 1, 2, 5, 10, 20, 50, 100)
    y_vals = [(1, "1"), (2, "2"), (5, "5"), (10, "10"), (20, "20"), (50, "50"), (100, "100")]
    for val, lbl in y_vals:
        # log10 mapping from 1 to 100 -> [0, 2]
        y_pos = oy - (math.log10(val) / 2.0) * gh
        p.append(line(ox, y_pos, ox + gw, y_pos, color="#e2e8f0", sw=1.0))
        p.append(text(ox - 10, y_pos + 4, lbl, size=11, color=MUTED, anchor="end"))
    p.append(text(ox - 35, oy - gh / 2, "F_R = R_ac / R_dc", size=12, color=INK, bold=True, anchor="middle"))

    # Вертикальні лінії (лінійна/логарифмічна шкала ξ від 0.1 до 4.0)
    x_vals = [(0.2, "0.2"), (0.5, "0.5"), (1.0, "1.0"), (1.5, "1.5"), (2.0, "2.0"), (2.5, "2.5"), (3.0, "3.0")]
    for val, lbl in x_vals:
        x_pos = ox + (val / 3.2) * gw
        if x_pos <= ox + gw:
            p.append(line(x_pos, oy, x_pos, oy - gh, color="#e2e8f0", sw=1.0))
            p.append(text(x_pos, oy + 18, lbl, size=11, color=MUTED))
    p.append(text(ox + gw / 2, oy + 38, "Відносна товщина провідника ξ = h / δ", size=12, color=INK, bold=True))

    # Формула Доуелла для побудови графіків
    def dowell_fr(xi, m):
        if xi < 1e-4:
            return 1.0
        # M(xi) = (sinh(2xi) + sin(2xi)) / (cosh(2xi) - cos(2xi))
        # D(xi) = (sinh(xi) - sin(xi)) / (cosh(xi) + cos(xi))
        # For small xi avoid division by zero
        try:
            m_term = (math.sinh(2 * xi) + math.sin(2 * xi)) / (math.cosh(2 * xi) - math.cos(2 * xi))
            d_term = (math.sinh(xi) - math.sin(xi)) / (math.cosh(xi) + math.cos(xi))
            fr = xi * (m_term + (2 * (m ** 2 - 1) / 3.0) * d_term)
            return max(1.0, fr)
        except OverflowError:
            return 100.0

    layers_info = [
        (1, "#2563eb", "m = 1 шар"),
        (2, "#059669", "m = 2 шари"),
        (3, "#d97706", "m = 3 шари"),
        (5, "#dc2626", "m = 5 шарів"),
        (10, "#9333ea", "m = 10 шарів"),
    ]

    for m, color, lbl in layers_info:
        pts = []
        n_steps = 100
        for i in range(n_steps + 1):
            xi = 0.05 + (3.15 * i / n_steps)
            fr = dowell_fr(xi, m)
            if fr > 100.0:
                fr = 100.0
            x_pos = ox + (xi / 3.2) * gw
            y_pos = oy - (math.log10(fr) / 2.0) * gh
            pts.append((x_pos, y_pos))

        d = "M %.1f,%.1f " % pts[0] + " ".join("L %.1f,%.1f" % q for q in pts[1:])
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, color))

        # Підпис біля кривої
        last_x, last_y = pts[-1]
        if m == 1:
            p.append(text(last_x + 6, last_y + 4, lbl, size=11, color=color, anchor="start", bold=True))
        elif m == 2:
            p.append(text(last_x + 6, last_y + 4, lbl, size=11, color=color, anchor="start", bold=True))
        elif m == 3:
            p.append(text(last_x + 6, last_y + 4, lbl, size=11, color=color, anchor="start", bold=True))
        elif m == 5:
            mid_x, mid_y = pts[65]
            p.append(text(mid_x - 10, mid_y - 8, lbl, size=11, color=color, anchor="end", bold=True))
        elif m == 10:
            mid_x, mid_y = pts[45]
            p.append(text(mid_x - 10, mid_y - 8, lbl, size=11, color=color, anchor="end", bold=True))

    # Зона оптимуму (мінімум для m >= 2)
    p.append(rect(ox + (0.6 / 3.2) * gw, oy - (math.log10(4) / 2.0) * gh - 35, 75, 45,
                  fill="#fef08a", stroke="#ca8a04", sw=1.2, rx=4))
    p.append(text(ox + (0.6 / 3.2) * gw + 37, oy - (math.log10(4) / 2.0) * gh - 20, "Оптимум ξ", size=10.5, color="#854d0e", bold=True))
    p.append(text(ox + (0.6 / 3.2) * gw + 37, oy - (math.log10(4) / 2.0) * gh - 6, "h ≈ 0.5...1.0 δ", size=9.5, color="#854d0e"))

    # Права панель з висновками
    px = 600
    p.append(rect(px, 75, 220, 335, fill="#f8fafc", stroke="#cbd5e1", sw=1.2))
    p.append(text(px + 110, 98, "Ключові висновки:", size=13, color=INK, bold=True))

    p.append(text(px + 15, 126, "1. Для m = 1:", size=11.5, color="#2563eb", anchor="start", bold=True))
    p.append(text(px + 15, 142, "   Опір росте плавно як ξ,", size=10.5, color=MUTED, anchor="start"))
    p.append(text(px + 15, 158, "   діє тільки скін-ефект.", size=10.5, color=MUTED, anchor="start"))

    p.append(text(px + 15, 186, "2. Для m ≥ 2 (багато шарів):", size=11.5, color="#dc2626", anchor="start", bold=True))
    p.append(text(px + 15, 202, "   F_R стрімко зростає ∝ m²!", size=10.5, color="#dc2626", anchor="start", bold=True))
    p.append(text(px + 15, 218, "   На 10 шарах опір може", size=10.5, color=MUTED, anchor="start"))
    p.append(text(px + 15, 234, "   вирости у 20–50 разів.", size=10.5, color=MUTED, anchor="start"))

    p.append(text(px + 15, 262, "3. Пастка товстого дроту:", size=11.5, color="#854d0e", anchor="start", bold=True))
    p.append(text(px + 15, 278, "   Збільшення товщини h", size=10.5, color=MUTED, anchor="start"))
    p.append(text(px + 15, 294, "   понад δ ЗБІЛЬШУЄ втрати,", size=10.5, color="#854d0e", anchor="start", bold=True))
    p.append(text(px + 15, 310, "   а не зменшує їх!", size=10.5, color="#854d0e", anchor="start", bold=True))

    render(os.path.join(IMG, "dowell-curves.svg"), W, H, *p)


# ── Фігура 4: Літцендрат та фольгова обмотка ──────────────────────────────────
def fig_litz_foil():
    W, H = 840, 440
    p = []
    p.append(text(W / 2, 26, "Конструктивні рішення: літцендрат та фольга", size=17, bold=True))
    p.append(text(W / 2, 46, "Способи пригнічення високочастотних втрат у силових моточних виробах",
                  size=12, color=MUTED, italic=True))

    # ── ЛІВОРУЧ: Літцендрат (Litz Wire) ───────────────────────────────────────
    lx = 210
    p.append(rect(20, 65, 380, 355, fill="#f8fafc", stroke="#cbd5e1", sw=1.2))
    p.append(text(lx, 88, "Багатожильний літцендрат (Litz Wire)", size=13.5, bold=True, color=INK))

    # Схема джгута літцендрату у розрізі
    cx, cy = lx, 185
    r_bundle = 70
    p.append(circle(cx, cy, r_bundle, fill="#f1f5f9", stroke="#64748b", sw=2.0))
    p.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="3,3"/>' % (cx, cy, r_bundle + 5))
    p.append(text(cx, cy - r_bundle - 12, "Загальна шовкова/капронова ізоляція", size=10, color=MUTED))

    # Тонкі ізольовані жили d < 2*delta
    angles = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]
    # Центральні жили
    p.append(circle(cx, cy, 11, fill="#fee2e2", stroke=POS, sw=1.2))
    p.append(circle(cx, cy, 9, fill="#fca5a5", stroke="none"))
    # Внутрішнє кільце
    for a in angles[::2]:
        rad = math.radians(a)
        jx = cx + 26 * math.cos(rad)
        jy = cy + 26 * math.sin(rad)
        p.append(circle(jx, jy, 10, fill="#fee2e2", stroke=POS, sw=1.2))
        p.append(circle(jx, jy, 8, fill="#fca5a5", stroke="none"))
    # Зовнішнє кільце
    for a in angles:
        rad = math.radians(a + 15)
        jx = cx + 50 * math.cos(rad)
        jy = cy + 50 * math.sin(rad)
        p.append(circle(jx, jy, 10, fill="#fee2e2", stroke=POS, sw=1.2))
        p.append(circle(jx, jy, 8, fill="#fca5a5", stroke="none"))

    p.append(arrow(cx + 60, cy + 35, cx + 85, cy + 55, color=POS, sw=1.5))
    p.append(text(cx + 90, cy + 60, "Окремі емальовані жили (d < 2δ)", size=10.5, color=POS, anchor="start", bold=True))

    p.append(text(lx, 290, "Кожна жила транспонована (сплетена так,", size=11, color=INK, bold=True))
    p.append(text(lx, 308, "що займає всі позиції від центру до краю)", size=11, color=INK))
    p.append(text(lx, 332, "ЕРС самоіндукції вирівнюється між жилами", size=10.5, color=MUTED))
    p.append(text(lx, 350, "Циркуляційні струми усунуто, R_ac ≈ R_dc", size=11, color=FIELD, bold=True))
    p.append(text(lx, 372, "Застосування: СМПС від 50 кГц до 1 МГц", size=10.5, color=MUTED))

    # ── ПРАВОРУЧ: Фольгова обмотка (Foil Winding) ──────────────────────────────
    rx = 630
    p.append(rect(440, 65, 380, 355, fill="#f8fafc", stroke="#cbd5e1", sw=1.2))
    p.append(text(rx, 88, "Мідна фольга / стрічка (Foil Winding)", size=13.5, bold=True, color=INK))

    # Каркас котушки та намотана фольга
    fy = 130
    # Каркас (осердя)
    p.append(rect(rx - 130, fy, 40, 120, fill="#64748b", stroke="#334155", sw=1.5, rx=3))
    p.append(text(rx - 110, fy + 65, "Осердя", size=11, color="#ffffff", bold=True))

    # Шари фольги на повну ширину вікна b_w
    for i in range(3):
        fx = rx - 70 + i * 45
        # Мідна фольга
        p.append(rect(fx, fy + 5, 24, 110, fill="#fed7aa", stroke="#ea580c", sw=1.5, rx=2))
        p.append(text(fx + 12, fy + 60, "Виток %d" % (i + 1), size=10, color="#9a3412", bold=True))
        # Міжвиткова ізоляційна стрічка
        p.append(rect(fx + 26, fy, 12, 120, fill="#fef08a", stroke="#ca8a04", sw=1.0, rx=1))

    # Розміри: ширина вікна b_w та товщина h
    p.append(line(rx - 70, fy - 10, rx + 80, fy - 10, color=LINE, sw=1.2))
    p.append(arrow(rx - 70, fy - 10, rx - 75, fy - 10, color=LINE, sw=1.2))
    p.append(arrow(rx + 80, fy - 10, rx + 85, fy - 10, color=LINE, sw=1.2))
    p.append(text(rx + 5, fy - 16, "Ширина вікна b_w (1 виток на шар)", size=10.5, color=INK, bold=True))

    p.append(line(rx + 25, fy + 125, rx + 49, fy + 125, color="#ea580c", sw=1.5))
    p.append(text(rx + 37, fy + 138, "Товщина h ≈ δ", size=10.5, color="#ea580c", bold=True))

    p.append(text(rx, 290, "1 виток = 1 шар на всю ширину каркаса", size=11, color=INK, bold=True))
    p.append(text(rx, 308, "Немає поперечних зазорів (пористість η = 1)", size=11, color=INK))
    p.append(text(rx, 332, "Поле розсіювання строго паралельне стрічці", size=10.5, color=MUTED))
    p.append(text(rx, 350, "Ідеально для вторинних низьковольтних обмоток", size=11, color=FIELD, bold=True))
    p.append(text(rx, 372, "Великі струми (десятки-сотні ампер)", size=10.5, color=MUTED))

    render(os.path.join(IMG, "litz-foil.svg"), W, H, *p)


if __name__ == "__main__":
    fig_skin_proximity()
    fig_mmf_interleaving()
    fig_dowell_curves()
    fig_litz_foil()
    print("All figures generated successfully.")
