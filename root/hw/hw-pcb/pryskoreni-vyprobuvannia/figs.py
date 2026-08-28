# -*- coding: utf-8 -*-
"""Фігури до теми «Прискорені випробування: термоцикл, тряска, вологість».
Запуск:  python figs.py   → створює SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

def ellipse(cx, cy, rx, ry, fill=FILL, stroke=LINE, sw=1.5):
    return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" '
            'stroke-width="%.1f"/>' % (cx, cy, rx, ry, fill, stroke, sw))

# ── 1. Границі HALT та вікно скринінгу HASS ──────────────────────────────────
def fig_halt_hass_margins():
    W, H = 860, 480
    f = []
    
    f.append(text(W / 2, 26, "Межі навантаження HALT та профіль виробничого скринінгу HASS", size=16, bold=True))
    f.append(text(W / 2, 46, "знаходження фізичних меж конструкції та вибір безпечного вікна відсіву дефектів",
                  size=11, color=MUTED, italic=True))

    ox, oy = 210, 410
    ax, ay = 800, 80
    
    # Горизонтальні рівні напружень
    y_udl = 110  # Upper Destruct Limit
    y_uol = 165  # Upper Operating Limit
    y_max_op = 220 # Max Spec Operating
    y_nom = 260   # Nominal
    y_min_op = 300 # Min Spec Operating
    y_lol = 350  # Lower Operating Limit
    y_ldl = 400  # Lower Destruct Limit
    
    # Фонове зонування
    f.append(rect(ox, ay, ax - ox, y_udl - ay, fill="#fdf2f0", stroke="none", rx=0))
    f.append(rect(ox, y_udl, ax - ox, y_uol - y_udl, fill="#fef9f0", stroke="none", rx=0))
    f.append(rect(ox, y_uol, ax - ox, y_max_op - y_uol, fill="#f4faf6", stroke="none", rx=0))
    f.append(rect(ox, y_max_op, ax - ox, y_min_op - y_max_op, fill="#edf6fd", stroke="none", rx=0))
    f.append(rect(ox, y_min_op, ax - ox, y_lol - y_min_op, fill="#f4faf6", stroke="none", rx=0))
    f.append(rect(ox, y_lol, ax - ox, y_ldl - y_lol, fill="#fef9f0", stroke="none", rx=0))
    f.append(rect(ox, y_ldl, ax - ox, oy - y_ldl, fill="#fdf2f0", stroke="none", rx=0))

    # Горизонтальні лінії рівнів
    f.append(line(ox, y_udl, ax, y_udl, color=POS, sw=1.8, dash="6,4"))
    f.append(line(ox, y_uol, ax, y_uol, color="#d35400", sw=1.5, dash="5,3"))
    f.append(line(ox, y_max_op, ax, y_max_op, color=NEG, sw=1.2, dash="3,3"))
    f.append(line(ox, y_nom, ax, y_nom, color=MUTED, sw=1.0, dash="2,2"))
    f.append(line(ox, y_min_op, ax, y_min_op, color=NEG, sw=1.2, dash="3,3"))
    f.append(line(ox, y_lol, ax, y_lol, color="#d35400", sw=1.5, dash="5,3"))
    f.append(line(ox, y_ldl, ax, y_ldl, color=POS, sw=1.8, dash="6,4"))

    # Підписи рівнів зліва
    f.append(text(ox - 10, y_udl + 4, "UDL (Верхня деструктивна межа)", size=10, color=POS, anchor="end", bold=True))
    f.append(text(ox - 10, y_uol + 4, "UOL (Верхня межа роботи)", size=10, color="#d35400", anchor="end", bold=True))
    f.append(text(ox - 10, y_max_op + 4, "T_max (Специфікація виробу)", size=10, color=NEG, anchor="end"))
    f.append(text(ox - 10, y_nom + 4, "T_nom (Номінальні умови)", size=10, color=MUTED, anchor="end"))
    f.append(text(ox - 10, y_min_op + 4, "T_min (Специфікація виробу)", size=10, color=NEG, anchor="end"))
    f.append(text(ox - 10, y_lol + 4, "LOL (Нижня межа роботи)", size=10, color="#d35400", anchor="end", bold=True))
    f.append(text(ox - 10, y_ldl + 4, "LDL (Нижня деструктивна межа)", size=10, color=POS, anchor="end", bold=True))

    # Ступінчастий профіль HALT
    halt_pts = [
        (230, y_nom), (255, y_nom),
        (255, y_max_op - 15), (285, y_max_op - 15),
        (285, y_uol - 10), (315, y_uol - 10),
        (315, y_uol + 10), (345, y_uol + 10),
        (345, y_udl - 8), (375, y_udl - 8),
        (375, y_udl + 15), (405, y_udl + 15),
        (405, y_nom), (425, y_nom),
        (425, y_lol - 15), (455, y_lol - 15),
        (455, y_ldl + 15), (485, y_ldl + 15),
        (485, y_nom)
    ]
    for i in range(len(halt_pts) - 1):
        f.append(line(halt_pts[i][0], halt_pts[i][1], halt_pts[i+1][0], halt_pts[i+1][1], color=POS, sw=2.2))

    f.append(text(360, 95, "HALT: ступінчастий стрес до руйнування", size=11, color=POS, bold=True))
    
    # Стрілки маржі міцності (Design Margin)
    f.append(arrow(460, y_max_op, 460, y_uol, color="#d35400", sw=1.5))
    f.append(arrow(460, y_uol, 460, y_max_op, color="#d35400", sw=1.5))
    f.append(text(468, (y_max_op + y_uol) / 2 + 3, "Експлуатаційний запас", size=9, color="#d35400", anchor="start", bold=True))

    f.append(arrow(390, y_uol, 390, y_udl, color=POS, sw=1.5))
    f.append(arrow(390, y_udl, 390, y_uol, color=POS, sw=1.5))
    f.append(text(398, (y_uol + y_udl) / 2 + 3, "Деструктивний запас", size=9, color=POS, anchor="start", bold=True))

    # Правий блок: HASS (виробничий скринінг)
    f.append(line(510, ay, 510, oy, color="#cccccc", sw=1.2, dash="4,4"))

    # HASS профіль: періодичний жорсткий, але безпечний цикл
    hass_pts = [
        (530, y_nom), (550, y_nom),
        (565, y_uol + 12), (595, y_uol + 12),
        (615, y_lol - 12), (645, y_lol - 12),
        (665, y_uol + 12), (695, y_uol + 12),
        (715, y_lol - 12), (745, y_lol - 12),
        (765, y_nom), (785, y_nom)
    ]
    for i in range(len(hass_pts) - 1):
        f.append(line(hass_pts[i][0], hass_pts[i][1], hass_pts[i+1][0], hass_pts[i+1][1], color=FIELD, sw=2.2))

    f.append(text(655, 95, "HASS: 100% виробничий скринінг", size=11, color=FIELD, bold=True))
    
    # Рамка-пояснення вікна HASS
    hass_box_w = 170
    hass_box_h = 42
    f.append(rect(570, 239, hass_box_w, hass_box_h, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(655, 255, "Безпечне вікно HASS:", size=10, color=FIELD, bold=True))
    f.append(text(655, 270, "виявляє приховані дефекти без зносу", size=9, color=INK))

    # Загальні осі
    f.append(line(ox, oy, ox, ay - 10, color=INK, sw=1.8))
    f.append(line(ox, oy, ax + 10, oy, color=INK, sw=1.8))
    f.append(text(ox, ay - 16, "Рівень навантаження (T, Вібрація, V)", size=11, bold=True, anchor="start"))
    f.append(text((ox + ax) / 2, oy + 32, "Час випробування / Етапи навантаження", size=11, bold=True))

    render(os.path.join(IMG, "halt-hass-margins.svg"), W, H, *f)


# ── 2. Механізм термічної втоми через різницю КТР ────────────────────────────
def fig_thermal_fatigue_cte():
    W, H = 820, 460
    f = []
    
    f.append(text(W / 2, 26, "Термомеханічна втома паяного з'єднання (CTE Mismatch)", size=16, bold=True))
    f.append(text(W / 2, 46, "різниця розширення кремнію та текстоліту створює циклічний зсув і тріщини в припої",
                  size=11, color=MUTED, italic=True))

    # 1. Холодний або нейтральний стан (T0)
    x1 = 210
    y_chip1 = 110
    chip_w = 260
    chip_h = 35
    pcb_w = 320
    pcb_h = 30
    
    f.append(text(x1, 85, "1. Нейтральний стан монтажу (25 °C)", size=12, bold=True, color=INK))
    
    f.append(rect(x1 - chip_w/2, y_chip1, chip_w, chip_h, fill="#2c3e50", stroke=LINE, sw=1.5, rx=3))
    f.append(text(x1, y_chip1 + 22, "Кремнієвий кристал / BGA (CTE ≈ 3–6 ppm/°C)", size=10, color="#ffffff", bold=True))
    
    ball_y = y_chip1 + chip_h + 12
    ball_r = 10
    ball_xs1 = [x1 - 100, x1 - 50, x1, x1 + 50, x1 + 100]
    for bx in ball_xs1:
        f.append(circle(bx, ball_y, ball_r, fill="#95a5a6", stroke="#7f8c8d", sw=1.5))
        f.append(rect(bx - 12, y_chip1 + chip_h, 24, 3, fill="#d35400", stroke="none", rx=0))
        f.append(rect(bx - 12, ball_y + ball_r, 24, 3, fill="#d35400", stroke="none", rx=0))

    y_pcb1 = ball_y + ball_r + 3
    f.append(rect(x1 - pcb_w/2, y_pcb1, pcb_w, pcb_h, fill="#27ae60", stroke=LINE, sw=1.5, rx=3))
    f.append(text(x1, y_pcb1 + 20, "Друкована плата FR4 (CTE ≈ 14–17 ppm/°C)", size=10, color="#ffffff", bold=True))
    
    f.append(text(x1, y_pcb1 + pcb_h + 20, "Симетрія, зсувні напруження мінімальні", size=10, color=MUTED, italic=True))

    # 2. Гарячий стан (T = 125 °C) - деформація
    x2 = 610
    y_chip2 = 110
    
    f.append(text(x2, 85, "2. Нагрів під час термоциклу (125 °C)", size=12, bold=True, color=POS))
    
    chip_w_hot = 266
    f.append(rect(x2 - chip_w_hot/2, y_chip2, chip_w_hot, chip_h, fill="#2c3e50", stroke=LINE, sw=1.5, rx=3))
    f.append(text(x2, y_chip2 + 22, "Розширення чіпа: мале", size=10, color="#ffffff", bold=True))
    
    pcb_w_hot = 338
    y_pcb2 = y_pcb1
    f.append(rect(x2 - pcb_w_hot/2, y_pcb2, pcb_w_hot, pcb_h, fill="#27ae60", stroke=LINE, sw=1.5, rx=3))
    f.append(text(x2, y_pcb2 + 20, "Розширення FR4: велике (ΔL_pcb >> ΔL_chip)", size=10, color="#ffffff", bold=True))

    offsets = [-16, -8, 0, 8, 16]
    for i, bx in enumerate(ball_xs1):
        curr_bx_chip = (x2 - chip_w_hot/2) + (bx - (x1 - chip_w/2)) * (chip_w_hot / chip_w)
        curr_bx_pcb = (x2 - pcb_w_hot/2) + (bx - (x1 - pcb_w/2)) * (pcb_w_hot / pcb_w)
        cx_mid = (curr_bx_chip + curr_bx_pcb) / 2
        
        f.append(rect(curr_bx_chip - 12, y_chip2 + chip_h, 24, 3, fill="#d35400", stroke="none", rx=0))
        f.append(rect(curr_bx_pcb - 12, ball_y + ball_r, 24, 3, fill="#d35400", stroke="none", rx=0))
        
        fill_col = POS if abs(offsets[i]) > 10 else "#95a5a6"
        f.append(circle(cx_mid, ball_y, ball_r, fill=fill_col, stroke="#c0392b" if abs(offsets[i]) > 10 else "#7f8c8d", sw=1.5))
        
        if offsets[i] > 10:
            f.append(arrow(curr_bx_chip, y_chip2 + chip_h + 3, curr_bx_pcb, ball_y + ball_r, color=POS, sw=1.8))
        elif offsets[i] < -10:
            f.append(arrow(curr_bx_chip, y_chip2 + chip_h + 3, curr_bx_pcb, ball_y + ball_r, color=POS, sw=1.8))

    f.append(text(x2, y_pcb2 + pcb_h + 20, "Максимальний зсув γ на крайніх кульках (DNP)", size=10, color=POS, bold=True))

    # Нижній детальний розріз: Зародження та ріст тріщини
    f.append(line(50, 265, W - 50, 265, color="#e0e0e0", sw=1.2))
    f.append(text(W / 2, 288, "Мікроструктурний розріз крайньої паяної кульки під дією втоми Коффіна — Менсона", size=12, bold=True))

    bx_zoom = 150
    by_zoom = 320
    bw_zoom = 520
    bh_zoom = 120
    f.append(rect(bx_zoom, by_zoom, bw_zoom, bh_zoom, fill="#fdfefe", stroke=LINE, sw=1.5, rx=4))

    f.append(rect(bx_zoom + 20, by_zoom + 10, bw_zoom - 40, 18, fill="#d35400", stroke=LINE, sw=1.2, rx=2))
    f.append(text(bx_zoom + 120, by_zoom + 23, "Мідна площадка компонента (Cu Pad)", size=10, color="#ffffff", bold=True))
    
    f.append(rect(bx_zoom + 20, by_zoom + 28, bw_zoom - 40, 8, fill="#8e44ad", stroke="none", rx=0))
    f.append(text(bx_zoom + bw_zoom - 110, by_zoom + 35, "Крихкий шар IMC (Cu₆Sn₅)", size=9, color="#ffffff", bold=True))

    f.append(rect(bx_zoom + 20, by_zoom + 36, bw_zoom - 40, 48, fill="#ecf0f1", stroke="none", rx=0))
    f.append(text(bx_zoom + 140, by_zoom + 62, "Масив припою SAC305 (Sn-Ag-Cu зерна)", size=10, color=MUTED, bold=True))

    crack_pts = [(bx_zoom + 20, by_zoom + 36), (bx_zoom + 80, by_zoom + 37), (bx_zoom + 160, by_zoom + 35),
                 (bx_zoom + 240, by_zoom + 38), (bx_zoom + 320, by_zoom + 36)]
    for j in range(len(crack_pts) - 1):
        f.append(line(crack_pts[j][0], crack_pts[j][1], crack_pts[j+1][0], crack_pts[j+1][1], color=POS, sw=2.5))
    
    f.append(arrow(bx_zoom + 180, by_zoom + 70, bx_zoom + 180, by_zoom + 42, color=POS, sw=1.5))
    f.append(text(bx_zoom + 180, by_zoom + 82, "Втомна тріщина розповсюджується вздовж межі IMC", size=10, color=POS, bold=True))

    f.append(rect(bx_zoom + 20, by_zoom + 84, bw_zoom - 40, 8, fill="#8e44ad", stroke="none", rx=0))
    f.append(rect(bx_zoom + 20, by_zoom + 92, bw_zoom - 40, 18, fill="#d35400", stroke=LINE, sw=1.2, rx=2))
    f.append(text(bx_zoom + 120, by_zoom + 105, "Мідна площадка плати FR4 (PCB Pad)", size=10, color="#ffffff", bold=True))

    render(os.path.join(IMG, "thermal-fatigue-cte.svg"), W, H, *f)


# ── 3. Вібраційне навантаження та резонанс плати ─────────────────────────────
def fig_vibration_psd_resonance():
    W, H = 820, 460
    f = []
    
    f.append(text(W / 2, 26, "Випадкова вібрація (PSD) та резонансний вигин друкованої плати", size=16, bold=True))
    f.append(text(W / 2, 46, "спектральна густина потужності збуджує резонансні моди плати, створюючи циклічні вигини",
                  size=11, color=MUTED, italic=True))

    # Спектральна густина потужності
    ox1, oy1 = 80, 240
    ax1, ay1 = 370, 90
    
    f.append(text((ox1 + ax1) / 2, 78, "Спектр випадкової вібрації (PSD профілю)", size=11, bold=True))

    f.append(line(ox1, oy1, ax1, oy1, color=INK, sw=1.5))
    f.append(line(ox1, oy1, ox1, ay1, color=INK, sw=1.5))
    
    p1 = (ox1 + 30, oy1 - 20)
    p2 = (ox1 + 90, ay1 + 25)
    p3 = (ox1 + 200, ay1 + 25)
    p4 = (ax1 - 20, oy1 - 35)
    
    poly_pts = "%f,%f %f,%f %f,%f %f,%f %f,%f %f,%f" % (
        ox1 + 30, oy1, p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], p4[0], p4[1], ax1 - 20, oy1
    )
    f.append('<polygon points="%s" fill="#eaf2f8" stroke="none"/>' % poly_pts)
    
    f.append(line(p1[0], p1[1], p2[0], p2[1], color=NEG, sw=2.0))
    f.append(line(p2[0], p2[1], p3[0], p3[1], color=NEG, sw=2.0))
    f.append(line(p3[0], p3[1], p4[0], p4[1], color=NEG, sw=2.0))

    f.append(text(p2[0] + 55, ay1 + 15, "Плато PSD (напр. 0.04 g²/Hz)", size=9, color=NEG, bold=True))
    f.append(text((ox1 + ax1) / 2, oy1 - 40, "G_rms = √(∫ PSD df)", size=11, color=INK, bold=True))

    f.append(text(ox1 - 10, ay1 + 30, "PSD (g²/Hz)", size=10, color=MUTED, anchor="end"))
    f.append(text(ax1, oy1 + 18, "Частота f (Гц)", size=10, color=MUTED, anchor="end"))
    f.append(text(p1[0], oy1 + 14, "20", size=9, color=MUTED))
    f.append(text(p2[0], oy1 + 14, "100", size=9, color=MUTED))
    f.append(text(p3[0], oy1 + 14, "1000", size=9, color=MUTED))
    f.append(text(p4[0], oy1 + 14, "2000", size=9, color=MUTED))

    # Передавальна функція відгуку
    ox2, oy2 = 450, 240
    ax2, ay2 = 740, 90
    
    f.append(text((ox2 + ax2) / 2, 78, "Відгук друкованої плати (Резонанс fn)", size=11, bold=True))
    
    f.append(line(ox2, oy2, ax2, oy2, color=INK, sw=1.5))
    f.append(line(ox2, oy2, ox2, ay2, color=INK, sw=1.5))

    fn_x = ox2 + 130
    fn_y = ay2 + 10
    
    res_pts = []
    for xx in range(int(ox2 + 20), int(ax2 - 20), 5):
        dist = abs(xx - fn_x)
        ampl = (oy2 - 15) - (oy2 - fn_y) / (1.0 + (dist / 14.0)**2)
        res_pts.append((xx, ampl))
        
    for j in range(len(res_pts) - 1):
        f.append(line(res_pts[j][0], res_pts[j][1], res_pts[j+1][0], res_pts[j+1][1], color=POS, sw=2.0))

    f.append(line(fn_x, oy2, fn_x, fn_y, color=POS, sw=1.0, dash="3,3"))
    f.append(text(fn_x, oy2 + 14, "fn (резонанс)", size=9, color=POS, bold=True))
    f.append(text(fn_x + 10, fn_y + 15, "Підсилення Q ≈ √fn", size=10, color=POS, anchor="start", bold=True))
    f.append(text(ax2, oy2 + 18, "Частота f (Гц)", size=10, color=MUTED, anchor="end"))
    f.append(text(ox2 - 10, ay2 + 30, "Прискорення g", size=10, color=MUTED, anchor="end"))

    # Динамічний вигин за Стейнбергом
    f.append(line(50, 275, W - 50, 275, color="#e0e0e0", sw=1.2))
    f.append(text(W / 2, 298, "Модель втоми Стейнберга: динамічний прогин плати Z та напруження виводів BGA", size=12, bold=True))

    py_base = 385
    px_left = 140
    px_right = 680
    
    f.append(rect(px_left - 15, py_base - 10, 30, 45, fill="#7f8c8d", stroke=LINE, sw=1.5, rx=2))
    f.append(rect(px_right - 15, py_base - 10, 30, 45, fill="#7f8c8d", stroke=LINE, sw=1.5, rx=2))
    f.append(text(px_left, py_base + 50, "Опора", size=10, color=MUTED))
    f.append(text(px_right, py_base + 50, "Опора", size=10, color=MUTED))

    arc_pts = []
    max_deflect = 35
    for xx in range(int(px_left), int(px_right) + 1, 10):
        frac = (xx - px_left) / (px_right - px_left)
        dy = math.sin(frac * math.pi) * max_deflect
        arc_pts.append((xx, py_base - dy))

    for j in range(len(arc_pts) - 1):
        f.append(line(arc_pts[j][0], arc_pts[j][1], arc_pts[j+1][0], arc_pts[j+1][1], color=FIELD, sw=5.0))

    center_idx = len(arc_pts) // 2
    cx_chip = arc_pts[center_idx][0]
    cy_chip = arc_pts[center_idx][1] - 12
    f.append(rect(cx_chip - 45, cy_chip - 12, 90, 16, fill="#2c3e50", stroke=LINE, sw=1.5, rx=2))
    f.append(text(cx_chip, cy_chip, "BGA / QFP", size=9, color="#ffffff", bold=True))

    f.append(arrow(cx_chip + 110, py_base, cx_chip + 110, py_base - max_deflect, color=POS, sw=1.8))
    f.append(arrow(cx_chip + 110, py_base - max_deflect, cx_chip + 110, py_base, color=POS, sw=1.8))
    f.append(text(cx_chip + 120, py_base - max_deflect / 2 + 4, "Динамічний прогин Z_max ≤ Z_3σ", size=10, color=POS, anchor="start", bold=True))
    f.append(text(cx_chip, py_base + 30, "Максимальна кривизна плати розтягує крайні кутові виводи чіпа", size=10, color=INK, italic=True))

    render(os.path.join(IMG, "vibration-psd-resonance.svg"), W, H, *f)


# ── 4. Механізми деградації у вологому та корозійному середовищі ──────────────
def fig_moisture_failure_modes():
    W, H = 840, 480
    f = []
    
    f.append(text(W / 2, 26, "Кліматична деградація: проникнення вологи, HAST та міграція CAF", size=16, bold=True))
    f.append(text(W / 2, 46, "дифузія пари у пластик та ріст провідних мідних містків вздовж скляних волокон FR4",
                  size=11, color=MUTED, italic=True))

    # Сорбція вологи та HAST
    bx1, by1 = 40, 80
    bw1, bh1 = 350, 370
    f.append(rect(bx1, by1, bw1, bh1, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    f.append(text(bx1 + bw1 / 2, by1 + 24, "1. Сорбція вологи та тиск пари (HAST)", size=12, bold=True, color=POS))

    ic_x = bx1 + 45
    ic_y = by1 + 55
    ic_w = 260
    ic_h = 130
    f.append(rect(ic_x, ic_y, ic_w, ic_h, fill="#34495e", stroke=LINE, sw=1.5, rx=3))
    f.append(text(ic_x + ic_w / 2, ic_y + 18, "Епоксидний компаунд (Mold Compound)", size=9, color="#ffffff"))

    die_w = 120
    die_h = 24
    die_x = ic_x + (ic_w - die_w) / 2
    die_y = ic_y + 40
    f.append(rect(die_x, die_y, die_w, die_h, fill="#7f8c8d", stroke="#95a5a6", sw=1.2, rx=1))
    f.append(text(die_x + die_w / 2, die_y + 16, "Кремній (Silicon Die)", size=9, color="#ffffff", bold=True))

    pad_w = 150
    pad_h = 10
    pad_x = ic_x + (ic_w - pad_w) / 2
    pad_y = die_y + die_h + 2
    f.append(rect(pad_x, pad_y, pad_w, pad_h, fill="#d35400", stroke="none", rx=0))

    for sx in (ic_x + 30, ic_x + 80, ic_x + 180, ic_x + 230):
        f.append(arrow(sx, by1 + 42, sx, ic_y + 8, color=NEG, sw=1.5))
    f.append(text(bx1 + bw1 / 2, by1 + 48, "Волога (H₂O) під тиском 2.3 атм", size=9, color=NEG, bold=True))

    f.append(ellipse(die_x + die_w / 2, pad_y + pad_h + 10, 55, 7, fill="#e74c3c", stroke=POS, sw=1.2))
    f.append(text(bx1 + bw1 / 2, pad_y + pad_h + 13, "Парова кишеня (Delamination)", size=9, color="#ffffff", bold=True))

    f.append(text(bx1 + bw1 / 2, by1 + 225, "При 130 °C та 85% RH волога насичує", size=10, color=INK))
    f.append(text(bx1 + bw1 / 2, by1 + 245, "полімер за 96 год замість 1000 год (85/85).", size=10, color=INK))
    f.append(text(bx1 + bw1 / 2, by1 + 268, "При різкому нагріві пара розриває корпус", size=10, color=POS, bold=True))
    f.append(text(bx1 + bw1 / 2, by1 + 288, "(ефект попкорну) та руйнує розварку виводів.", size=10, color=POS))

    # Електрохімічна міграція (ECM) та волоконні містки CAF
    bx2, by2 = 430, 80
    bw2, bh2 = 370, 370
    f.append(rect(bx2, by2, bw2, bh2, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    f.append(text(bx2 + bw2 / 2, by2 + 24, "2. Анодні містки CAF та міграція міді", size=12, bold=True, color=POS))

    pcb_rx = bx2 + 25
    pcb_ry = by2 + 65
    pcb_rw = 320
    pcb_rh = 150
    
    # Тіло плати FR4
    f.append(rect(pcb_rx, pcb_ry, pcb_rw, pcb_rh, fill="#27ae60", stroke=LINE, sw=1.5, rx=3))

    fiber_y1 = pcb_ry + 50
    fiber_y2 = pcb_ry + 95
    f.append(rect(pcb_rx + 5, fiber_y1 - 6, pcb_rw - 10, 12, fill="#a9dfbf", stroke="none", rx=0))
    f.append(rect(pcb_rx + 5, fiber_y2 - 6, pcb_rw - 10, 12, fill="#a9dfbf", stroke="none", rx=0))
    f.append(text(pcb_rx + 160, pcb_ry + 20, "Скловолокно + епоксидна смола", size=9, color="#ffffff"))

    # Перехідні отвори (анод і катод) - чітко розбиті без виходу за межі плати
    via1_x = pcb_rx + 45
    # Верхній контактний майданчик
    f.append(rect(via1_x - 10, pcb_ry - 10, 20, 10, fill="#d35400", stroke=LINE, sw=1.2, rx=1))
    # Стовбур перехідного отвору всередині плати
    f.append(rect(via1_x - 6, pcb_ry, 12, pcb_rh, fill="#d35400", stroke="none", rx=0))
    # Нижній контактний майданчик
    f.append(rect(via1_x - 10, pcb_ry + pcb_rh, 20, 10, fill="#d35400", stroke=LINE, sw=1.2, rx=1))

    f.append(text(via1_x, pcb_ry - 16, "Анод (+)", size=10, color=POS, bold=True))
    f.append(text(via1_x, pcb_ry + pcb_rh + 24, "Cu → Cu²⁺ + 2e⁻", size=9, color=POS, bold=True))

    via2_x = pcb_rx + 275
    # Верхній контактний майданчик
    f.append(rect(via2_x - 10, pcb_ry - 10, 20, 10, fill="#2980b9", stroke=LINE, sw=1.2, rx=1))
    # Стовбур перехідного отвору всередині плати
    f.append(rect(via2_x - 6, pcb_ry, 12, pcb_rh, fill="#2980b9", stroke="none", rx=0))
    # Нижній контактний майданчик
    f.append(rect(via2_x - 10, pcb_ry + pcb_rh, 20, 10, fill="#2980b9", stroke=LINE, sw=1.2, rx=1))

    f.append(text(via2_x, pcb_ry - 16, "Катод (−)", size=10, color=NEG, bold=True))
    f.append(text(via2_x, pcb_ry + pcb_rh + 24, "Cu²⁺ + 2e⁻ → Cu", size=9, color=NEG, bold=True))

    caf_pts = [(via1_x + 6, fiber_y1), (via1_x + 60, fiber_y1 - 2), (via1_x + 120, fiber_y1 + 1),
               (via1_x + 180, fiber_y1 - 1), (via2_x - 6, fiber_y1)]
    for k in range(len(caf_pts) - 1):
        f.append(line(caf_pts[k][0], caf_pts[k][1], caf_pts[k+1][0], caf_pts[k+1][1], color="#f39c12", sw=3.0))

    f.append(text(bx2 + bw2 / 2, fiber_y1 - 14, "Ріст нитки солей міді (CAF)", size=10, color="#f39c12", bold=True))

    f.append(text(bx2 + bw2 / 2, by2 + 250, "1. Гідроліз послаблює зв'язок смола-скловолокно.", size=9, color=INK))
    f.append(text(bx2 + bw2 / 2, by2 + 270, "2. Градієнт напруги розчиняє мідь анода.", size=9, color=INK))
    f.append(text(bx2 + bw2 / 2, by2 + 290, "3. Іони Cu²⁺ мігрують по мікрокапілярах.", size=9, color=INK))
    f.append(text(bx2 + bw2 / 2, by2 + 310, "4. Внутрішнє КЗ між шарами живлення.", size=9, color=POS, bold=True))

    render(os.path.join(IMG, "moisture-failure-modes.svg"), W, H, *f)

if __name__ == "__main__":
    fig_halt_hass_margins()
    fig_thermal_fatigue_cte()
    fig_vibration_psd_resonance()
    fig_moisture_failure_modes()
    print("Всі 4 фігури успішно згенеровано у ./img/")
