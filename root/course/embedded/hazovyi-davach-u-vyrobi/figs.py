# -*- coding: utf-8 -*-
import sys, os

# 4 levels up to scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Colors
HEAT = POS        # Нагрівач / висока температура
COLD = NEG        # Холодне / опорні точки
ACCENT = "#7c3aed" # Оптичне випромінювання / NDIR
CHEM = FIELD      # Електрохімія / хемосорбція


# ── 1. sensor-types-comparison: Три фізичні принципи детекції ─────────────────
def fig_sensor_types_comparison():
    W, H = 880, 440
    p = []

    col_w = 260
    xs = [30, 310, 590]

    # Стовпчик 1: MOX
    x = xs[0]
    p.append(rect(x, 40, col_w, 380, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))
    b, _, _ = textbox(x + col_w / 2, 65, "MOX (Напівпровідник)", size=13, bold=True, fill="#fff", stroke=HEAT)
    p.append(b)
    
    p.append(rect(x + 15, 95, col_w - 30, 100, fill="#fff", stroke=MUTED, sw=1, rx=4))
    p.append(line(x + 35, 168, x + col_w - 35, 168, color=HEAT, sw=3))
    p.append(text(x + col_w / 2, 184, "Мікронагрівач (250–400 °C)", size=10, color=HEAT, bold=True))
    p.append(rect(x + 35, 108, col_w - 70, 42, fill="#fef3c7", stroke=LINE, sw=1))
    p.append(text(x + col_w / 2, 126, "Кристалічний SnO₂", size=10.5, bold=True))
    p.append(text(x + col_w / 2, 140, "Хемосорбований O⁻", size=9.5, color=MUTED))
    
    lines_mox = [
        "Газ: VOC, спирти, CO, H₂",
        "Механізм: окиснення газу",
        "на гарячій поверхні вивільняє",
        "електрони в зону провідності.",
        "Сигнал: опір плівки Rs падає.",
        "Плюси: дешеві, малі, довгий вік.",
        "Мінуси: жеруть струм, неселективні."
    ]
    p.append(fitbox(x + 15, 205, col_w - 30, 200, "\n".join(lines_mox), size=11, pad=8, fill="#fff", stroke=MUTED))

    # Стовпчик 2: Електрохімія
    x = xs[1]
    p.append(rect(x, 40, col_w, 380, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))
    b, _, _ = textbox(x + col_w / 2, 65, "Електрохімічна комірка", size=13, bold=True, fill="#fff", stroke=CHEM)
    p.append(b)
    
    p.append(rect(x + 15, 95, col_w - 30, 100, fill="#fff", stroke=MUTED, sw=1, rx=4))
    p.append(rect(x + 30, 105, 55, 18, fill="#d1fae5", stroke=CHEM, sw=1))
    p.append(text(x + 57, 118, "WE", size=10, bold=True, color=CHEM))
    p.append(rect(x + 102, 105, 55, 18, fill="#e0f2fe", stroke=NEG, sw=1))
    p.append(text(x + 129, 118, "RE", size=10, bold=True, color=NEG))
    p.append(rect(x + 175, 105, 55, 18, fill="#f3f4f6", stroke=LINE, sw=1))
    p.append(text(x + 202, 118, "CE", size=10, bold=True))
    p.append(rect(x + 30, 132, col_w - 60, 50, fill="#ecfdf5", stroke=CHEM, sw=1, rx=2))
    p.append(text(x + col_w / 2, 160, "Рідкий/гелевий електроліт", size=10.5, color=CHEM))

    lines_ec = [
        "Газ: CO, O₂, NO₂, H₂S, NH₃",
        "Механізм: окисно-відновна",
        "реакція на робочому електроді.",
        "Сигнал: струм Фарадея I ∝ ppm.",
        "Плюси: висока вибірковість,",
        "лінійність від 0, мікроампери.",
        "Мінуси: сохне електроліт (2–3 р)."
    ]
    p.append(fitbox(x + 15, 205, col_w - 30, 200, "\n".join(lines_ec), size=11, pad=8, fill="#fff", stroke=MUTED))

    # Стовпчик 3: NDIR
    x = xs[2]
    p.append(rect(x, 40, col_w, 380, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))
    b, _, _ = textbox(x + col_w / 2, 65, "Оптичний NDIR (CO₂)", size=13, bold=True, fill="#fff", stroke=ACCENT)
    p.append(b)

    p.append(rect(x + 15, 95, col_w - 30, 100, fill="#fff", stroke=MUTED, sw=1, rx=4))
    p.append(circle(x + 45, 145, 14, fill="#fef08a", stroke=HEAT, sw=1.5))
    p.append(text(x + 45, 149, "IR", size=10, bold=True, color=HEAT))
    p.append(arrow(x + 65, 145, x + 155, 145, color=ACCENT, sw=2))
    p.append(text(x + 110, 133, "λ = 4.26 мкм", size=9.5, color=ACCENT, bold=True))
    p.append(text(x + 110, 162, "Кювета з газом", size=9.5, color=MUTED))
    p.append(rect(x + 165, 128, 10, 34, fill=ACCENT, stroke=LINE, sw=1))
    p.append(rect(x + 182, 122, 34, 46, fill="#ede9fe", stroke=ACCENT, sw=1.5, rx=2))
    p.append(text(x + 199, 149, "Det", size=10, bold=True, color=ACCENT))

    lines_ndir = [
        "Газ: CO₂ (вуглекислий газ)",
        "Механізм: закон Бера-Ламберта,",
        "поглинання фотонів зв'язками C=O.",
        "Сигнал: падіння теплового потоку.",
        "Плюси: нульова крос-чутливість,",
        "не труїться силіконом, 10+ років.",
        "Мінуси: дорогий, більші габарити."
    ]
    p.append(fitbox(x + 15, 205, col_w - 30, 200, "\n".join(lines_ndir), size=11, pad=8, fill="#fff", stroke=MUTED))

    render(os.path.join(OUT, "sensor-types-comparison.svg"), W, H, *p,
           title="Порівняння фізичних принципів побудови газових давачів")


# ── 2. heater-preheat-phases: Фази прогріву та термостабілізації ──────────────
def fig_heater_preheat_phases():
    W, H = 860, 400
    p = []

    x0, y0 = 100, 270
    x_end = 780
    p.append(arrow(x0, y0, x_end + 30, y0, color=INK, sw=1.8))
    p.append(text(x_end + 35, y0 + 18, "Час t", size=11, bold=True))

    p.append(arrow(x0, y0, x0, 50, color=INK, sw=1.8))
    p.append(text(x0 - 10, 55, "Rs (опір)", size=11, bold=True, anchor="end"))

    x_b = 240
    x_w = 460

    p.append(line(x_b, 60, x_b, y0, color=MUTED, sw=1.2, dash="4 4"))
    p.append(line(x_w, 60, x_w, y0, color=MUTED, sw=1.2, dash="4 4"))

    b1, _, _ = textbox(x0 + (x_b - x0) / 2, 75, "Фаза 1: Burn-In (Кондиціонування)\n24–48 годин для нового чипа", size=10, fill="#fef2f2", stroke=POS)
    p.append(b1)

    b2, _, _ = textbox(x_b + (x_w - x_b) / 2, 75, "Фаза 2: Прогрів (Warm-up)\n10–60 с після подачі Vcc", size=10, fill="#fffbeb", stroke="#d97706")
    p.append(b2)

    b3, _, _ = textbox(x_w + (x_end - x_w) / 2, 75, "Фаза 3: Робочий режим\nТермодинамічна рівновага", size=10, fill="#f0fdf4", stroke=FIELD)
    p.append(b3)

    path_burn = f"M {x0} 90 Q {x0 + 40} 240 {x0 + 80} 130 T {x0 + 140} 190 Q {x_b} 175 {x_b} 170"
    p.append(f'<path d="{path_burn}" fill="none" stroke="{POS}" stroke-width="2.2"/>')

    path_warm = f"M {x_b} 250 C {x_b + 50} 80, {x_b + 120} 165, {x_w} 165"
    p.append(f'<path d="{path_warm}" fill="none" stroke="#d97706" stroke-width="2.2"/>')

    path_run = f"M {x_w} 165 L {x_w + 50} 165 Q {x_w + 90} 220 {x_w + 130} 165 L {x_w + 190} 165 Q {x_w + 240} 240 {x_end} 165"
    p.append(f'<path d="{path_run}" fill="none" stroke="{FIELD}" stroke-width="2.4"/>')

    p.append(text(x0 + 70, 225, "Випаровування флюсу", size=9.5, color=POS))
    p.append(text(x_b + 100, 225, "Тепловий стрибок", size=9.5, color="#d97706"))
    p.append(text(x_w + 90, 245, "Сплеск газу (VOC)", size=10, color=FIELD, bold=True))

    p.append(rect(x0, 290, x_b - x0 - 5, 55, fill="#fee2e2", stroke=POS, sw=1, rx=4))
    p.append(text(x0 + (x_b - x0) / 2, 312, "СТАН: UNCALIBRATED", size=10, bold=True, color=POS))
    p.append(text(x0 + (x_b - x0) / 2, 330, "Видача даних заборонена", size=9.5, color=MUTED))

    p.append(rect(x_b + 5, 290, x_w - x_b - 10, 55, fill="#fef3c7", stroke="#d97706", sw=1, rx=4))
    p.append(text(x_b + (x_w - x_b) / 2, 312, "СТАН: WARMUP", size=10, bold=True, color="#d97706"))
    p.append(text(x_b + (x_w - x_b) / 2, 330, "Таймер блокує інтерфейс", size=9.5, color=MUTED))

    p.append(rect(x_w + 5, 290, x_end - x_w - 5, 55, fill="#dcfce7", stroke=FIELD, sw=1, rx=4))
    p.append(text(x_w + (x_end - x_w) / 2, 312, "СТАН: READY_VALID", size=10, bold=True, color=FIELD))
    p.append(text(x_w + (x_end - x_w) / 2, 330, "Валідні виміри з корекцією T/RH", size=9.5, color=MUTED))

    render(os.path.join(OUT, "heater-preheat-phases.svg"), W, H, *p,
           title="Термодинамічні фази прогріву газового сенсора та реакція драйвера")


# ── 3. rh-temp-compensation-surface: Спотворення вологою та компенсація ───────
def fig_rh_temp_compensation():
    W, H = 860, 400
    p = []

    ox, oy = 90, 310
    gw, gh = 280, 220
    p.append(arrow(ox, oy, ox + gw + 25, oy, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox, oy - gh - 20, color=INK, sw=1.6))
    p.append(text(ox + gw + 25, oy + 20, "Абсолютна вологість AH (г/м³)", size=10, bold=True))
    p.append(text(ox - 10, oy - gh - 15, "Rs / R₀ (відносний опір)", size=10, bold=True, anchor="end"))

    # T = 15 C
    p.append(line(ox + 20, oy - 200, ox + gw - 20, oy - 120, color=COLD, sw=2))
    p.append(text(ox + gw - 10, oy - 120, "15 °C", size=10, color=COLD, bold=True))
    # T = 25 C
    p.append(line(ox + 20, oy - 170, ox + gw - 20, oy - 80, color=FIELD, sw=2.2))
    p.append(text(ox + gw - 10, oy - 80, "25 °C", size=10, color=FIELD, bold=True))
    # T = 35 C
    p.append(line(ox + 20, oy - 140, ox + gw - 20, oy - 45, color=HEAT, sw=2))
    p.append(text(ox + gw - 10, oy - 45, "35 °C", size=10, color=HEAT, bold=True))

    p.append(text(ox + 120, oy - 225, "Паразитна чутливість до води: H₂O", size=10, bold=True))
    p.append(text(ox + 120, oy - 210, "витісняє O⁻ і знижує Rs (хибний газ)", size=9.5, color=MUTED))

    cx0 = 460
    p.append(rect(cx0, 60, 360, 310, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    b_h, _, _ = textbox(cx0 + 180, 85, "Тракт цифрової компенсації", size=12, bold=True, fill="#fff", stroke=ACCENT)
    p.append(b_h)

    b_in1 = fitbox(cx0 + 20, 115, 140, 45, "Давач T / RH\n(SHT40 / BME280)", size=10.5, fill="#e0f2fe", stroke=NEG)
    b_in2 = fitbox(cx0 + 200, 115, 140, 45, "Сирий MOX ADC\n(Rs_raw)", size=10.5, fill="#fef3c7", stroke="#d97706")
    p.append(b_in1)
    p.append(b_in2)

    p.append(arrow(cx0 + 90, 160, cx0 + 90, 185, color=LINE, sw=1.5))
    b_ah = fitbox(cx0 + 20, 185, 140, 50, "Формула Магнуса:\nAH = f(T, RH) [г/м³]", size=10, fill="#fff", stroke=MUTED)
    p.append(b_ah)

    p.append(arrow(cx0 + 90, 235, cx0 + 170, 260, color=LINE, sw=1.5))
    p.append(arrow(cx0 + 270, 160, cx0 + 190, 260, color=LINE, sw=1.5))

    b_corr = fitbox(cx0 + 60, 260, 240, 50, "Коректор опору:\nR_comp = Rs_raw · K(T, AH)", size=10.5, bold=True, fill="#dcfce7", stroke=FIELD)
    p.append(b_corr)

    p.append(arrow(cx0 + 180, 310, cx0 + 180, 335, color=FIELD, sw=2))
    p.append(text(cx0 + 180, 355, "Істинна концентрація газу (ppm / VOC Index)", size=10, bold=True, color=FIELD))

    render(os.path.join(OUT, "rh-temp-compensation-surface.svg"), W, H, *p,
           title="Вплив вологості на газовий сенсор та алгоритм обчислення компенсації")


# ── 4. abc-baseline-drift: Автоматичне калібрування базової лінії (ABC) ────────
def fig_abc_baseline_drift():
    W, H = 880, 420
    p = []

    ox, oy = 80, 310
    gw, gh = 740, 230
    p.append(arrow(ox, oy, ox + gw + 30, oy, color=INK, sw=1.8))
    p.append(arrow(ox, oy, ox, oy - gh - 20, color=INK, sw=1.8))
    p.append(text(ox + gw + 30, oy + 20, "Час (дні тижня / 7-добовий цикл ABC)", size=10.5, bold=True))
    p.append(text(ox - 10, oy - gh - 15, "CO₂ (ppm)", size=10.5, bold=True, anchor="end"))

    day_w = gw / 7.0
    days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]
    for i, d in enumerate(days):
        dx = ox + i * day_w
        p.append(line(dx, oy, dx, oy - gh, color="#f1f5f9", sw=1))
        p.append(text(dx + day_w / 2, oy + 18, d, size=10, color=MUTED))

    y_400 = oy - 45
    p.append(line(ox, y_400, ox + gw, y_400, color=FIELD, sw=1.5, dash="6 4"))
    p.append(text(ox + gw + 10, y_400 + 4, "400 ppm (Вулиця)", size=9.5, color=FIELD, bold=True, anchor="start"))

    y_drift_start = y_400 - 30
    y_drift_end = y_400 - 45
    p.append(line(ox, y_drift_start, ox + gw, y_drift_end, color=POS, sw=1.8, dash="4 4"))
    p.append(text(ox + 10, y_drift_start - 8, "Дрейф базової лінії (старіння / зміщення)", size=9.5, color=POS, anchor="start"))

    curve_data = [
        (0.0, 520), (0.4, 1400), (0.8, 550),
        (1.0, 510), (1.4, 1350), (1.8, 530),
        (2.0, 500), (2.4, 1500), (2.8, 520),
        (3.0, 490), (3.4, 1420), (3.8, 510),
        (4.0, 500), (4.4, 1300), (4.8, 480),
        (5.0, 440), (5.5, 460),  (5.9, 410),
        (6.0, 405), (6.5, 400),  (7.0, 410)
    ]

    path_pts = []
    for f_day, ppm in curve_data:
        px = ox + f_day * day_w
        py = y_400 - (ppm - 400) * 0.15 - 30
        path_pts.append(f"{px:.1f} {py:.1f}")

    d_str = "M " + " L ".join(path_pts)
    p.append(f'<path d="{d_str}" fill="none" stroke="{NEG}" stroke-width="2.2"/>')

    min_x = ox + 6.5 * day_w
    min_y = y_400 - (400 - 400) * 0.15 - 30
    p.append(circle(min_x, min_y, 6, fill="#fff", stroke=ACCENT, sw=2.5))
    p.append(line(min_x, min_y, min_x, y_400, color=ACCENT, sw=2, dash="3 3"))
    p.append(arrow(min_x, min_y, min_x, y_400, color=ACCENT, sw=2))

    b_abc, _, _ = textbox(min_x - 100, min_y - 45,
                          "Мінімум за 7 днів: 480 ppm сирих\nABC коригує зміщення: Δ = −80 ppm",
                          size=9.5, fill="#fff", stroke=ACCENT)
    p.append(b_abc)

    b_warn, _, _ = textbox(ox + 220, 80,
                           "⚠️ ПАСТКА АВТОКАЛІБРУВАННЯ ABC:\nУ теплицях або непровітрюваних спальнях концентрація ніколи не падає до 400 ppm.\nABC помилково прийме 800 ppm за норму і штучно занизить усі покази!",
                           size=10, fill="#fef2f2", stroke=POS)
    p.append(b_warn)

    render(os.path.join(OUT, "abc-baseline-drift.svg"), W, H, *p,
           title="Автоматичне калібрування базової лінії (ABC): пошук глобального мінімуму чистого повітря")


if __name__ == "__main__":
    fig_sensor_types_comparison()
    fig_heater_preheat_phases()
    fig_rh_temp_compensation()
    fig_abc_baseline_drift()
    print("All figures generated successfully!")
