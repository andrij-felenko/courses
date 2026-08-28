# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Порівняння типів кріплення корисного навантаження
# ════════════════════════════════════════════════════════════════════════════
def fig_mounting_types_comparison():
    W, H = 840, 360
    pw = 250
    gap = 20
    x_start = 25
    body = ""

    panels = [
        ("Жорстке (Hard Mount)", [
            ("Монтаж безпосередньо на силову раму", MUTED),
            ("Абсолютна кутова точність (<0.001°)", POS),
            ("100% вібрацій іде в сенсор", INK),
            ("Немає динамічного люфту при маневрах", MUTED),
            ("Для LiDAR, картографії, геодезії", FIELD),
        ]),
        ("М'яке (Soft / Damper)", [
            ("Силіконові демпфери та гелеві втулки", MUTED),
            ("Фільтр вібрацій на частотах f > √2·f₀", POS),
            ("Усуває ефект желе (Rolling Shutter)", INK),
            ("Кутовий дрейф і зміщення центру мас", MUTED),
            ("Для фото/відео камер та гімбалів", FIELD),
        ]),
        ("Знімне (Quick-Release)", [
            ("Ластівчин хвіст або байонетний замок", MUTED),
            ("Заміна модуля за 5 с без інструментів", POS),
            ("Інтегровані Pogo Pins (живлення + шини)", INK),
            ("Вимога до зусилля притиску й контактів", MUTED),
            ("Для модульних розвідувальних дронів", FIELD),
        ]),
    ]

    for i, (title_text, items) in enumerate(panels):
        px = x_start + i * (pw + gap)
        py = 55
        ph = 280

        # Фон картки
        body += rect(px, py, pw, ph, fill="#fafbfc", stroke="#d1d5db", sw=1.5, rx=8)

        # Заголовок картки
        body += fitbox(px + 10, py + 12, pw - 20, 32, title_text, size=13, bold=True, fill="#eef2f6", stroke="#cbd5e1")

        # Елементи списку
        for j, (txt, col) in enumerate(items):
            iy = py + 62 + j * 42
            body += circle(px + 20, iy + 7, 3.5, fill=col, stroke=col)
            body += fitbox(px + 30, iy - 6, pw - 42, 28, txt, size=11, color=col, bold=(col == POS or col == FIELD), fill="none", stroke="none")

    render(os.path.join(OUT, "mounting-types-comparison.svg"), W, H, body,
           title="Порівняння концепцій кріплення корисного навантаження на БПЛА")


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Крива передавання вібрації (Transmissibility Curve)
# ════════════════════════════════════════════════════════════════════════════
def fig_vibration_transmissibility_curve():
    W, H = 840, 420
    body = ""

    x0, y0 = 100, 340
    gw, gh = 680, 270

    # Фонова розмітка зон
    body += rect(x0, y0 - gh, 170, gh, fill="#f8fafc", stroke="none")
    body += rect(x0 + 170, y0 - gh, 70, gh, fill="#fef2f2", stroke="none")
    body += rect(x0 + 240, y0 - gh, 440, gh, fill="#f0fdf4", stroke="none")

    # Горизонтальна лінія TR = 1.0
    y_tr1 = y0 - int(gh * (1.0 / 4.0))
    body += line(x0, y_tr1, x0 + gw, y_tr1, color="#94a3b8", sw=1.5, dash="4 4")
    body += text(x0 + gw - 8, y_tr1 - 6, "T_R = 1.0 (Без зміни амплітуди)", size=11, color="#64748b", anchor="end")

    # Вертикальна лінія r = sqrt(2) = 1.414
    x_sqrt2 = x0 + int(gw * (1.414 / 4.0))
    body += line(x_sqrt2, y0, x_sqrt2, y0 - gh, color="#16a34a", sw=1.5, dash="3 3")
    body += text(x_sqrt2, y0 + 36, "r = √2 ≈ 1.414", size=11, color="#16a34a", anchor="middle", bold=True)
    body += text(x_sqrt2, y0 + 50, "Межа ізоляції", size=10, color="#16a34a", anchor="middle")

    # Підписи зон угорі
    body += fitbox(x0 + 10, y0 - gh + 10, 150, 24, "Статична передача", size=11, color="#64748b", bold=True, fill="#ffffff", stroke="#cbd5e1")
    body += fitbox(x0 + 172, y0 - gh + 10, 66, 24, "Резонанс", size=11, color=POS, bold=True, fill="#ffffff", stroke="#fca5a5")
    body += fitbox(x0 + 330, y0 - gh + 10, 240, 24, "Зона віброізоляції (T_R < 1)", size=11, color="#15803d", bold=True, fill="#ffffff", stroke="#86efac")

    # Координатна сітка
    for r_val in [1.0, 2.0, 3.0, 4.0]:
        rx = x0 + int(gw * (r_val / 4.0))
        body += line(rx, y0, rx, y0 - gh, color="#e2e8f0", sw=1, dash="2 2")
        body += text(rx, y0 + 18, "%.1f" % r_val, size=11, color=MUTED, anchor="middle")

    for tr_val in [0.0, 1.0, 2.0, 3.0, 4.0]:
        ty = y0 - int(gh * (tr_val / 4.0))
        body += line(x0, ty, x0 + gw, ty, color="#e2e8f0", sw=1, dash="2 2")
        body += text(x0 - 10, ty + 4, "%.1f" % tr_val, size=11, color=MUTED, anchor="end")

    # Осі
    body += line(x0, y0, x0 + gw + 15, y0, color=LINE, sw=2)
    body += line(x0, y0, x0, y0 - gh - 15, color=LINE, sw=2)
    body += text(x0 + gw + 15, y0 + 18, "Відношення частот r = f / f₀", size=11, color=INK, anchor="end", bold=True)
    body += text(x0 - 15, y0 - gh - 18, "Коефіцієнт передачі T_R", size=11, color=INK, anchor="start", bold=True)

    # Функція TR(r, zeta)
    def calc_tr(r, zeta):
        num = 1.0 + (2.0 * zeta * r)**2
        den = (1.0 - r**2)**2 + (2.0 * zeta * r)**2
        return math.sqrt(num / den)

    # Малювання кривих
    zetas = [
        (0.12, POS, "ζ = 0.12 (Низьке демпфування: високий резонансний пік Q≈4.2)"),
        (0.28, NEG, "ζ = 0.28 (Силіконовий демпфер: згладжений пік, плавний спад)"),
    ]

    for zeta, col, label_text in zetas:
        pts = []
        for step in range(250):
            r = 0.01 + step * (4.0 / 249.0)
            tr = calc_tr(r, zeta)
            tr_clamped = min(tr, 4.2)
            px = x0 + (r / 4.0) * gw
            py = y0 - (tr_clamped / 4.0) * gh
            pts.append((px, py))

        path_d = "M " + " ".join(["%.1f,%.1f" % (p[0], p[1]) for p in pts])
        body += '<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_d, col)

    # Легенда
    body += rect(x0 + 350, y0 - 140, 310, 58, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6)
    body += line(x0 + 360, y0 - 122, x0 + 390, y0 - 122, color=POS, sw=2.5)
    body += text(x0 + 398, y0 - 118, "ζ = 0.12 (Гума: гострий резонанс)", size=10, color=INK, anchor="start")
    body += line(x0 + 360, y0 - 96, x0 + 390, y0 - 96, color=NEG, sw=2.5)
    body += text(x0 + 398, y0 - 92, "ζ = 0.28 (Силікон: м'який перехід)", size=10, color=INK, anchor="start")

    render(os.path.join(OUT, "vibration-transmissibility-curve.svg"), W, H, body,
           title="Передаваність вібрації T_R: залежність від частоти та демпфування")


# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Швидкознімний механізм: Ластівчин хвіст та Pogo Pins
# ════════════════════════════════════════════════════════════════════════════
def fig_quick_release_dovetail_pogo():
    W, H = 840, 380
    body = ""

    # Ліва панель: Механічний профіль "ластівчин хвіст" (Dovetail)
    lx, ly = 40, 60
    lw, lh = 360, 290
    body += rect(lx, ly, lw, lh, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8)
    body += text(lx + lw/2, ly + 25, "Механічний замок «Ластівчин хвіст»", size=13, color=INK, anchor="middle", bold=True)

    # Базова пластина (на рамі дрона)
    body += rect(lx + 40, ly + 60, lw - 80, 50, fill="#e2e8f0", stroke="#64748b", sw=1.8, rx=4)
    body += text(lx + lw/2, ly + 90, "Базова напрямна рами (Al 6061-T6)", size=11, color=INK, anchor="middle", bold=True)

    # Профіль клину "ластівчин хвіст"
    body += '<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>' % (
        lx + 60, ly + 140,
        lx + lw - 60, ly + 140,
        lx + lw - 35, ly + 195,
        lx + 35, ly + 195
    )
    body += text(lx + lw/2, ly + 172, "Слайдер навантаження (кут 60°)", size=11, color="#1e40af", anchor="middle", bold=True)

    # Ексцентриковий затискач
    body += circle(lx + lw - 25, ly + 140, 14, fill="#fee2e2", stroke=POS, sw=2)
    body += text(lx + lw - 25, ly + 144, "Lock", size=9, color=POS, anchor="middle", bold=True)
    body += line(lx + lw - 25, ly + 126, lx + lw - 5, ly + 105, color=POS, sw=2)
    body += text(lx + lw - 5, ly + 98, "Важіль фіксації", size=10, color=POS, anchor="middle")

    # Позиціонуючі конічні штифти
    body += rect(lx + 70, ly + 120, 16, 20, fill="#64748b", stroke="#334155", sw=1.2)
    body += rect(lx + lw - 86, ly + 120, 16, 20, fill="#64748b", stroke="#334155", sw=1.2)
    body += text(lx + lw/2, ly + 235, "Конічні напрямні штифти (повторюваність <0.05 мм)", size=10, color=MUTED, anchor="middle")
    body += text(lx + lw/2, ly + 258, "Витримує 10–15g динамічних перевантажень", size=10, color=FIELD, anchor="middle", bold=True)

    # Права панель: Інтерфейс контактних пого-пінів (Pogo Pins)
    rx, ry = 440, 60
    rw, rh = 360, 290
    body += rect(rx, ry, rw, rh, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8)
    body += text(rx + rw/2, ry + 25, "Контактний блок Pogo Pins", size=13, color=INK, anchor="middle", bold=True)

    # Дронова сторона: Контактні площадки (Gold target pads)
    body += rect(rx + 35, ry + 60, rw - 70, 40, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4)
    body += text(rx + rw/2, ry + 84, "Позолочені площадки (Au 30 μin)", size=11, color="#92400e", anchor="middle", bold=True)

    # Ряд пінів
    pin_labels = ["V_BAT", "GND", "CAN_H", "CAN_L", "ETH_TX", "ETH_RX"]
    for p_idx, p_name in enumerate(pin_labels):
        px = rx + 55 + p_idx * 44
        # Пружинний штифт
        body += line(px, ry + 105, px, ry + 145, color="#d97706", sw=3)
        body += rect(px - 6, ry + 145, 12, 25, fill="#cbd5e1", stroke="#475569", sw=1.2, rx=2)
        body += circle(px, ry + 103, 3, fill="#f59e0b", stroke="#b45309", sw=1)
        body += text(px, ry + 186, p_name, size=9, color=INK, anchor="middle", bold=True)

    # Характеристики з'єднання
    body += line(rx + 30, ry + 205, rx + rw - 30, ry + 205, color="#e2e8f0", sw=1)
    body += text(rx + rw/2, ry + 225, "Сила притиску: 0.8–1.2 Н на кожен пін", size=10, color=MUTED, anchor="middle")
    body += text(rx + rw/2, ry + 245, "Контактний опір R_cont < 25 мОм", size=10, color=MUTED, anchor="middle")
    body += text(rx + rw/2, ry + 265, "Силіконовий O-ring захищає від пилу та вологи (IP65)", size=10, color=FIELD, anchor="middle", bold=True)

    render(os.path.join(OUT, "quick-release-dovetail-pogo.svg"), W, H, body,
           title="Швидкознімне кріплення: механічний клин та інтерфейс Pogo Pins")


# ════════════════════════════════════════════════════════════════════════════
# Фігура 4 — Тепловідведення від корисного навантаження в набігаючий потік
# ════════════════════════════════════════════════════════════════════════════
def fig_thermal_airflow_stack():
    W, H = 840, 390
    body = ""

    # Ліва частина: Схема шарів тепловідведення (Thermal Stack)
    sx, sy = 40, 60
    sw_panel, sh_panel = 420, 300

    body += rect(sx, sy, sw_panel, sh_panel, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8)
    body += text(sx + sw_panel/2, sy + 25, "Тепловий ланцюг: від кристала до повітря", size=13, color=INK, anchor="middle", bold=True)

    # 1. AI SoC / Compute Module
    body += rect(sx + 50, sy + 55, 320, 42, fill="#fee2e2", stroke=POS, sw=1.8, rx=4)
    body += text(sx + 210, sy + 75, "AI SoC / Джерело тепла (15–30 Вт, T_j max = 105°C)", size=11, color=POS, anchor="middle", bold=True)
    body += text(sx + 210, sy + 90, "Кремнієвий кристал (R_θjc ≈ 0.8 °C/Вт)", size=9, color="#991b1b", anchor="middle")

    # 2. Термоінтерфейс (TIM)
    body += rect(sx + 50, sy + 105, 320, 24, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=3)
    body += text(sx + 210, sy + 121, "Термопрокладка / TIM (k = 6.0 Вт/(м·К), R_θcs ≈ 0.4 °C/Вт)", size=10, color="#92400e", anchor="middle", bold=True)

    # 3. Алюмінієвий радіатор із ребрами
    body += rect(sx + 50, sy + 137, 320, 35, fill="#e2e8f0", stroke="#475569", sw=1.8, rx=4)
    body += text(sx + 210, sy + 158, "Підошва радіатора (Al 6061, товщина 4.0 мм)", size=10, color="#1e293b", anchor="middle", bold=True)

    # Ребра радіатора
    for fin_i in range(11):
        fx = sx + 60 + fin_i * 28
        body += rect(fx, sy + 175, 14, 45, fill="#cbd5e1", stroke="#475569", sw=1.2, rx=2)

    body += text(sx + 210, sy + 240, "Поздовжні аеродинамічні ребра (h = 15 мм, крок 4 мм)", size=10, color="#475569", anchor="middle")

    # Стрілки теплового потоку
    body += arrow(sx + 210, sy + 252, sx + 210, sy + 282, color=POS, sw=2.5)
    body += text(sx + 210, sy + 295, "Тепловий потік Q = P_diss = 25 Вт", size=11, color=POS, anchor="middle", bold=True)

    # Права частина: Порівняння режимів конвекції (Hover vs Cruise)
    rx, ry = 480, 60
    rw_panel, rh_panel = 320, 300
    body += rect(rx, ry, rw_panel, rh_panel, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8)
    body += text(rx + rw_panel/2, ry + 25, "Режими охолодження в польоті", size=13, color=INK, anchor="middle", bold=True)

    # Режим 1: Висіння (Downwash)
    body += rect(rx + 20, ry + 55, rw_panel - 40, 95, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=6)
    body += text(rx + rw_panel/2, ry + 75, "Режим висіння (Hover / Downwash)", size=11, color=INK, anchor="middle", bold=True)
    body += text(rx + rw_panel/2, ry + 95, "Швидкість потоку v ≈ 5–10 м/с", size=10, color=MUTED, anchor="middle")
    body += text(rx + rw_panel/2, ry + 113, "Коефіцієнт тепловіддачі h ≈ 35 Вт/(м²·К)", size=10, color=MUTED, anchor="middle")
    body += text(rx + rw_panel/2, ry + 132, "R_θsa ≈ 1.8 °C/Вт → ΔT_sa ≈ 45 °C", size=10, color=POS, anchor="middle", bold=True)

    # Режим 2: Горизонтальний політ (Cruise)
    body += rect(rx + 20, ry + 165, rw_panel - 40, 95, fill="#f0fdf4", stroke="#86efac", sw=1.2, rx=6)
    body += text(rx + rw_panel/2, ry + 185, "Крейсерський політ (Cruise Airflow)", size=11, color="#166534", anchor="middle", bold=True)
    body += text(rx + rw_panel/2, ry + 205, "Швидкість набігання v ≈ 18–25 м/с", size=10, color=MUTED, anchor="middle")
    body += text(rx + rw_panel/2, ry + 223, "Коефіцієнт тепловіддачі h ≈ 80 Вт/(м²·К)", size=10, color=MUTED, anchor="middle")
    body += text(rx + rw_panel/2, ry + 242, "R_θsa ≈ 0.8 °C/Вт → ΔT_sa ≈ 20 °C", size=10, color=FIELD, anchor="middle", bold=True)

    body += text(rx + rw_panel/2, ry + 282, "Загальний перегрів: ΔT_tot = P·(R_jc + R_cs + R_sa)", size=10, color=INK, anchor="middle", bold=True)

    render(os.path.join(OUT, "thermal-airflow-stack.svg"), W, H, body,
           title="Тепловідведення від AI-процесора: тепловий ланцюг та обдув радіатора")


# ════════════════════════════════════════════════════════════════════════════
# Фігура 5 — Механіка різьбового кріплення та захист від вібрації
# ════════════════════════════════════════════════════════════════════════════
def fig_fastener_joint_mechanics():
    W, H = 840, 370
    body = ""

    # Лівий блок: Правильний монтаж у композит та полімер
    lx, ly = 40, 55
    lw, lh = 360, 290
    body += rect(lx, ly, lw, lh, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8)
    body += text(lx + lw/2, ly + 25, "Вузол з'єднання: Карбон + Латунна втулка", size=13, color=INK, anchor="middle", bold=True)

    # Карбонова пластина (з отвором посередині)
    body += rect(lx + 35, ly + 65, lw/2 - 65, 36, fill="#334155", stroke="#0f172a", sw=1.8, rx=2)
    body += rect(lx + lw/2 + 30, ly + 65, lw/2 - 65, 36, fill="#334155", stroke="#0f172a", sw=1.8, rx=2)
    body += text(lx + 85, ly + 87, "Карбон 3K", size=10, color="#f8fafc", anchor="middle", bold=True)
    body += text(lx + lw - 85, ly + 87, "Товщина 2.5 мм", size=10, color="#f8fafc", anchor="middle")

    # Латунна нарізна втулка (Threaded Brass Insert)
    body += rect(lx + lw/2 - 28, ly + 60, 56, 46, fill="#fbbf24", stroke="#b45309", sw=1.5, rx=3)
    body += text(lx + lw/2, ly + 87, "Латунь M3", size=10, color="#78350f", anchor="middle", bold=True)

    # Головка сталевого болта M3
    body += rect(lx + lw/2 - 18, ly + 36, 36, 14, fill="#475569", stroke="#0f172a", sw=1.5, rx=2)
    body += text(lx + lw/2, ly + 28, "Болт M3 (Клас 10.9)", size=9, color=INK, anchor="middle", bold=True)

    # Синій анаеробний фіксатор на різьбі
    body += rect(lx + lw/2 - 16, ly + 115, 32, 22, fill="#93c5fd", stroke="#2563eb", sw=1.2, rx=2)
    body += text(lx + lw/2, ly + 130, "Loctite 243", size=9, color="#1d4ed8", anchor="middle", bold=True)

    # Пояснення
    body += text(lx + lw/2, ly + 175, "1. Насічка втулки усуває прокручування в полімері", size=10, color=MUTED, anchor="middle")
    body += text(lx + lw/2, ly + 195, "2. Відсутність прямого тиску на шари карбону (no delam)", size=10, color=MUTED, anchor="middle")
    body += text(lx + lw/2, ly + 215, "3. Момент затяжки M3: 0.9–1.2 Н·м (контроль динамометром)", size=10, color=MUTED, anchor="middle")
    body += text(lx + lw/2, ly + 245, "Анаеробний клей запобігає самовідкручуванню від вібрацій", size=10, color=FIELD, anchor="middle", bold=True)

    # Правий блок: Кабельний роз'єм та розвантаження натягу (Strain Relief)
    rx, ry = 440, 55
    rw, rh = 360, 290
    body += rect(rx, ry, rw, rh, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8)
    body += text(rx + rw/2, ry + 25, "Фіксація кабелів і розвантаження натягу", size=13, color=INK, anchor="middle", bold=True)

    # Роз'єм JST-GH із засувкою
    body += rect(rx + 65, ry + 50, 60, 30, fill="#f1f5f9", stroke="#334155", sw=1.5, rx=3)
    body += text(rx + 95, ry + 69, "JST-GH", size=9, color=INK, anchor="middle", bold=True)
    body += circle(rx + 118, ry + 58, 3.5, fill=POS, stroke=POS) # засувка

    # Плата PCB нижче роз'єму
    body += rect(rx + 35, ry + 88, 120, 20, fill="#15803d", stroke="#14532d", sw=1.5, rx=2)
    body += text(rx + 95, ry + 102, "PCB плата", size=10, color="#ffffff", anchor="middle", bold=True)

    # Кабельний джгут
    body += '<path d="M %d,%d C %d,%d %d,%d %d,%d" fill="none" stroke="#ea580c" stroke-width="4"/>' % (
        rx + 125, ry + 65,
        rx + 175, ry + 65,
        rx + 175, ry + 125,
        rx + 225, ry + 125
    )

    # Кабельний хомут / затискач (Strain relief clamp)
    body += rect(rx + 225, ry + 110, 45, 30, fill="#475569", stroke="#0f172a", sw=1.5, rx=3)
    body += text(rx + 247, ry + 128, "Clamp", size=9, color="#ffffff", anchor="middle", bold=True)
    body += text(rx + 247, ry + 155, "Затискач навантаження", size=9, color=INK, anchor="middle")

    # Пояснення
    body += line(rx + 30, ry + 175, rx + rw - 30, ry + 175, color="#e2e8f0", sw=1)
    body += text(rx + rw/2, ry + 195, "1. JST-GH: позитивний механічний замок від випадання", size=10, color=MUTED, anchor="middle")
    body += text(rx + rw/2, ry + 215, "2. Радіус вигину кабелю R_bend ≥ 5 · D_кабелю", size=10, color=MUTED, anchor="middle")
    body += text(rx + rw/2, ry + 235, "3. Віброізоляційна петля (service loop) перед роз'ємом", size=10, color=MUTED, anchor="middle")
    body += text(rx + rw/2, ry + 258, "Механічне розвантаження захищає паяні контакти від втоми", size=10, color=FIELD, anchor="middle", bold=True)

    render(os.path.join(OUT, "fastener-joint-mechanics.svg"), W, H, body,
           title="Механічна надійність: різьбові вузли та розвантаження кабельних ліній")


# ════════════════════════════════════════════════════════════════════════════
# Головний запуск
# ════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    fig_mounting_types_comparison()
    fig_vibration_transmissibility_curve()
    fig_quick_release_dovetail_pogo()
    fig_thermal_airflow_stack()
    fig_fastener_joint_mechanics()
    print("OK: All 5 figures successfully rendered to img/ directory.")
