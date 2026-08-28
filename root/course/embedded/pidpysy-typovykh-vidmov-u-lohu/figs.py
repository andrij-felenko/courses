# -*- coding: utf-8 -*-
"""Фігури до статті «Підписи типових відмов у логу: осциляції, «унітаз», десинх, кліпінг»
(root/course/embedded/pidpysy-typovykh-vidmov-u-lohu).
Чистий Python, без зовнішніх бібліотек; svgkit імпортується зі scripts/."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Патерн «Унітаз» (Toilet-bowling): векторна геометрія розсинхрону компаса,
#    траєкторія спіралі на площині North-East та зсув фаз Roll/Pitch на 90°.
# ─────────────────────────────────────────────────────────────────────────────
def fig_toilet_bowling():
    W, H = 960, 480
    frags = [text(W / 2, 40, "Патерн «Унітаз»: розсинхрон компаса з вектором швидкості GPS", size=14, color=MUTED)]

    # ── Лівий блок: Векторна геометрія хибного прискорення ──
    bx1 = 170
    frags.append(text(bx1, 75, "Геометрія хибної корекції", size=12, color=INK, bold=True))
    frags.append(circle(bx1, 200, 75, fill="#fcfdfe", stroke=LINE, sw=1.2))
    # Бажаний вектор повернення до точки (до центру)
    frags.append(line(bx1, 200, bx1, 125, color=FIELD, sw=2.0))
    frags.append(arrow(bx1, 200, bx1, 125, color=FIELD, sw=2.0))
    frags.append(text(bx1 - 10, 155, "V_des", size=11, color=FIELD, bold=True, anchor="end"))
    
    # Фактичний вектор нахилу через помилку компаса theta_err
    ang = math.radians(40)
    tx = bx1 + 75 * math.sin(ang)
    ty = 200 - 75 * math.cos(ang)
    frags.append(line(bx1, 200, tx, ty, color=POS, sw=2.2))
    frags.append(arrow(bx1, 200, tx, ty, color=POS, sw=2.2))
    frags.append(text(tx + 8, ty - 6, "a_cmd (хибний крен)", size=11, color=POS, bold=True, anchor="start"))
    
    # Тангенціальна складова швидкості
    frags.append(arrow(tx, ty, tx + 45 * math.cos(ang), ty + 45 * math.sin(ang), color=NEG, sw=1.8))
    frags.append(text(tx + 48, ty + 20, "V_tan (розгін по спіралі)", size=10, color=NEG, bold=True, anchor="start"))

    b_geo, _, _ = textbox(bx1, 335, "Помилка курсу theta_err:\nзамість гальмування апарат\nприскорюється вбік,\nроздмухуючи радіус",
                          size=11, pad=8, stroke=POS, fill="#fdecea", min_w=220)
    frags.append(b_geo)

    # ── Середній блок: Розбіжна спіраль на площині North-East ──
    bx2 = 470
    frags.append(text(bx2, 75, "Траєкторія на карті (North - East)", size=12, color=INK, bold=True))
    frags.append(line(bx2 - 100, 200, bx2 + 100, 200, color=MUTED, sw=1.0, dash="3 3"))
    frags.append(line(bx2, 200 - 100, bx2, 200 + 100, color=MUTED, sw=1.0, dash="3 3"))
    frags.append(text(bx2 + 95, 192, "East", size=10, color=MUTED))
    frags.append(text(bx2 + 6, 110, "North", size=10, color=MUTED))
    frags.append(circle(bx2, 200, 4, fill=FIELD, stroke=INK, sw=1.5))
    frags.append(text(bx2, 218, "Ціль (Hold)", size=10, color=FIELD, bold=True))

    # Малювання розбіжної спіралі Архімеда / логарифмічної
    s_pts = []
    for step in range(120):
        t_val = step / 120.0 * 4.5 * math.pi
        r_val = 6.0 + 5.5 * t_val
        sx = bx2 + r_val * math.cos(t_val)
        sy = 200 - r_val * math.sin(t_val)
        s_pts.append((sx, sy))
    spath = "M %.1f %.1f " % s_pts[0] + " ".join("L %.1f %.1f" % p for p in s_pts[1:])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (spath, POS))
    frags.append(arrow(s_pts[-2][0], s_pts[-2][1], s_pts[-1][0], s_pts[-1][1], color=POS, sw=2.2))

    b_sp, _, _ = textbox(bx2, 335, "Лог позиції POS.RelOrigin:\nрадіус відхилення експоненційно\nзростає з кожним витком\n(смертельна вирва)",
                         size=11, pad=8, stroke=INK, fill="#f4f6f8", min_w=220)
    frags.append(b_sp)

    # ── Правий блок: Синусоїди Roll і Pitch зі зсувом 90° ──
    bx3 = 760
    frags.append(text(bx3, 75, "Часові сигнали Roll і Pitch", size=12, color=INK, bold=True))
    frags.append(line(bx3 - 110, 200, bx3 + 110, 200, color=MUTED, sw=1.0))
    frags.append(line(bx3 - 110, 130, bx3 - 110, 270, color=MUTED, sw=1.0))
    frags.append(text(bx3 + 105, 215, "t, c", size=10, color=MUTED))
    frags.append(text(bx3 - 110, 120, "Кут, град", size=10, color=MUTED))

    # Малювання двох гармонік
    r_pts = []
    p_pts = []
    for step in range(100):
        t_norm = step / 100.0
        cur_x = bx3 - 105 + t_norm * 210
        amp = 12.0 + t_norm * 38.0  # зростаюча амплітуда
        ang_w = t_norm * 4.0 * math.pi
        r_y = 200 - amp * math.sin(ang_w)
        p_y = 200 - amp * math.cos(ang_w)  # зсув 90 градусів (pi/2)
        r_pts.append((cur_x, r_y))
        p_pts.append((cur_x, p_y))

    r_path = "M %.1f %.1f " % r_pts[0] + " ".join("L %.1f %.1f" % p for p in r_pts[1:])
    p_path = "M %.1f %.1f " % p_pts[0] + " ".join("L %.1f %.1f" % p for p in p_pts[1:])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.0"/>' % (r_path, POS))
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.0" stroke-dasharray="4 3"/>' % (p_path, NEG))

    frags.append(text(bx3 - 20, 135, "— Roll (крен)", size=10, color=POS, bold=True))
    frags.append(text(bx3 + 65, 135, "-- Pitch (тангаж)", size=10, color=NEG, bold=True))

    b_sin, _, _ = textbox(bx3, 335, "Характерний автограф:\nRoll та Pitch коливаються на\nчастоті витка зі зсувом рівно 90°\n(фазовий квадрат кругового руху)",
                          size=11, pad=8, stroke=INK, fill="#f4f6f8", min_w=220)
    frags.append(b_sin)

    frags.append(text(W / 2, H - 25, "Коли компас зсунутий відносно GPS: корекція позиції живить відцентрове прискорення замість гальмування.",
                      size=12, color=INK, bold=True))
    render(os.path.join(IMG, 'toilet-bowling-spiral.svg'), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Десинхронізація мотора (Motor Desync) проти механічного відриву лопаті
# ─────────────────────────────────────────────────────────────────────────────
def fig_motor_desync():
    W, H = 960, 500
    frags = [text(W / 2, 40, "Підпис десинхронізації в логу: зрив eRPM, сплеск D-терма і переворот", size=14, color=MUTED)]

    # Координатна сітка графіків у часі (0..200 мс)
    ox, oy = 90, 80
    gw, gh = 480, 75
    gap = 18

    labels = [
        ("gyroADC vs Setpoint", "Кутова швидкість, °/s", [("Setpoint", FIELD, False), ("gyroADC (Roll)", POS, True)]),
        ("PID D-term / P-term", "Вихід регулятора", [("axisD", POS, True), ("axisP", NEG, False)]),
        ("Motor Output [0..100%]", "Команда на ESC", [("motor[3] (збійний)", POS, True), ("motor[0..2]", MUTED, False)]),
        ("eRPM (DShot Telemetry)", "Оберти мотора, тис/хв", [("eRPM[3] (десинх)", POS, True), ("eRPM[3] (відрив лопаті)", FIELD, False)])
    ]

    t_fault = ox + gw * 0.35

    for row, (title, unit, legend) in enumerate(labels):
        cy = oy + row * (gh + gap)
        # Рамка каналу
        frags.append(rect(ox, cy, gw, gh, fill="#ffffff", stroke="#d1d5db", sw=1.0, rx=3))
        frags.append(line(t_fault, cy, t_fault, cy + gh, color="#ef4444", sw=1.2, dash="3 3"))
        frags.append(text(ox - 10, cy + gh / 2, unit, size=10, color=MUTED, anchor="end"))
        frags.append(text(ox + 8, cy + 16, title, size=11, color=INK, bold=True, anchor="start"))
        
        # Легенда
        lx = ox + gw - 8
        for lname, lcol, lbold in reversed(legend):
            frags.append(text(lx, cy + 16, lname, size=10, color=lcol, bold=lbold, anchor="end"))
            lx -= text_width(lname, 10, lbold) + 16

    # Часова мітка аварії
    frags.append(text(t_fault, oy - 8, "t_0: зрив комутації", size=11, color=POS, bold=True))
    frags.append(text(ox + gw, oy + 4 * (gh + gap) - gap + 18, "Час (t), мс →", size=10, color=MUTED, anchor="end"))

    # Канал 0: gyroADC vs Setpoint
    y0 = oy
    frags.append(line(ox, y0 + gh / 2, ox + gw, y0 + gh / 2, color=FIELD, sw=1.8))  # Setpoint = 0
    # gyroADC
    g_pts = [(ox, y0 + gh / 2), (t_fault, y0 + gh / 2)]
    for s in range(50):
        t_frac = s / 50.0
        cur_x = t_fault + t_frac * (ox + gw - t_fault)
        cur_y = y0 + gh / 2 + math.pow(t_frac, 2) * (gh * 0.45)
        g_pts.append((cur_x, cur_y))
    g_path = "M %.1f %.1f " % g_pts[0] + " ".join("L %.1f %.1f" % p for p in g_pts[1:])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (g_path, POS))

    # Канал 1: D-term spike
    y1 = oy + (gh + gap)
    d_pts = [(ox, y1 + gh / 2), (t_fault - 5, y1 + gh / 2), (t_fault + 8, y1 + 6),
             (t_fault + 40, y1 + gh * 0.8), (ox + gw, y1 + gh * 0.85)]
    d_path = "M %.1f %.1f " % d_pts[0] + " ".join("L %.1f %.1f" % p for p in d_pts[1:])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d_path, POS))

    # Канал 2: Motor output (pegged at 100%)
    y2 = oy + 2 * (gh + gap)
    frags.append(line(ox, y2 + gh * 0.6, t_fault, y2 + gh * 0.6, color=POS, sw=2.0))
    frags.append(line(t_fault, y2 + gh * 0.6, t_fault + 10, y2 + 8, color=POS, sw=2.0))
    frags.append(line(t_fault + 10, y2 + 8, ox + gw, y2 + 8, color=POS, sw=2.2))
    # Інші мотори на 0%
    frags.append(line(t_fault + 10, y2 + gh - 8, ox + gw, y2 + gh - 8, color=MUTED, sw=1.5))

    # Канал 3: eRPM collapse (десинх) vs eRPM jump (відрив лопаті)
    y3 = oy + 3 * (gh + gap)
    frags.append(line(ox, y3 + gh * 0.45, t_fault, y3 + gh * 0.45, color=INK, sw=1.8))
    # Десинх -> 0
    frags.append(line(t_fault, y3 + gh * 0.45, t_fault + 20, y3 + gh - 6, color=POS, sw=2.2))
    frags.append(line(t_fault + 20, y3 + gh - 6, ox + gw, y3 + gh - 6, color=POS, sw=2.2))
    # Відрив лопаті -> зашкал
    frags.append(line(t_fault, y3 + gh * 0.45, t_fault + 25, y3 + 6, color=FIELD, sw=1.8, dash="4 3"))
    frags.append(line(t_fault + 25, y3 + 6, ox + gw, y3 + 6, color=FIELD, sw=1.8, dash="4 3"))

    # ── Правий блок: Порівняльна діагностика ──
    rx = 770
    frags.append(text(rx, 75, "Діагностичне розрізнення", size=13, color=INK, bold=True))

    b_desync, _, _ = textbox(rx, 160, "ДЕCИНХРОНІЗАЦІЯ ESC:\n• eRPM миттєво падає до 0\n• Струм мотора спадає або шумить\n• D-терм б'є в стелю\n• Мотор 100%, тяги немає\nПричина: тривале розмагнічування (demag)",
                             size=11, pad=10, stroke=POS, fill="#fdecea", min_w=280)
    frags.append(b_desync)

    b_prop, _, _ = textbox(rx, 305, "ВІДРИВ ЛОПАТІ ГВИНТА:\n• eRPM підскакує в 1.5–2 рази\n  (знято навантаження з вала)\n• Струм падає до холостого\n• Колосальна вібрація на 1x RPM\nПричина: механічне руйнування",
                            size=11, pad=10, stroke=FIELD, fill="#eafaf0", min_w=280)
    frags.append(b_prop)

    b_fix, _, _ = textbox(rx, 420, "Лікування десинхрону в BLHeli / AM32:\n• Підняти Demag Compensation (Low → High)\n• Збільшити Motor Timing (15° → 22.5°)\n• Знизити різкість D-term або rampup power",
                          size=11, pad=8, stroke=INK, fill="#f4f6f8", min_w=280)
    frags.append(b_fix)

    render(os.path.join(IMG, 'motor-desync-signature.svg'), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Кліпінг давача (Sensor Clipping) та зсув постійної складової (DC offset)
# ─────────────────────────────────────────────────────────────────────────────
def fig_sensor_clipping():
    W, H = 960, 480
    frags = [text(W / 2, 40, "Кліпінг сенсора: нелінійне зрізання вібрації та хибний завал горизонту", size=14, color=MUTED)]

    # ── Лівий блок: Симетричний vs Несиметричний кліпінг ──
    lx = 270
    frags.append(text(lx, 75, "Сигнал вібрації в межах і за межами АЦП", size=12, color=INK, bold=True))

    # Вісь часу
    frags.append(line(lx - 200, 200, lx + 200, 200, color=MUTED, sw=1.0))
    # Межі кліпінгу (+-16g або +-2000 deg/s)
    frags.append(line(lx - 200, 135, lx + 200, 135, color=POS, sw=1.2, dash="4 4"))
    frags.append(line(lx - 200, 265, lx + 200, 265, color=POS, sw=1.2, dash="4 4"))
    frags.append(text(lx + 205, 138, "+FullScale (+16g)", size=10, color=POS, anchor="start"))
    frags.append(text(lx + 205, 268, "−FullScale (−16g)", size=10, color=POS, anchor="start"))

    # Справжня фізична вібрація (велика синусоїда, виходить за межі)
    pts_real = []
    pts_clip = []
    for s in range(160):
        t_val = s / 160.0 * 6.0 * math.pi
        cur_x = lx - 190 + s * 2.4
        # Зміщена синусоїда (постійна складова 1g гравітації зміщує нуль вгору)
        raw_val = 200 - (18 + 90 * math.sin(t_val))
        pts_real.append((cur_x, raw_val))
        # Кліпований сигнал
        clip_val = max(135, min(265, raw_val))
        pts_clip.append((cur_x, clip_val))

    path_real = "M %.1f %.1f " % pts_real[0] + " ".join("L %.1f %.1f" % p for p in pts_real[1:])
    path_clip = "M %.1f %.1f " % pts_clip[0] + " ".join("L %.1f %.1f" % p for p in pts_clip[1:])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="3 3"/>' % (path_real, MUTED))
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (path_clip, POS))

    frags.append(text(lx - 120, 115, "Справжня вібрація рами", size=10, color=MUTED))
    frags.append(text(lx + 80, 115, "Кліпований сигнал АЦП", size=10, color=POS, bold=True))

    # Зміщене середнє
    frags.append(line(lx - 190, 212, lx + 190, 212, color=NEG, sw=1.8, dash="5 3"))
    frags.append(text(lx + 5, 226, "Зміщене середнє (DC Offset != 0)", size=10, color=NEG, bold=True))

    b_clp, _, _ = textbox(lx, 350, "Через несиметричне зрізання верхівок виникає\n«детекторний ефект» (випрямлення шуму):\nфільтр бачить постійне хибне прискорення вбік,\nякого фізично не існує",
                          size=11, pad=10, stroke=INK, fill="#f4f6f8", min_w=420)
    frags.append(b_clp)

    # ── Правий блок: Наслідки для EKF та орієнтації ──
    rx = 730
    frags.append(text(rx, 75, "Наслідки для польотного стека", size=12, color=INK, bold=True))

    b_ekf, _, _ = textbox(rx, 155, "1. ЗРИВ ОЦІНКИ ГОРИЗОНТУ:\nEKF зливає хибний DC-offset акселерометра,\nвважаючи його вектором сили тяжіння.\nОцінка нахилу завалюється на 20°–50°",
                          size=11, pad=10, stroke=POS, fill="#fdecea", min_w=360)
    frags.append(b_ekf)

    b_drift, _, _ = textbox(rx, 270, "2. НЕКЕРАВАНЕ ВТЕЧА ВБІК:\nКонтролер горизонту намагається «вирівняти»\nдрон за хибним вектором і сам розганяє його\nна максимальній швидкості в землю/перешкоду",
                            size=11, pad=10, stroke=NEG, fill="#eaf0fd", min_w=360)
    frags.append(b_drift)

    b_ard, _, _ = textbox(rx, 385, "3. ДІАГНОСТИКА В DATAFLASH:\nДивись поля VIBE.Clip0, Clip1, Clip2.\nНорма: 0 кліпів за політ.\nБільше 50–100 кліпів — критична вібрація",
                          size=11, pad=10, stroke=FIELD, fill="#eafaf0", min_w=360)
    frags.append(b_ard)

    render(os.path.join(IMG, 'sensor-clipping-rectification.svg'), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Насичення мікшера (Mixer Saturation) та пріоритети керування
# ─────────────────────────────────────────────────────────────────────────────
def fig_mixer_saturation():
    W, H = 960, 480
    frags = [text(W / 2, 40, "Насичення мікшера: втрата авторитету стабілізації проти AirMode", size=14, color=MUTED)]

    # ── Лівий блок: Запит мікшера перевищує 100% ──
    bx1 = 180
    frags.append(text(bx1, 75, "Запит регулятора (90% газ + крен)", size=12, color=INK, bold=True))
    frags.append(line(bx1 - 105, 240 - 100 * 1.3, bx1 + 105, 240 - 100 * 1.3, color=POS, sw=1.2, dash="3 3"))
    frags.append(text(bx1 + 115, 240 - 100 * 1.3 + 4, "100%", size=10, color=POS, anchor="start"))
    
    # 4 стовпчики моторів
    m_demands = [110, 70, 70, 110]
    for i, dem in enumerate(m_demands):
        mx = bx1 - 75 + i * 50
        h_bar = dem * 1.3
        col = POS if dem > 100 else NEG
        frags.append(rect(mx - 16, 240 - h_bar, 32, h_bar, fill="#eaf0fd" if dem <= 100 else "#fdecea",
                          stroke=col, sw=1.5, rx=3))
        frags.append(text(mx, 240 + 16, "M%d" % (i + 1), size=11, color=INK, bold=True))
        frags.append(text(mx, 240 - h_bar - 8, "%d%%" % dem, size=10, color=col, bold=True))

    b_dem, _, _ = textbox(bx1, 350, "Сума Throttle + Roll + Pitch + Yaw\nперевищує фізичну межу 100%.\nМотори M1 і M4 фізично не можуть\nрозвинути 110% тяги",
                          size=11, pad=10, stroke=INK, fill="#f4f6f8", min_w=240)
    frags.append(b_dem)

    # ── Середній блок: Жорстке зрізання (Hard Clipping) ──
    bx2 = 480
    frags.append(text(bx2, 75, "Жорстке зрізання (Hard Clip)", size=12, color=POS, bold=True))
    frags.append(line(bx2 - 105, 240 - 100 * 1.3, bx2 + 105, 240 - 100 * 1.3, color=POS, sw=1.2, dash="3 3"))
    frags.append(text(bx2 + 115, 240 - 100 * 1.3 + 4, "100%", size=10, color=POS, anchor="start"))

    m_clip = [100, 70, 70, 100]
    for i, val in enumerate(m_clip):
        mx = bx2 - 75 + i * 50
        h_bar = val * 1.3
        frags.append(rect(mx - 16, 240 - h_bar, 32, h_bar, fill="#f4f6f8", stroke=INK, sw=1.5, rx=3))
        frags.append(text(mx, 240 + 16, "M%d" % (i + 1), size=11, color=INK, bold=True))
        frags.append(text(mx, 240 - h_bar - 8, "%d%%" % val, size=10, color=INK, bold=True))

    b_cl, _, _ = textbox(bx2, 350, "ВТРАТА МОМЕНТУ СТАБІЛІЗАЦІЇ:\nРізниця між моторами зменшилась\nіз 40% до 30% (а по Yaw — до нуля).\nАпарат стає «ватним» і некерованим",
                         size=11, pad=10, stroke=POS, fill="#fdecea", min_w=240)
    frags.append(b_cl)

    # ── Правий блок: Динамічне масштабування (AirMode) ──
    bx3 = 780
    frags.append(text(bx3, 75, "Динамічний мікшер / AirMode", size=12, color=FIELD, bold=True))
    frags.append(line(bx3 - 105, 240 - 100 * 1.3, bx3 + 105, 240 - 100 * 1.3, color=POS, sw=1.2, dash="3 3"))
    frags.append(text(bx3 + 115, 240 - 100 * 1.3 + 4, "100%", size=10, color=POS, anchor="start"))

    m_air = [100, 60, 60, 100]  # Зниження бази газу з 90% до 80% зберігає різницю 40%
    for i, val in enumerate(m_air):
        mx = bx3 - 75 + i * 50
        h_bar = val * 1.3
        frags.append(rect(mx - 16, 240 - h_bar, 32, h_bar, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=3))
        frags.append(text(mx, 240 + 16, "M%d" % (i + 1), size=11, color=INK, bold=True))
        frags.append(text(mx, 240 - h_bar - 8, "%d%%" % val, size=10, color=FIELD, bold=True))

    b_air, _, _ = textbox(bx3, 350, "ЗБЕРЕЖЕННЯ АВТОРИТЕТУ:\nМікшер автоматично зменшує базовий газ,\nщоб зберегти повну різницю тяги 40%.\nКутова керованість не втрачається",
                          size=11, pad=10, stroke=FIELD, fill="#eafaf0", min_w=240)
    frags.append(b_air)

    render(os.path.join(IMG, 'mixer-saturation-priority.svg'), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# 5. Повний діагностичний маршрут розслідування за логом (Blackbox / DataFlash)
# ─────────────────────────────────────────────────────────────────────────────
def fig_diagnostic_tree():
    W, H = 960, 520
    frags = [text(W / 2, 36, "Дерево розслідування відмов за бортовим журналом (Blackbox / PlotJuggler)", size=14, color=MUTED)]

    # 4 гілки симптомів
    cols = [
        ("«Унітаз» / Спіраль", "#3b82f6", [
            ("Сигнал логу", "Roll/Pitch синус 90°\nPOS розбіжна спіраль\nEKF Yaw variance > 1"),
            ("Першопричина", "Зсув магнітометра\nНаведення силових шин\nХибний AHRS_ORIENT"),
            ("Рішення", "Калібрування компаса\nПідняти GPS/Mag на щоглу\nCompass-motor compensation")
        ]),
        ("Миттєвий переворот", "#ef4444", [
            ("Сигнал логу", "gyroADC лавиноподібно\nD-term у стелі\neRPM падає в 0 (мотор 100%)"),
            ("Першопричина", "Десинхрон ESC\nЗрив проти-ЕРС / Demag\nХолодна пайка фази"),
            ("Рішення", "Demag Comp -> High\nПідняти Motor Timing\nПеревірити силові фази")
        ]),
        ("Завал горизонту", "#f59e0b", [
            ("Сигнал логу", "accADC плато (+-16g)\nVIBE.Clip > 100\nDC-offset зміщення"),
            ("Першопричина", "Резонансна вібрація\nЖорстке кріплення FC\nПошкоджений підшипник"),
            ("Рішення", "М'які силіконові демпфери\nRPM-Notch фільтрація\nБалансування гвинтів")
        ]),
        ("В'ялість / Дзвін осей", "#10b981", [
            ("Сигнал логу", "Полиця мотора 100%\nI-term windup на упорі\nПровал частоти Yaw"),
            ("Першопричина", "Насичення мікшера\nБрак запасу тяги\nПереважний апарат"),
            ("Рішення", "Увімкнути AirMode\nAnti-Windup I-term clamp\nПолегшити батарею/дрон")
        ])
    ]

    for col_idx, (symp_title, col_theme, cards) in enumerate(cols):
        cx = 135 + col_idx * 230
        # Заголовок симптому
        b_sym, _, _ = textbox(cx, 80, symp_title, size=12, bold=True, pad=8,
                              stroke=col_theme, fill="#ffffff", min_w=210)
        frags.append(b_sym)
        frags.append(arrow(cx, 105, cx, 135, color=col_theme))

        # 3 рівні: Сигнал -> Причина -> Рішення
        y_pos = [175, 285, 395]
        for lvl_idx, (lvl_name, lvl_content) in enumerate(cards):
            cy = y_pos[lvl_idx]
            b_card, _, _ = textbox(cx, cy, lvl_name.upper() + ":\n" + lvl_content,
                                   size=10, pad=8, stroke=col_theme if lvl_idx == 0 else INK,
                                   fill="#fdfdfe" if lvl_idx == 0 else ("#fdecea" if lvl_idx == 1 else "#eafaf0"),
                                   min_w=210)
            frags.append(b_card)
            if lvl_idx < 2:
                frags.append(arrow(cx, cy + 38, cx, y_pos[lvl_idx + 1] - 38, color=MUTED))

    frags.append(text(W / 2, H - 20, "Швидкий алгоритм: дивись розбіжність Setpoint/Gyro → перевір відгук D/I-термів → стан моторів та eRPM → якість сенсорів.",
                      size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, 'blackbox-diagnostic-tree.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_toilet_bowling()
    fig_motor_desync()
    fig_sensor_clipping()
    fig_mixer_saturation()
    fig_diagnostic_tree()
    print("OK: all figures successfully generated in", IMG)
