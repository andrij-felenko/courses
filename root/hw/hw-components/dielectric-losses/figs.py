# -*- coding: utf-8 -*-
"""Фігури до статті «Діелектричні втрати та ESR»
(book/electronics/components/dielectric-losses).

Фігури:
  polarization-lag.svg          — відставання вектора зміщення D від поля E та векторна діаграма струмів
  capacitor-equivalent-full.svg — повна еквівалентна схема неідеального конденсатора
  impedance-esr-freq.svg        — частотні залежності імпедансу |Z(f)| та ESR(f) з розбиттям на складові
  dielectrics-loss-chart.svg    — порівняльний спектр тангенса кута втрат tan(δ) для різних діелектриків
  thermal-ripple-derating.svg   — тепловий баланс розсіювання втрат та вплив перегріву на ресурс

Запуск: python figs.py  → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def fig_polarization_lag():
    w, h = 820, 370
    frags = []

    frags.append(textbox(210, 26, "Часове відставання поляризації D(t) від поля E(t)", size=13, bold=True, fill="#eef2f7")[0])
    frags.append(textbox(620, 26, "Комплексна площина: струми та кут втрат δ", size=13, bold=True, fill="#eef2f7")[0])

    ox, oy = 50, 190
    gw, gh = 320, 120

    frags.append(arrow(ox, oy, ox + gw + 20, oy, color=MUTED, sw=1.2))
    frags.append(arrow(ox, oy + gh/2 + 20, ox, oy - gh/2 - 20, color=MUTED, sw=1.2))
    frags.append(text(ox + gw + 25, oy + 4, "t", size=12, color=MUTED, italic=True))
    frags.append(text(ox - 10, oy - gh/2 - 15, "E, D", size=12, color=MUTED, italic=True))

    pts_e = []
    pts_d = []
    delta_px = 28
    for ix in range(300):
        t = ix / 45.0
        val_e = -math.sin(t) * 50.0
        val_d = -math.sin(t - (delta_px / 45.0)) * 42.0
        pts_e.append((ox + ix, oy + val_e))
        pts_d.append((ox + ix, oy + val_d))

    path_e = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts_e)
    path_d = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts_d)

    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (path_e, POS))
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="5,3"/>' % (path_d, NEG))

    frags.append(text(ox + 90, oy - 56, "E(t) — напруженість поля", size=11, color=POS, bold=True, anchor="start"))
    frags.append(text(ox + 130, oy + 58, "D(t) — зміщення (із запізненням)", size=11, color=NEG, bold=True, anchor="start"))

    frags.append(line(ox + 71, oy - 60, ox + 71, oy + 10, color=MUTED, sw=1, dash="2,2"))
    frags.append(line(ox + 71 + delta_px, oy - 60, ox + 71 + delta_px, oy + 10, color=MUTED, sw=1, dash="2,2"))
    frags.append(arrow(ox + 71, oy - 25, ox + 71 + delta_px, oy - 25, color=LINE, sw=1.2))
    frags.append(text(ox + 71 + delta_px/2, oy - 32, "δ/ω", size=11, color=INK, bold=True))

    frags.append(textbox(210, 325, "Релаксаційне тертя молекул породжує гістерезис:\nвтрачена енергія циклу W = ∮ E dD перетворюється на тепло", size=11, fill="#fdfbf7", pad=6)[0])

    vcx, vcy = 580, 230
    axis_len = 160

    frags.append(arrow(vcx - 20, vcy, vcx + axis_len + 25, vcy, color=MUTED, sw=1.2))
    frags.append(arrow(vcx, vcy + 20, vcx, vcy - axis_len - 25, color=MUTED, sw=1.2))
    frags.append(text(vcx + axis_len + 30, vcy + 4, "Re (Напруга U)", size=11, color=MUTED))
    frags.append(text(vcx - 15, vcy - axis_len - 20, "+j", size=12, color=MUTED, bold=True))

    len_ic = 140
    frags.append(arrow(vcx, vcy, vcx, vcy - len_ic, color=NEG, sw=2.5))
    frags.append(text(vcx - 12, vcy - len_ic + 15, "I_C", size=13, color=NEG, bold=True, anchor="end"))
    frags.append(text(vcx - 12, vcy - len_ic + 30, "(реактивний)", size=10, color=NEG, anchor="end"))

    len_ir = 55
    frags.append(arrow(vcx, vcy, vcx + len_ir, vcy, color=POS, sw=2.5))
    frags.append(text(vcx + len_ir + 8, vcy + 16, "I_R (втрати)", size=11, color=POS, bold=True, anchor="start"))

    frags.append(line(vcx, vcy - len_ic, vcx + len_ir, vcy - len_ic, color=MUTED, sw=1, dash="3,3"))
    frags.append(line(vcx + len_ir, vcy, vcx + len_ir, vcy - len_ic, color=MUTED, sw=1, dash="3,3"))
    frags.append(arrow(vcx, vcy, vcx + len_ir, vcy - len_ic, color=FIELD, sw=2.8))
    frags.append(text(vcx + len_ir + 10, vcy - len_ic - 6, "I_tot (повний струм)", size=12, color=FIELD, bold=True, anchor="start"))

    arc_r = 65
    frags.append('<path d="M %d %d A %d %d 0 0 1 %.1f %.1f" fill="none" stroke="%s" stroke-width="1.6"/>'
                 % (vcx, vcy - arc_r, arc_r, arc_r, vcx + 24, vcy - 60, POS))
    frags.append(text(vcx + 14, vcy - arc_r - 6, "δ", size=13, color=POS, bold=True))

    phi_r = 45
    frags.append('<path d="M %d %d A %d %d 0 0 0 %.1f %.1f" fill="none" stroke="%s" stroke-width="1.4"/>'
                 % (vcx + phi_r, vcy, phi_r, phi_r, vcx + 17, vcy - 41, LINE))
    frags.append(text(vcx + 28, vcy - 16, "φ", size=12, color=LINE, bold=True))

    frags.append(textbox(645, 325, "tan(δ) = I_R / I_C = ε'' / ε' = DF\nДобротність: Q = 1 / tan(δ)", size=12, bold=True, fill="#fdfbf7", pad=6)[0])

    render(os.path.join(IMG, "polarization-lag.svg"), w, h, *frags)


def fig_capacitor_equivalent():
    w, h = 820, 310
    frags = []

    frags.append(textbox(w / 2, 24, "Повна еквівалентна схема неідеального конденсатора", size=15, bold=True, fill="#eef2f7")[0])

    y_main = 120
    x_in = 60
    x_out = 760

    frags.append(circle(x_in, y_main, 4, fill=BG, stroke=LINE, sw=2))
    frags.append(text(x_in - 14, y_main + 5, "Вхід", size=12, color=MUTED, bold=True, anchor="end"))

    x_rohm = 140
    frags.append(line(x_in, y_main, x_rohm - 30, y_main, color=LINE, sw=2))
    frags.append(fitbox(x_rohm - 30, y_main - 18, 60, 36, "R_ohm", size=12, bold=True, fill="#feebe8", stroke=POS))
    frags.append(text(x_rohm, y_main + 32, "Виводи, фольга, контакти", size=10, color=MUTED))

    x_rdi = 270
    frags.append(line(x_rohm + 30, y_main, x_rdi - 35, y_main, color=LINE, sw=2))
    frags.append(fitbox(x_rdi - 35, y_main - 18, 70, 36, "R_di(f)", size=12, bold=True, fill="#feebe8", stroke=POS))
    frags.append(text(x_rdi, y_main + 32, "tan(δ) / (ω·C)", size=10, color=POS, bold=True))

    x_esl = 400
    frags.append(line(x_rdi + 35, y_main, x_esl - 30, y_main, color=LINE, sw=2))
    frags.append(fitbox(x_esl - 30, y_main - 18, 60, 36, "ESL", size=12, bold=True, fill="#eaf7ee", stroke=FIELD))
    frags.append(text(x_esl, y_main + 32, "Паразитна індуктивність", size=10, color=MUTED))

    x_node1 = 490
    frags.append(line(x_esl + 30, y_main, x_node1, y_main, color=LINE, sw=2))
    frags.append(circle(x_node1, y_main, 3.5, fill=LINE, stroke=LINE))

    x_cap = 580
    frags.append(line(x_node1, y_main, x_cap - 6, y_main, color=LINE, sw=2))
    frags.append(line(x_cap - 6, y_main - 22, x_cap - 6, y_main + 22, color=NEG, sw=3))
    frags.append(line(x_cap + 6, y_main - 22, x_cap + 6, y_main + 22, color=NEG, sw=3))
    frags.append(text(x_cap, y_main - 30, "C", size=14, color=NEG, bold=True))
    frags.append(text(x_cap, y_main + 32, "Номінальна ємність", size=10, color=MUTED))

    x_node2 = 670
    frags.append(line(x_cap + 6, y_main, x_node2, y_main, color=LINE, sw=2))
    frags.append(circle(x_node2, y_main, 3.5, fill=LINE, stroke=LINE))

    frags.append(line(x_node2, y_main, x_out, y_main, color=LINE, sw=2))
    frags.append(circle(x_out, y_main, 4, fill=BG, stroke=LINE, sw=2))
    frags.append(text(x_out + 14, y_main + 5, "Вихід", size=12, color=MUTED, bold=True, anchor="start"))

    y_leak = 215
    frags.append(line(x_node1, y_main, x_node1, y_leak, color=LINE, sw=1.6))
    frags.append(line(x_node1, y_leak, x_cap - 40, y_leak, color=LINE, sw=1.6))
    frags.append(fitbox(x_cap - 40, y_leak - 16, 80, 32, "R_leak", size=12, bold=True, fill="#f4f6f8", stroke=LINE))
    frags.append(line(x_cap + 40, y_leak, x_node2, y_leak, color=LINE, sw=1.6))
    frags.append(line(x_node2, y_leak, x_node2, y_main, color=LINE, sw=1.6))
    frags.append(text(x_cap, y_leak + 26, "Опір ізоляції (витік на DC, 10⁸…10¹² Ом)", size=10, color=MUTED))

    frags.append(rect(90, 60, 235, 115, fill="none", stroke=POS, sw=1.4, rx=6))
    frags.append(text(207, 78, "ESR = R_ohm + R_di(f)", size=12, color=POS, bold=True))

    frags.append(textbox(w / 2, 280, "Повний імпеданс: Z(ω) = ESR(ω) + j·[ ω·ESL − 1 / (ω·C) ]  (при R_leak >> 1/ωC)", size=12, bold=True, fill="#fdfbf7", pad=6)[0])

    render(os.path.join(IMG, "capacitor-equivalent-full.svg"), w, h, *frags)


def fig_impedance_esr_freq():
    w, h = 840, 420
    frags = []

    frags.append(textbox(w / 2, 24, "Частотна характеристика повного імпедансу |Z(f)| та опору втрат ESR(f)", size=14, bold=True, fill="#eef2f7")[0])

    ox, oy = 80, 340
    gw, gh = 700, 260

    frags.append(arrow(ox, oy, ox + gw + 30, oy, color=MUTED, sw=1.2))
    frags.append(arrow(ox, oy, ox, oy - gh - 20, color=MUTED, sw=1.2))
    frags.append(text(ox + gw + 35, oy + 4, "f (Гц)", size=12, color=MUTED, bold=True))
    frags.append(text(ox - 10, oy - gh - 15, "Опір (Ом)", size=12, color=MUTED, bold=True))

    freqs = [
        (0, "10 Гц"), (100, "100 Гц"), (200, "1 кГц"), (300, "10 кГц"),
        (400, "100 кГц"), (500, "1 МГц"), (600, "10 МГц"), (700, "100 МГц")
    ]
    for x_rel, lbl in freqs:
        gx = ox + x_rel
        frags.append(line(gx, oy, gx, oy - gh, color="#e5e9f0", sw=1, dash="3,3"))
        frags.append(line(gx, oy, gx, oy + 4, color=MUTED, sw=1.2))
        frags.append(text(gx, oy + 16, lbl, size=10, color=MUTED))

    y_marks = [
        (0, "1 мОм"), (65, "10 мОм"), (130, "100 мОм"), (195, "1 Ом"), (260, "10 Ом")
    ]
    for y_rel, lbl in y_marks:
        gy = oy - y_rel
        frags.append(line(ox, gy, ox + gw, gy, color="#e5e9f0", sw=1, dash="3,3"))
        frags.append(line(ox - 4, gy, ox, gy, color=MUTED, sw=1.2))
        frags.append(text(ox - 8, gy + 4, lbl, size=10, color=MUTED, anchor="end"))

    srf_x = ox + 470
    srf_y = oy - 70

    pts_z = [
        (ox, oy - 250),
        (ox + 100, oy - 200),
        (ox + 200, oy - 150),
        (ox + 300, oy - 105),
        (ox + 400, oy - 75),
        (srf_x, srf_y),
        (ox + 530, oy - 95),
        (ox + 600, oy - 145),
        (ox + 700, oy - 215)
    ]
    path_z = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts_z)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (path_z, NEG))
    frags.append(text(ox + 120, oy - 215, "|Z(f)| — спад −20 дБ/дек", size=11, color=NEG, bold=True))
    frags.append(text(ox + 630, oy - 180, "Зростання +20 дБ/дек", size=11, color=NEG, bold=True))

    frags.append(circle(srf_x, srf_y, 5, fill="#ffffff", stroke=NEG, sw=2.5))
    frags.append(textbox(srf_x + 5, srf_y - 28, "Точка SRF: |Z| = ESR\n(X_C = X_L, чисто активний опір)", size=10, bold=True, fill="#ffffff", stroke=NEG, pad=4)[0])

    pts_esr = [
        (ox, oy - 180),
        (ox + 100, oy - 135),
        (ox + 200, oy - 95),
        (ox + 300, oy - 75),
        (ox + 400, oy - 68),
        (ox + 500, oy - 67),
        (ox + 600, oy - 72),
        (ox + 700, oy - 82)
    ]
    path_esr = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts_esr)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="6,2"/>' % (path_esr, POS))
    frags.append(text(ox + 210, oy - 105, "ESR(f)", size=12, color=POS, bold=True))

    # Розміщуємо плашки строго між лініями сітки, щоб не перетинати їх
    frags.append(textbox(ox + 50, oy - 55, "Низькі частоти:\nдомінує діелектрик R_di ∝ 1/f", size=10, fill="#fffaf9", stroke=POS, pad=4)[0])
    frags.append(textbox(ox + 350, oy - 25, "Середні частоти:\nплато омічних втрат R_ohm", size=10, fill="#fffaf9", stroke=POS, pad=4)[0])
    frags.append(textbox(ox + 650, oy - 35, "Високі частоти:\nскін-ефект виводів ∝ √f", size=10, fill="#fffaf9", stroke=POS, pad=4)[0])

    render(os.path.join(IMG, "impedance-esr-freq.svg"), w, h, *frags)


def fig_dielectrics_loss_chart():
    w, h = 840, 360
    frags = []

    frags.append(textbox(w / 2, 24, "Порівняльний спектр тангенса кута втрат tan(δ) та типового ESR", size=14, bold=True, fill="#eef2f7")[0])

    items = [
        ("Поліпропілен (PP)", "0.0001–0.0002", "1–10 мОм", "Ідеальний: аудіо, резонансні Snubber, високі струми", 0.00015, "#27ae60"),
        ("Кераміка C0G (NP0)", "0.0005–0.001", "5–20 мОм", "Надстабільний: ВЧ фільтри, задавальні контури, RF", 0.0008, "#2ecc71"),
        ("Кераміка X7R (Клас 2)", "0.015–0.030", "10–50 мОм", "Універсальний: Decoupling живлення, буферизація", 0.025, "#f39c12"),
        ("Полімерний тантал", "0.020–0.040", "5–25 мОм", "Компактний Low-ESR: виходи DC-DC, VRM процесорів", 0.030, "#e67e22"),
        ("Тантал MnO2", "0.040–0.080", "100–800 мОм", "Стабільна ємність: аналогове живлення, авіоніка", 0.060, "#d35400"),
        ("Алюмінієвий електроліт", "0.100–0.250", "200–2000 мОм", "Максимальна ємність/вартість: мережеві фільтри", 0.180, "#c0392b")
    ]

    y_start = 65
    row_h = 42

    for i, (name, df_str, esr_str, note, val, col) in enumerate(items):
        cy = y_start + i * row_h
        frags.append(text(25, cy + 4, name, size=11, color=INK, bold=True, anchor="start"))

        log_val = math.log10(val)
        bar_len = ((log_val - (-4.0)) / 3.3) * 230.0 + 20.0
        bar_len = max(20.0, min(260.0, bar_len))

        frags.append(rect(205, cy - 10, bar_len, 20, fill=col, stroke="none", rx=3))
        frags.append(text(215 + bar_len, cy + 4, "tan(δ) ≈ " + df_str, size=10, color=col, bold=True, anchor="start"))

        frags.append(textbox(565, cy, "ESR: " + esr_str, size=10, bold=True, fill="#f8fafc", pad=4)[0])
        frags.append(text(660, cy + 4, note[:38] + "...", size=9, color=MUTED, anchor="start"))

    frags.append(textbox(w / 2, 328, "Чим менший tan(δ), тим менше тепла виділяється в діелектрику: різниця між PP та електролітом сягає 1000 разів!", size=11, bold=True, fill="#fdfbf7", pad=6)[0])

    render(os.path.join(IMG, "dielectrics-loss-chart.svg"), w, h, *frags)


def fig_thermal_ripple_derating():
    w, h = 820, 330
    frags = []

    frags.append(textbox(w / 2, 24, "Тепловий баланс саморозігріву та деградація ресурсу конденсатора", size=14, bold=True, fill="#eef2f7")[0])

    frags.append(textbox(210, 65, "Ланцюг теплового розсіювання", size=12, bold=True, fill="#f1f5f9")[0])

    b1 = textbox(210, 110, "Пульсуючий струм I_rms\nкрізь конденсатор", size=11, fill="#eef2fd", stroke=NEG, pad=6)[0]
    b2 = textbox(210, 175, "Втрати потужності:\nP = I_rms² · ESR(f)", size=11, bold=True, fill="#feebe8", stroke=POS, pad=6)[0]
    b3 = textbox(210, 240, "Перегрів корпусу над середовищем:\nΔT = P · R_th_канал-середовище", size=11, fill="#fef3eb", stroke="#d35400", pad=6)[0]

    frags.extend([b1, b2, b3])
    frags.append(arrow(210, 132, 210, 153, color=LINE, sw=1.5))
    frags.append(arrow(210, 197, 210, 218, color=LINE, sw=1.5))

    frags.append(line(410, 50, 410, 290, color="#e2e8f0", sw=1.5, dash="4,4"))

    frags.append(textbox(615, 65, "Правило Арреніуса (термін служби)", size=12, bold=True, fill="#f1f5f9")[0])

    table_rows = [
        ("T = 105 °C (номінал)", "2 000 годин", "100% номінального ресурсу", "#c0392b"),
        ("T = 95 °C (−10 °C)", "4 000 годин", "Ресурс подвоюється (×2)", "#e67e22"),
        ("T = 85 °C (−20 °C)", "8 000 годин", "Ресурс зростає вчетверо (×4)", "#f39c12"),
        ("T = 75 °C (−30 °C)", "16 000 годин", "Ресурс зростає у 8 разів (×8)", "#27ae60"),
        ("T = 65 °C (−40 °C)", "32 000 годин", "Ресурс зростає у 16 разів (×16)", "#2ecc71")
    ]

    ty = 105
    for temp, hours, desc, col in table_rows:
        frags.append(rect(435, ty - 12, 140, 24, fill="#f8fafc", stroke=col, sw=1.2, rx=4))
        frags.append(text(505, ty + 4, temp, size=10, color=col, bold=True))

        frags.append(rect(585, ty - 12, 90, 24, fill=col, stroke="none", rx=4))
        frags.append(text(630, ty + 4, hours, size=10, color="#ffffff", bold=True))

        frags.append(text(685, ty + 4, desc, size=10, color=MUTED, anchor="start"))
        ty += 34

    frags.append(textbox(w / 2, 305, "Закон надійності: кожні +10 °C перегріву від струму I_rms скорочують життя електроліту вдвічі!", size=11, bold=True, fill="#fdfbf7", pad=6)[0])

    render(os.path.join(IMG, "thermal-ripple-derating.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_polarization_lag()
    fig_capacitor_equivalent()
    fig_impedance_esr_freq()
    fig_dielectrics_loss_chart()
    fig_thermal_ripple_derating()
    print("All figures generated successfully.")
