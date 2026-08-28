# -*- coding: utf-8 -*-
import sys, os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_takeover_spoofing_stages():
    """Три фази синхронного захоплення контурів стеження (Takeover Spoofing)."""
    W, H = 860, 380
    frags = []

    # Заголовок
    frags.append(text(W / 2, 28, "Фази синхронного перехоплення контурів стеження (Takeover Spoofing)", size=16, bold=True))

    # Створюємо 3 колонки для етапів
    col_w = 260
    col_h = 300
    gap = 20
    x_start = 20
    y_top = 55

    stages = [
        ("Етап 1: Синхронізація", "Збіг за кодом, фазою та Доплером", "#eaf0fd", NEG),
        ("Етап 2: Захоплення (+3..+10 дБ)", "Пригнічення справжнього сигналу", "#fdecea", POS),
        ("Етап 3: Відведення (Drag-off)", "Плавний зсув піка корелятора", "#fef9e7", "#b7791f")
    ]

    for idx, (title_text, subtitle_text, bg_color, accent_color) in enumerate(stages):
        cx = x_start + idx * (col_w + gap)
        frags.append(rect(cx, y_top, col_w, col_h, fill="#fafbfc", stroke="#cbd5e1", sw=1.2, rx=8))
        frags.append(rect(cx + 10, y_top + 10, col_w - 20, 42, fill=bg_color, stroke=accent_color, sw=1.2, rx=6))
        frags.append(text(cx + col_w / 2, y_top + 26, title_text, size=12, bold=True, color=accent_color))
        frags.append(text(cx + col_w / 2, y_top + 43, subtitle_text, size=10, color=MUTED))

        # Графік кореляційної функції (Delay vs Correlation Power)
        gx = cx + 25
        gy = y_top + 225
        gw = col_w - 50
        gh = 130

        frags.append(line(gx, gy, gx + gw, gy, color=LINE, sw=1.2))
        frags.append(line(gx + gw / 2, gy + 10, gx + gw / 2, gy - gh, color="#94a3b8", sw=1.0, dash="3,2"))
        frags.append(text(gx + gw / 2, gy + 18, "Затримка коду τ", size=10, color=MUTED))

        if idx == 0:
            # Справжній сигнал (синій трикутний пік)
            peak_x = gx + gw / 2
            frags.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#2457d6" fill-opacity="0.25" stroke="%s" stroke-width="1.8"/>' %
                         (peak_x - 45, gy, peak_x, gy - 75, peak_x + 45, gy, NEG))
            # Фальшивий сигнал підходить поруч, трохи слабший або рівний
            frags.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#c0392b" fill-opacity="0.2" stroke="%s" stroke-width="1.8" stroke-dasharray="3,2"/>' %
                         (peak_x - 50, gy, peak_x - 5, gy - 70, peak_x + 40, gy, POS))
            frags.append(text(cx + col_w / 2, gy - 90, "Автентичний сигнал", size=10, bold=True, color=NEG))
            frags.append(text(cx + col_w / 2, gy - 105, "Підгонка фальшивого піка", size=10, color=POS))
            frags.append(fitbox(cx + 15, y_top + 245, col_w - 30, 46, "Спуфер оцінює поточні\nкоординати цілі та генерує\nсинхронний фальшивий сигнал", size=10, fill="#ffffff", stroke="#e2e8f0"))

        elif idx == 1:
            # Справжній сигнал (синій, 75px)
            peak_x = gx + gw / 2
            frags.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#2457d6" fill-opacity="0.15" stroke="%s" stroke-width="1.4" stroke-dasharray="3,2"/>' %
                         (peak_x - 45, gy, peak_x, gy - 75, peak_x + 45, gy, NEG))
            # Фальшивий сигнал з потужністю +6 дБ (червоний, 115px)
            frags.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#c0392b" fill-opacity="0.35" stroke="%s" stroke-width="2.2"/>' %
                         (peak_x - 45, gy, peak_x, gy - 115, peak_x + 45, gy, POS))
            frags.append(text(cx + col_w / 2, gy - 122, "Спуфер: +3..+10 дБ", size=10, bold=True, color=POS))
            frags.append(fitbox(cx + 15, y_top + 245, col_w - 30, 46, "Дискримінатор DLL захоплює\nсильніший пік. Справжній пік\nпригнічується АРП (AGC)", size=10, fill="#ffffff", stroke="#e2e8f0"))

        elif idx == 2:
            # Справжній сигнал лишився на старому місці
            peak_x_real = gx + gw / 2 - 35
            frags.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#2457d6" fill-opacity="0.15" stroke="%s" stroke-width="1.2" stroke-dasharray="3,2"/>' %
                         (peak_x_real - 40, gy, peak_x_real, gy - 65, peak_x_real + 40, gy, NEG))
            # Фальшивий пік змістився вправо (Drag-off)
            peak_x_fake = gx + gw / 2 + 25
            frags.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#c0392b" fill-opacity="0.35" stroke="%s" stroke-width="2.2"/>' %
                         (peak_x_fake - 45, gy, peak_x_fake, gy - 110, peak_x_fake + 45, gy, POS))
            frags.append(arrow(peak_x_real + 10, gy - 85, peak_x_fake - 5, gy - 85, color=POS, sw=1.8))
            frags.append(text(peak_x_fake, gy - 118, "Зсунутий пік Δτ", size=10, bold=True, color=POS))
            frags.append(text(peak_x_real, gy - 72, "Істинний τ", size=10, color=NEG))
            frags.append(fitbox(cx + 15, y_top + 245, col_w - 30, 46, "Корелятор безперервно тягне\nпсевдодальність у хибний бік.\nКоординати плавно дрейфують", size=10, fill="#ffffff", stroke="#e2e8f0"))

        if idx < 2:
            frags.append(arrow(cx + col_w + 3, y_top + 150, cx + col_w + gap - 3, y_top + 150, color="#64748b", sw=2.0))

    return render(os.path.join(OUT, "takeover-spoofing-stages.svg"), W, H, *frags)


def fig_cn0_elevation_profile():
    """Порівняння енергетичного профілю C/N0 для справжнього сузір'я проти спуфера."""
    W, H = 840, 360
    frags = []

    frags.append(text(W / 2, 28, "Енергетичний профіль C/N0: супутники на орбіті проти наземного спуфера", size=16, bold=True))

    # Панель 1: Справжні супутники (природна залежність від кута піднесення)
    cx1 = 20
    w_p = 385
    h_p = 280
    y_p = 55
    frags.append(rect(cx1, y_p, w_p, h_p, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(cx1 + w_p / 2, y_p + 25, "Автентичні сигнали GNSS", size=13, bold=True, color=NEG))
    frags.append(text(cx1 + w_p / 2, y_p + 42, "C/N0 зростає разом із кутом піднесення супутника", size=11, color=MUTED))

    # Графік 1
    gx1, gy1 = cx1 + 55, y_p + 230
    gw, gh = 300, 160
    frags.append(line(gx1, gy1, gx1 + gw, gy1, color=LINE, sw=1.2))
    frags.append(line(gx1, gy1, gx1, gy1 - gh, color=LINE, sw=1.2))
    frags.append(text(gx1 + gw - 25, gy1 + 18, "Елевація θ", size=11, color=MUTED))
    frags.append(text(gx1 - 12, gy1 - gh + 15, "C/N0 (дБ-Гц)", size=11, color=MUTED, anchor="end"))

    # Позначки шкали
    frags.append(text(gx1 + 20, gy1 + 16, "10°", size=10, color=MUTED))
    frags.append(text(gx1 + gw / 2, gy1 + 16, "45°", size=10, color=MUTED))
    frags.append(text(gx1 + gw - 25, gy1 + 16, "85°", size=10, color=MUTED))

    frags.append(text(gx1 - 8, gy1 - 25, "32", size=10, color=MUTED, anchor="end"))
    frags.append(text(gx1 - 8, gy1 - 85, "42", size=10, color=MUTED, anchor="end"))
    frags.append(text(gx1 - 8, gy1 - 145, "52", size=10, color=MUTED, anchor="end"))
    frags.append(line(gx1, gy1 - 85, gx1 + gw, gy1 - 85, color="#e2e8f0", sw=1.0, dash="2,2"))

    # Точки супутників для справжнього профілю
    sat_real = [
        (25, 33.5, "PRN03 (12°)"),
        (65, 36.2, "PRN14 (22°)"),
        (110, 39.8, "PRN08 (35°)"),
        (160, 43.1, "PRN21 (48°)"),
        (215, 46.4, "PRN10 (65°)"),
        (270, 48.2, "PRN27 (82°)")
    ]
    curve_pts = []
    for deg in range(10, 86, 2):
        frac = (deg - 10) / 75.0
        # Модель C/N0 = 32 + 16 * sin(deg)
        cn0_val = 32.0 + 16.5 * math.sin(math.radians(deg))
        px = gx1 + frac * (gw - 30)
        py = gy1 - (cn0_val - 28.0) * (gh / 26.0)
        curve_pts.append("%.1f,%.1f" % (px, py))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0" stroke-dasharray="4,3"/>' % (" ".join(curve_pts), NEG))

    for x_offset, cn0_val, label in sat_real:
        px = gx1 + x_offset
        py = gy1 - (cn0_val - 28.0) * (gh / 26.0)
        frags.append(circle(px, py, 4.5, fill=NEG, stroke="#ffffff", sw=1.5))
        frags.append(text(px, py - 8, label.split()[0], size=9, bold=True, color=NEG))

    frags.append(text(cx1 + w_p / 2, y_p + h_p - 12, "Діапазон 34..48 дБ-Гц, сильна кореляція з атмосферою", size=10, bold=True, color=FIELD))

    # Панель 2: Наземний спуфінг (аномально рівна та надвисока потужність)
    cx2 = cx1 + w_p + 30
    frags.append(rect(cx2, y_p, w_p, h_p, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(cx2 + w_p / 2, y_p + 25, "Наземна підміна (GNSS Spoofing)", size=13, bold=True, color=POS))
    frags.append(text(cx2 + w_p / 2, y_p + 42, "Всі канали мають аномально однаковий високий C/N0", size=11, color=MUTED))

    # Графік 2
    gx2, gy2 = cx2 + 55, y_p + 230
    frags.append(line(gx2, gy2, gx2 + gw, gy2, color=LINE, sw=1.2))
    frags.append(line(gx2, gy2, gx2, gy2 - gh, color=LINE, sw=1.2))
    frags.append(text(gx2 + gw - 25, gy2 + 18, "Елевація θ", size=11, color=MUTED))
    frags.append(text(gx2 - 12, gy2 - gh + 15, "C/N0 (дБ-Гц)", size=11, color=MUTED, anchor="end"))

    frags.append(text(gx2 + 20, gy2 + 16, "10°", size=10, color=MUTED))
    frags.append(text(gx2 + gw / 2, gy2 + 16, "45°", size=10, color=MUTED))
    frags.append(text(gx2 + gw - 25, gy2 + 16, "85°", size=10, color=MUTED))

    frags.append(text(gx2 - 8, gy2 - 25, "32", size=10, color=MUTED, anchor="end"))
    frags.append(text(gx2 - 8, gy2 - 85, "42", size=10, color=MUTED, anchor="end"))
    frags.append(text(gx2 - 8, gy2 - 145, "52", size=10, color=MUTED, anchor="end"))
    frags.append(line(gx2, gy2 - 85, gx2 + gw, gy2 - 85, color="#e2e8f0", sw=1.0, dash="2,2"))

    # Лінія супутникового спуфера
    spoof_line_y = gy2 - (51.5 - 28.0) * (gh / 26.0)
    frags.append(line(gx2 + 10, spoof_line_y, gx2 + gw - 15, spoof_line_y, color=POS, sw=2.2))
    frags.append(text(gx2 + gw / 2, spoof_line_y - 12, "Спуфер: 51.5 дБ-Гц (єдина антена SDR)", size=10, bold=True, color=POS))

    sat_spoof = [
        (25, 51.2, "PRN03"),
        (65, 51.8, "PRN14"),
        (110, 51.4, "PRN08"),
        (160, 51.6, "PRN21"),
        (215, 51.5, "PRN10"),
        (270, 51.3, "PRN27")
    ]
    for x_offset, cn0_val, label in sat_spoof:
        px = gx2 + x_offset
        py = gy2 - (cn0_val - 28.0) * (gh / 26.0)
        frags.append(circle(px, py, 4.5, fill=POS, stroke="#ffffff", sw=1.5))
        frags.append(text(px, py + 14, label, size=9, bold=True, color=POS))

    frags.append(text(cx2 + w_p / 2, y_p + h_p - 12, "Аномалія: дисперсія σ²(C/N0) < 0.4 при низьких супутниках", size=10, bold=True, color=POS))

    return render(os.path.join(OUT, "cn0-elevation-profile.svg"), W, H, *frags)


def fig_imu_doppler_crosscheck():
    """Геометрична сутність перехресної перевірки Доплера з інерціальним блоком (IMU)."""
    W, H = 840, 360
    frags = []

    frags.append(text(W / 2, 28, "Перехресна перевірка швидкості: Доплерівський зсув GNSS проти бортового ІВБ", size=16, bold=True))

    # Ліва частина: Дрон у просторі з векторами
    cx_drone, cy_drone = 260, 210
    frags.append(rect(20, 55, 480, 280, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(260, 80, "Проекція кінематичного прискорення та швидкості на LOS", size=13, bold=True, color=INK))

    # Корпус дрона (схематично квадрокоптер)
    frags.append(line(cx_drone - 40, cy_drone, cx_drone - 16, cy_drone, color=LINE, sw=3.0))
    frags.append(line(cx_drone + 16, cy_drone, cx_drone + 40, cy_drone, color=LINE, sw=3.0))
    frags.append(line(cx_drone, cy_drone - 30, cx_drone, cy_drone - 16, color=LINE, sw=3.0))
    frags.append(line(cx_drone, cy_drone + 16, cx_drone, cy_drone + 30, color=LINE, sw=3.0))
    frags.append(circle(cx_drone - 40, cy_drone, 10, fill="#cbd5e1", stroke=LINE, sw=1.5))
    frags.append(circle(cx_drone + 40, cy_drone, 10, fill="#cbd5e1", stroke=LINE, sw=1.5))
    frags.append(circle(cx_drone, cy_drone - 30, 10, fill="#cbd5e1", stroke=LINE, sw=1.5))
    frags.append(circle(cx_drone, cy_drone + 30, 10, fill="#cbd5e1", stroke=LINE, sw=1.5))
    frags.append(circle(cx_drone, cy_drone, 15, fill="#ffffff", stroke=POS, sw=2.0))
    frags.append(text(cx_drone, cy_drone + 4, "ІВБ", size=10, bold=True, color=POS))

    # Вектор фізичної швидкості від IMU
    frags.append(arrow(cx_drone + 15, cy_drone - 10, cx_drone + 75, cy_drone - 40, color=POS, sw=2.5))
    frags.append(text(cx_drone + 95, cy_drone - 48, "v_imu (швидкість)", size=10, bold=True, color=POS))

    # Супутники на небі
    sats = [
        (80, 115, "Супутник 1", "e₁"),
        (260, 105, "Супутник 2", "e₂"),
        (430, 125, "Супутник 3", "e₃")
    ]
    for sx, sy, sname, e_vec in sats:
        frags.append(rect(sx - 25, sy - 12, 50, 24, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=4))
        frags.append(text(sx, sy + 4, sname, size=9.5, bold=True, color=NEG))
        # Промінь видимості LOS
        frags.append(line(cx_drone, cy_drone, sx, sy, color="#94a3b8", sw=1.2, dash="4,3"))
        # Вектор прямої видимості e_i
        vx = (sx - cx_drone)
        vy = (sy - cy_drone)
        dist = math.hypot(vx, vy)
        ex = cx_drone + (vx / dist) * 50
        ey = cy_drone + (vy / dist) * 50
        frags.append(arrow(cx_drone, cy_drone, ex, ey, color=NEG, sw=1.8))
        frags.append(text(ex + 10, ey + 4, e_vec, size=10, bold=True, color=NEG))

    frags.append(fitbox(30, 280, 460, 44, "Доплерівська швидкість GNSS: ρ̇_i = −λ · f_d_i = (v_sat − v_drone) · e_i + c·ḋt\nНев'язка проекції IMU: r_doppler_i = ρ̇_i − (v_sat · e_i − v_imu · e_i + c·ḋt)", size=10, fill="#ffffff", stroke="#cbd5e1"))

    # Права частина: Порівняння сигналів при маневрі
    cx_r = 520
    w_r = 300
    frags.append(rect(cx_r, 55, w_r, 280, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(cx_r + w_r / 2, 80, "Поведінка під час маневру", size=13, bold=True, color=INK))

    frags.append(fitbox(cx_r + 15, 105, w_r - 30, 80, "Автентичний політ:\nКожен ривок або крен дрона миттєво\nвідображається як в акселерометрі ІВБ,\nтак і в доплерівських зсувах усіх супутників.\nНев'язка r_doppler ≈ 0.", size=10, fill="#ffffff", stroke=FIELD))

    frags.append(fitbox(cx_r + 15, 200, w_r - 30, 115, "Атака підміни (Spoofing):\nНаземний спуфер транслює фіктивну\nтраєкторію або статичну точку. При маневрі\nдрона інерційні сили реєструються ІВБ,\nале відсутні у підробленому Доплері.\nНев'язка |r_doppler| > 1.5 м/с → ТРИВОГА!", size=10, fill="#ffffff", stroke=POS))

    return render(os.path.join(OUT, "imu-doppler-crosscheck.svg"), W, H, *frags)


def fig_multi_layer_anti_spoof_pipeline():
    """Багаторівнева конвеєрна архітектура виявлення спуфінгу."""
    W, H = 840, 360
    frags = []

    frags.append(text(W / 2, 26, "Багаторівневий контур виявлення підміни GNSS на борту БПЛА", size=16, bold=True))

    # Вхідні дані (ліворуч)
    in_w = 170
    frags.append(fitbox(20, 55, in_w, 65, "Сирі вимірювання GNSS\n(UBX-RAWX/SFRBX)\nC/N0, AGC, Доплер, L1/L5", size=10, bold=True, fill="#eaf0fd", stroke=NEG))
    frags.append(fitbox(20, 140, in_w, 65, "Інерціальний блок (ІВБ)\n(Акселерометр + Гіроскоп)\nШвидкість v_imu, кути R", size=10, bold=True, fill="#fdecea", stroke=POS))
    frags.append(fitbox(20, 225, in_w, 65, "Багатосузірне PVT\nGPS, Galileo, BeiDou\nНезалежні розв'язки", size=10, bold=True, fill="#eafaf1", stroke=FIELD))

    # Центральні аналітичні модулі (4 перевірки)
    c_x = 225
    c_w = 340
    checks = [
        (55, "1. РФ та енергетичний профіль", "Перевірка стрибка AGC, однорідності C/N0", NEG),
        (125, "2. Доплерівсько-інерціальний тест", "Нев'язка |ρ̇_i − (v_sat − v_imu)·e_i| < ε_dopp", POS),
        (195, "3. Статистичний контроль цілісності RAIM", "Вектор нев'язок p = S·y, тест хі-квадрат SSE", "#b7791f"),
        (265, "4. Мультисистемна та міжчастотна дельта", "GPS vs Galileo vs BeiDou, іоносферна дисперсія", FIELD)
    ]

    for y_pos, header, desc, col in checks:
        frags.append(rect(c_x, y_pos, c_w, 55, fill="#ffffff", stroke=col, sw=1.4, rx=6))
        frags.append(text(c_x + 15, y_pos + 20, header, size=11, bold=True, color=col, anchor="start"))
        frags.append(text(c_x + 15, y_pos + 40, desc, size=9.5, color=MUTED, anchor="start"))

    # Стрілки від входів до блоків
    frags.append(arrow(190, 87, c_x - 5, 82, color="#64748b", sw=1.4))
    frags.append(arrow(190, 87, c_x - 5, 222, color="#64748b", sw=1.4))
    frags.append(arrow(190, 172, c_x - 5, 152, color="#64748b", sw=1.4))
    frags.append(arrow(190, 257, c_x - 5, 292, color="#64748b", sw=1.4))

    # Блок об'єднання метрик та автомат станів (праворуч)
    r_x = 600
    r_w = 220
    frags.append(rect(r_x, 55, r_w, 140, fill="#f8fafc", stroke="#94a3b8", sw=1.4, rx=8))
    frags.append(text(r_x + r_w / 2, 78, "Фільтр довіри (Trust Score)", size=12, bold=True, color=INK))
    frags.append(text(r_x + r_w / 2, 98, "Вагова сума індикаторів завад:", size=9.5, color=MUTED))
    frags.append(text(r_x + r_w / 2, 118, "T = w₁·M_rf + w₂·M_dop + w₃·M_raim", size=9.5, bold=True, color=INK))
    frags.append(text(r_x + r_w / 2, 138, "Інтегрування ризику в часі", size=9.5, color=MUTED))
    frags.append(text(r_x + r_w / 2, 158, "Захист від хибних спрацювань", size=9.5, color=MUTED))
    frags.append(text(r_x + r_w / 2, 178, "Гістерезисний поріг тривоги", size=9.5, bold=True, color=POS))

    # Стрілки до блоку метрик
    for y_pos in [82, 152, 222, 292]:
        frags.append(arrow(c_x + c_w + 3, y_pos, r_x - 5, 125, color="#64748b", sw=1.2))

    # Автомат станів автопілота (внизу праворуч)
    frags.append(rect(r_x, 210, r_w, 125, fill="#ffffff", stroke=POS, sw=1.5, rx=8))
    frags.append(text(r_x + r_w / 2, 230, "Рішення автопілота (Failsafe)", size=11, bold=True, color=POS))

    frags.append(rect(r_x + 15, 245, r_w - 30, 24, fill="#eafaf1", stroke=FIELD, sw=1.0, rx=4))
    frags.append(text(r_x + r_w / 2, 261, "0: CLEAN (GNSS + IMU EKF)", size=9.5, bold=True, color=FIELD))

    frags.append(rect(r_x + 15, 274, r_w - 30, 24, fill="#fef9e7", stroke="#b7791f", sw=1.0, rx=4))
    frags.append(text(r_x + r_w / 2, 290, "1: DEGRADED (Ізоляція супутника)", size=9.5, bold=True, color="#b7791f"))

    frags.append(rect(r_x + 15, 303, r_w - 30, 24, fill="#fdecea", stroke=POS, sw=1.0, rx=4))
    frags.append(text(r_x + r_w / 2, 319, "2: SPOOFED (Dead Reckoning)", size=9.5, bold=True, color=POS))

    frags.append(arrow(r_x + r_w / 2, 195, r_x + r_w / 2, 207, color=POS, sw=1.8))

    return render(os.path.join(OUT, "multi-layer-anti-spoof-pipeline.svg"), W, H, *frags)


def main():
    fig_takeover_spoofing_stages()
    fig_cn0_elevation_profile()
    fig_imu_doppler_crosscheck()
    fig_multi_layer_anti_spoof_pipeline()
    print("All figures generated successfully.")


if __name__ == "__main__":
    main()
