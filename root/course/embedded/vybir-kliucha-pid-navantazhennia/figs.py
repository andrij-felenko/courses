# -*- coding: utf-8 -*-
"""Фігури для статті vybir-kliucha-pid-navantazhennia («Вибір ключа під навантаження»).
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. gpio-vs-load: обмеження GPIO мікроконтролера та реальні навантаження ──
def fig_gpio_vs_load():
    W, H = 840, 340
    p = []

    # Лівий блок: Мікроконтролер
    b_mcu, _, _ = textbox(150, 160, "Мікроконтролер (МК)\n3.3 В / 5 В логіка\nGPIO: max 8–20 мА\nСумарно: ≤ 100–150 мА\nЧутливий до сплесків",
                          size=12, pad=12, fill="#eef4ff", stroke=NEG, sw=1.8, min_w=200)
    p.append(b_mcu)

    # Правий блок: Реальні навантаження
    loads = [
        (690, 75, "Реле / Соленоїд\n12 В / 24 В, 0.1–1 А\n+ індуктивний викид!", POS, "#fdecea"),
        (690, 160, "Світлодіодна стрічка\n12 В / 24 В, 2–10 А\nВеликий постійний струм", "#b8860b", "#fdf6e3"),
        (690, 245, "DC Електродвигун\n12 В, 1–5 А (пусковий > 15 А)\nШІМ + індуктивність", POS, "#fdecea"),
    ]
    for lx, ly, ltext, lcol, lfill in loads:
        b_ld, _, _ = textbox(lx, ly, ltext, size=11, pad=8, fill=lfill, stroke=lcol, sw=1.5, min_w=210)
        p.append(b_ld)

    # Центральний блок: Прірва / Силовий ключ як міст
    b_mid, _, _ = textbox(420, 160, "СИЛОВИЙ КЛЮЧ\n(BJT / MOSFET / Smart Switch)\n\n• Підсилення по струму\n• Узгодження напруг\n• Захист логіки від аварій",
                          size=12, pad=12, fill="#eafaf0", stroke=FIELD, sw=2.0, min_w=200)
    p.append(b_mid)

    # Стрілки з'єднання
    p.append(arrow(255, 160, 315, 160, color=NEG, sw=2.0))
    p.append(text(285, 145, "I_gpio < 15 мА", size=10, color=NEG, bold=True))

    p.append(arrow(525, 140, 580, 80, color=POS, sw=2.0))
    p.append(arrow(525, 160, 580, 160, color=POS, sw=2.0))
    p.append(arrow(525, 180, 580, 240, color=POS, sw=2.0))
    p.append(text(555, 125, "I_load > 1 А", size=10, color=POS, bold=True))

    p.append(text(W / 2, H - 15, "Пряме підключення навантаження до GPIO спалює вихідний каскад МК або скидає чип через просідання живлення",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "gpio-vs-load.svg"), W, H, *p,
           title="Чому GPIO мікроконтролера потребує силового ключа")


# ── 2. bjt-saturation: вихідні характеристики BJT та вимога глибокого насичення ──
def fig_bjt_saturation():
    W, H = 840, 360
    ox, oy = 80, 290
    aw, ah = 360, 220
    p = []

    # Осі графіка
    p.append(arrow(ox, oy, ox + aw + 20, oy, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox, oy - ah - 20, color=INK, sw=1.6))
    p.append(text(ox + aw + 15, oy + 20, "V_ce (В)", size=12, color=INK, italic=True))
    p.append(text(ox - 15, oy - ah - 10, "I_c", size=12, color=INK, bold=True, italic=True, anchor="end"))

    # Криві струму колектора
    ib_levels = [30, 70, 120, 170]
    for h_lvl in ib_levels:
        pts = [
            f"{ox},{oy}",
            f"{ox + 25},{oy - h_lvl * 0.9}",
            f"{ox + 60},{oy - h_lvl}",
            f"{ox + aw},{oy - h_lvl * 1.05}"
        ]
        p.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{LINE}" stroke-width="1.8"/>')

    # Область насичення (вертикальна смуга біля осі Y)
    sat_w = 45
    p.append(rect(ox, oy - ah, sat_w, ah, fill="#eafaf0", stroke=FIELD, sw=1.2, rx=0))
    p.append(line(ox + sat_w, oy, ox + sat_w, oy - ah, color=FIELD, sw=1.5, dash="4 3"))
    p.append(text(ox + sat_w / 2, oy - ah + 15, "Насичення", size=10, color=FIELD, bold=True))
    p.append(text(ox + sat_w + 10, oy + 15, "V_ce_sat ≈ 0.2 В", size=10, color=FIELD, bold=True, anchor="start"))

    # Активна область
    b_act, _, _ = textbox(ox + 220, oy - 120, "Активний (лінійний) режим\nI_c = h_FE × I_b\nКлюч напіввідкритий → кипить!",
                          size=10, pad=8, fill="#fdecea", stroke=POS, sw=1.4)
    p.append(b_act)

    # Правий інформаційний блок з формулами розрахунку
    calc_text = (
        "РОЗРАХУНОК БАЗОВОГО РЕЗИСТОРА:\n\n"
        "1. Паспортний h_FE (100–300) — для підсилювача!\n"
        "2. Для надійного КЛЮЧА беруть h_FE_sat = 10..20\n"
        "3. Необхідний струм бази:\n"
        "   I_b = I_load / h_FE_sat\n\n"
        "4. Базовий резистор R_b:\n"
        "   R_b = (V_gpio − V_be) / I_b\n"
        "   де V_be ≈ 0.7 В для кремнію\n\n"
        "5. Втрати потужності ключа:\n"
        "   P_loss = (V_ce_sat × I_c) + (V_be × I_b)"
    )
    b_calc, _, _ = textbox(635, 175, calc_text, size=11, pad=12, fill="#fdf6e3", stroke="#b8860b", sw=1.6, min_w=280)
    p.append(b_calc)

    p.append(text(W / 2, H - 10, "Без надлишкового струму бази транзистор залишається в активному режимі та розсіює надлишкове тепло",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "bjt-saturation.svg"), W, H, *p,
           title="Робота BJT у режимі ключа: вимушене насичення (h_FE_sat = 10..20)")


# ── 3. mosfet-vgs-curves: порогова напруга Vgs(th) проти повного відкриття ──
def fig_mosfet_vgs_curves():
    W, H = 840, 360
    ox, oy = 80, 280
    aw, ah = 360, 200
    p = []

    # Осі графіка Rds(on) vs Vgs
    p.append(arrow(ox, oy, ox + aw + 20, oy, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox, oy - ah - 20, color=INK, sw=1.6))
    p.append(text(ox + aw + 15, oy + 20, "V_gs (В)", size=12, color=INK, italic=True))
    p.append(text(ox - 15, oy - ah - 10, "R_ds(on)", size=12, color=INK, bold=True, italic=True, anchor="end"))

    # Крива спаду Rds(on) зі зростанням Vgs
    curve_pts = [
        f"{ox + 30},{oy - 190}",
        f"{ox + 50},{oy - 180}",
        f"{ox + 70},{oy - 150}",
        f"{ox + 90},{oy - 100}",
        f"{ox + 120},{oy - 45}",
        f"{ox + 160},{oy - 22}",
        f"{ox + 240},{oy - 14}",
        f"{ox + aw},{oy - 10}"
    ]
    p.append(f'<polyline points="{" ".join(curve_pts)}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    # Позначка Vgs(th)
    vth_x = ox + 60
    p.append(line(vth_x, oy, vth_x, oy - 190, color=NEG, sw=1.2, dash="3 3"))
    p.append(text(vth_x, oy + 15, "V_gs(th) (1.5–2 В)", size=10, color=NEG, bold=True))
    
    # Виноска Vgs(th) праворуч угорі від кривої
    b_th, _, _ = textbox(ox + 200, oy - 165, "Пастка V_gs(th)!\nСтрум I_d лише 250 мкА!\nТранзистор ЩЕ ЗАКРИТИЙ",
                         size=10, pad=6, fill="#fdecea", stroke=POS, sw=1.2)
    p.append(b_th)
    p.append(arrow(ox + 140, oy - 165, vth_x + 5, oy - 150, color=POS, sw=1.2))

    # Позначка Vgs = 3.3V (Logic-Level)
    v33_x = ox + 140
    p.append(line(v33_x, oy, v33_x, oy - 190, color=FIELD, sw=1.2, dash="3 3"))
    p.append(text(v33_x, oy + 15, "3.3 В (МК)", size=10, color=FIELD, bold=True))
    p.append(circle(v33_x, oy - 33, 4, fill=FIELD, stroke=FIELD))
    
    b_ll, _, _ = textbox(ox + 230, oy - 70, "Logic-Level FET:\nR_ds(on) мінімальний",
                         size=10, pad=5, fill="#eafaf0", stroke=FIELD, sw=1.2)
    p.append(b_ll)
    p.append(arrow(ox + 175, oy - 70, v33_x + 4, oy - 35, color=FIELD, sw=1.2))

    # Позначка Vgs = 10V (Стандартний силовий FET)
    v10_x = ox + 320
    p.append(line(v10_x, oy, v10_x, oy - 190, color=MUTED, sw=1.2, dash="3 3"))
    p.append(text(v10_x, oy + 15, "10 В (Драйвер)", size=10, color=MUTED, bold=True))
    p.append(circle(v10_x, oy - 11, 4, fill=MUTED, stroke=MUTED))

    # Права панель порівняння FET
    comp_box = (
        "ПРАВИЛО ВИБОРУ ПОЛЬОВОГО ТРАНЗИСТОРА:\n\n"
        "• Звичайний MOSFET (IRFZ44N, IRF540):\n"
        "  - V_gs(th) = 2..4 В\n"
        "  - Повне відкриття лише при V_gs = 10 В!\n"
        "  - Від 3.3 В ледь прочиняється → перегрів.\n\n"
        "• Logic-Level MOSFET (IRLZ44N, AO3400):\n"
        "  - Гарантований R_ds(on) при V_gs = 2.5–3.3 В\n"
        "  - Втрати провідності: P = I_d² × R_ds(on)\n"
        "  - Наприклад: 5 А при 0.02 Ом = 0.5 Вт (холодний)"
    )
    b_cmp, _, _ = textbox(635, 175, comp_box, size=11, pad=12, fill="#eef4ff", stroke=NEG, sw=1.5, min_w=280)
    p.append(b_cmp)

    p.append(text(W / 2, H - 10, "Ніколи не вибирайте транзистор за V_gs(th) — дивіться графік R_ds(on) при напрузі вашого GPIO (3.3 В)",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "mosfet-vgs-curves.svg"), W, H, *p,
           title="Залежність опору R_ds(on) від напруги затвора V_gs")


# ── 4. gate-drive-circuit: обв'язка затвора MOSFET (R_gate та R_pull) ─────────
def fig_gate_drive_circuit():
    W, H = 840, 340
    p = []

    # МК пін зліва
    b_gpio, _, _ = textbox(110, 160, "GPIO МК\n(0 / 3.3 В)\nC_out ≈ 5 пФ",
                           size=11, pad=10, fill="#eef4ff", stroke=NEG, sw=1.5, min_w=120)
    p.append(b_gpio)

    # Дріт від GPIO до R_gate
    p.append(line(170, 160, 230, 160, color=LINE, sw=2.0))

    # R_gate послідовно
    b_rg, _, _ = textbox(275, 160, "R_gate\n(22–100 Ω)", size=10, pad=6, fill="#fdf6e3", stroke="#b8860b", sw=1.5)
    p.append(b_rg)

    # Дріт від R_gate до затвора
    p.append(line(320, 160, 420, 160, color=LINE, sw=2.0))

    # Вузол перед затвором
    p.append(circle(370, 160, 3.5, fill=INK, stroke=INK))
    p.append(line(370, 160, 370, 210, color=LINE, sw=1.8))

    # R_pull-down паралельно на GND
    b_rp, _, _ = textbox(370, 245, "R_pull (10–100 кОм)\nСтягує затвор на GND\nпід час Reset / Hi-Z",
                         size=10, pad=6, fill="#fdf6e3", stroke="#b8860b", sw=1.5)
    p.append(b_rp)
    p.append(line(370, 280, 370, 305, color=LINE, sw=1.8))
    p.append(line(355, 305, 385, 305, color=LINE, sw=2.0))  # GND позначка
    p.append(line(360, 309, 380, 309, color=LINE, sw=1.5))
    p.append(line(365, 313, 375, 313, color=LINE, sw=1.2))

    # N-MOSFET праворуч
    b_fet, _, _ = textbox(530, 160, "N-MOSFET\nLogic-Level\n(C_iss = C_gs + C_gd)\nЗатвор = конденсатор",
                          size=11, pad=10, fill="#eafaf0", stroke=FIELD, sw=1.8, min_w=140)
    p.append(b_fet)
    p.append(line(420, 160, 460, 160, color=LINE, sw=2.0))

    # Пояснювальні виноски
    b_rg_expl, _, _ = textbox(275, 75, "НАВІЩО R_gate:\n1. Обмежує піковий струм заряду C_iss\n   (захищає GPIO від імпульсу > 100 мА)\n2. Гасить LC-дзвін паразитної індуктивності",
                              size=10, pad=8, fill="#ffffff", stroke="#b8860b", sw=1.2, min_w=240)
    p.append(b_rg_expl)
    p.append(arrow(275, 115, 275, 135, color="#b8860b", sw=1.4))

    # Силова частина праворуч від FET
    p.append(line(600, 130, 680, 130, color=POS, sw=2.0))
    p.append(text(690, 130, "До навантаження (Drain)", size=10, color=POS, bold=True, anchor="start"))
    p.append(line(600, 190, 680, 190, color=NEG, sw=2.0))
    p.append(text(690, 190, "GND (Source)", size=10, color=NEG, bold=True, anchor="start"))

    p.append(text(W / 2, H - 8, "Затвор не споживає постійного струму, але є ємнісним навантаженням під час кожного фронту перемикання",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "gate-drive-circuit.svg"), W, H, *p,
           title="Обов'язкова обв'язка затвора MOSFET: резистори R_gate та R_pull")


# ── 5. high-side-vs-low-side: порівняння комутації по плюсу та по землі ───────
def fig_high_side_vs_low_side():
    W, H = 840, 360
    p = []

    # Розділювач навпіл
    p.append(line(W / 2, 45, W / 2, H - 25, color="#d0d7de", sw=1.5, dash="6 4"))

    # Ліва половина: Low-Side Switch
    p.append(text(210, 60, "LOW-SIDE КЛЮЧ (Комутація по GND)", size=13, bold=True, color=NEG))
    ls_box = (
        "+ V_supply (наприклад, 12 В)\n"
        "    │\n"
        " [ НАВАНТАЖЕННЯ ]\n"
        "    │  ← «Плаваюча» точка!\n"
        " [ N-MOSFET ]\n"
        "    │\n"
        "   GND\n\n"
        "ПЕРЕВАГИ:\n"
        "• Просте пряме керування від 3.3 В GPIO\n"
        "• Дешеві n-канальні транзистори з низьким R_ds\n\n"
        "НЕДОЛІКИ ТА НЕБЕЗПЕКИ:\n"
        "• Навантаження завжди під плюсовим потенціалом!\n"
        "• Замикання дроту навантаження на корпус (GND)\n"
        "  вмикає навантаження НАЗАВЖДИ без відома МК!"
    )
    b_ls, _, _ = textbox(210, 205, ls_box, size=10, pad=10, fill="#f4f6f8", stroke=NEG, sw=1.4, min_w=360)
    p.append(b_ls)

    # Права половина: High-Side Switch
    p.append(text(630, 60, "HIGH-SIDE КЛЮЧ (Комутація по VCC)", size=13, bold=True, color=POS))
    hs_box = (
        "+ V_supply (12 В)\n"
        "    │\n"
        " [ P-MOSFET / Smart Switch ]\n"
        "    │  ← Відключається плюс живлення\n"
        " [ НАВАНТАЖЕННЯ ]\n"
        "    │\n"
        "   GND (Твердий спільний корпус)\n\n"
        "ПЕРЕВАГИ:\n"
        "• Повна безпека: вимкнений прилад знеструмлений\n"
        "• Замикання на корпус викликає КЗ джерела,\n"
        "  а не аварійний самовільний запуск приводу\n\n"
        "СКЛАДНІСТЬ:\n"
        "• P-MOSFET потребує проміжного NPN-транзистора\n"
        "  для зсуву логічного рівня 3.3 В → 12 В"
    )
    b_hs, _, _ = textbox(630, 205, hs_box, size=10, pad=10, fill="#fdf6e3", stroke=POS, sw=1.4, min_w=360)
    p.append(b_hs)

    p.append(text(W / 2, H - 10, "В автопромі та промислових приводах стандартом безпеки є комутація верхнього плеча (High-Side)",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "high-side-vs-low-side.svg"), W, H, *p,
           title="Порівняння топологій комутації: Low-Side проти High-Side")


# ── 6. flyback-diode-action: індуктивний викид і захисний діод ─────────────────
def fig_flyback_diode_action():
    W, H = 840, 360
    p = []

    # Розділювач двох станів
    p.append(line(W / 2, 45, W / 2, H - 25, color="#d0d7de", sw=1.5, dash="6 4"))

    # Лівий стан: БЕЗ діода — аварія
    p.append(text(210, 60, "1. БЕЗ захисного діода (АВАРІЯ)", size=13, bold=True, color=POS))
    no_d_text = (
        "+ VCC (12 В)\n"
        "    │\n"
        " [ КОТУШКА (L) ]  → Струм розривається!\n"
        "    │\n"
        " [ КЛЮЧ: РОЗМИКАЄТЬСЯ ]\n"
        "    │\n"
        "   GND\n\n"
        "ФІЗИКА ПРОЦЕСУ:\n"
        "• Закон Фарадея: e = −L × (di/dt)\n"
        "• di/dt прямує до нескінченності за мікросекунди\n"
        "• Напруга на колекторі/стоку стрибає до +200..1000 В!\n"
        "• РЕЗУЛЬТАТ: Миттєвий лавинний пробій і смерть ключа"
    )
    b_nod, _, _ = textbox(210, 205, no_d_text, size=10, pad=10, fill="#fdecea", stroke=POS, sw=1.5, min_w=360)
    p.append(b_nod)

    # Правий стан: З діодом Шотткі — безпечне коло
    p.append(text(630, 60, "2. Зі зворотним діодом (Flyback Diode)", size=13, bold=True, color=FIELD))
    with_d_text = (
        "+ VCC (12 В) ───┐\n"
        "    │           │ (Катод діода до +)\n"
        " [ КОТУШКА ]  [ ДІОД ШОТТКІ ] ↺ Струм циркулює\n"
        "    │           │ (Анод діода до стоку)\n"
        "    ├───────────┘\n"
        " [ КЛЮЧ: ВИМКНЕНО ]\n"
        "    │\n"
        "   GND\n\n"
        "ЯК ПРАЦЮЄ ЗАХИСТ:\n"
        "• Діод відмикається самоіндукцією: V_drain = VCC + 0.4 В\n"
        "• Енергія магнітного поля E = 0.5 × L × I²\n"
        "  безпечно розсіюється на активному опорі котушки\n"
        "• Ключ бачить лише напругу живлення + спад на діоді"
    )
    b_wd, _, _ = textbox(630, 205, with_d_text, size=10, pad=10, fill="#eafaf0", stroke=FIELD, sw=1.5, min_w=360)
    p.append(b_wd)

    p.append(text(W / 2, H - 10, "Діод паралельно індуктивному навантаженню — обов'язковий елемент схеми для будь-якого реле, клапана чи мотора",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "flyback-diode-action.svg"), W, H, *p,
           title="Захист ключа від індуктивного викиду зворотної ЕРС за допомогою діода")


# ── 7. smart-switch-block: внутрішня архітектура інтелектуального ключа ───────
def fig_smart_switch_block():
    W, H = 840, 360
    p = []

    # Загальний корпус мікросхеми (PROFET / TPS2xxx)
    p.append(rect(60, 45, 720, 275, fill="#f8fafc", stroke=LINE, sw=2.0, rx=10))
    p.append(text(420, 68, "Smart High-Side Switch (PROFET / High-Side Power Switch)", size=13, bold=True, color=INK))

    # Виводи зліва (МК сторона)
    b_in, _, _ = textbox(150, 120, "IN (GPIO 3.3 В)", size=10, pad=6, fill="#eef4ff", stroke=NEG, sw=1.2, min_w=120)
    b_is, _, _ = textbox(150, 240, "IS / CS (Струм / Статус)\nДо АЦП мікроконтролера", size=10, pad=6, fill="#eef4ff", stroke=NEG, sw=1.2, min_w=140)
    p.append(b_in)
    p.append(b_is)

    # Внутрішні блоки
    b_cp, _, _ = textbox(340, 120, "Charge Pump\n(Помпа заряду)\nV_gate = V_bat + 10 В", size=10, pad=6, fill="#fdf6e3", stroke="#b8860b", sw=1.2, min_w=140)
    b_prot, _, _ = textbox(340, 195, "Блок захисту:\n• Обмеження струму (КЗ)\n• Тепловий захист (150°C)\n• Захист від зникнення GND",
                           size=10, pad=6, fill="#fdecea", stroke=POS, sw=1.2, min_w=160)
    b_sens, _, _ = textbox(340, 270, "Струмове дзеркало:\nI_sense = I_load / k_ILIS", size=10, pad=6, fill="#eafaf0", stroke=FIELD, sw=1.2, min_w=150)
    p.append(b_cp)
    p.append(b_prot)
    p.append(b_sens)

    # Силовий N-MOSFET праворуч
    b_fet, _, _ = textbox(580, 160, "Силовий N-MOSFET\nВерхнього плеча\n(R_ds = 10..50 мОм)", size=11, pad=10, fill="#eafaf0", stroke=FIELD, sw=1.8, min_w=160)
    p.append(b_fet)

    # Зовнішні виводи живлення та навантаження
    p.append(arrow(660, 120, 750, 120, color=POS, sw=2.0))
    p.append(text(710, 105, "V_bat (+12 В / +24 В)", size=10, color=POS, bold=True))

    p.append(arrow(660, 200, 750, 200, color=POS, sw=2.0))
    p.append(text(710, 220, "OUT (До навантаження)", size=10, color=POS, bold=True))

    # Зв'язки між блоками
    p.append(arrow(210, 120, 270, 120, color=LINE, sw=1.5))
    p.append(arrow(410, 120, 500, 140, color=LINE, sw=1.5))
    p.append(arrow(420, 195, 500, 175, color=POS, sw=1.5))
    p.append(arrow(580, 210, 420, 270, color=FIELD, sw=1.5))
    p.append(arrow(260, 240, 220, 240, color=FIELD, sw=1.5))

    p.append(text(W / 2, H - 10, "Інтелектуальний ключ замінює десятки дискретних деталей: захищає проводку, комутує плюс і вимірює струм",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "smart-switch-block.svg"), W, H, *p,
           title="Архітектура інтелектуального силового ключа (Smart Power Switch)")


def main():
    fig_gpio_vs_load()
    fig_bjt_saturation()
    fig_mosfet_vgs_curves()
    fig_gate_drive_circuit()
    fig_high_side_vs_low_side()
    fig_flyback_diode_action()
    fig_smart_switch_block()
    print("Усі 7 фігур успішно згенеровано.")

if __name__ == "__main__":
    main()
