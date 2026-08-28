# -*- coding: utf-8 -*-
"""Фігури до теми «Справжній RMS проти середньовипрямленого».
Запуск: python figs.py   → створює SVG у теці ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Фізичний зміст RMS: тепловий еквівалент ─────────────────────────────
def fig_heating_equivalent():
    W, H = 860, 420
    f = [text(W / 2, 28, "Фізичний зміст RMS: еквівалент теплової потужності на резисторі", size=15, bold=True)]

    # --- Ліва панель: Змінна напруга v(t) ---
    lx = 40
    f.append(rect(lx, 55, 360, 335, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    f.append(text(lx + 180, 82, "Змінний струм / напруга v(t)", size=13, bold=True, color=NEG))

    # Схема ліворуч: джерело AC + резистор
    # Джерело AC
    f.append(circle(lx + 80, 160, 24, fill="#ffffff", stroke=NEG, sw=2))
    # Хвиля всередині джерела
    f.append('<path d="M%d %d Q%d %d %d %d T%d %d" fill="none" stroke="%s" stroke-width="2"/>'
             % (lx + 68, 160, lx + 74, 150, lx + 80, 160, lx + 92, 160, NEG))
    f.append(text(lx + 80, 200, "v(t) = V_pk·sin(ωt)", size=10.5, color=NEG, bold=True))

    # Резистор-нагрівач R
    f.append(rect(lx + 240, 135, 45, 50, fill="#fff3e0", stroke=POS, sw=1.8, rx=4))
    f.append(text(lx + 262, 164, "R", size=13, bold=True, color=POS))
    f.append(text(lx + 262, 200, "Нагрівач", size=10.5, color=MUTED))

    # З'єднувальні дроти
    f.append(line(lx + 80, 136, lx + 80, 120, color=LINE, sw=1.8))
    f.append(line(lx + 80, 120, lx + 262, 120, color=LINE, sw=1.8))
    f.append(line(lx + 262, 120, lx + 262, 135, color=LINE, sw=1.8))
    f.append(line(lx + 80, 184, lx + 80, 225, color=LINE, sw=1.8))
    f.append(line(lx + 80, 225, lx + 262, 225, color=LINE, sw=1.8))
    f.append(line(lx + 262, 225, lx + 262, 185, color=LINE, sw=1.8))

    # Теплові хвилі вгору
    for hx in [lx + 248, lx + 262, lx + 276]:
        f.append('<path d="M%d 130 Q%d 120 %d 110 T%d 95" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="2 2"/>'
                 % (hx, hx + 4, hx, hx, POS))

    # Графік миттєвої потужності p(t)
    gx, gy, gw, gh = lx + 40, 270, 280, 80
    f.append(line(gx, gy + gh / 2, gx + gw, gy + gh / 2, color=MUTED, sw=1))
    f.append(line(gx, gy + gh, gx, gy, color=MUTED, sw=1.2))

    # Крива потужності p(t) = v^2/R = (Vpk^2/R) * sin^2(wt) (завжди >= 0)
    pts = []
    for i in range(gw + 1):
        x = gx + i
        t = (i / gw) * 4 * math.pi
        p_val = math.sin(t) ** 2
        y = (gy + gh) - p_val * (gh - 10)
        pts.append((x, y))
    d_path = "M " + " ".join("%.1f,%.1f" % pt for pt in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (d_path, POS))

    # Рівень середньої потужності P_avg
    p_avg_y = (gy + gh) - 0.5 * (gh - 10)
    f.append(line(gx, p_avg_y, gx + gw, p_avg_y, color="#d35400", sw=1.6, dash="4 3"))
    f.append(text(gx + gw - 4, p_avg_y - 6, "P_avg = V_RMS² / R", size=10, color="#d35400", bold=True, anchor="end"))
    f.append(text(gx + 10, gy + 12, "p(t) = v²(t) / R (пульсує з 2f)", size=9.5, color=MUTED, anchor="start"))

    # --- Права панель: Еквівалентна постійна напруга V_DC ---
    rx = 460
    f.append(rect(rx, 55, 360, 335, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    f.append(text(rx + 180, 82, "Постійний струм / напруга V_DC = V_RMS", size=13, bold=True, color=FIELD))

    # Схема праворуч: джерело DC + резистор
    # Джерело DC (батарея)
    f.append(circle(rx + 80, 160, 24, fill="#ffffff", stroke=FIELD, sw=2))
    f.append(line(rx + 72, 154, rx + 88, 154, color=FIELD, sw=2))
    f.append(line(rx + 80, 146, rx + 80, 162, color=FIELD, sw=2))
    f.append(line(rx + 74, 168, rx + 86, 168, color=FIELD, sw=2))
    f.append(text(rx + 80, 200, "V_DC = V_RMS", size=10.5, color=FIELD, bold=True))

    # Резистор-нагрівач R
    f.append(rect(rx + 240, 135, 45, 50, fill="#fff3e0", stroke=POS, sw=1.8, rx=4))
    f.append(text(rx + 262, 164, "R", size=13, bold=True, color=POS))
    f.append(text(rx + 262, 200, "Той самий нагрівач", size=10.5, color=MUTED))

    # З'єднувальні дроти
    f.append(line(rx + 80, 136, rx + 80, 120, color=LINE, sw=1.8))
    f.append(line(rx + 80, 120, rx + 262, 120, color=LINE, sw=1.8))
    f.append(line(rx + 262, 120, rx + 262, 135, color=LINE, sw=1.8))
    f.append(line(rx + 80, 184, rx + 80, 225, color=LINE, sw=1.8))
    f.append(line(rx + 80, 225, rx + 262, 225, color=LINE, sw=1.8))
    f.append(line(rx + 262, 225, rx + 262, 185, color=LINE, sw=1.8))

    # Теплові хвилі вгору
    for hx in [rx + 248, rx + 262, rx + 276]:
        f.append('<path d="M%d 130 Q%d 120 %d 110 T%d 95" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="2 2"/>'
                 % (hx, hx + 4, hx, hx, POS))

    # Графік постійної потужності P_DC
    rgx, rgy, rgw, rgh = rx + 40, 270, 280, 80
    f.append(line(rgx, rgy + rgh / 2, rgx + rgw, rgy + rgh / 2, color=MUTED, sw=1))
    f.append(line(rgx, rgy + rgh, rgx, rgy, color=MUTED, sw=1.2))

    # Стала потужність
    rp_y = (rgy + rgh) - 0.5 * (rgh - 10)
    f.append(line(rgx, rp_y, rgx + rgw, rp_y, color=POS, sw=2))
    f.append(text(rgx + rgw - 4, rp_y - 6, "P_DC = V_DC² / R = P_avg", size=10, color=POS, bold=True, anchor="end"))
    f.append(text(rgx + 10, rgy + 12, "Постійне виділення тепла Q", size=9.5, color=MUTED, anchor="start"))

    # Центральна зв'язка - знак еквівалентності тепла
    tb, _, _ = textbox(W / 2, 210, "ОДНАКОВЕ\nТЕПЛО Q\nQ = P_avg · Δt", size=11, fill="#fef3c7", stroke="#d97706", color="#92400e", bold=True)
    f.append(tb)
    f.append(arrow(W / 2 - 38, 210, lx + 295, 210, color="#d97706", sw=1.8))
    f.append(arrow(W / 2 + 38, 210, rx + 65, 210, color="#d97706", sw=1.8))

    return render(os.path.join(IMG, "fig-heating-equivalent.svg"), W, H, *f)


# ── 2. Порівняння: Пік, Середньовипрямлене (MAV) і True RMS ────────────────
def fig_rectified_vs_rms():
    W, H = 860, 440
    f = [text(W / 2, 26, "Середньовипрямлене (MAV × 1.111) проти True RMS для двох форм сигналу", size=15, bold=True)]

    # --- Ліва панель: Чистий синус ---
    lx = 30
    f.append(rect(lx, 48, 385, 370, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    f.append(text(lx + 192, 72, "1. Чистий синусоїдний сигнал", size=13, bold=True, color=FIELD))

    # Осцилограма синуса
    ox, oy, ow, oh = lx + 35, 88, 320, 160
    f.append(line(ox, oy + oh / 2, ox + ow, oy + oh / 2, color=MUTED, sw=1))
    f.append(line(ox, oy + oh, ox, oy, color=MUTED, sw=1.2))

    # Синусоїда та випрямлений модуль
    sin_pts = []
    mav_pts = []
    for i in range(ow + 1):
        x = ox + i
        t = (i / ow) * 2 * math.pi
        v = math.sin(t)
        y = oy + oh / 2 - v * 65
        sin_pts.append((x, y))
        y_mav = oy + oh / 2 - abs(v) * 65
        mav_pts.append((x, y_mav))

    # Випрямлений сигнал (модуль |v(t)|)
    d_mav = "M " + " ".join("%.1f,%.1f" % pt for pt in mav_pts)
    f.append('<path d="%s" fill="#eff6ff" stroke="%s" stroke-width="1.2" stroke-dasharray="3 3"/>' % (d_mav, NEG))

    # Початковий синус
    d_sin = "M " + " ".join("%.1f,%.1f" % pt for pt in sin_pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (d_sin, INK))

    # Горизонтальні рівні
    y_pk = oy + oh / 2 - 65
    y_rms = oy + oh / 2 - 0.7071 * 65
    y_mav_lvl = oy + oh / 2 - 0.6366 * 65

    f.append(line(ox, y_pk, ox + ow, y_pk, color=POS, sw=1.2, dash="3 2"))
    f.append(text(ox + ow - 4, y_pk - 4, "V_peak = 1.000 (100%)", size=9.5, color=POS, bold=True, anchor="end"))

    f.append(line(ox, y_rms, ox + ow, y_rms, color=FIELD, sw=1.6))
    f.append(text(ox + ow - 4, y_rms - 4, "V_RMS = 0.707 (True RMS)", size=9.5, color=FIELD, bold=True, anchor="end"))

    f.append(line(ox, y_mav_lvl, ox + ow, y_mav_lvl, color=NEG, sw=1.4, dash="4 2"))
    f.append(text(ox + ow - 4, y_mav_lvl + 12, "V_MAV = 0.637 (середнє модуля)", size=9.5, color=NEG, bold=True, anchor="end"))

    # Підсумок розрахунку ліворуч
    f.append(rect(lx + 15, 260, 355, 145, fill="#f8fafc", stroke=LINE, sw=1, rx=6))
    f.append(text(lx + 25, 282, "Калібрування простого мультиметра:", size=11, bold=True, anchor="start"))
    f.append(text(lx + 25, 304, "• Виміряно: V_MAV = (2/π)·V_pk ≈ 0.6366 · V_pk", size=10.5, color=INK, anchor="start"))
    f.append(text(lx + 25, 326, "• Множник шкали: k_f = 0.7071 / 0.6366 = 1.1107 ≈ 1.111", size=10.5, color=NEG, bold=True, anchor="start"))
    f.append(text(lx + 25, 348, "• Показ приладу: V_показ = 1.111 × V_MAV = 0.707 · V_pk", size=10.5, color=FIELD, bold=True, anchor="start"))
    f.append(text(lx + 25, 372, "✓ Похибка = 0.0% (показ збігається з True RMS)", size=11, color=FIELD, bold=True, anchor="start"))
    f.append(text(lx + 25, 392, "  Пік-фактор: CF = V_pk / V_RMS = √2 ≈ 1.414", size=10, color=MUTED, anchor="start"))

    # --- Права панель: Імпульсний сигнал ІБЖ / ШІМ (D = 10%) ---
    rx = 445
    f.append(rect(rx, 48, 385, 370, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    f.append(text(rx + 192, 72, "2. Імпульсний струм ІБЖ (ШІМ D = 10%)", size=13, bold=True, color=POS))

    # Осцилограма імпульсів
    rox, roy, row, roh = rx + 35, 88, 320, 160
    f.append(line(rox, roy + roh - 20, rox + row, roy + roh - 20, color=MUTED, sw=1))
    f.append(line(rox, roy + roh, rox, roy, color=MUTED, sw=1.2))

    # Прямокутні короткі імпульси D = 10%
    f.append(rect(rox + 20, roy + roh - 20 - 100, 20, 100, fill="#fee2e2", stroke=POS, sw=2))
    f.append(rect(rox + 180, roy + roh - 20 - 100, 20, 100, fill="#fee2e2", stroke=POS, sw=2))

    y_rpk = roy + roh - 20 - 100
    y_rrms = roy + roh - 20 - 31.6
    y_rdisp = roy + roh - 20 - 11.1

    f.append(line(rox, y_rpk, rox + row, y_rpk, color=POS, sw=1.2, dash="3 2"))
    f.append(text(rox + row - 4, y_rpk - 4, "V_peak = 1.000", size=9.5, color=POS, bold=True, anchor="end"))

    f.append(line(rox, y_rrms, rox + row, y_rrms, color=FIELD, sw=1.8))
    f.append(text(rox + row - 4, y_rrms - 4, "V_RMS = 0.316 (Справжній нагрів)", size=9.5, color=FIELD, bold=True, anchor="end"))

    f.append(line(rox, y_rdisp, rox + row, y_rdisp, color=NEG, sw=1.6, dash="4 2"))
    f.append(text(rox + row - 4, y_rdisp + 12, "V_показ = 0.111 (MAV × 1.111)", size=9.5, color=NEG, bold=True, anchor="end"))

    # Підсумок розрахунку праворуч
    f.append(rect(rx + 15, 260, 355, 145, fill="#fff1f2", stroke="#fda4af", sw=1, rx=6))
    f.append(text(rx + 25, 282, "Катастрофа простого вимірювача:", size=11, bold=True, color="#9f1239", anchor="start"))
    f.append(text(rx + 25, 304, "• Справжнє значення: V_RMS = V_pk·√D = 0.316 · V_pk", size=10.5, color=FIELD, bold=True, anchor="start"))
    f.append(text(rx + 25, 326, "• Виміряно MAV: V_MAV = V_pk·D = 0.100 · V_pk", size=10.5, color=INK, anchor="start"))
    f.append(text(rx + 25, 348, "• Показ приладу: V_показ = 1.111 × 0.100 = 0.111 · V_pk", size=10.5, color=NEG, bold=True, anchor="start"))
    f.append(text(rx + 25, 372, "✖ ПОХИБКА = −64.9% (заниження у 2.85 раза!)", size=11, color="#e11d48", bold=True, anchor="start"))
    f.append(text(rx + 25, 392, "  Пік-фактор: CF = 1 / √0.1 ≈ 3.16 (небезпека пожежі)", size=10, color="#9f1239", anchor="start"))

    return render(os.path.join(IMG, "fig-rectified-vs-rms.svg"), W, H, *f)


# ── 3. Пік-фактор (Crest Factor) та обмеження динамічного діапазону ─────────
def fig_crest_factor_waveforms():
    W, H = 860, 420
    f = [text(W / 2, 26, "Пік-фактор (CF = V_peak / V_RMS) та насичення аналогових перетворювачів", size=15, bold=True)]

    col_w = 190
    forms = [
        ("Меандр (Square)", "CF = 1.000", "V_RMS = V_pk", "V_MAV = V_pk", "Похибка: +11.1%", "#2563eb", "square"),
        ("Синусоїда (Sine)", "CF = 1.414", "V_RMS = 0.707·V_pk", "V_MAV = 0.637·V_pk", "Похибка: 0.0%", "#16a34a", "sine"),
        ("Трикутник (Triangle)", "CF = 1.732", "V_RMS = 0.577·V_pk", "V_MAV = 0.500·V_pk", "Похибка: −3.8%", "#d97706", "triangle"),
        ("Імпульси (CF = 5)", "CF = 5.000", "V_RMS = 0.200·V_pk", "V_MAV = 0.040·V_pk", "Похибка: −77.8%", "#dc2626", "pulse")
    ]

    for idx, (title, cf_str, rms_str, mav_str, err_str, col_color, shape) in enumerate(forms):
        cx = 25 + idx * (col_w + 15)
        f.append(rect(cx, 55, col_w, 245, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
        f.append(text(cx + col_w / 2, 75, title, size=11, bold=True, color=INK))
        f.append(text(cx + col_w / 2, 92, cf_str, size=12, bold=True, color=col_color))

        gx, gy, gw, gh = cx + 15, 105, col_w - 30, 80
        f.append(line(gx, gy + gh / 2, gx + gw, gy + gh / 2, color="#e2e8f0", sw=1))
        f.append(line(gx, gy + gh, gx, gy, color="#cbd5e1", sw=1))

        if shape == "square":
            f.append('<path d="M%d %d L%d %d L%d %d L%d %d L%d %d L%d %d L%d %d" fill="none" stroke="%s" stroke-width="1.8"/>'
                     % (gx, gy + 10, gx + gw/4, gy + 10, gx + gw/4, gy + gh - 10, gx + gw*3/4, gy + gh - 10, gx + gw*3/4, gy + 10, gx + gw, gy + 10, gx + gw, gy + gh - 10, col_color))
        elif shape == "sine":
            s_pts = []
            for i in range(int(gw) + 1):
                t = (i / gw) * 2 * math.pi
                s_pts.append((gx + i, gy + gh / 2 - math.sin(t) * (gh / 2 - 10)))
            f.append('<path d="M %s" fill="none" stroke="%s" stroke-width="1.8"/>' % (" ".join("%.1f,%.1f" % pt for pt in s_pts), col_color))
        elif shape == "triangle":
            f.append('<path d="M%d %d L%d %d L%d %d L%d %d" fill="none" stroke="%s" stroke-width="1.8"/>'
                     % (gx, gy + gh / 2, gx + gw/4, gy + 10, gx + gw*3/4, gy + gh - 10, gx + gw, gy + gh / 2, col_color))
        elif shape == "pulse":
            f.append('<path d="M%d %d L%d %d L%d %d L%d %d L%d %d" fill="none" stroke="%s" stroke-width="1.8"/>'
                     % (gx, gy + gh - 10, gx + 15, gy + gh - 10, gx + 15, gy + 10, gx + 25, gy + 10, gx + 25, gy + gh - 10, col_color))
            f.append(line(gx + 25, gy + gh - 10, gx + gw, gy + gh - 10, color=col_color, sw=1.8))

        f.append(text(cx + col_w / 2, 205, rms_str, size=9.5, color=INK))
        f.append(text(cx + col_w / 2, 222, mav_str, size=9.5, color=MUTED))
        f.append(text(cx + col_w / 2, 242, err_str, size=10.5, bold=True, color=col_color))

    bx, by, bw, bh = 25, 312, 810, 95
    f.append(rect(bx, by, bw, bh, fill="#fffbeb", stroke="#fde68a", sw=1.2, rx=6))
    f.append(text(bx + 20, by + 24, "Метрологічна межа апаратних RMS-перетворювачів (AD736, AD8436, LTC1966):", size=11.5, bold=True, color="#92400e", anchor="start"))
    f.append(text(bx + 20, by + 46, "1. Динамічний діапазон піків: піковий вхід не може перевищувати шини живлення (V_pk ≤ V_supply - 1.5V). При CF = 5 шкала вимірювання RMS падає у 5 разів!", size=10, color=INK, anchor="start"))
    f.append(text(bx + 20, by + 66, "2. Смуга пропускання ядра: високий CF означає потужні гармоніки (f_h >> f_0). Смуга пропускання AD736 спадає з 200 кГц (CF=1) до <10 кГц (CF=5).", size=10, color=INK, anchor="start"))
    f.append(text(bx + 20, by + 86, "3. Додаткова похибка нелінійності: паспорт гарантує похибку 0.3% при CF=1..2, але додає +1.5% при CF=3 та +3..5% при CF=5.", size=10, color="#b45309", bold=True, anchor="start"))

    return render(os.path.join(IMG, "fig-crest-factor-waveforms.svg"), W, H, *f)


# ── 4. Структура аналогового True RMS ядра (Implicit method) ────────────────
def fig_analog_rms_core():
    W, H = 860, 400
    f = [text(W / 2, 26, "Апаратний True RMS конвертер: ядро непрямого обчислення (Implicit Core)", size=15, bold=True)]

    f.append(text(40, 150, "Вхідний\nсигнал\nV_in(t)", size=11, bold=True, color=NEG))
    f.append(arrow(65, 150, 115, 150, color=LINE, sw=1.8))

    b1 = fitbox(115, 115, 130, 70, "Прецизійний\nвипрямляч\n|V_in|", size=11, bold=True, fill="#eff6ff", stroke=NEG)
    f.append(b1)

    f.append(arrow(245, 150, 295, 150, color=LINE, sw=1.8))
    f.append(text(270, 140, "|V_in|", size=10, color=NEG, bold=True))

    b2 = fitbox(295, 105, 175, 90, "Логарифмічне ядро\n(Log-Antilog Cell)\nI_c = V_in² / V_out", size=11.5, bold=True, fill="#fef3c7", stroke="#d97706")
    f.append(b2)

    f.append(arrow(470, 150, 520, 150, color=LINE, sw=1.8))
    f.append(text(495, 140, "I_c(t)", size=10, color="#d97706", bold=True))

    b3 = fitbox(520, 115, 140, 70, "Фільтр середнього\n(Low-Pass Filter)\nI_avg = Avg(I_c)", size=11, bold=True, fill="#ecfdf5", stroke=FIELD)
    f.append(b3)

    f.append(line(590, 185, 590, 230, color=LINE, sw=1.8))
    f.append(line(575, 230, 605, 230, color=FIELD, sw=2.2))
    f.append(line(575, 236, 605, 236, color=FIELD, sw=2.2))
    f.append(line(590, 236, 590, 260, color=LINE, sw=1.8))
    f.append(line(580, 260, 600, 260, color=LINE, sw=2))
    f.append(line(584, 264, 596, 264, color=LINE, sw=1.6))
    f.append(line(588, 268, 592, 268, color=LINE, sw=1.2))
    f.append(text(640, 235, "C_AV (Averaging\nCapacitor)", size=10.5, color=FIELD, bold=True, anchor="start"))

    f.append(arrow(660, 150, 710, 150, color=LINE, sw=1.8))

    b4 = fitbox(710, 115, 110, 70, "Вихідний\nбуфер\nV_out", size=11, bold=True, fill="#f5f3ff", stroke="#7c3aed")
    f.append(b4)

    f.append(arrow(820, 150, 845, 150, color=LINE, sw=1.8))
    f.append(text(835, 135, "V_out", size=11, bold=True, color="#7c3aed"))

    f.append(line(765, 185, 765, 305, color="#7c3aed", sw=1.8))
    f.append(line(765, 305, 382, 305, color="#7c3aed", sw=1.8))
    f.append(arrow(382, 305, 382, 195, color="#7c3aed", sw=1.8))
    f.append(text(570, 322, "Петля зворотного зв'язку ділення на V_out:  V_out = Avg( V_in² / V_out )  ⇒  V_out² = Avg(V_in²)  ⇒  V_out = √( Avg(V_in²) )", size=10.5, bold=True, color="#6d28d9"))

    bx, by, bw, bh = 40, 345, 780, 45
    f.append(rect(bx, by, bw, bh, fill="#f8fafc", stroke=LINE, sw=1, rx=4))
    f.append(text(bx + bw/2, by + 18, "Чому непрямий метод (Implicit): пряме обчислення V_in² звужує динамічний діапазон (1 мВ² = 1 мкВ — тоне в шумах).", size=10, color=INK))
    f.append(text(bx + bw/2, by + 34, "Непряме ділення в лог-ядрі тримає внутрішні напруги в масштабі першого степеня, забезпечуючи динамічний діапазон > 60 дБ.", size=10, color=FIELD, bold=True))

    return render(os.path.join(IMG, "fig-analog-rms-core.svg"), W, H, *f)


# ── 5. DSP тракт обчислення True RMS на мікроконтролері ─────────────────────
def fig_dsp_pipeline():
    W, H = 880, 440
    f = [text(W / 2, 26, "Цифровий тракт обчислення True RMS у реальному часі на мікроконтролері", size=15, bold=True)]

    b_adc = fitbox(25, 90, 115, 95, "АЦП (ADC)\nВідліки x[n]\nf_s ≥ 10 кГц\n12..16 біт", size=11, bold=True, fill="#f1f5f9", stroke=LINE)
    f.append(b_adc)
    f.append(arrow(140, 137, 175, 137, color=LINE, sw=1.8))

    b_dc = fitbox(175, 80, 165, 115, "DC-Blocker (IIR)\ny[n] = x[n] - x[n-1]\n       + α·y[n-1]\nУсунення V_ref/2\nта зміщення нуля", size=10.5, bold=True, fill="#eff6ff", stroke=NEG)
    f.append(b_dc)
    f.append(arrow(340, 137, 375, 137, color=LINE, sw=1.8))
    f.append(text(357, 127, "y[n]", size=10, color=NEG, bold=True))

    b_sq = fitbox(375, 80, 145, 115, "Квадратор (MAC)\nAccum += y[n]²\nФіксована: 64-біт\nРухома: FPU\nQ15/Q31 множення", size=10.5, bold=True, fill="#fef3c7", stroke="#d97706")
    f.append(b_sq)
    f.append(arrow(520, 137, 555, 137, color=LINE, sw=1.8))
    f.append(text(537, 127, "∑ y²", size=10, color="#d97706", bold=True))

    b_zc = fitbox(555, 80, 155, 115, "Zero-Crossing &\nСинхронізація\nПідрахунок N\nточно за M періодів\n(без витоку спектра)", size=10.5, bold=True, fill="#ecfdf5", stroke=FIELD)
    f.append(b_zc)
    f.append(arrow(710, 137, 745, 137, color=LINE, sw=1.8))

    b_rt = fitbox(745, 80, 110, 115, "Корінь\n(Root)\nMean = ∑y² / N\nRMS = √Mean\nQ-sqrt / Newton", size=10.5, bold=True, fill="#f5f3ff", stroke="#7c3aed")
    f.append(b_rt)

    f.append(arrow(855, 137, 875, 137, color=LINE, sw=1.8))

    f.append(rect(25, 225, 400, 195, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    f.append(text(40, 248, "1. Усунення постійної складової (DC Offset):", size=11, bold=True, color=NEG, anchor="start"))
    f.append(text(40, 270, "• Катастрофічне скасування у двопрохідній формулі:", size=10, color=POS, bold=True, anchor="start"))
    f.append(text(40, 288, "  Var = E[x²] - (E[x])²  ⇒ при малій AC і великій DC", size=9.5, color=MUTED, anchor="start"))
    f.append(text(40, 304, "  віднімання двох близьких великих чисел нищить молодші біти!", size=9.5, color=POS, anchor="start"))
    f.append(text(40, 326, "• Однопрохідний рекурсивний IIR фільтр (DC-Blocker):", size=10, color=FIELD, bold=True, anchor="start"))
    f.append(text(40, 344, "  y[n] = x[n] - x[n-1] + α · y[n-1],  де α = 1 - 2π(f_c/f_s)", size=9.5, color=INK, anchor="start"))
    f.append(text(40, 362, "  При f_s = 10 кГц, f_c = 2 Гц: α ≈ 0.9987 (або Q15: 32725)", size=9.5, color=INK, anchor="start"))
    f.append(text(40, 380, "  Зрізає дрейф нуля, не вимагаючи збереження всього масиву в RAM.", size=9.5, color=FIELD, anchor="start"))

    f.append(rect(455, 225, 400, 195, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    f.append(text(470, 248, "2. Синхронізація вибірки (Zero-Crossing):", size=11, bold=True, color=FIELD, anchor="start"))
    f.append(text(470, 270, "• Несинхронне прямокутне вікно (наприклад, рівно 1000 семплів):", size=10, color=POS, bold=True, anchor="start"))
    f.append(text(470, 288, "  Якщо вікно містить 5.3 періоду сигналу, неповний залишок (0.3 T)", size=9.5, color=MUTED, anchor="start"))
    f.append(text(470, 304, "  дає пульсації показу RMS (Spectral Leakage / биття) до 5..10%.", size=9.5, color=POS, anchor="start"))
    f.append(text(470, 326, "• Когерентне інтегрування за M повних періодів:", size=10, color=FIELD, bold=True, anchor="start"))
    f.append(text(470, 344, "  Компаратор або програмний гістерезисний Zero-Cross детектор", size=9.5, color=INK, anchor="start"))
    f.append(text(470, 362, "  замикає накопичення суми квадратів строго при переході через нуль.", size=9.5, color=INK, anchor="start"))
    f.append(text(470, 380, "  Результат: похибка усереднення падає практично до рівня шуму АЦП.", size=9.5, color=FIELD, anchor="start"))

    return render(os.path.join(IMG, "fig-dsp-pipeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_heating_equivalent()
    fig_rectified_vs_rms()
    fig_crest_factor_waveforms()
    fig_analog_rms_core()
    fig_dsp_pipeline()
    print("All figures generated successfully.")
