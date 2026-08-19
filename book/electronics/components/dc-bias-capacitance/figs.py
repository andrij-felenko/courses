# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. perovskite-ferroelectric-domain: кристалічна комірка BaTiO3 та домени ──
def fig_perovskite_domain():
    W, H = 760, 390
    p = []

    # Фон лівої панелі (кристалічна гратка)
    p.append(rect(20, 45, 345, 325, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    p.append(text(192, 70, "Сегнетоелектрична комірка BaTiO₃", size=13, color=INK, bold=True))
    p.append(text(192, 88, "Перовскітна структура нижче точки Кюрі (<125 °C)", size=10, color=MUTED))

    # Кристалічна комірка (тетрагональна)
    cx, cy = 180, 185
    s = 65
    # Задня грань
    p.append(rect(cx - s/2 + 18, cy - s/2 - 22, s, s + 14, fill="#edf2f7", stroke="#a0aec0", sw=1.2, rx=2))
    # З'єднувальні ребра
    p.append(line(cx - s/2, cy - s/2, cx - s/2 + 18, cy - s/2 - 22, color="#a0aec0", sw=1.2))
    p.append(line(cx + s/2, cy - s/2, cx + s/2 + 18, cy - s/2 - 22, color="#a0aec0", sw=1.2))
    p.append(line(cx - s/2, cy + s/2 + 14, cx - s/2 + 18, cy + s/2 - 8, color="#a0aec0", sw=1.2))
    p.append(line(cx + s/2, cy + s/2 + 14, cx + s/2 + 18, cy + s/2 - 8, color="#a0aec0", sw=1.2))
    # Передня грань
    p.append(rect(cx - s/2, cy - s/2, s, s + 14, fill="none", stroke=LINE, sw=1.5, rx=2))

    # Іони Ba2+ у вершинах (сірі)
    for vx, vy in [
        (cx - s/2, cy - s/2), (cx + s/2, cy - s/2),
        (cx - s/2, cy + s/2 + 14), (cx + s/2, cy + s/2 + 14),
        (cx - s/2 + 18, cy - s/2 - 22), (cx + s/2 + 18, cy - s/2 - 22),
        (cx - s/2 + 18, cy + s/2 - 8), (cx + s/2 + 18, cy + s/2 - 8)
    ]:
        p.append(circle(vx, vy, 6, fill="#718096", stroke=LINE, sw=1))

    # Іони O2- на центрах граней (сині)
    for ox, oy in [
        (cx, cy - s/2), (cx, cy + s/2 + 14),
        (cx - s/2, cy + 7), (cx + s/2, cy + 7),
        (cx + 9, cy - 11 + 7)
    ]:
        p.append(circle(ox, oy, 5, fill="#3182ce", stroke=LINE, sw=1))

    # Центральний іон Ti4+ зміщений вгору вздовж осі c (червоний)
    tix, tiy = cx + 9, cy - 11 + 7 - 12
    p.append(circle(tix, tiy, 7, fill=POS, stroke=LINE, sw=1.5))
    # Вектор спонтанної поляризації P0
    p.append(arrow(cx + 9, cy + 18, cx + 9, cy - 24, color=POS, sw=2))
    p.append(text(cx + 68, cy - 4, "P_спонт", size=10, color=POS, bold=True))

    # Пояснення до кристала
    p.append(text(192, 290, "Ti⁴⁺ зміщений від центру на ~0.01 нм", size=10, color=INK, bold=True))
    p.append(text(192, 308, "утворює постійний спонтанний диполь у кожній комірці", size=9, color=MUTED))
    p.append(text(192, 335, "Ba²⁺ (вершини)   O²⁻ (грані)   Ti⁴⁺ (центр)", size=9, color=INK))

    # Фон правої панелі (поведінка доменів під полем)
    p.append(rect(385, 45, 355, 325, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    p.append(text(562, 70, "Поляризація доменів під зовнішнім полем", size=13, color=INK, bold=True))

    # Стан А: E = 0 (вільні домени)
    p.append(rect(405, 95, 150, 110, fill="#ffffff", stroke="#4a5568", sw=1.2, rx=4))
    p.append(text(480, 115, "E = 0 (без DC-зміщення)", size=10, color=FIELD, bold=True))
    # Доменні межі та випадкові стрілки
    p.append(line(480, 125, 480, 200, color="#cbd5e0", sw=1.2, dash="3,3"))
    p.append(line(405, 162, 555, 162, color="#cbd5e0", sw=1.2, dash="3,3"))
    p.append(arrow(430, 150, 460, 135, color=POS, sw=1.5))
    p.append(arrow(530, 140, 500, 155, color=POS, sw=1.5))
    p.append(arrow(435, 175, 455, 195, color=POS, sw=1.5))
    p.append(arrow(510, 195, 535, 175, color=POS, sw=1.5))
    p.append(text(480, 218, "Доменні стінки вільно коливаються", size=9, color=INK))
    p.append(text(480, 232, "величезна відповідь dP/dE → висока ємність", size=9, color=FIELD, bold=True))

    # Стан Б: E >> 0 (насичення DC-полем)
    p.append(rect(575, 95, 150, 110, fill="#fff5f5", stroke=POS, sw=1.5, rx=4))
    p.append(text(650, 115, "E >> 0 (сильне DC-поле)", size=10, color=POS, bold=True))
    # Зовнішнє поле Edc
    p.append(arrow(590, 130, 710, 130, color="#2b6cb0", sw=2))
    p.append(text(650, 144, "Зовнішнє поле E = V/d", size=9, color="#2b6cb0", bold=True))
    # Усі диполі повернуті вздовж поля, межі затиснуті
    p.append(arrow(600, 165, 640, 165, color=POS, sw=1.8))
    p.append(arrow(660, 165, 700, 165, color=POS, sw=1.8))
    p.append(arrow(600, 190, 640, 190, color=POS, sw=1.8))
    p.append(arrow(660, 190, 700, 190, color=POS, sw=1.8))
    p.append(text(650, 218, "Усі домени вишикувані й заблоковані", size=9, color=INK))
    p.append(text(650, 232, "насичення: dP/dE → 0 → ємність падає", size=9, color=POS, bold=True))

    # Підсумок внизу правої панелі
    p.append(rect(405, 255, 320, 95, fill="#edf2f7", stroke="#cbd5e0", sw=1, rx=6))
    p.append(text(565, 275, "Механізм втрати ємності під напругою:", size=10, color=INK, bold=True))
    p.append(text(565, 295, "1. Постійна напруга створює поле E = V/d всередині шару", size=9, color=INK))
    p.append(text(565, 313, "2. Поле примусово повертає спонтанні диполі до насичення", size=9, color=INK))
    p.append(text(565, 331, "3. На малий змінний сигнал AC відгуку майже не лишається", size=9, color=POS, bold=True))

    render(os.path.join(OUT, "perovskite-ferroelectric-domain.svg"), W, H, *p,
           title="Перовскітна структура BaTiO3 та насичення сегнетоелектричних доменів під DC-зміщенням")


# ── 2. dc-bias-curves-classes: графіки C(V) для різних діелектриків і корпусів ──
def fig_dc_bias_curves():
    W, H = 760, 380
    p = []

    # Вісь графіка
    ox, oy = 90, 310
    gw, gh = 450, 230
    p.append(rect(30, 45, 700, 315, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    p.append(text(380, 70, "Залежність залишкової ємності від прикладеної постійної напруги", size=13, color=INK, bold=True))

    # Сітка графіка
    for y_pct, y_val in [(100, 0), (75, gh*0.25), (50, gh*0.5), (25, gh*0.75), (0, gh)]:
        y_pos = oy - gh + y_val
        p.append(line(ox, y_pos, ox + gw, y_pos, color="#e2e8f0", sw=1))
        p.append(text(ox - 10, y_pos + 4, "%d%%" % y_pct, size=10, color=MUTED, anchor="end"))

    for x_v in [0, 5, 10, 15, 20, 25]:
        x_pos = ox + (x_v / 25.0) * gw
        p.append(line(x_pos, oy - gh, x_pos, oy, color="#e2e8f0", sw=1))
        p.append(text(x_pos, oy + 18, "%d В" % x_v, size=10, color=MUTED))

    # Осі X та Y
    p.append(arrow(ox, oy, ox + gw + 20, oy, color=LINE, sw=1.5))
    p.append(text(ox + gw + 10, oy + 32, "Постійна напруга зміщення V_dc (В)", size=10, color=INK, anchor="end", bold=True))
    p.append(arrow(ox, oy, ox, oy - gh - 20, color=LINE, sw=1.5))
    p.append(text(ox - 15, oy - gh - 15, "C_eff / C_nom", size=10, color=INK, bold=True))

    # Крива 1: C0G / NP0 (Клас I) — 100% плоска лінія
    p.append(line(ox, oy - gh, ox + gw, oy - gh, color="#2b6cb0", sw=3))

    # Крива 2: X7R 1206 (25V номінал) — плавний спад до ~65%
    pts_x7r_1206 = [(0, 1.0), (5, 0.93), (10, 0.84), (15, 0.76), (20, 0.70), (25, 0.64)]
    for i in range(len(pts_x7r_1206)-1):
        x1, y1 = ox + (pts_x7r_1206[i][0]/25.0)*gw, oy - pts_x7r_1206[i][1]*gh
        x2, y2 = ox + (pts_x7r_1206[i+1][0]/25.0)*gw, oy - pts_x7r_1206[i+1][1]*gh
        p.append(line(x1, y1, x2, y2, color="#27ae60", sw=2.5))

    # Крива 3: X7R 0603 (16V номінал) — спад до ~35%
    pts_x7r_0603 = [(0, 1.0), (3.3, 0.82), (5, 0.70), (10, 0.46), (16, 0.32), (25, 0.22)]
    for i in range(len(pts_x7r_0603)-1):
        x1, y1 = ox + (pts_x7r_0603[i][0]/25.0)*gw, oy - pts_x7r_0603[i][1]*gh
        x2, y2 = ox + (pts_x7r_0603[i+1][0]/25.0)*gw, oy - pts_x7r_0603[i+1][1]*gh
        p.append(line(x1, y1, x2, y2, color="#d69e2e", sw=2.5))

    # Крива 4: X5R 0402 (10V номінал) — різкий обвал до 20%
    pts_x5r_0402 = [(0, 1.0), (2.5, 0.65), (5, 0.32), (10, 0.18), (16, 0.12), (25, 0.08)]
    for i in range(len(pts_x5r_0402)-1):
        x1, y1 = ox + (pts_x5r_0402[i][0]/25.0)*gw, oy - pts_x5r_0402[i][1]*gh
        x2, y2 = ox + (pts_x5r_0402[i+1][0]/25.0)*gw, oy - pts_x5r_0402[i+1][1]*gh
        p.append(line(x1, y1, x2, y2, color=POS, sw=2.5))

    # Крива 5: Y5V 0805 (16V номінал) — катастрофічний обвал <10%
    pts_y5v = [(0, 1.0), (2, 0.45), (5, 0.15), (10, 0.07), (16, 0.04), (25, 0.02)]
    for i in range(len(pts_y5v)-1):
        x1, y1 = ox + (pts_y5v[i][0]/25.0)*gw, oy - pts_y5v[i][1]*gh
        x2, y2 = ox + (pts_y5v[i+1][0]/25.0)*gw, oy - pts_y5v[i+1][1]*gh
        p.append(line(x1, y1, x2, y2, color="#805ad5", sw=2, dash="4,3"))

    # Легенда справа
    lx, ly = 555, 95
    p.append(rect(lx, ly, 160, 215, fill="#f8fafc", stroke="#cbd5e0", sw=1, rx=6))
    p.append(text(lx + 80, ly + 20, "Типи та корпуси:", size=11, color=INK, bold=True))

    leg_items = [
        ("C0G (Клас I, будь-який)", "#2b6cb0", "0% втрати"),
        ("X7R 1206 (25V)", "#27ae60", "−35% при 25V"),
        ("X7R 0603 (16V)", "#d69e2e", "−68% при 16V"),
        ("X5R 0402 (10V)", POS, "−82% при 10V"),
        ("Y5V 0805 (16V)", "#805ad5", "−96% при 16V")
    ]
    cur_y = ly + 40
    for label, col, note in leg_items:
        p.append(line(lx + 10, cur_y + 4, lx + 28, cur_y + 4, color=col, sw=3))
        p.append(text(lx + 34, cur_y + 6, label, size=9, color=INK, anchor="start", bold=True))
        p.append(text(lx + 34, cur_y + 20, note, size=9, color=MUTED, anchor="start"))
        cur_y += 35

    render(os.path.join(OUT, "dc-bias-curves-classes.svg"), W, H, *p,
           title="Порівняння падіння ємності під напругою для різних класів діелектриків і корпусів MLCC")


# ── 3. package-size-layer-field: товщина діелектрика та напруженість E = V/d ──
def fig_package_field():
    W, H = 760, 360
    p = []

    p.append(rect(20, 40, 720, 305, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    p.append(text(380, 65, "Чому мініатюризація корпусу посилює DC-bias: зв'язок E = V / d", size=13, color=INK, bold=True))

    # Лівий блок: 1206 (великий корпус, товстий діелектрик)
    bx1 = 40
    p.append(rect(bx1, 85, 320, 240, fill="#f0fff4", stroke="#27ae60", sw=1.5, rx=6))
    p.append(text(bx1 + 160, 110, "Корпус 1206 (3.2 × 1.6 мм) · 10 мкФ 25V", size=11, color="#27ae60", bold=True))

    # Схема шарів 1206
    for i in range(4):
        sy = 135 + i * 26
        p.append(rect(bx1 + 40, sy, 240, 18, fill="#c6f6d5", stroke="#27ae60", sw=1))
        p.append(line(bx1 + 25, sy, bx1 + 250, sy, color="#2d3748", sw=2))
        p.append(line(bx1 + 70, sy + 18, bx1 + 295, sy + 18, color="#2d3748", sw=2))

    # Торці
    p.append(rect(bx1 + 20, 130, 15, 105, fill="#718096", stroke=LINE, sw=1.2, rx=2))
    p.append(rect(bx1 + 285, 130, 15, 105, fill="#718096", stroke=LINE, sw=1.2, rx=2))

    p.append(text(bx1 + 220, 148, "d ≈ 8.0 мкм", size=10, color=INK, bold=True))

    # Розрахунок поля для 1206
    p.append(text(bx1 + 160, 255, "При напрузі шини V_dc = 5 В:", size=10, color=INK))
    p.append(text(bx1 + 160, 275, "E = 5 В / 8 мкм = 0.625 МВ/м (слабке поле)", size=10, color="#27ae60", bold=True))
    p.append(text(bx1 + 160, 295, "Залишок ємності C_eff ≈ 8.5 мкФ (втрата лише ~15%)", size=9, color=INK))

    # Правий блок: 0402 (дрібний корпус, тонкий діелектрик)
    bx2 = 400
    p.append(rect(bx2, 85, 320, 240, fill="#fff5f5", stroke=POS, sw=1.5, rx=6))
    p.append(text(bx2 + 160, 110, "Корпус 0402 (1.0 × 0.5 мм) · 10 мкФ 10V", size=11, color=POS, bold=True))

    # Схема шарів 0402 (багато тонких шарів)
    for i in range(8):
        sy = 132 + i * 13
        p.append(rect(bx2 + 40, sy, 240, 8, fill="#fed7d7", stroke=POS, sw=0.8))
        p.append(line(bx2 + 25, sy, bx2 + 255, sy, color="#2d3748", sw=1.5))
        p.append(line(bx2 + 65, sy + 8, bx2 + 295, sy + 8, color="#2d3748", sw=1.5))

    # Торці
    p.append(rect(bx2 + 20, 130, 15, 105, fill="#718096", stroke=LINE, sw=1.2, rx=2))
    p.append(rect(bx2 + 285, 130, 15, 105, fill="#718096", stroke=LINE, sw=1.2, rx=2))

    p.append(text(bx2 + 220, 144, "d ≈ 1.0 мкм", size=10, color=POS, bold=True))

    # Розрахунок поля для 0402
    p.append(text(bx2 + 160, 255, "При тій самій напрузі шини V_dc = 5 В:", size=10, color=INK))
    p.append(text(bx2 + 160, 275, "E = 5 В / 1 мкм = 5.0 МВ/м (глибоке насичення!)", size=10, color=POS, bold=True))
    p.append(text(bx2 + 160, 295, "Залишок ємності C_eff ≈ 2.2 мкФ (катастрофічна втрата ~78%)", size=9, color=POS, bold=True))

    render(os.path.join(OUT, "package-size-layer-field.svg"), W, H, *p,
           title="Порівняння товщини шарів діелектрика та внутрішнього електричного поля в корпусах 1206 та 0402")


# ── 4. dcdc-stability-ripple-impact: вплив на пульсації та фазовий запас DC-DC ──
def fig_dcdc_impact():
    W, H = 760, 390
    p = []

    p.append(rect(20, 45, 720, 325, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    p.append(text(380, 70, "Вплив деградації ємності на вихідний фільтр та стійкість перетворювача", size=13, color=INK, bold=True))

    # Ліва панель: Пульсації вихідної напруги
    p.append(rect(35, 90, 335, 265, fill="#f8fafc", stroke="#cbd5e0", sw=1.2, rx=6))
    p.append(text(202, 110, "А. Пульсації напруги: ΔV = ΔI_L / (8 · f_sw · C_eff)", size=10, color=INK, bold=True))
    p.append(text(202, 128, "Зелений: номінальні 44 мкФ (ΔV = 15 мВ)", size=9, color="#27ae60", bold=True))
    p.append(text(202, 144, "Червоний: залишок 11 мкФ під DC-bias (ΔV = 60 мВ)", size=9, color=POS, bold=True))

    # Осцилограма
    ox1, oy1 = 55, 250
    w1, h1 = 295, 90
    p.append(rect(ox1, oy1 - h1, w1, h1, fill="#1a202c", stroke="#4a5568", sw=1, rx=4))
    # Сітка осцилографа
    for gy in range(oy1 - h1 + 18, oy1, 18):
        p.append(line(ox1, gy, ox1 + w1, gy, color="#2d3748", sw=0.8, dash="2,2"))
    for gx in range(ox1 + 35, ox1 + w1, 35):
        p.append(line(gx, oy1 - h1, gx, oy1, color="#2d3748", sw=0.8, dash="2,2"))

    # Хвиля 1: Розрахункова ємність (44 мкФ) -> мала пульсація 15 мВ
    pts_nom = []
    for k in range(4):
        x0 = ox1 + 10 + k * 65
        pts_nom.append((x0, oy1 - 45))
        pts_nom.append((x0 + 32, oy1 - 37))
        pts_nom.append((x0 + 65, oy1 - 45))
    for i in range(len(pts_nom)-1):
        p.append(line(pts_nom[i][0], pts_nom[i][1], pts_nom[i+1][0], pts_nom[i+1][1], color="#48bb78", sw=2))

    # Хвиля 2: Деградована ємність під DC-bias (11 мкФ) -> пульсація 60 мВ
    pts_deg = []
    for k in range(4):
        x0 = ox1 + 10 + k * 65
        pts_deg.append((x0, oy1 - 45))
        pts_deg.append((x0 + 32, oy1 - 15))
        pts_deg.append((x0 + 65, oy1 - 45))
    for i in range(len(pts_deg)-1):
        p.append(line(pts_deg[i][0], pts_deg[i][1], pts_deg[i+1][0], pts_deg[i+1][1], color=POS, sw=2))

    p.append(text(202, 326, "Пульсації зростають у 4 рази при 75% втраті ємності", size=9, color=INK))
    p.append(text(202, 342, "Стрибок навантаження спричиняє просідання напруги та UVLO", size=9, color=MUTED))

    # Права панель: Діаграма Боде та запас фази
    p.append(rect(390, 90, 335, 265, fill="#f8fafc", stroke="#cbd5e0", sw=1.2, rx=6))
    p.append(text(557, 110, "Б. Зсув полюса LC-фільтра та деградація фази", size=10, color=INK, bold=True))
    p.append(text(557, 128, "Зсув полюса fp = 1 / (2π√(L·C_eff)) вгору", size=9, color=INK))
    p.append(text(557, 144, "Запас фази падає з 60° до < 20° (автоколивання)", size=9, color=POS, bold=True))

    ox2, oy2 = 410, 250
    w2, h2 = 295, 90
    p.append(rect(ox2, oy2 - h2, w2, h2, fill="#ffffff", stroke="#4a5568", sw=1, rx=4))

    # Осі
    p.append(line(ox2, oy2 - 45, ox2 + w2, oy2 - 45, color="#a0aec0", sw=1, dash="4,4")) # 0 dB лінія
    p.append(text(ox2 + 6, oy2 - 49, "0 dB", size=9, color="#718096", anchor="start"))

    # Крива підсилення номінальна (зелена): полюс на fp1 = 8 кГц
    p.append(line(ox2 + 10, oy2 - 70, ox2 + 80, oy2 - 70, color="#27ae60", sw=2))
    p.append(line(ox2 + 80, oy2 - 70, ox2 + 190, oy2 - 25, color="#27ae60", sw=2))
    p.append(line(ox2 + 190, oy2 - 25, ox2 + 280, oy2 - 10, color="#27ae60", sw=2))

    # Крива підсилення зі зсунутим полюсом через DC-bias (червона): полюс fp2 = 16 кГц
    p.append(line(ox2 + 10, oy2 - 70, ox2 + 140, oy2 - 70, color=POS, sw=2, dash="3,2"))
    p.append(line(ox2 + 140, oy2 - 70, ox2 + 250, oy2 - 25, color=POS, sw=2, dash="3,2"))
    p.append(line(ox2 + 250, oy2 - 25, ox2 + 280, oy2 - 15, color=POS, sw=2, dash="3,2"))

    p.append(line(ox2 + 80, oy2 - h2, ox2 + 80, oy2, color="#27ae60", sw=1, dash="2,2"))
    p.append(text(ox2 + 80, oy2 - 6, "fp(ном)", size=9, color="#27ae60", bold=True))

    p.append(line(ox2 + 140, oy2 - h2, ox2 + 140, oy2, color=POS, sw=1, dash="2,2"))
    p.append(text(ox2 + 140, oy2 - 6, "fp(bias)", size=9, color=POS, bold=True))

    p.append(text(557, 326, "Частота зрізу зміщується в область малої фази", size=9, color=INK))
    p.append(text(557, 342, "Контур перетворювача втрачає стійкість", size=9, color=MUTED))

    render(os.path.join(OUT, "dcdc-stability-ripple-impact.svg"), W, H, *p,
           title="Вплив падіння ємності MLCC під DC-зміщенням на пульсації та стійкість контуру керування DC-DC")


if __name__ == "__main__":
    fig_perovskite_domain()
    fig_dc_bias_curves()
    fig_package_field()
    fig_dcdc_impact()
    print("Всі фігури успішно згенеровано у %s" % OUT)
