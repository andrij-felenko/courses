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
# Фігура 1 — Геометрія прецесії вектора намагніченості у полю H_eff та h(t)
# ════════════════════════════════════════════════════════════════════════════
def fig_fmr_precession_geometry():
    W, H = 820, 420
    f = []

    # Розділювальна пунктирна лінія
    f.append(line(410, 25, 410, 395, color=MUTED, sw=1.5, dash="4 4"))

    # ── Ліва панель: Рівноважний стан та ефективне поле ──
    f.append(text(205, 38, "Рівноважна орієнтація намагніченості", size=14, bold=True, color=INK))
    f.append(text(205, 58, "Зовнішнє поле H₀ та розмагнічування H_d", size=12, color=MUTED))

    # Зразок (феромагнітний еліпсоїд / плівка)
    f.append(ellipse_custom(205, 250, 120, 45, fill="#ebf5fb", stroke="#2980b9", sw=2.0))
    f.append(text(205, 275, "Феромагнітний зразок (M_s)", size=11, bold=True, color="#1b4f72"))

    # Зовнішнє поле H0 (вертикально вгору)
    for x in [120, 205, 290]:
        f.append(line(x, 340, x, 110, color="#27ae60", sw=1.8, dash="5 3"))
        f.append(polygon([(x-4, 115), (x, 105), (x+4, 115)], fill="#27ae60"))
    f.append(text(300, 115, "H₀ (статичне поле)", size=11.5, bold=True, color="#27ae60"))

    # Вектор размагнічувального поля Hd (вниз, протидія)
    f.append(line(160, 220, 160, 280, color="#e74c3c", sw=2.0))
    f.append(polygon([(156, 275), (160, 285), (164, 275)], fill="#e74c3c"))
    f.append(text(85, 255, "H_d = -N · M", size=11, bold=True, color="#c0392b"))

    # Вектор спонтанної намагніченості M (вгору)
    f.append(line(205, 250, 205, 130, color="#8e44ad", sw=3.0))
    f.append(polygon([(200, 135), (205, 120), (210, 135)], fill="#8e44ad"))
    f.append(text(215, 145, "M (намагніченість)", size=12, bold=True, color="#8e44ad"))

    # Формула ефективного поля
    f.append(text(205, 375, "H_eff = H₀ + H_d + H_k", size=13, bold=True, color=INK))

    # ── Права панель: Конус прецесії та НВЧ-збудження h(t) ──
    f.append(text(615, 38, "НВЧ-резонансна прецесія та згасання", size=14, bold=True, color=INK))
    f.append(text(615, 58, "Взаємодія з змінним полем h(t) = h₀ cos(ω t)", size=12, color=MUTED))

    pcx, pcy = 615, 260
    top_y = 130

    # Ос прецесії (z / H_eff)
    f.append(line(pcx, pcy, pcx, 95, color=DARK, sw=1.2, dash="4 4"))
    f.append(text(pcx + 8, 105, "z (H_eff)", size=11, bold=True, color=DARK))

    # Еліпс конуса прецесії зверху
    f.append(ellipse_custom(pcx, top_y, 75, 28, fill="none", stroke="#7f8c8d", sw=1.5, dash="3 3"))

    # Вектор намагніченості M під кутом θ
    mx = pcx + 75 * math.cos(math.radians(35))
    my = top_y - 28 * math.sin(math.radians(35))
    f.append(line(pcx, pcy, mx, my, color="#8e44ad", sw=3.0))
    f.append(polygon([(mx-5, my+8), (mx+3, my-6), (mx-8, my-4)], fill="#8e44ad"))
    f.append(text(mx + 10, my - 5, "M(t)", size=12, bold=True, color="#8e44ad"))

    # Дуга прецесії з стрілкою обертання
    arc_pts = []
    for deg in range(35, 160, 5):
        rad = math.radians(deg)
        ax = pcx + 75 * math.cos(rad)
        ay = top_y - 28 * math.sin(rad)
        arc_pts.append((ax, ay))
    arc_path = "M " + " L ".join("%.1f %.1f" % p for p in arc_pts)
    f.append(svg_path(arc_path, stroke="#d35400", sw=2.0, fill="none"))
    f.append(polygon([(arc_pts[-1][0]-6, arc_pts[-1][1]-3), (arc_pts[-1][0]+4, arc_pts[-1][1]+4), (arc_pts[-1][0]-2, arc_pts[-1][1]+8)], fill="#d35400"))
    f.append(text(pcx - 85, top_y - 15, "Прецесія ω₀", size=11, bold=True, color="#d35400"))

    # Кут прецесії θ
    f.append(line(pcx, pcy - 40, pcx + 18, pcy - 40, color=MUTED, sw=1.0))
    f.append(text(pcx + 12, pcy - 50, "θ", size=12, bold=True, color=DARK))

    # Змінне магнітне НВЧ-поле h(t) у площині xy
    f.append(line(pcx - 90, pcy, pcx + 90, pcy, color="#e67e22", sw=2.2))
    f.append(polygon([(pcx + 85, pcy - 4), (pcx + 95, pcy), (pcx + 85, pcy + 4)], fill="#e67e22"))
    f.append(text(pcx + 35, pcy + 22, "h(t) [НВЧ-поле]", size=11, bold=True, color="#e67e22"))

    # Вектори моментів сил
    f.append(text(615, 375, "dM/dt = -γ (M × H_eff) + (α/M_s) (M × dM/dt)", size=12, bold=True, color="#8e44ad"))

    render(os.path.join(OUT, "fmr-precession-geometry.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Залежність частоти Кіттеля від поля H0 для різних геометрій
# ════════════════════════════════════════════════════════════════════════════
def fig_kittel_modes_geometry():
    W, H = 800, 420
    f = []

    ox, oy = 100, 340
    # Осі координатні
    f.append(line(ox, oy, 740, oy, color=DARK, sw=1.5))
    f.append(line(ox, oy, ox, 45, color=DARK, sw=1.5))
    f.append(polygon([(740, oy-4), (750, oy), (740, oy+4)], fill=DARK))
    f.append(polygon([(ox-4, 45), (ox, 35), (ox+4, 45)], fill=DARK))

    f.append(text(725, oy + 25, "Зовнішнє магнітне поле H₀ (кЕ / Тл)", size=11.5, bold=True, color=DARK))
    f.append(text(20, 38, "Частота FMR f₀ (ГГц)", size=11.5, bold=True, color=DARK))

    # Позначка M_s на осі поля H0
    ms_x = ox + 180
    f.append(line(ms_x, oy - 4, ms_x, oy + 4, color=DARK, sw=1.5))
    f.append(line(ms_x, oy, ms_x, 60, color=MUTED, sw=1.0, dash="3 3"))
    f.append(text(ms_x - 12, oy + 22, "M_s", size=11, bold=True, color="#c0392b"))

    # 1. Тонка плівка (поле в площині плівки): f = γ √(H0 (H0 + Ms))
    pts_inplane = []
    for x in range(ox, 720, 3):
        h0 = (x - ox) / 180.0
        val = math.sqrt(h0 * (h0 + 1.0))
        y = oy - int(val * 110)
        pts_inplane.append((x, y))
    path_ip = "M " + " L ".join("%d %d" % p for p in pts_inplane)
    f.append(svg_path(path_ip, stroke="#c0392b", sw=2.5, fill="none"))

    # 2. Сфера: f = γ H0
    pts_sphere = []
    for x in range(ox, 720, 3):
        h0 = (x - ox) / 180.0
        val = h0
        y = oy - int(val * 110)
        pts_sphere.append((x, y))
    path_sp = "M " + " L ".join("%d %d" % p for p in pts_sphere)
    f.append(svg_path(path_sp, stroke="#2980b9", sw=2.5, fill="none"))

    # 3. Тонка плівка (поле перпендикулярно до площини): f = γ (H0 - Ms) при H0 > Ms
    pts_outplane = []
    for x in range(ms_x, 720, 3):
        h0 = (x - ox) / 180.0
        val = h0 - 1.0
        y = oy - int(val * 110)
        pts_outplane.append((x, y))
    path_op = "M " + " L ".join("%d %d" % p for p in pts_outplane)
    f.append(svg_path(path_op, stroke="#27ae60", sw=2.5, fill="none"))

    # Легенда
    lx, ly = 130, 75
    f.append(rect(lx, ly, 380, 115, fill="#f9f9f9", stroke="#bdc3c7", sw=1.0))

    f.append(line(lx + 15, ly + 25, lx + 45, ly + 25, color="#c0392b", sw=2.5))
    f.append(text(lx + 55, ly + 29, "Плівка у площині: f = γ √[ H₀ (H₀ + M_s) ]", size=11, bold=True, color="#c0392b"))

    f.append(line(lx + 15, ly + 58, lx + 45, ly + 58, color="#2980b9", sw=2.5))
    f.append(text(lx + 55, ly + 62, "Сфера (ізотропна): f = γ · H₀", size=11, bold=True, color="#2980b9"))

    f.append(line(lx + 15, ly + 91, lx + 45, ly + 91, color="#27ae60", sw=2.5))
    f.append(text(lx + 55, ly + 95, "Плівка перпендикулярно: f = γ · (H₀ - M_s)", size=11, bold=True, color="#27ae60"))

    # Підпис порогу насичення перпендикулярного поля
    f.append(text(ms_x - 70, oy - 20, "Поріг насичення H₀ > M_s", size=10, bold=True, color="#27ae60"))

    render(os.path.join(OUT, "kittel-modes-geometry.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Спектр поглинання FMR та ширина лінії залежно від частоти
# ════════════════════════════════════════════════════════════════════════════
def fig_fmr_linewidth_damping():
    W, H = 840, 420
    f = []

    f.append(line(420, 25, 420, 395, color=MUTED, sw=1.5, dash="4 4"))

    # ── Ліва панель: Лінія резонансного поглинання та її похідна ──
    f.append(text(210, 38, "Форма лінії поглинання FMR P_abs(H)", size=14, bold=True, color=INK))
    f.append(text(210, 58, "Поглинання χ''(H) та похідна dP/dH", size=12, color=MUTED))

    lox, loy = 60, 340
    f.append(line(lox, loy, 390, loy, color=DARK, sw=1.5))
    f.append(line(lox, loy, lox, 70, color=DARK, sw=1.5))
    f.append(polygon([(390, loy-4), (400, loy), (390, loy+4)], fill=DARK))
    f.append(polygon([(lox-4, 70), (lox, 60), (lox+4, 70)], fill=DARK))
    f.append(text(340, loy + 25, "Поле H₀", size=11, bold=True, color=DARK))
    f.append(text(15, 62, "Сигнал", size=11, bold=True, color=DARK))

    # Резонансне поле Hr
    hr_x = lox + 160
    f.append(line(hr_x, loy, hr_x, 80, color=MUTED, sw=1.0, dash="3 3"))
    f.append(text(hr_x - 10, loy + 20, "H_r", size=11, bold=True, color=DARK))

    # Крива поглинання χ'' (Лоренціан)
    pts_abs = []
    for x in range(lox, 380, 2):
        dh = (x - hr_x) / 30.0
        val = 1.0 / (1.0 + dh**2)
        y = loy - int(val * 180)
        pts_abs.append((x, y))
    path_abs = "M " + " L ".join("%d %d" % p for p in pts_abs)
    f.append(svg_path(path_abs, stroke="#8e44ad", sw=2.2, fill="none"))
    f.append(text(hr_x + 35, loy - 165, "Поглинання P_abs(H)", size=10.5, bold=True, color="#8e44ad"))

    # Ширина лінії ΔH на напіввисоті
    half_y = loy - 90
    f.append(line(hr_x - 30, half_y, hr_x + 30, half_y, color="#c0392b", sw=1.8))
    f.append(line(hr_x - 30, half_y - 5, hr_x - 30, half_y + 5, color="#c0392b", sw=1.8))
    f.append(line(hr_x + 30, half_y - 5, hr_x + 30, half_y + 5, color="#c0392b", sw=1.8))
    f.append(text(hr_x - 22, half_y - 8, "Ширина ΔH", size=10.5, bold=True, color="#c0392b"))

    # Похідна лінії dP/dH (стандартний результат модуляційного FMR)
    pts_der = []
    for x in range(lox, 380, 2):
        dh = (x - hr_x) / 30.0
        val = -2.0 * dh / ((1.0 + dh**2)**2)
        y = loy - 90 - int(val * 80)
        pts_der.append((x, y))
    path_der = "M " + " L ".join("%d %d" % p for p in pts_der)
    f.append(svg_path(path_der, stroke="#27ae60", sw=2.0, fill="none", dash="4 2"))
    f.append(text(hr_x + 65, loy - 40, "Похідна dP/dH", size=10.5, bold=True, color="#27ae60"))

    # ── Права панель: Ширина лінії ΔH(f) та параметр Гільберта α ──
    f.append(text(630, 38, "Залежність ширини лінії від частоти", size=14, bold=True, color=INK))
    f.append(text(630, 58, "Визначення параметра згасання Гільберта α", size=12, color=MUTED))

    rox, roy = 480, 340
    f.append(line(rox, roy, 810, roy, color=DARK, sw=1.5))
    f.append(line(rox, roy, rox, 70, color=DARK, sw=1.5))
    f.append(polygon([(810, roy-4), (820, roy), (810, roy+4)], fill=DARK))
    f.append(polygon([(rox-4, 70), (rox, 60), (rox+4, 70)], fill=DARK))
    f.append(text(745, roy + 25, "Частота f (ГГц)", size=11, bold=True, color=DARK))
    f.append(text(435, 62, "Ширина ΔH", size=11, bold=True, color=DARK))

    # Пряма лінія ΔH(f) = ΔH0 + (2 α / γ) · 2π f
    f.append(line(rox, roy - 40, rox + 310, roy - 240, color="#c0392b", sw=2.5))

    # Неоднорідне уширення ΔH0 (перетин із віссю y)
    f.append(circle(rox, roy - 40, 4, fill="#c0392b"))
    f.append(line(rox, roy - 40, rox - 15, roy - 40, color="#c0392b", sw=1.0, dash="2 2"))
    f.append(text(rox + 10, roy - 35, "ΔH₀ (неоднорідне уширення)", size=10.5, bold=True, color="#c0392b"))

    # Спектральні точки (експериментальні виміри VNA-FMR)
    exp_pts = [(50, 72), (100, 105), (150, 138), (200, 170), (250, 202), (300, 233)]
    for dx, dy in exp_pts:
        f.append(circle(rox + dx, roy - dy, 4, fill="#2980b9", stroke="#1b4f72", sw=1.2))

    # Нахил прямої -> Параметр Гільберта α
    f.append(text(rox + 140, roy - 190, "Кутовий нахил ∝ α", size=11.5, bold=True, color="#c0392b"))
    f.append(text(630, 375, "ΔH = ΔH₀ + (2 α / γ) · 2π f", size=12, bold=True, color=INK))

    render(os.path.join(OUT, "fmr-linewidth-damping.svg"), W, H, *f)


if __name__ == '__main__':
    fig_fmr_precession_geometry()
    fig_kittel_modes_geometry()
    fig_fmr_linewidth_damping()
    print("FMR figures generated successfully.")
