# -*- coding: utf-8 -*-
"""Фігури до теми «Вимірювання струму за DCR котушки»."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

# ── 1. Еквівалентна схема реальної котушки та паралельний RC-фільтр ────────────
def fig_dcr_equivalent_rc():
    W, H = 840, 460
    frags = []
    frags.append(text(W / 2, 24, "Еквівалентна схема реальної котушки та паралельний RC-ланцюг сенсингу", size=15, bold=True))

    # Силовий тракт зверху
    y_pwr = 110
    sw_x = 70
    vout_x = 770

    # Вузол SW
    frags.append(circle(sw_x, y_pwr, 4.5, fill=POS, stroke=POS))
    frags.append(text(sw_x, y_pwr - 14, "Вузол SW", size=12, color=POS, bold=True, anchor="middle"))
    frags.append(text(sw_x, y_pwr + 20, "(0 В ↔ V_in)", size=10, color=MUTED, anchor="middle"))

    # Лінія від SW до дроселя
    frags.append(line(sw_x, y_pwr, 180, y_pwr, color=LINE, sw=3))

    # Символ індуктивності L
    lx0 = 180
    for k in range(4):
        cx = lx0 + 15 + k * 26
        frags.append(f'<path d="M{cx-13:.1f} {y_pwr:.1f} A13 13 0 0 1 {cx+13:.1f} {y_pwr:.1f}" fill="none" stroke="{INK}" stroke-width="3"/>')
    frags.append(text(lx0 + 52, y_pwr - 22, "L (ідеальна індуктивність)", size=12, color=INK, anchor="middle", bold=True))

    # Струм котушки i_L(t)
    frags.append(arrow(lx0 + 20, y_pwr - 34, lx0 + 84, y_pwr - 34, color=POS, sw=2))
    frags.append(text(lx0 + 52, y_pwr - 40, "i_L(t)", size=12, color=POS, anchor="middle", bold=True))

    # З'єднання між L та DCR
    dcr_start = lx0 + 104
    dcr_x = dcr_start + 40
    frags.append(line(dcr_start, y_pwr, dcr_x, y_pwr, color=LINE, sw=3))

    # Резистор DCR (паразитичний опір обмотки)
    frags.append(rect(dcr_x, y_pwr - 15, 90, 30, fill="#fef2f2", stroke=POS, sw=2, rx=3))
    frags.append(text(dcr_x + 45, y_pwr + 5, "DCR", size=13, color=POS, bold=True))
    frags.append(text(dcr_x + 45, y_pwr + 32, "R_Cu (+0.393%/°C)", size=10, color=POS))

    # Лінія до V_out
    frags.append(line(dcr_x + 90, y_pwr, vout_x, y_pwr, color=LINE, sw=3))
    frags.append(circle(vout_x, y_pwr, 4.5, fill=FIELD, stroke=FIELD))
    frags.append(text(vout_x, y_pwr - 14, "V_out (навантаження)", size=12, color=FIELD, bold=True, anchor="middle"))

    # Пунктирна рамка реальної котушки
    frags.append(f'<rect x="150" y="52" width="385" height="100" fill="none" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="5,4" rx="6"/>')
    frags.append(text(342, 68, "Реальна силова котушка індуктивності", size=11, color=MUTED, anchor="middle"))

    # ── Сенсорний RC-ланцюг знизу
    y_rc = 250
    kelvin_sw_x = 130
    kelvin_out_x = 560

    # Точки кельвінівського підключення
    frags.append(circle(kelvin_sw_x, y_pwr, 3.5, fill=NEG, stroke=NEG))
    frags.append(line(kelvin_sw_x, y_pwr, kelvin_sw_x, y_rc, color=NEG, sw=1.8))
    frags.append(line(kelvin_sw_x, y_rc, 230, y_rc, color=NEG, sw=1.8))

    # Резистор сенсингу R_s
    frags.append(rect(230, y_rc - 14, 70, 28, fill="#eff6ff", stroke=NEG, sw=1.8, rx=3))
    frags.append(text(265, y_rc + 5, "R_s", size=12, color=NEG, bold=True))

    # З'єднання між R_s та C_s
    frags.append(line(300, y_rc, 390, y_rc, color=NEG, sw=1.8))

    # Вимірювальний вузол ISEN+ (між R_s та C_s)
    frags.append(circle(350, y_rc, 4, fill=NEG, stroke=NEG))
    frags.append(text(350, y_rc - 12, "ISEN+ (V_C+)", size=11, color=NEG, bold=True, anchor="middle"))

    # Конденсатор C_s
    cs_x = 390
    frags.append(line(cs_x, y_rc - 16, cs_x, y_rc + 16, color=NEG, sw=2.5))
    frags.append(line(cs_x + 8, y_rc - 16, cs_x + 8, y_rc + 16, color=NEG, sw=2.5))
    frags.append(text(cs_x + 4, y_rc + 32, "C_s", size=12, color=NEG, bold=True, anchor="middle"))

    # Лінія повернення до V_out (ISEN−)
    frags.append(line(cs_x + 8, y_rc, kelvin_out_x, y_rc, color=NEG, sw=1.8))
    frags.append(circle(480, y_rc, 4, fill=NEG, stroke=NEG))
    frags.append(text(480, y_rc - 12, "ISEN− (V_C−)", size=11, color=NEG, bold=True, anchor="middle"))

    frags.append(line(kelvin_out_x, y_rc, kelvin_out_x, y_pwr, color=NEG, sw=1.8))
    frags.append(circle(kelvin_out_x, y_pwr, 3.5, fill=NEG, stroke=NEG))

    # Стрілка напруги на конденсаторі V_C
    frags.append(line(350, y_rc + 14, 350, y_rc + 48, color=NEG, sw=1.2))
    frags.append(line(480, y_rc + 14, 480, y_rc + 48, color=NEG, sw=1.2))
    frags.append(arrow(400, y_rc + 45, 350, y_rc + 45, color=NEG, sw=1.5))
    frags.append(arrow(430, y_rc + 45, 480, y_rc + 45, color=NEG, sw=1.5))
    frags.append(text(415, y_rc + 49, "V_C(t)", size=12, color=NEG, bold=True, anchor="middle"))

    # Пояснювальні блоки внизу
    tb1 = fitbox(60, 340, 330, 85, "Напруга реальної котушки:\nV_L(s) = i_L(s) · (s·L + DCR)\nМістить корисний спад (i_L·DCR)\nта шкідливу комутаційну ЕРС (s·L·i_L)", size=11, fill="#fef2f2", stroke=POS)
    frags.append(tb1)

    tb2 = fitbox(430, 340, 360, 85, "Умова балансу сталих часу:\nR_s · C_s = L / DCR\n⇒ Нуль скорочує полюс:\nV_C(t) = DCR · i_L(t) (миттєвий точний сигнал)", size=11, fill="#eff6ff", stroke=NEG, bold=True)
    frags.append(tb2)

    render(os.path.join(IMG, "dcr-equivalent-rc.svg"), W, H, *frags)


# ── 2. Вплив балансу сталих часу на перехідну характеристику ───────────────────
def fig_time_constant_matching():
    W, H = 840, 560
    frags = []
    frags.append(text(W / 2, 24, "Відгук вимірювальної напруги V_C(t) при стрибку струму навантаження", size=15, bold=True))

    x_st, x_step1, x_step2, x_end = 90, 240, 550, 780

    # ── 1. Струм котушки i_L(t) зверху
    y_i = 85
    frags.append(text(x_st, y_i - 16, "1. Реальний струм котушки i_L(t) (постійний рівень + ШІМ-пульсації)", size=12, color=INK, anchor="start", bold=True))
    frags.append(line(x_st, y_i + 35, x_end, y_i + 35, color="#cbd5e1", sw=1))

    # Побудова пилкоподібного струму
    pts_i = [(x_st, y_i + 30)]
    # Низький рівень (до стрибка)
    x = x_st
    while x < x_step1:
        pts_i.append((x + 10, y_i + 20))
        pts_i.append((x + 20, y_i + 30))
        x += 20
    # Стрибок вгору
    pts_i.append((x_step1 + 5, y_i - 5))
    # Високий рівень
    x = x_step1 + 5
    while x < x_step2:
        pts_i.append((x + 10, y_i - 15))
        pts_i.append((x + 20, y_i - 5))
        x += 20
    # Скидання вниз
    pts_i.append((x_step2 + 5, y_i + 30))
    # Низький рівень до кінця
    x = x_step2 + 5
    while x < x_end - 20:
        pts_i.append((x + 10, y_i + 20))
        pts_i.append((x + 20, y_i + 30))
        x += 20
    pts_i.append((x_end, y_i + 25))

    p_i = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_i)
    frags.append(f'<path d="{p_i}" fill="none" stroke="{INK}" stroke-width="2"/>')

    # Позначки струму
    frags.append(text(x_st - 10, y_i + 28, "I_min", size=10, color=MUTED, anchor="end"))
    frags.append(text(x_st - 10, y_i - 10, "I_max", size=10, color=MUTED, anchor="end"))

    # ── 2. Ідеальне узгодження (R_s*C_s = L/DCR)
    y_m = 205
    frags.append(text(x_st, y_m - 16, "2. Ідеальний баланс (R_s·C_s = L/DCR): V_C(t) точно повторює струм i_L(t)", size=12, color=FIELD, anchor="start", bold=True))
    frags.append(line(x_st, y_m + 35, x_end, y_m + 35, color="#cbd5e1", sw=1))

    pts_m = [(px, py + (y_m - y_i)) for px, py in pts_i]
    p_m = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_m)
    frags.append(f'<path d="{p_m}" fill="none" stroke="{FIELD}" stroke-width="2.2"/>')
    frags.append(text(x_step1 + 60, y_m + 2, "V_C(t) = DCR · i_L(t)", size=11, color=FIELD, bold=True))

    # ── 3. Недофільтрація (R_s*C_s < L/DCR)
    y_u = 330
    frags.append(text(x_st, y_u - 24, "3. Недофільтрація (R_s·C_s < L/DCR): диференційний сплеск (хибний OCP)", size=12, color=POS, anchor="start", bold=True))
    frags.append(line(x_st, y_u + 35, x_end, y_u + 35, color="#cbd5e1", sw=1))

    p_u_str = (f"M {x_st} {y_u+30} L {x_step1} {y_u+30} "
               f"L {x_step1+4} {y_u-18} L {x_step1+20} {y_u-2} "
               f"L {x_step2} {y_u-5} "
               f"L {x_step2+4} {y_u+50} L {x_step2+20} {y_u+28} "
               f"L {x_end} {y_u+28}")
    frags.append(f'<path d="{p_u_str}" fill="none" stroke="{POS}" stroke-width="2.2"/>')
    frags.append(text(x_step1 + 18, y_u - 22, "Сплеск напруги!", size=10, color=POS, bold=True, anchor="start"))

    # ── 4. Перефільтрація (R_s*C_s > L/DCR)
    y_o = 450
    frags.append(text(x_st, y_o - 16, "4. Перефільтрація (R_s·C_s > L/DCR): інтегрування сигналу (завал фронту)", size=12, color=NEG, anchor="start", bold=True))
    frags.append(line(x_st, y_o + 35, x_end, y_o + 35, color="#cbd5e1", sw=1))

    p_o_str = (f"M {x_st} {y_o+30} L {x_step1} {y_o+30} "
               f"Q {x_step1+25} {y_o+30} {x_step1+60} {y_o-10} "
               f"L {x_step2} {y_o-10} "
               f"Q {x_step2+25} {y_o-10} {x_step2+60} {y_o+30} "
               f"L {x_end} {y_o+30}")
    frags.append(f'<path d="{p_o_str}" fill="none" stroke="{NEG}" stroke-width="2.2"/>')
    frags.append(text(x_step1 + 75, y_o + 12, "Затягнутий фронт (запізнення)", size=10, color=NEG, bold=True, anchor="start"))

    # Вертикальні лінії зв'язку перехідних подій
    frags.append(line(x_step1, 60, x_step1, 500, color="#94a3b8", sw=1, dash="3,3"))
    frags.append(line(x_step2, 60, x_step2, 500, color="#94a3b8", sw=1, dash="3,3"))
    frags.append(text(x_step1, 520, "Стрибок навантаження (+ΔI)", size=11, color=INK, anchor="middle"))
    frags.append(text(x_step2, 520, "Скидання навантаження (−ΔI)", size=11, color=INK, anchor="middle"))

    render(os.path.join(IMG, "time-constant-matching.svg"), W, H, *frags)


# ── 3. Температурний дрейф міді та NTC-компенсація ─────────────────────────────
def fig_temperature_drift_ntc():
    W, H = 820, 440
    frags = []
    frags.append(text(W / 2, 24, "Температурний дрейф опору міді та стабілізація сигналу мережею NTC", size=15, bold=True))

    ox, oy = 100, 360
    gw, gh = 640, 280

    # Осі
    frags.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.8))
    frags.append(arrow(ox + gw, oy, ox + gw + 25, oy, color=LINE, sw=1.8))
    frags.append(text(ox + gw + 30, oy + 4, "Температура T (°C)", size=12, color=INK, anchor="start"))

    frags.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.8))
    frags.append(arrow(ox, oy - gh, ox, oy - gh - 25, color=LINE, sw=1.8))
    frags.append(text(ox, oy - gh - 32, "Відносний коефіцієнт (відн. 25 °C)", size=12, color=INK, anchor="middle"))

    # Позначки температури на осі X
    t_points = [(ox + 40, "0 °C"), (ox + 160, "25 °C"), (ox + 320, "50 °C"), (ox + 460, "75 °C"), (ox + 580, "100 °C")]
    for tx, tlabel in t_points:
        frags.append(line(tx, oy, tx, oy + 6, color=LINE, sw=1.2))
        frags.append(text(tx, oy + 22, tlabel, size=11, color=INK, anchor="middle"))
        frags.append(line(tx, oy, tx, oy - gh + 20, color="#f1f5f9", sw=1, dash="2,2"))

    # Базовий рівень 1.0 (при 25 °C)
    y_1_0 = oy - 120
    frags.append(line(ox, y_1_0, ox + gw, y_1_0, color="#94a3b8", sw=1, dash="4,4"))
    frags.append(text(ox - 8, y_1_0 + 4, "1.00 (100%)", size=11, color=MUTED, anchor="end"))
    frags.append(text(ox - 8, oy - 235, "1.30 (130%)", size=11, color=POS, anchor="end"))
    frags.append(text(ox - 8, oy - 45, "0.77 (77%)", size=11, color=NEG, anchor="end"))

    # 1. Крива опору міді DCR(T) = 1 + 0.00393*(T - 25)
    # При 25 C -> 1.0; при 100 C -> 1.295 (+29.5%)
    x_25 = ox + 160
    x_100 = ox + 580
    y_cu_25 = y_1_0
    y_cu_100 = oy - 235
    frags.append(line(ox + 40, y_1_0 + 38, x_100, y_cu_100, color=POS, sw=2.8))
    frags.append(circle(x_25, y_cu_25, 4, fill=POS, stroke=POS))
    frags.append(circle(x_100, y_cu_100, 4, fill=POS, stroke=POS))
    frags.append(text(x_100 + 10, y_cu_100 + 4, "DCR міді (+39.3% при 125°C)", size=11, color=POS, bold=True, anchor="start"))

    # 2. Коефіцієнт передачі лінеаризованого NTC-дільника G_ntc(T)
    # При 25 C -> 1.0; при 100 C -> 0.772 (1 / 1.295)
    y_ntc_25 = y_1_0
    y_ntc_100 = oy - 45
    pts_ntc = [
        (ox + 40, y_1_0 - 45),
        (x_25, y_ntc_25),
        (ox + 320, oy - 90),
        (ox + 460, oy - 65),
        (x_100, y_ntc_100)
    ]
    p_ntc = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_ntc)
    frags.append(f'<path d="{p_ntc}" fill="none" stroke="{NEG}" stroke-width="2.5"/>')
    frags.append(circle(x_25, y_ntc_25, 4, fill=NEG, stroke=NEG))
    frags.append(circle(x_100, y_ntc_100, 4, fill=NEG, stroke=NEG))
    frags.append(text(x_100 + 10, y_ntc_100 + 4, "Коефіцієнт передачі NTC-мережі G_ntc(T)", size=11, color=NEG, bold=True, anchor="start"))

    # 3. Результуючий виміряний сигнал з компенсацією: DCR(T) * G_ntc(T) = const
    frags.append(line(ox + 40, y_1_0, x_100 + 30, y_1_0, color=FIELD, sw=3.5))
    frags.append(text(x_100 + 10, y_1_0 - 10, "Скомпенсований струмовий сигнал (похибка < ±1.5%)", size=11, color=FIELD, bold=True, anchor="start"))

    # Інформаційні плашки
    tb = fitbox(ox + 30, oy - gh + 15, 340, 60, "Закон нагріву міді: DCR(T) = DCR_25 · [1 + α_Cu·(T − 25°C)]\nПри нагріві до 100 °C нескомпенсований DCR завищує\nструм на +29.5%, викликаючи фатальний збій VRM!", size=10, fill="#fef2f2", stroke=POS)
    frags.append(tb)

    render(os.path.join(IMG, "temperature-drift-ntc.svg"), W, H, *frags)


# ── 4. Трасування друкованої плати: підключення Кельвіна та завадозахист ────────
def fig_pcb_kelvin_layout():
    W, H = 860, 460
    frags = []
    frags.append(text(W / 2, 24, "Топологія трасування DCR-сенсингу: підключення Кельвіна та захист від SW", size=15, bold=True))

    # Силова котушка у лівій верхній зоні
    ind_x, ind_y, ind_w, ind_h = 120, 70, 200, 110
    frags.append(rect(ind_x, ind_y, ind_w, ind_h, fill="#f8fafc", stroke="#475569", sw=2, rx=6))
    frags.append(text(ind_x + ind_w/2, ind_y + 30, "Силова SMD-котушка (L + DCR)", size=12, color=INK, bold=True))
    frags.append(text(ind_x + ind_w/2, ind_y + 50, "Струм 30–60 А", size=11, color=POS, bold=True))

    # Силові паяльні майданчики (Pads)
    pad_sw_x, pad_sw_y = ind_x - 35, ind_y + 20
    pad_vo_x, pad_vo_y = ind_x + ind_w - 5, ind_y + 20
    pad_w, pad_h = 40, 70
    frags.append(rect(pad_sw_x, pad_sw_y, pad_w, pad_h, fill="#fee2e2", stroke=POS, sw=2, rx=2))
    frags.append(text(pad_sw_x + 20, pad_sw_y + 38, "SW", size=11, color=POS, bold=True))

    frags.append(rect(pad_vo_x, pad_vo_y, pad_w, pad_h, fill="#dcfce7", stroke=FIELD, sw=2, rx=2))
    frags.append(text(pad_vo_x + 20, pad_vo_y + 38, "V_out", size=11, color=FIELD, bold=True))

    # Силові широкі мідні полігони
    frags.append(rect(20, pad_sw_y + 10, pad_sw_x - 20, 50, fill="#fee2e2", stroke="none"))
    frags.append(text(55, pad_sw_y - 8, "Силовий вузол SW", size=10, color=POS, bold=True))
    frags.append(text(55, pad_sw_y + 6, "(dv/dt > 10 В/нс)", size=9, color=POS))

    frags.append(rect(pad_vo_x + pad_w, pad_vo_y + 10, 80, 50, fill="#dcfce7", stroke="none"))
    frags.append(text(pad_vo_x + pad_w + 40, pad_vo_y + 38, "Полігон V_out", size=10, color=FIELD, bold=True))

    # Сенсорні точки Кельвіна (внутрішній край контактного майданчика)
    k_sw_x, k_sw_y = pad_sw_x + 30, pad_sw_y + 55
    k_vo_x, k_vo_y = pad_vo_x + 10, pad_vo_y + 55
    frags.append(circle(k_sw_x, k_sw_y, 4, fill=NEG, stroke="#ffffff", sw=1.5))
    frags.append(circle(k_vo_x, k_vo_y, 4, fill=NEG, stroke="#ffffff", sw=1.5))
    frags.append(text(k_sw_x - 10, k_sw_y + 20, "Кельвін SW", size=10, color=NEG, bold=True))
    frags.append(text(k_vo_x + 10, k_vo_y + 20, "Кельвін V_out", size=10, color=NEG, bold=True))

    # NTC термістор поруч із котушкою (праворуч від V_out полігона, без перетинів)
    ntc_x, ntc_y = 450, 85
    frags.append(rect(ntc_x, ntc_y, 75, 45, fill="#ecfdf5", stroke=FIELD, sw=1.8, rx=4))
    frags.append(text(ntc_x + 37, ntc_y + 20, "NTC", size=12, color=FIELD, bold=True))
    frags.append(text(ntc_x + 37, ntc_y + 36, "термістор", size=9, color=FIELD))
    # Тепловий зв'язок
    frags.append(line(pad_vo_x + pad_w + 80, pad_vo_y + 35, ntc_x, ntc_y + 22, color="#f59e0b", sw=2, dash="3,3"))
    frags.append(text(ntc_x + 37, ntc_y - 8, "Тепловий зв'язок", size=9, color="#b45309", anchor="middle"))

    # Контролер перетворювача внизу
    ic_x, ic_y, ic_w, ic_h = 230, 310, 270, 110
    frags.append(rect(ic_x, ic_y, ic_w, ic_h, fill="#eff6ff", stroke=NEG, sw=2, rx=6))
    frags.append(text(ic_x + ic_w/2, ic_y + 26, "ШІМ / VRM Контролер", size=14, color=NEG, bold=True))
    frags.append(text(ic_x + 45, ic_y + 60, "ISEN+", size=11, color=INK, bold=True))
    frags.append(text(ic_x + 135, ic_y + 60, "ISEN−", size=11, color=INK, bold=True))
    frags.append(text(ic_x + 225, ic_y + 60, "TSEN (NTC)", size=11, color=FIELD, bold=True))

    # Компоненти RC фільтра (розміщені прямо біля мікросхеми)
    rc_box_x, rc_box_y = 80, 220
    frags.append(rect(rc_box_x, rc_box_y, 160, 60, fill="#ffffff", stroke="#64748b", sw=1.5, rx=4))
    frags.append(text(rc_box_x + 80, rc_box_y + 20, "RC-фільтр (R_s, C_s)", size=11, color=INK, bold=True))
    frags.append(text(rc_box_x + 80, rc_box_y + 42, "розміщують УПРИТУЛ до чипа", size=9, color=POS, bold=True))

    # Диференційна пара від кельвінівських точок до RC-фільтра
    frags.append(line(k_sw_x, k_sw_y, k_sw_x, rc_box_y + 20, color=NEG, sw=1.5))
    frags.append(line(k_sw_x, rc_box_y + 20, rc_box_x, rc_box_y + 20, color=NEG, sw=1.5))

    frags.append(line(k_vo_x, k_vo_y, k_vo_x, rc_box_y + 40, color=NEG, sw=1.5))
    frags.append(line(k_vo_x, rc_box_y + 40, rc_box_x + 160, rc_box_y + 40, color=NEG, sw=1.5))

    # З'єднання від RC-фільтра до ISEN ніжок
    frags.append(line(rc_box_x + 50, rc_box_y + 60, ic_x + 45, ic_y + 45, color=NEG, sw=2))
    frags.append(line(rc_box_x + 120, rc_box_y + 60, ic_x + 135, ic_y + 45, color=NEG, sw=2))

    # З'єднання від NTC до TSEN
    frags.append(line(ntc_x + 37, ntc_y + 45, ntc_x + 37, ic_y + 20, color=FIELD, sw=1.5, dash="4,4"))
    frags.append(line(ntc_x + 37, ic_y + 20, ic_x + 225, ic_y + 20, color=FIELD, sw=1.5, dash="4,4"))
    frags.append(arrow(ic_x + 225, ic_y + 20, ic_x + 225, ic_y + 45, color=FIELD, sw=1.5))

    # Правила трасування праворуч
    tb_rules = fitbox(550, 160, 290, 260, "Золоті правила PCB:\n1. 4-провідне підключення Кельвіна\n(безпосередньо на контактні майданчики).\n2. Трасування диференційною парою\nна внутрішньому шарі між двома GND.\n3. R_s та C_s ставлять біля ніжок чипа,\nа не біля галасливої котушки!\n4. NTC монтують упритул до корпусу\nнайгарячішої фази.", size=11, fill="#f8fafc", stroke="#64748b")
    frags.append(tb_rules)

    render(os.path.join(IMG, "pcb-kelvin-layout.svg"), W, H, *frags)


# ── 5. Багатофазне сумування струмів на віртуальній землі ──────────────────────
def fig_multiphase_summing():
    W, H = 840, 480
    frags = []
    frags.append(text(W / 2, 24, "Багатофазне сумування струмів (Current Summing) та придушення пульсацій", size=15, bold=True))

    # Ліворуч: 3 фази зі своїми котушками та RC-фільтрами
    p_ys = [90, 180, 270]
    for i, py in enumerate(p_ys):
        frags.append(rect(50, py - 18, 170, 65, fill="#f8fafc", stroke=LINE, sw=1.5, rx=4))
        frags.append(text(135, py + 5, f"Фаза {i+1} (L_{i+1}, DCR_{i+1})", size=11, color=INK, bold=True))
        frags.append(text(135, py + 26, f"RC-фільтр R_s{i+1}, C_s{i+1}", size=10, color=NEG))

        # Сигнал від конденсатора фази
        frags.append(line(220, py + 15, 290, py + 15, color=NEG, sw=1.8))
        frags.append(circle(290, py + 15, 3.5, fill=NEG, stroke=NEG))

        # Сумуючий резистор R_sum
        frags.append(rect(290, py + 2, 55, 26, fill="#ffffff", stroke=NEG, sw=1.5, rx=2))
        frags.append(text(317, py + 18, "R_sum", size=10, color=NEG, bold=True))

        # Лінія до спільного вузла CS_SUM
        frags.append(line(345, py + 15, 430, py + 15, color=NEG, sw=1.8))
        frags.append(line(430, py + 15, 430, 180, color=NEG, sw=1.8))

    # Спільний вузол CS_SUM
    frags.append(circle(430, 180, 5, fill=POS, stroke=POS))
    frags.append(text(430, 125, "Вузол CS_SUM", size=11, color=POS, bold=True, anchor="middle"))

    # З'єднання з підсилювачем сумування струму
    frags.append(line(430, 180, 500, 180, color=POS, sw=2))

    # Підсилювач струму (ОУ з віртуальною землею)
    amp_x, amp_y = 500, 130
    frags.append(f'<polygon points="{amp_x},{amp_y} {amp_x+80},{amp_y+50} {amp_x},{amp_y+100}" fill="#eff6ff" stroke="{NEG}" stroke-width="2"/>')
    frags.append(text(amp_x + 15, amp_y + 35, "−", size=16, color=NEG, bold=True))
    frags.append(text(amp_x + 15, amp_y + 75, "+", size=16, color=POS, bold=True))

    # Вхід «+» на опорну напругу V_out / VREF
    frags.append(line(amp_x - 30, amp_y + 75, amp_x, amp_y + 75, color=LINE, sw=1.5))
    frags.append(text(amp_x - 40, amp_y + 79, "V_out", size=11, color=FIELD, bold=True, anchor="end"))

    # Резистор зворотного зв'язку R_fb та NTC термокомпенсації
    frags.append(line(amp_x + 20, amp_y + 15, amp_x + 20, amp_y - 25, color=NEG, sw=1.5))
    frags.append(line(amp_x + 20, amp_y - 25, amp_x + 50, amp_y - 25, color=NEG, sw=1.5))
    frags.append(rect(amp_x + 50, amp_y - 37, 70, 24, fill="#ecfdf5", stroke=FIELD, sw=1.5, rx=2))
    frags.append(text(amp_x + 85, amp_y - 21, "R_fb(NTC)", size=10, color=FIELD, bold=True))
    frags.append(line(amp_x + 120, amp_y - 25, amp_x + 150, amp_y - 25, color=NEG, sw=1.5))
    frags.append(line(amp_x + 150, amp_y - 25, amp_x + 150, amp_y + 50, color=NEG, sw=1.5))

    # Вихід підсилювача V_DROOP / I_TOTAL
    frags.append(line(amp_x + 80, amp_y + 50, 750, amp_y + 50, color=POS, sw=2.5))
    frags.append(circle(750, amp_y + 50, 4, fill=POS, stroke=POS))
    frags.append(text(750, amp_y + 35, "V_DROOP = R_LL · I_total", size=12, color=POS, bold=True, anchor="middle"))
    frags.append(text(750, amp_y + 70, "До контуру навантажувальної прямої", size=10, color=MUTED, anchor="middle"))

    # Пояснення компенсації пульсацій внизу
    tb_ripple = fitbox(50, 360, 740, 90, "Ефект багатофазного сумування (Interleaving):\n1. Миттєві струми N фаз мають фазовий зсув 360° / N.\n2. Високочастотні трикутні пульсації струмів окремих котушок взаємно віднімаються у вузлі CS_SUM.\n3. Результуючий сигнал сумарного струму I_total має амплітуду пульсацій у N разів меншу, а частоту — у N разів вищу,\nзабезпечуючи ідеальну чистоту сигналу регулювання без затримок додаткової фільтрації!", size=11, fill="#eff6ff", stroke=NEG)
    frags.append(tb_ripple)

    render(os.path.join(IMG, "multiphase-summing.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_dcr_equivalent_rc()
    fig_time_constant_matching()
    fig_temperature_drift_ntc()
    fig_pcb_kelvin_layout()
    fig_multiphase_summing()
    print("Усі 5 фігур DCR sensing згенеровано успішно.")
