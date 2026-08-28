# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Низька батарея: три пороги й що по кожному».
Генерує SVG-схеми в ./img/ за допомогою спільного svgkit.
"""
import sys, os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)
sys.path.insert(0, os.path.join(SCRIPT_DIR, '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(SCRIPT_DIR, "img"), exist_ok=True)


# ── Фігура 1: Три рівні реагування на розряд батареї ────────────────────────
def fig_battery_failsafe_three_tiers():
    W, H = 980, 500
    P = []
    P.append(text(W / 2, 28, "Трирівнева драбина аварійного захисту за зарядом батареї", size=16, bold=True))

    col_w = 280
    gap = 25
    x_start = (W - (3 * col_w + 2 * gap)) / 2 + col_w / 2

    tiers = [
        {
            "num": "РІВЕНЬ 1: ПОПЕРЕДЖЕННЯ",
            "sub": "Warning / ~30% / 3.65 В на банку",
            "col": "#27ae60",
            "bg": "#eafaf1",
            "items": [
                ("Умова спрацьовування", "U_ocv ≤ 3.65 В або SOC ≤ 30%\n(утримання > 5 с)"),
                ("Статус польоту", "Штатний політ триває\n(без втручання в кермо)"),
                ("Дія системи", "MAVLink STATUSTEXT (WARNING)\nЗвуковий та візуальний сигнал на GCS"),
                ("Мета реакції", "Попередити оператора\nРекомендація завершити місію"),
            ]
        },
        {
            "num": "РІВЕНЬ 2: ПОВЕРНЕННЯ",
            "sub": "RTL / ~20% / 3.55 В на банку",
            "col": "#d35400",
            "bg": "#fef5e7",
            "items": [
                ("Умова спрацьовування", "U_ocv ≤ 3.55 В або SOC ≤ 20%\n(утримання > 3 с)"),
                ("Статус польоту", "Переривання місії\nАвтономне перехоплення"),
                ("Дія системи", "Перехід у режим RTL (Return-to-Launch)\nНабір висоти та політ до точки старту"),
                ("Мета реакції", "Гарантовано досягти бази\nпоки є запас енергії на вітер і маневр"),
            ]
        },
        {
            "num": "РІВЕНЬ 3: ЕКСТРЕНА ПОСАДКА",
            "sub": "Forced Land / ~10% / 3.40 В на банку",
            "col": "#c0392b",
            "bg": "#fdecea",
            "items": [
                ("Умова спрацьовування", "U_ocv ≤ 3.40 В або SOC ≤ 10%\n(утримання > 1 с)"),
                ("Статус польоту", "Заборона дальніх перельотів\nБлокування режиму RTL"),
                ("Дія системи", "Примусове вертикальне зниження (LAND)\nШвидкість спуску 1.0–1.5 м/с до торкання"),
                ("Мета реакції", "Запобігти знеструмленню (Brownout)\nта некерованому падінню в повітрі"),
            ]
        }
    ]

    for i, t in enumerate(tiers):
        cx = x_start + i * (col_w + gap)
        top_y = 65
        
        # Header card
        hdr_rect = rect(cx - col_w / 2, top_y, col_w, 48, fill=t["bg"], stroke=t["col"], sw=2, rx=6)
        hdr_t1 = text(cx, top_y + 19, t["num"], size=12.5, color=t["col"], bold=True)
        hdr_t2 = text(cx, top_y + 36, t["sub"], size=10.5, color=INK, bold=False)
        P.append(hdr_rect + hdr_t1 + hdr_t2)

        cur_y = top_y + 58
        for title, desc in t["items"]:
            b_box, bw, bh = textbox(cx, cur_y + 36, f"{title}\n{desc}", size=11, fill="#fcfdfd", stroke="#d0d7de", sw=1.2, min_w=col_w)
            P.append(b_box)
            cur_y += 76

    # Bottom summary note
    summary_box, sw, sh = textbox(W / 2, H - 28, "Логіка ескалації: що критичніший стан джерела енергії, то радикальніше скорочується допустимий радіус польоту", size=12, color=INK, bold=True, fill="#f0f4f8", stroke="#8c959f", sw=1.5, min_w=W - 100)
    P.append(summary_box)

    render(os.path.join(SCRIPT_DIR, "img", "battery-failsafe-three-tiers.svg"), W, H, *P)


# ── Фігура 2: Просідання напруги під навантаженням та компенсація ────────────
def fig_voltage_sag_compensation():
    W, H = 960, 480
    P = []
    P.append(text(W / 2, 28, "Просідання напруги під струмом та оцінка ЕРС (Open-Circuit Voltage)", size=16, bold=True))

    # Left: Circuit model
    lx, ly, lw, lh = 50, 65, 390, 365
    P.append(rect(lx, ly, lw, lh, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    P.append(text(lx + lw / 2, ly + 25, "Еквівалентна схема комірки під навантаженням", size=13, bold=True, color=INK))

    # Circuit diagram inside box
    P.append(line(lx + 40, ly + 80, lx + 120, ly + 80, color=LINE, sw=2))
    # Battery symbol (EMF)
    P.append(line(lx + 120, ly + 60, lx + 120, ly + 100, color=POS, sw=3)) # + plate
    P.append(line(lx + 132, ly + 68, lx + 132, ly + 92, color=NEG, sw=2))  # - plate
    P.append(text(lx + 126, ly + 122, "ЕРС (U_ocv)", size=12, color=INK, bold=True))

    # Resistor R_internal
    P.append(line(lx + 132, ly + 80, lx + 190, ly + 80, color=LINE, sw=2))
    P.append(rect(lx + 190, ly + 68, 55, 24, fill="#fff", stroke=LINE, sw=2, rx=3))
    P.append(text(lx + 217, ly + 84, "R_int", size=11, color=INK, bold=True))
    P.append(text(lx + 217, ly + 122, "Внутрішній опір", size=11, color=MUTED))

    # Terminal output
    P.append(arrow(lx + 245, ly + 80, lx + 340, ly + 80, color=LINE, sw=2))
    P.append(text(lx + 310, ly + 70, "Струм I (А)", size=11, color=POS, bold=True))
    P.append(circle(lx + 340, ly + 80, 4, fill=POS, stroke=LINE, sw=1.5))
    P.append(circle(lx + 340, ly + 155, 4, fill=NEG, stroke=LINE, sw=1.5))
    P.append(line(lx + 40, ly + 155, lx + 340, ly + 155, color=LINE, sw=2))
    P.append(line(lx + 40, ly + 80, lx + 40, ly + 155, color=LINE, sw=2))

    # Voltage markers
    P.append(text(lx + lw / 2, ly + 185, "U_measured = U_ocv − I · R_internal", size=13, color=NEG, bold=True))
    P.append(text(lx + lw / 2, ly + 210, "U_ocv = U_measured + I · R_internal", size=13, color=FIELD, bold=True))

    # Real flight numbers box
    expl_text = "Приклад маневру (6S LiPo, R_int = 10 мОм/банку):\n• Струм зависання: 20 А  →  просідання 0.20 В/банку\n• Ривок газу (Punch): 80 А →  просідання 0.80 В/банку\n• Заряд 60% (3.80 В) при 80 А просідає до 3.00 В!\nБез компенсації автопілот виконає хибний LAND."
    b_expl, bw, bh = textbox(lx + lw / 2, ly + 295, expl_text, size=11, fill="#ffffff", stroke="#cbd5e1", sw=1.2, min_w=lw - 30)
    P.append(b_expl)

    # Right: Response comparison plot / timeline
    rx_b, ry_b, rw_b, rh_b = 460, 65, 470, 365
    P.append(rect(rx_b, ry_b, rw_b, rh_b, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    P.append(text(rx_b + rw_b / 2, ry_b + 25, "Динаміка напруги під час маневру повного газу", size=13, bold=True, color=INK))

    # Axes
    ox, oy = rx_b + 55, ry_b + 230
    ax_w, ax_h = 380, 160
    P.append(arrow(ox, oy, ox + ax_w, oy, color=LINE, sw=1.5))
    P.append(arrow(ox, oy, ox, oy - ax_h, color=LINE, sw=1.5))
    P.append(text(ox + ax_w - 20, oy + 20, "Час (с)", size=11, color=INK, bold=True))
    P.append(text(ox - 25, oy - ax_h + 15, "U (В)", size=11, color=INK, bold=True))

    # Threshold line 3.40V
    thresh_y = oy - 50
    P.append(line(ox, thresh_y, ox + ax_w - 20, thresh_y, color=POS, sw=1.5, dash="4,4"))
    P.append(text(ox + 80, thresh_y - 8, "Поріг Land (3.40 В)", size=10.5, color=POS, bold=True))

    # Compensated OCV curve (smooth slowly decaying curve at ~3.75V)
    ocv_y = oy - 120
    P.append(line(ox, ocv_y, ox + 100, ocv_y + 4, color=FIELD, sw=2.5))
    P.append(line(ox + 100, ocv_y + 4, ox + 220, ocv_y + 12, color=FIELD, sw=2.5))
    P.append(line(ox + 220, ocv_y + 12, ox + ax_w - 30, ocv_y + 20, color=FIELD, sw=2.5))
    P.append(text(ox + 290, ocv_y - 6, "Оцінена ЕРС U_ocv", size=11, color=FIELD, bold=True))

    # Raw measured voltage curve with deep dip during current spike
    P.append(line(ox, ocv_y + 20, ox + 90, ocv_y + 22, color=NEG, sw=2)) # hover sag
    P.append(line(ox + 90, ocv_y + 22, ox + 110, thresh_y + 25, color=NEG, sw=2)) # steep sag under punch-out
    P.append(line(ox + 110, thresh_y + 25, ox + 190, thresh_y + 28, color=NEG, sw=2)) # high current sag below threshold!
    P.append(line(ox + 190, thresh_y + 28, ox + 210, ocv_y + 34, color=NEG, sw=2)) # recovery after throttle release
    P.append(line(ox + 210, ocv_y + 34, ox + ax_w - 30, ocv_y + 42, color=NEG, sw=2))
    P.append(text(ox + 150, thresh_y + 42, "Сира напруга U_meas", size=10.5, color=NEG, bold=True))

    # Annotation of false trigger zone
    P.append(rect(ox + 105, thresh_y, 90, 30, fill="#fdecea", stroke=POS, sw=1, rx=3))
    P.append(text(ox + 150, thresh_y + 15, "Хибний збій", size=10, color=POS, bold=True))
    P.append(text(ox + 150, thresh_y + 25, "(без компенсації)", size=9, color=POS))

    # Current pulse bar chart below
    cur_y = oy + 60
    P.append(text(ox + 50, cur_y - 15, "Струм моторів:", size=11, bold=True, color=INK))
    P.append(rect(ox + 100, cur_y - 25, 100, 30, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    P.append(text(ox + 150, cur_y - 8, "Імпульс 80 А (маневр)", size=10.5, color=POS, bold=True))

    # Bottom summary
    P.append(text(W / 2, H - 20, "Компенсація напруги запобігає перериванню місії під час динамічних ривків тяги та зустрічного вітру", size=11.5, bold=True, color=INK))

    render(os.path.join(SCRIPT_DIR, "img", "voltage-sag-compensation.svg"), W, H, *P)


# ── Фігура 3: Архітектура конвеєра злиття (Dual-Source Fusion Pipeline) ───────
def fig_dual_source_fusion_pipeline():
    W, H = 960, 490
    P = []
    P.append(text(W / 2, 28, "Архітектура оцінки заряду та автомата станів аварійного живлення", size=16, bold=True))

    # Sensor Inputs (Left)
    in_x = 120
    b_v, _, _ = textbox(in_x, 90, "АЦП напруги батареї\nU_measured (В)", size=11.5, fill="#eaf0fd", stroke=NEG, sw=1.5, min_w=170)
    b_i, _, _ = textbox(in_x, 210, "Давач струму (шунт/Холл)\nI_measured (А)", size=11.5, fill="#fdecea", stroke=POS, sw=1.5, min_w=170)
    P.append(b_v + b_i)

    # Middle tier 1: Processing Channels
    mid1_x = 360
    b_sag, _, _ = textbox(mid1_x, 90, "Компенсація просідання\nU_ocv = U_meas + I · R_int\nФільтрація шуму НЧ (Low-Pass)", size=11, fill="#f0fdf4", stroke=FIELD, sw=1.5, min_w=220)
    b_coulomb, _, _ = textbox(mid1_x, 210, "Кулонівський лічильник\nΔQ = ∫ I dt (мА·год)\nSOC_mAh = (1 − Q_used/Q_total)", size=11, fill="#fef9c3", stroke="#ca8a04", sw=1.5, min_w=220)
    P.append(b_sag + b_coulomb)

    # Arrows from sensors to processing
    P.append(arrow(in_x + 85, 90, mid1_x - 110, 90, color=LINE, sw=1.5))
    P.append(arrow(in_x + 85, 210, mid1_x - 110, 210, color=LINE, sw=1.5))
    P.append(arrow(in_x + 85, 200, mid1_x - 110, 105, color=MUTED, sw=1.2)) # current to sag comp

    # Middle tier 2: Dual-Source Arbiter
    mid2_x = 640
    arbiter_txt = "Арбітр та злиття каналів\n• Порівняння з 3 порогами\n• Консервативний вибір:\n  Рівень = max(Рівень_U, Рівень_Q)\n• Захист від розбалансу банок"
    b_arb, _, _ = textbox(mid2_x, 150, arbiter_txt, size=11, fill="#ffffff", stroke="#6366f1", sw=2, min_w=220)
    P.append(b_arb)

    P.append(arrow(mid1_x + 110, 90, mid2_x - 110, 130, color=LINE, sw=1.5))
    P.append(arrow(mid1_x + 110, 210, mid2_x - 110, 170, color=LINE, sw=1.5))

    # Right: Debounce & Action Engine
    out_x = 850
    act_txt = "Автомат Failsafe\n• Таймери дебаунсу\n  (1 с / 3 с / 5 с)\n• Фіксація стану (Latch)\n• Команда: WARN / RTL / LAND"
    b_act, _, _ = textbox(out_x, 150, act_txt, size=11, fill="#f8fafc", stroke=INK, sw=2, min_w=170)
    P.append(b_act)

    P.append(arrow(mid2_x + 110, 150, out_x - 85, 150, color=LINE, sw=2))

    # Output dispatch arrows
    P.append(arrow(out_x, 215, out_x, 280, color=LINE, sw=1.8))
    
    # 3 outputs at bottom right
    P.append(rect(100, 310, 760, 140, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    P.append(text(480, 335, "Виконавчі контури польотного стека", size=13, bold=True, color=INK))

    b_o1, _, _ = textbox(230, 395, "GCS & Телеметрія\nПопередження пілоту\nЗвуковий сигнал (Level 1)", size=10.5, fill="#eafaf1", stroke=FIELD, min_w=200)
    b_o2, _, _ = textbox(480, 395, "Навігаційний автомат\nПереривання поточної місії\nЗапуск повернення RTL (Level 2)", size=10.5, fill="#fef5e7", stroke="#d35400", min_w=220)
    b_o3, _, _ = textbox(730, 395, "Регулятор тяги / Мікшер\nПримусова вертикальна\nпосадка LAND (Level 3)", size=10.5, fill="#fdecea", stroke=POS, min_w=200)
    P.append(b_o1 + b_o2 + b_o3)

    render(os.path.join(SCRIPT_DIR, "img", "dual-source-fusion-pipeline.svg"), W, H, *P)


if __name__ == "__main__":
    fig_battery_failsafe_three_tiers()
    fig_voltage_sag_compensation()
    fig_dual_source_fusion_pipeline()
    print("OK: 3 figures generated in img/")
