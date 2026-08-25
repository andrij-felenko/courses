# -*- coding: utf-8 -*-
"""Фігури до теми «ESR та імпеданс конденсатора»
(book/electronics/components/capacitor-esr-impedance).

Фігури:
  equivalent-circuit-model.svg  — повна 4-елементна еквівалентна схема неідеального конденсатора
  impedance-frequency-curve.svg — V-подібна частотна характеристика модуля імпедансу |Z(f)| та фази
  esr-frequency-breakdown.svg   — фізичні складники ESR(f): омічний опір металу та діелектричні втрати
  pdn-antiresonance-peaks.svg   — антирезонансні піки імпедансу в шині живлення при паралельному з'єднанні
  ripple-current-heating.svg    — самонагрів конденсатора, розсіювання тепла та частотний множник ripple current

Запуск: python figs.py  → генерує SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Повна еквівалентна схема ──────────────────────────────────────────────
def make_equivalent_circuit_model():
    w, h = 840, 400
    out = []

    out.append(text(w / 2, 28, "Повна еквівалентна схема неідеального конденсатора", size=16, bold=True))

    # Контур діелектричної та конструктивної оболонки
    out.append(rect(90, 50, 660, 330, fill="#fcfdfd", stroke="#95a5a6", sw=1.5, rx=8))
    out.append(text(105, 75, "Корпус реального конденсатора", size=12, color=MUTED, bold=True, anchor="start"))

    # Виводи схеми
    y_main = 160
    out.append(circle(50, y_main, 6, fill="#ffffff", stroke=POS, sw=2.5))
    out.append(text(25, y_main + 5, "A (+)", size=13, color=POS, bold=True))
    out.append(circle(790, y_main, 6, fill="#ffffff", stroke=NEG, sw=2.5))
    out.append(text(815, y_main + 5, "B (−)", size=13, color=NEG, bold=True))

    # З'єднання до вузлів
    out.append(line(56, y_main, 120, y_main, color=LINE, sw=2))
    out.append(circle(120, y_main, 4, fill=LINE, stroke=LINE, sw=1))
    
    out.append(line(720, y_main, 784, y_main, color=LINE, sw=2))
    out.append(circle(720, y_main, 4, fill=LINE, stroke=LINE, sw=1))

    # 1. ESL
    out.append(line(120, y_main, 160, y_main, color=LINE, sw=2))
    x_esl = 160
    r_c = 6
    for i in range(4):
        bx = x_esl + i * 2 * r_c
        out.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" fill="none" stroke="%s" stroke-width="2.2"/>'
                   % (bx, y_main, r_c, r_c, bx + 2 * r_c, y_main, FIELD))
    out.append(line(x_esl + 8 * r_c, y_main, 280, y_main, color=LINE, sw=2))
    out.append(textbox(208, 105, "ESL\nІндуктивність виводів\nта геометрії", size=11, pad=5, fill="#eafaf1", stroke=FIELD, bold=True)[0])

    # 2. ESR
    out.append(rect(280, y_main - 15, 60, 30, fill="#fdedec", stroke=POS, sw=2))
    out.append(text(310, y_main + 5, "ESR", size=12, color=POS, bold=True))
    out.append(line(340, y_main, 470, y_main, color=LINE, sw=2))
    out.append(textbox(375, 105, "ESR(f)\nОпір металу R_ohm +\nвтрати в діелектрику R_di", size=11, pad=5, fill="#fdedec", stroke=POS, bold=True)[0])

    # 3. Ємність C
    out.append(line(470, y_main, 530, y_main, color=LINE, sw=2))
    out.append(line(530, y_main - 22, 530, y_main + 22, color=NEG, sw=3.5))
    out.append(line(544, y_main - 22, 544, y_main + 22, color=NEG, sw=3.5))
    out.append(line(544, y_main, 720, y_main, color=LINE, sw=2))
    out.append(textbox(600, 105, "C\nІдеальна ємність\nнакопичення заряду", size=11, pad=5, fill="#eaf2f8", stroke=NEG, bold=True)[0])

    # Паралельна гілка витоку R_leak
    y_leak = 290
    out.append(line(120, y_main, 120, y_leak, color=LINE, sw=2))
    out.append(line(120, y_leak, 370, y_leak, color=LINE, sw=2))

    out.append(rect(370, y_leak - 15, 100, 30, fill="#f4f6f8", stroke=MUTED, sw=2))
    out.append(text(420, y_leak + 5, "R_leak", size=12, color=INK, bold=True))

    out.append(line(470, y_leak, 720, y_leak, color=LINE, sw=2))
    out.append(line(720, y_leak, 720, y_main, color=LINE, sw=2))
    out.append(textbox(420, 345, "R_leak (опір витоку ізоляції, 10⁶…10¹¹ Ом) — визначає постійний струм витоку", size=11, pad=5, fill="#ffffff", stroke=MUTED)[0])

    render(os.path.join(IMG, "equivalent-circuit-model.svg"), w, h, *out)


# ── 2. V-крива імпедансу та фази |Z(f)| ──────────────────────────────────────
def make_impedance_frequency_curve():
    w, h = 860, 480
    out = []

    out.append(text(w / 2, 26, "Частотна характеристика імпедансу |Z(f)| та фазового зсуву", size=16, bold=True))

    x0, y0 = 90, 60
    gw, gh = 700, 300

    out.append(rect(x0, y0, gw, gh, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=4))

    freqs = ["100 Гц", "1 кГц", "10 кГц", "100 кГц", "1 МГц", "10 МГц", "100 МГц", "1 ГГц"]
    for i in range(8):
        gx = x0 + i * (gw / 7)
        if 0 < i < 7:
            out.append(line(gx, y0, gx, y0 + gh, color="#e1e4e8", sw=1, dash="4,4"))
        out.append(text(gx, y0 + gh + 18, freqs[i], size=11, color=MUTED))
    out.append(text(x0 + gw / 2, y0 + gh + 38, "Частота f (логарифмічна шкала)", size=12, bold=True))

    z_labels = ["10 кОм", "1 кОм", "100 Ом", "10 Ом", "1 Ом", "100 мОм", "10 мОм", "1 мОм"]
    for j in range(8):
        gy = y0 + j * (gh / 7)
        if 0 < j < 7:
            out.append(line(x0, gy, x0 + gw, gy, color="#e1e4e8", sw=1, dash="4,4"))
        out.append(text(x0 - 10, gy + 4, z_labels[j], size=11, color=MUTED, anchor="end"))
    out.append(text(25, y0 + gh / 2, "Модуль |Z|", size=12, bold=True, anchor="middle"))

    xsrf = x0 + gw * 0.58
    ysrf = y0 + gh * 0.82

    path_pts = []
    phase_pts = []
    for px in range(int(x0), int(x0 + gw + 1), 4):
        rel_f = (px - xsrf) / 80.0
        xc = math.exp(-rel_f)
        xl = math.exp(rel_f)
        esr_norm = 0.08
        z_norm = math.sqrt(esr_norm**2 + (xl - xc)**2)
        log_z = math.log10(z_norm)
        py = ysrf - (log_z - math.log10(esr_norm)) * 52.0
        py = max(y0 + 10, min(y0 + gh - 5, py))
        path_pts.append((px, py))

        phi = math.atan2(xl - xc, esr_norm) * (180.0 / math.pi)
        phi_y = y0 + gh * 0.5 - (phi / 90.0) * (gh * 0.38)
        phase_pts.append((px, phi_y))

    phase_d = "M " + " ".join("%.1f,%.1f" % pt for pt in phase_pts)
    out.append('<path d="%s" fill="none" stroke="#e67e22" stroke-width="2" stroke-dasharray="6,4"/>' % phase_d)

    path_d = "M " + " ".join("%.1f,%.1f" % pt for pt in path_pts)
    out.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.2"/>' % (path_d, NEG))

    # Пунктирна лінія SRF
    out.append(line(xsrf, y0, xsrf, ysrf - 65, color=POS, sw=1.5, dash="5,5"))
    out.append(line(xsrf, ysrf - 25, xsrf, y0 + gh, color=POS, sw=1.5, dash="5,5"))
    out.append(circle(xsrf, ysrf, 6, fill=POS, stroke="#ffffff", sw=2))

    out.append(textbox(xsrf + 68, ysrf - 45, "SRF: Резонанс\n|Z_min| = ESR\nФаза = 0°", size=10, pad=4, fill="#fdedec", stroke=POS, bold=True)[0])

    out.append(textbox(x0 + 140, y0 + 60, "Ємнісна зона (f < SRF)\n|Z| ≈ 1 / (2·π·f·C)\nСпад: −20 дБ/декаду\nФаза: −90°", size=11, pad=5, fill="#eaf2f8", stroke=NEG, bold=True)[0])

    out.append(textbox(x0 + gw - 140, y0 + 60, "Індуктивна зона (f > SRF)\n|Z| ≈ 2·π·f·ESL\nЗростання: +20 дБ/декаду\nФаза: +90°", size=11, pad=5, fill="#fcf3cf", stroke="#b7950b", bold=True)[0])

    # Легенда унизу
    out.append(line(x0 + 180, y0 + gh + 55, x0 + 220, y0 + gh + 55, color=NEG, sw=3))
    out.append(text(x0 + 225, y0 + gh + 59, "Модуль |Z|", size=11, color=INK, anchor="start", bold=True))

    out.append(line(x0 + 380, y0 + gh + 55, x0 + 420, y0 + gh + 55, color="#e67e22", sw=2, dash="6,4"))
    out.append(text(x0 + 425, y0 + gh + 59, "Фазовий кут θ", size=11, color=INK, anchor="start", bold=True))

    render(os.path.join(IMG, "impedance-frequency-curve.svg"), w, h, *out)


# ── 3. Фізичні складники ESR(f) ─────────────────────────────────────────────
def make_esr_frequency_breakdown():
    w, h = 860, 460
    out = []

    out.append(text(w / 2, 24, "Частотна залежність та структура ESR: ESR(f) = R_ohm + R_di(f)", size=16, bold=True))

    # Виноски зверху над сіткою
    out.append(textbox(280, 52, "R_di(f) = tan(δ) / (2·π·f·C) — втрати в діелектрику спадають як 1/f", size=10, pad=4, fill="#eafaf1", stroke=FIELD, bold=True)[0])
    out.append(textbox(640, 52, "R_ohm(f) — опір металу зростає на ВЧ через скін-ефект ~√f", size=10, pad=4, fill="#fef5e7", stroke="#e67e22", bold=True)[0])

    x0, y0 = 90, 80
    gw, gh = 700, 260
    out.append(rect(x0, y0, gw, gh, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=4))

    f_pts = ["100 Гц", "1 кГц", "10 кГц", "100 кГц", "1 МГц", "10 МГц", "100 МГц"]
    for i in range(7):
        gx = x0 + i * (gw / 6)
        if 0 < i < 6:
            out.append(line(gx, y0, gx, y0 + gh, color="#e1e4e8", sw=1, dash="4,4"))
        out.append(text(gx, y0 + gh + 18, f_pts[i], size=11, color=MUTED))
    out.append(text(x0 + gw / 2, y0 + gh + 38, "Частота f", size=12, bold=True))

    r_labels = ["100 Ом", "10 Ом", "1 Ом", "100 мОм", "10 мОм", "1 мОм"]
    for j in range(6):
        gy = y0 + j * (gh / 5)
        if 0 < j < 5:
            out.append(line(x0, gy, x0 + gw, gy, color="#e1e4e8", sw=1, dash="4,4"))
        out.append(text(x0 - 10, gy + 4, r_labels[j], size=11, color=MUTED, anchor="end"))
    out.append(text(25, y0 + gh / 2, "Опір", size=12, bold=True, anchor="middle"))

    r_di_pts = []
    for px in range(int(x0), int(x0 + gw * 0.75), 5):
        norm = (px - x0) / (gw * 0.75)
        py = y0 + 35 + norm * (gh - 65)
        r_di_pts.append((px, py))
    d_di = "M " + " ".join("%.1f,%.1f" % pt for pt in r_di_pts)
    out.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="6,4"/>' % (d_di, FIELD))

    r_ohm_pts = []
    for px in range(int(x0), int(x0 + gw + 1), 5):
        norm = (px - x0) / gw
        if norm < 0.6:
            py = y0 + gh * 0.78
        else:
            py = y0 + gh * 0.78 - ((norm - 0.6) / 0.4)**1.5 * 45
        r_ohm_pts.append((px, py))
    d_ohm = "M " + " ".join("%.1f,%.1f" % pt for pt in r_ohm_pts)
    out.append('<path d="%s" fill="none" stroke="#e67e22" stroke-width="2.2" stroke-dasharray="6,4"/>' % d_ohm)

    esr_pts = []
    for px in range(int(x0), int(x0 + gw + 1), 5):
        norm = (px - x0) / gw
        if norm < 0.75:
            val_di = math.exp(-norm * 4.5) * 10.0
        else:
            val_di = 0.01
        val_ohm = 0.05 if norm < 0.6 else 0.05 + ((norm - 0.6) / 0.4)**1.5 * 0.15
        tot = val_di + val_ohm
        log_tot = math.log10(tot)
        py = y0 + gh * 0.78 - (log_tot - math.log10(0.05)) * 52
        py = max(y0 + 20, min(y0 + gh - 10, py))
        esr_pts.append((px, py))
    d_esr = "M " + " ".join("%.1f,%.1f" % pt for pt in esr_pts)
    out.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.2"/>' % (d_esr, POS))

    # Виноска в зоні між лініями 90 та 206
    out.append(textbox(200, y0 + gh - 35, "Полиця мінімуму ESR", size=10, pad=4, fill="#fdedec", stroke=POS, bold=True)[0])

    # Легенда унизу
    out.append(line(x0 + 60, y0 + gh + 55, x0 + 95, y0 + gh + 55, color=POS, sw=3))
    out.append(text(x0 + 100, y0 + gh + 59, "Сумарний ESR(f)", size=11, color=INK, anchor="start", bold=True))

    out.append(line(x0 + 260, y0 + gh + 55, x0 + 295, y0 + gh + 55, color=FIELD, sw=2, dash="6,4"))
    out.append(text(x0 + 300, y0 + gh + 59, "Втрати в діелектрику R_di", size=11, color=INK, anchor="start"))

    out.append(line(x0 + 500, y0 + gh + 55, x0 + 535, y0 + gh + 55, color="#e67e22", sw=2, dash="6,4"))
    out.append(text(x0 + 540, y0 + gh + 59, "Омічний опір металу R_ohm", size=11, color=INK, anchor="start"))

    render(os.path.join(IMG, "esr-frequency-breakdown.svg"), w, h, *out)


# ── 4. Антирезонансні піки в PDN ─────────────────────────────────────────────
def make_pdn_antiresonance_peaks():
    w, h = 860, 480
    out = []

    out.append(text(w / 2, 26, "Паразитний антирезонансний пік при паралельному з'єднанні (PDN)", size=16, bold=True))

    x0, y0 = 90, 80
    gw, gh = 700, 280
    out.append(rect(x0, y0, gw, gh, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=4))

    f_lbls = ["10 кГц", "100 кГц", "1 МГц", "10 МГц", "100 МГц", "1 ГГц"]
    for i in range(6):
        gx = x0 + i * (gw / 5)
        if 0 < i < 5:
            out.append(line(gx, y0, gx, y0 + gh, color="#e1e4e8", sw=1, dash="4,4"))
        out.append(text(gx, y0 + gh + 18, f_lbls[i], size=11, color=MUTED))
    out.append(text(x0 + gw / 2, y0 + gh + 38, "Частота f", size=12, bold=True))

    z_lbls = ["10 Ом", "1 Ом", "100 мОм", "10 мОм", "1 мОм"]
    for j in range(5):
        gy = y0 + j * (gh / 4)
        if 0 < j < 4:
            out.append(line(x0, gy, x0 + gw, gy, color="#e1e4e8", sw=1, dash="4,4"))
        out.append(text(x0 - 10, gy + 4, z_lbls[j], size=11, color=MUTED, anchor="end"))
    out.append(text(25, y0 + gh / 2, "Імпеданс |Z|", size=12, bold=True, anchor="middle"))

    y_target = y0 + gh * 0.62
    out.append(line(x0, y_target, x0 + gw, y_target, color=POS, sw=1.8, dash="6,3"))
    out.append(text(x0 + gw - 10, y_target - 8, "Цільовий імпеданс Z_target", size=11, color=POS, bold=True, anchor="end"))

    c1_pts = []
    x_srf1 = x0 + gw * 0.32
    y_srf1 = y0 + gh * 0.72
    for px in range(int(x0), int(x0 + gw + 1), 4):
        rf = (px - x_srf1) / 70.0
        xc = math.exp(-rf)
        xl = math.exp(rf)
        z = math.sqrt(0.12**2 + (xl - xc)**2)
        py = y_srf1 - (math.log10(z) - math.log10(0.12)) * 55
        py = max(y0 + 10, min(y0 + gh - 5, py))
        c1_pts.append((px, py))
    d_c1 = "M " + " ".join("%.1f,%.1f" % pt for pt in c1_pts)
    out.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="5,4"/>' % (d_c1, FIELD))

    c2_pts = []
    x_srf2 = x0 + gw * 0.68
    y_srf2 = y0 + gh * 0.88
    for px in range(int(x0), int(x0 + gw + 1), 4):
        rf = (px - x_srf2) / 60.0
        xc = math.exp(-rf)
        xl = math.exp(rf)
        z = math.sqrt(0.04**2 + (xl - xc)**2)
        py = y_srf2 - (math.log10(z) - math.log10(0.04)) * 55
        py = max(y0 + 10, min(y0 + gh - 5, py))
        c2_pts.append((px, py))
    d_c2 = "M " + " ".join("%.1f,%.1f" % pt for pt in c2_pts)
    out.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="5,4"/>' % (d_c2, NEG))

    res_pts = []
    x_anti = x0 + gw * 0.48
    y_anti = y0 + gh * 0.22
    for px in range(int(x0), int(x0 + gw + 1), 4):
        if px < x_srf1:
            py = c1_pts[(px - int(x0)) // 4][1]
        elif px > x_srf2:
            py = c2_pts[(px - int(x0)) // 4][1]
        else:
            norm = (px - x_anti) / (x_srf2 - x_srf1) * 2.0
            peak_shape = math.exp(- (norm * 2.2)**2)
            base_y = min(c1_pts[(px - int(x0)) // 4][1], c2_pts[(px - int(x0)) // 4][1])
            py = base_y * (1 - peak_shape) + y_anti * peak_shape
        res_pts.append((px, py))
    d_res = "M " + " ".join("%.1f,%.1f" % pt for pt in res_pts)
    out.append('<path d="%s" fill="none" stroke="#2c3e50" stroke-width="3"/>' % d_res)

    out.append(circle(x_anti, y_anti, 6, fill=POS, stroke="#ffffff", sw=2))
    out.append(textbox(x_anti, y_anti - 35, "Паралельний антирезонанс!\nESL1 (велика ємність) || C2 (кераміка)\n|Z_peak| перевищує Z_target", size=10, pad=4, fill="#fdedec", stroke=POS, bold=True)[0])

    out.append(text(x_srf1, y_srf1 + 18, "SRF 1 (Bulk)", size=10, color=FIELD, bold=True))
    out.append(text(x_srf2, y_srf2 + 18, "SRF 2 (MLCC)", size=10, color=NEG, bold=True))

    # Легенда над графіком
    out.append(line(x0 + 40, 52, x0 + 70, 52, color=FIELD, sw=2, dash="5,4"))
    out.append(text(x0 + 75, 56, "Cap 1 (Bulk 10 мкФ)", size=11, color=INK, anchor="start"))

    out.append(line(x0 + 260, 52, x0 + 290, 52, color=NEG, sw=2, dash="5,4"))
    out.append(text(x0 + 295, 56, "Cap 2 (MLCC 100 нФ)", size=11, color=INK, anchor="start"))

    out.append(line(x0 + 490, 52, x0 + 520, 52, color="#2c3e50", sw=3))
    out.append(text(x0 + 525, 56, "Сумарний паралельний Z", size=11, color=INK, anchor="start", bold=True))

    render(os.path.join(IMG, "pdn-antiresonance-peaks.svg"), w, h, *out)


# ── 5. Самонагрів та Ripple Current ──────────────────────────────────────────
def make_ripple_current_heating():
    w, h = 840, 380
    out = []

    out.append(text(w / 2, 26, "Тепловий баланс та допустимий пульсуючий струм (Ripple Current)", size=16, bold=True))

    # Ліва частина: тепловий потік
    out.append(rect(40, 60, 360, 290, fill="#fdfefe", stroke="#ccd1d9", sw=1.5, rx=8))
    out.append(text(220, 85, "Тепловий баланс конденсатора", size=14, bold=True))

    out.append(textbox(220, 130, "Пульсуючий змінний струм I_rms\nкрізь внутрішній ESR", size=12, pad=6, fill="#fdedec", stroke=POS, bold=True)[0])
    out.append(arrow(220, 155, 220, 180, color=POS, sw=2))

    out.append(textbox(220, 210, "Внутрішній самонагрів:\nP_loss = I_rms² · ESR(f)  (Вт)", size=12, pad=6, fill="#fef5e7", stroke="#e67e22", bold=True)[0])
    out.append(arrow(220, 235, 220, 260, color="#e67e22", sw=2))

    out.append(textbox(220, 295, "Перегрів корпусу:\nΔT = P_loss · θ_JA ≤ ΔT_max (+5…+10 °C)", size=11, pad=5, fill="#eafaf1", stroke=FIELD, bold=True)[0])

    # Права частина: графік частотного множника Ripple Current
    rx0, ry0 = 440, 80
    rw, rh = 360, 220
    out.append(rect(rx0, ry0, rw, rh, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=4))
    out.append(text(rx0 + rw / 2, ry0 - 10, "Частотний коефіцієнт струму I_ripple(f) / I_ripple(120 Гц)", size=11, bold=True))

    rf_lbls = ["120 Гц", "1 кГц", "10 кГц", "100 кГц"]
    for i in range(4):
        gx = rx0 + i * (rw / 3)
        if 0 < i < 3:
            out.append(line(gx, ry0, gx, ry0 + rh, color="#e1e4e8", sw=1, dash="4,4"))
        out.append(text(gx, ry0 + rh + 16, rf_lbls[i], size=10, color=MUTED))

    rm_lbls = ["2.0×", "1.5×", "1.0×", "0.5×"]
    for j in range(4):
        gy = ry0 + j * (rh / 3)
        if 0 < j < 3:
            out.append(line(rx0, gy, rx0 + rw, gy, color="#e1e4e8", sw=1, dash="4,4"))
        out.append(text(rx0 - 6, gy + 4, rm_lbls[j], size=10, color=MUTED, anchor="end"))

    mult_pts = [
        (rx0, ry0 + rh * 0.667),
        (rx0 + rw * 0.333, ry0 + rh * 0.48),
        (rx0 + rw * 0.667, ry0 + rh * 0.28),
        (rx0 + rw, ry0 + rh * 0.16)
    ]
    d_m = "M %.1f,%.1f Q %.1f,%.1f %.1f,%.1f T %.1f,%.1f" % (
        mult_pts[0][0], mult_pts[0][1],
        mult_pts[1][0] - 20, mult_pts[1][1] + 10,
        mult_pts[2][0], mult_pts[2][1],
        mult_pts[3][0], mult_pts[3][1]
    )
    out.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (d_m, FIELD))
    for pt in mult_pts:
        out.append(circle(pt[0], pt[1], 4.5, fill=FIELD, stroke="#ffffff", sw=1.5))

    out.append(textbox(rx0 + rw / 2, ry0 + rh * 0.85, "На високих частотах ESR нижчий,\nтому допустимий струм I_ripple зростає", size=10, pad=4, fill="#ffffff", stroke=MUTED)[0])

    render(os.path.join(IMG, "ripple-current-heating.svg"), w, h, *out)


if __name__ == "__main__":
    make_equivalent_circuit_model()
    make_impedance_frequency_curve()
    make_esr_frequency_breakdown()
    make_pdn_antiresonance_peaks()
    make_ripple_current_heating()
    print("Всі SVG-фігури успішно згенеровано у ./img/")
