# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра
AMBER   = "#d97706"
AMBERBG = "#fffbeb"
REDBG   = "#fef2f2"
GRNBG   = "#f0fdf4"
BLUEBG  = "#eff6ff"
BORDER  = "#cbd5e1"
GRAYBG  = "#f8fafc"

# ── 1. arrhenius-energy-barrier: енергетичний бар'єр активації ───────────────
def fig_arrhenius_energy_barrier():
    W, H = 760, 420
    p = []

    p.append(rect(0, 0, W, H, fill=BG))

    ox, oy = 80, 340
    gw, gh = 620, 260

    # Осі
    p.append(arrow(ox, oy, ox + gw + 30, oy, color=LINE, sw=1.8))
    p.append(arrow(ox, oy, ox, oy - gh - 25, color=LINE, sw=1.8))
    p.append(text(ox + gw + 30, oy + 28, "Кінетична енергія частинок E (еВ)", size=11, color=INK, anchor="end", bold=True))
    p.append(text(ox - 10, oy - gh - 15, "Густина ймовірності f(E)", size=11, color=INK, anchor="start", bold=True))

    # Вертикальна лінія бар'єру Ea
    ea_x = ox + 380
    p.append(line(ea_x, oy + 5, ea_x, oy - gh - 5, color=POS, sw=2, dash="5,4"))
    p.append(text(ea_x, oy - gh - 18, "Бар'єр активації Ea", size=12, color=POS, bold=True))

    # Побудова розподілів Максвелла-Больцмана f(E) = C * sqrt(E) * exp(-E / kT)
    pts1 = []
    pts2 = []
    steps = 100
    for i in range(steps + 1):
        e_norm = i / float(steps) * 4.5
        x = ox + (i / float(steps)) * gw
        kT1 = 0.8
        kT2 = 1.3
        y1_val = 2.4 * math.sqrt(max(0.001, e_norm)) * math.exp(-e_norm / kT1)
        y2_val = 1.7 * math.sqrt(max(0.001, e_norm)) * math.exp(-e_norm / kT2)
        y1 = oy - y1_val * 90
        y2 = oy - y2_val * 90
        pts1.append((x, y1))
        pts2.append((x, y2))

    # Заливка хвостів за Ea
    poly1 = [f"{ea_x:.1f},{oy:.1f}"]
    poly2 = [f"{ea_x:.1f},{oy:.1f}"]
    for x, y in pts1:
        if x >= ea_x:
            poly1.append(f"{x:.1f},{y:.1f}")
    poly1.append(f"{pts1[-1][0]:.1f},{oy:.1f}")

    for x, y in pts2:
        if x >= ea_x:
            poly2.append(f"{x:.1f},{y:.1f}")
    poly2.append(f"{pts2[-1][0]:.1f},{oy:.1f}")

    p.append(f'<polygon points="{" ".join(poly2)}" fill="{REDBG}" stroke="none"/>')
    p.append(f'<polygon points="{" ".join(poly1)}" fill="{BLUEBG}" stroke="none"/>')

    # Лінії кривих
    path1 = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts1)
    path2 = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts2)
    p.append(f'<path d="{path1}" fill="none" stroke="{NEG}" stroke-width="2.5"/>')
    p.append(f'<path d="{path2}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    # Підписи кривих
    p.append(text(ox + 160, oy - 230, "T₁ = +25 °C (холодний стан)", size=11, color=NEG, bold=True))
    p.append(text(ox + 250, oy - 165, "T₂ = +85 °C (робочий нагрів)", size=11, color=POS, bold=True))

    # Стрілка показує експоненційне зростання частки
    tb_amber, _, _ = textbox(ox + 500, oy - 140, "Експоненційне збільшення\nчастоти подолання бар'єру:\nк-сть часток з E ≥ Ea\nзростає у десятки разів", size=10, fill=AMBERBG, stroke=AMBER, bold=True)
    p.append(tb_amber)

    tb_grn, _, _ = textbox(ox + 160, oy - 50, "Безпечна зона: енергія недостатня\nдля руйнування зв'язків", size=10, fill=GRNBG, stroke=FIELD)
    p.append(tb_grn)

    render(os.path.join(OUT, "arrhenius-energy-barrier.svg"), W, H, *p, title="Енергетичний бар'єр деградації")


# ── 2. activation-energy-failure-modes: спектр енергій активації ─────────────
def fig_activation_energy_failure_modes():
    W, H = 760, 420
    p = []

    p.append(rect(0, 0, W, H, fill=BG))

    # Рамка фону
    p.append(rect(25, 20, 710, 380, fill=GRAYBG, stroke=BORDER, rx=8))
    p.append(text(W / 2, 45, "Спектр енергій активації Ea типових механізмів відмов в електроніці", size=13, color=INK, bold=True))

    # Горизонтальна шкала енергії активації
    ox, oy = 70, 95
    w_scale = 620

    p.append(arrow(ox, oy, ox + w_scale + 25, oy, color=LINE, sw=2))
    p.append(text(ox + w_scale + 30, oy + 4, "Ea (еВ)", size=11, color=INK, anchor="start", bold=True))

    # Позначки на шкалі (0.2 до 1.2 еВ)
    ticks = [(0.2, "0.2"), (0.4, "0.4"), (0.6, "0.6"), (0.8, "0.8"), (1.0, "1.0"), (1.2, "1.2")]
    for ev, lbl in ticks:
        x = ox + (ev - 0.2) / 1.0 * w_scale
        p.append(line(x, oy - 6, x, oy + 6, color=LINE, sw=1.5))
        p.append(text(x, oy - 12, f"{lbl} еВ", size=10, color=MUTED, bold=True))

    # Механізми відмов у вигляді блоків
    mechanisms = [
        ("Випаровування рідкого електроліту крізь гумовий ущільнювач", 0.35, 0.48, 150, "#0284c7", "#e0f2fe", "Al-Elec: висихання, ріст ESR (+1.4–1.6× на кожні 10 °C)"),
        ("Корозія металізації та електрохімічна міграція у волозі", 0.50, 0.75, 215, "#059669", "#d1fae5", "Пекометрична модель: деградація доріжок і пайки"),
        ("Термічна деструкція полімерів і діелектриків плівкових конденсаторів", 0.70, 0.95, 280, "#d97706", "#fef3c7", "Плівкові конденсатори, компаунди (+2.0–2.5× на кожні 10 °C)"),
        ("Електроміграція (Black's equation) та пробій оксиду затвора (TDDB)", 0.85, 1.15, 345, "#dc2626", "#fee2e2", "MOSFET / ВІС: руйнування провідників Al/Cu та діелектрика SiO2 (+3.0–4.0× на 10 °C)"),
    ]

    for title_txt, ev_start, ev_end, y_pos, stroke_c, fill_c, sub_txt in mechanisms:
        x1 = ox + (ev_start - 0.2) / 1.0 * w_scale
        x2 = ox + (ev_end - 0.2) / 1.0 * w_scale
        bw = 640
        bx = ox

        # Кольорова плашка
        p.append(rect(bx, y_pos - 16, bw, 50, fill=fill_c, stroke=stroke_c, sw=1.5, rx=6))

        # Полоса діапазону вгорі плашки
        p.append(rect(x1, y_pos - 16, x2 - x1, 6, fill=stroke_c, stroke="none", rx=3))

        p.append(text(bx + bw / 2, y_pos + 6, title_txt, size=11, color=INK, bold=True))
        p.append(text(bx + bw / 2, y_pos + 24, sub_txt, size=9, color=MUTED))

    render(os.path.join(OUT, "activation-energy-failure-modes.svg"), W, H, *p, title="Енергії активації механізмів відмов")


# ── 3. ten-degree-rule-error: похибка правила 10 градусів ───────────────────
def fig_ten_degree_rule_error():
    W, H = 760, 420
    p = []

    p.append(rect(0, 0, W, H, fill=BG))

    ox, oy = 80, 340
    gw, gh = 420, 260

    # Сітка та осі
    p.append(arrow(ox, oy, ox + gw + 30, oy, color=LINE, sw=1.8))
    p.append(arrow(ox, oy, ox, oy - gh - 25, color=LINE, sw=1.8))
    p.append(text(ox + gw + 30, oy + 28, "Перепад температури ΔT (°C)", size=11, color=INK, anchor="end", bold=True))
    p.append(text(ox - 10, oy - gh - 15, "Коефіцієнт прискорення AF", size=11, color=INK, anchor="start", bold=True))

    # Позначки ΔT: 0, 10, 20, 30, 40 °C
    for dt in [0, 10, 20, 30, 40]:
        x = ox + (dt / 40.0) * gw
        p.append(line(x, oy, x, oy - gh, color="#e2e8f0", sw=1))
        p.append(text(x, oy + 18, f"+{dt} °C", size=10, color=MUTED, bold=True))

    # Позначки AF на осі Y (1, 2, 4, 8, 16)
    af_ticks = [(1, "1×"), (2, "2×"), (4, "4×"), (8, "8×"), (16, "16×")]
    for af, lbl in af_ticks:
        y_norm = math.log2(af) / 4.0
        y = oy - y_norm * gh
        p.append(line(ox, y, ox + gw, y, color="#e2e8f0", sw=1))
        p.append(text(ox - 10, y + 4, lbl, size=10, color=MUTED, anchor="end", bold=True))

    # Розрахунок кривих
    kB = 8.617333e-5
    T0 = 298.15

    pts_rule = []
    pts_04 = []
    pts_07 = []
    pts_10 = []

    steps = 40
    for i in range(steps + 1):
        dt = i * (40.0 / steps)
        x = ox + (dt / 40.0) * gw
        T1 = T0 + dt

        af_r = math.pow(2.0, dt / 10.0)
        af_04 = math.exp((0.4 / kB) * (1.0 / T0 - 1.0 / T1))
        af_07 = math.exp((0.7 / kB) * (1.0 / T0 - 1.0 / T1))
        af_10 = math.exp((1.0 / kB) * (1.0 / T0 - 1.0 / T1))

        def to_y(af_val):
            val = max(1.0, af_val)
            norm = math.log2(val) / 4.0
            return oy - min(1.0, norm) * gh

        pts_rule.append((x, to_y(af_r)))
        pts_04.append((x, to_y(af_04)))
        pts_07.append((x, to_y(af_07)))
        pts_10.append((x, to_y(af_10)))

    # Малювання кривих
    p.append(f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_rule)}" fill="none" stroke="{LINE}" stroke-width="2" stroke-dasharray="6,4"/>')
    p.append(f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_04)}" fill="none" stroke="#0284c7" stroke-width="2.5"/>')
    p.append(f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_07)}" fill="none" stroke="{FIELD}" stroke-width="2.5"/>')
    p.append(f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_10)}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    # Блок пояснення праворуч
    bx = ox + gw + 30
    p.append(rect(bx, 60, 220, 280, fill=GRAYBG, stroke=BORDER, rx=8))
    p.append(text(bx + 110, 85, "Легенда та похибки:", size=11, color=INK, bold=True))

    p.append(line(bx + 10, 115, bx + 35, 115, color=POS, sw=2.5))
    p.append(text(bx + 42, 118, "Ea = 1.0 еВ (TDDB / EM)", size=10, color=POS, anchor="start", bold=True))
    p.append(text(bx + 42, 134, "Правило «10 °C» недооцінює", size=9, color=MUTED, anchor="start"))
    p.append(text(bx + 42, 147, "прискорення у 2–4 рази!", size=9, color=POS, anchor="start", bold=True))

    p.append(line(bx + 10, 175, bx + 35, 175, color=FIELD, sw=2.5))
    p.append(text(bx + 42, 178, "Ea = 0.7 еВ (Плівка / Оксиди)", size=10, color=FIELD, anchor="start", bold=True))
    p.append(text(bx + 42, 194, "Ідеальний збіг із правилом", size=9, color=FIELD, anchor="start", bold=True))

    p.append(line(bx + 10, 225, bx + 35, 225, color=LINE, sw=2, dash="6,4"))
    p.append(text(bx + 42, 228, "Правило 10 °C (2^(ΔT/10))", size=10, color=INK, anchor="start", bold=True))
    p.append(text(bx + 42, 244, "Емпіричний орієнтир", size=9, color=MUTED, anchor="start"))

    p.append(line(bx + 10, 275, bx + 35, 275, color="#0284c7", sw=2.5))
    p.append(text(bx + 42, 278, "Ea = 0.4 еВ (Al-електроліт)", size=10, color="#0284c7", anchor="start", bold=True))
    p.append(text(bx + 42, 294, "Правило «10 °C» переоцінює", size=9, color=MUTED, anchor="start"))
    p.append(text(bx + 42, 307, "фактичний виграш у ресурсі", size=9, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "ten-degree-rule-error.svg"), W, H, *p, title="Порівняння правила 10 градусів з моделлю Арреніуса")


# ── 4. accelerated-testing-mapping: методологія прискорених випробувань ──────
def fig_accelerated_testing_mapping():
    W, H = 760, 360
    p = []

    p.append(rect(0, 0, W, H, fill=BG))

    p.append(rect(30, 30, 700, 300, fill=GRAYBG, stroke=BORDER, rx=8))
    p.append(text(W / 2, 60, "Методологія HTOL / ALT: компресія часу через температурне прискорення", size=13, color=INK, bold=True))

    # Блок стресового тесту зліва (червоний)
    p.append(rect(55, 95, 230, 170, fill=REDBG, stroke=POS, sw=2, rx=6))
    p.append(text(170, 120, "Стресовий тест HTOL", size=12, color=POS, bold=True))
    p.append(text(170, 145, "Температура: T_stress = +125 °C", size=10, color=INK))
    p.append(text(170, 170, "Тривалість: 1000 годин (~42 доби)", size=10, color=POS, bold=True))
    p.append(text(170, 195, "Напруга: 1.0–1.1 · V_rated", size=10, color=INK))
    p.append(text(170, 220, "Вибірка: N = 77...231 зразок", size=10, color=MUTED))
    p.append(text(170, 242, "0 відмов: r = 0", size=10, color=POS, bold=True))

    # Центральна стрілка перетворення з формулою
    p.append(arrow(300, 180, 440, 180, color=AMBER, sw=3))
    tb_af, _, _ = textbox(370, 135, "Коефіцієнт прискорення\nAF ≈ 80...120×\n(Ea = 0.7 еВ)", size=10, fill=AMBERBG, stroke=AMBER, bold=True)
    p.append(tb_af)

    # Блок реальної експлуатації справа (зелений)
    p.append(rect(455, 95, 245, 170, fill=GRNBG, stroke=FIELD, sw=2, rx=6))
    p.append(text(577, 120, "Реальна експлуатація у полі", size=12, color=FIELD, bold=True))
    p.append(text(577, 145, "Температура: T_use = +45 °C", size=10, color=INK))
    p.append(text(577, 170, "Еквівалент: 80 000 – 120 000 год", size=10, color=FIELD, bold=True))
    p.append(text(577, 195, "Ресурс: 10–15 років безперервно", size=10, color=FIELD, bold=True))
    p.append(text(577, 220, "Гарантований рівень FIT / MTBF", size=10, color=MUTED))
    p.append(text(577, 242, "Розрахунок довірчих меж χ²", size=10, color=FIELD, bold=True))

    p.append(text(W / 2, 305, "1000 годин у кліматичній камері еквівалентні понад десятиліттю надійної польової роботи", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "accelerated-testing-mapping.svg"), W, H, *p, title="Прискорені випробування надійності")


# ── 5. capacitor-lifetime-thermal-stress: ресурс електролітичного конденсатора ─
def fig_capacitor_lifetime_thermal_stress():
    W, H = 760, 420
    p = []

    p.append(rect(0, 0, W, H, fill=BG))

    ox, oy = 80, 340
    gw, gh = 420, 260

    # Сітка та осі
    p.append(arrow(ox, oy, ox + gw + 30, oy, color=LINE, sw=1.8))
    p.append(arrow(ox, oy, ox, oy - gh - 25, color=LINE, sw=1.8))
    p.append(text(ox + gw + 30, oy + 28, "Температура серцевини конденсатора T_core (°C)", size=11, color=INK, anchor="end", bold=True))
    p.append(text(ox - 10, oy - gh - 15, "Очікуваний ресурс L (годин)", size=11, color=INK, anchor="start", bold=True))

    # Позначки T_core: 45, 65, 85, 105 °C
    temps = [45, 65, 85, 105]
    for t_val in temps:
        x = ox + (t_val - 45) / 60.0 * gw
        p.append(line(x, oy, x, oy - gh, color="#e2e8f0", sw=1))
        p.append(text(x, oy + 18, f"+{t_val} °C", size=10, color=MUTED, bold=True))

    # Позначки ресурсу по логарифмічній осі: 2 000, 8 000, 32 000, 128 000 годин
    life_ticks = [(2000, "2k"), (8000, "8k (~1 рік)"), (32000, "32k (~3.6 р)"), (128000, "128k (~14.6 р)")]
    for l_val, lbl in life_ticks:
        y_norm = (math.log2(l_val) - math.log2(2000)) / (math.log2(128000) - math.log2(2000))
        y = oy - y_norm * gh
        p.append(line(ox, y, ox + gw, y, color="#e2e8f0", sw=1))
        p.append(text(ox - 10, y + 4, lbl, size=10, color=MUTED, anchor="end", bold=True))

    # Криві:
    def calc_pts(L0, Tmax):
        pts = []
        for i in range(41):
            tc = 45.0 + i * (60.0 / 40.0)
            x = ox + (tc - 45.0) / 60.0 * gw
            life = L0 * math.pow(2.0, (Tmax - tc) / 10.0)
            life_clamped = max(2000, min(128000, life))
            y_norm = (math.log2(life_clamped) - math.log2(2000)) / (math.log2(128000) - math.log2(2000))
            y = oy - y_norm * gh
            pts.append((x, y))
        return pts

    pts_std = calc_pts(2000, 105)
    pts_long = calc_pts(5000, 105)
    pts_125 = calc_pts(2000, 125)

    p.append(f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_std)}" fill="none" stroke="{AMBER}" stroke-width="2.5"/>')
    p.append(f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_long)}" fill="none" stroke="{FIELD}" stroke-width="2.5"/>')
    p.append(f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_125)}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    # Блок опису праворуч
    bx = ox + gw + 30
    p.append(rect(bx, 60, 220, 280, fill=GRAYBG, stroke=BORDER, rx=8))
    p.append(text(bx + 110, 85, "Серії електролітів:", size=11, color=INK, bold=True))

    p.append(line(bx + 10, 115, bx + 35, 115, color=POS, sw=2.5))
    p.append(text(bx + 42, 118, "Серія +125 °C (2000 год)", size=10, color=POS, anchor="start", bold=True))
    p.append(text(bx + 42, 134, "При +65 °C: > 128 000 год", size=9, color=POS, anchor="start", bold=True))

    p.append(line(bx + 10, 175, bx + 35, 175, color=FIELD, sw=2.5))
    p.append(text(bx + 42, 178, "Long-Life +105 °C (5000 год)", size=10, color=FIELD, anchor="start", bold=True))
    p.append(text(bx + 42, 194, "При +65 °C: ~80 000 год", size=9, color=FIELD, anchor="start", bold=True))

    p.append(line(bx + 10, 235, bx + 35, 235, color=AMBER, sw=2.5))
    p.append(text(bx + 42, 238, "Standard +105 °C (2000 год)", size=10, color=AMBER, anchor="start", bold=True))
    p.append(text(bx + 42, 254, "При +65 °C: ~32 000 год", size=9, color=AMBER, anchor="start", bold=True))

    tb_core, _, _ = textbox(bx + 110, 305, "ΔT_core = I_ripple² · ESR / (h·A)\nПульсації струму нагрівають\nсерцевину вище довкілля!", size=9, fill=REDBG, stroke=POS)
    p.append(tb_core)

    render(os.path.join(OUT, "capacitor-lifetime-thermal-stress.svg"), W, H, *p, title="Залежність ресурсу конденсатора від температури")


if __name__ == "__main__":
    fig_arrhenius_energy_barrier()
    fig_activation_energy_failure_modes()
    fig_ten_degree_rule_error()
    fig_accelerated_testing_mapping()
    fig_capacitor_lifetime_thermal_stress()
    print("Всі 5 SVG-фігур успішно згенеровано.")
