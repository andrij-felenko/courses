# -*- coding: utf-8 -*-
"""Фігури до статті «Тракт одного давача: від термістора до °C на екрані»
(root/course/embedded/trakt-odnoho-davacha).

Чотири змістовні інженерні фігури:
  1) signal-chain-schematic.svg  — Повний наскрізний вимірювальний ланцюг (дільник, захист, RC-ФНЧ, SAR АЦП)
  2) ratiometric-principle.svg   — Логометричний вимір: взаємне скасування дрейфу напруги живлення
  3) sampling-settling-curve.svg — Експоненційний процес заряду C_sample та вибір t_sample під ½ LSB
  4) lut-piecewise-linear.svg    — Таблична кусково-лінійна інтерполяція нелінійної характеристики NTC
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def path_tag(d, stroke=LINE, sw=1.5, fill="none", dash=None):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>' %
            (d, fill, stroke, sw, d_attr))


# ── 1. Наскрізний вимірювальний ланцюг ─────────────────────────────────────────
def fig_signal_chain():
    W, H = 880, 310
    els = []

    # Заголовок
    els.append(text(W / 2, 28, "Наскрізний аналогово-цифровий вимірювальний тракт NTC-термістора", size=15, bold=True))

    # Блок 1: Дільник напруги
    b1_x, b1_y, b1_w, b1_h = 30, 55, 200, 230
    els.append(rect(b1_x, b1_y, b1_w, b1_h, fill=FILL, stroke=MUTED, sw=1.2, rx=6))
    els.append(text(b1_x + b1_w / 2, b1_y + 22, "1. Вхідний дільник", size=13, bold=True, color=INK))

    # Схема дільника
    # Лінія живлення зверху
    els.append(line(b1_x + 80, b1_y + 35, b1_x + 80, b1_y + 55, color=POS, sw=2))
    els.append(text(b1_x + 95, b1_y + 48, "VDDA / VREF", size=11, color=POS, bold=True, anchor="start"))
    
    # Резистор R_ref
    els.append(rect(b1_x + 68, b1_y + 55, 24, 40, fill=BG, stroke=INK, sw=1.5))
    els.append(text(b1_x + 105, b1_y + 74, "R_ref", size=12, bold=True, anchor="start"))
    els.append(text(b1_x + 105, b1_y + 90, "10 кОм 0.1%", size=10, color=MUTED, anchor="start"))

    # Середня точка
    els.append(line(b1_x + 80, b1_y + 95, b1_x + 80, b1_y + 130, color=INK, sw=2))
    els.append(circle(b1_x + 80, b1_y + 115, 3.5, fill=INK, stroke=INK))
    els.append(text(b1_x + 50, b1_y + 118, "V_div", size=12, bold=True, color=FIELD))

    # Термістор R_ntc
    els.append(rect(b1_x + 68, b1_y + 130, 24, 40, fill=BG, stroke=INK, sw=1.5))
    # Діагональна лінія зі стрілкою/поличкою для позначення терморезистора
    els.append(line(b1_x + 62, b1_y + 172, b1_x + 98, b1_y + 128, color=INK, sw=1.4))
    els.append(line(b1_x + 56, b1_y + 172, b1_x + 62, b1_y + 172, color=INK, sw=1.4))
    els.append(text(b1_x + 105, b1_y + 148, "R_ntc (t°)", size=12, bold=True, anchor="start", color=POS))
    els.append(text(b1_x + 105, b1_y + 164, "10 кОм NTC", size=10, color=MUTED, anchor="start"))

    # Земля
    els.append(line(b1_x + 80, b1_y + 170, b1_x + 80, b1_y + 195, color=INK, sw=2))
    els.append(line(b1_x + 65, b1_y + 195, b1_x + 95, b1_y + 195, color=INK, sw=2))
    els.append(line(b1_x + 70, b1_y + 200, b1_x + 90, b1_y + 200, color=INK, sw=1.5))
    els.append(line(b1_x + 75, b1_y + 205, b1_x + 85, b1_y + 205, color=INK, sw=1.2))
    els.append(text(b1_x + b1_w / 2, b1_y + 222, "Логометричне джерело", size=10, color=MUTED))

    # Зв'язок до Блоку 2
    els.append(line(b1_x + 80, b1_y + 115, b1_x + b1_w, b1_y + 115, color=INK, sw=2))
    els.append(arrow(b1_x + b1_w, b1_y + 115, b1_x + b1_w + 25, b1_y + 115, color=INK, sw=2))

    # Блок 2: Захист та RC-фільтр
    b2_x, b2_y, b2_w, b2_h = 265, 55, 260, 230
    els.append(rect(b2_x, b2_y, b2_w, b2_h, fill=FILL, stroke=MUTED, sw=1.2, rx=6))
    els.append(text(b2_x + b2_w / 2, b2_y + 22, "2. Захист та Anti-Aliasing", size=13, bold=True, color=INK))

    # Вхідна лінія
    els.append(line(b2_x, b2_y + 115, b2_x + 40, b2_y + 115, color=INK, sw=2))
    els.append(circle(b2_x + 40, b2_y + 115, 3, fill=INK, stroke=INK))

    # TVS / ESD супресор на вході
    els.append(line(b2_x + 40, b2_y + 115, b2_x + 40, b2_y + 145, color=INK, sw=1.5))
    els.append(rect(b2_x + 32, b2_y + 145, 16, 26, fill=BG, stroke=NEG, sw=1.5))
    els.append(text(b2_x + 40, b2_y + 162, "TVS", size=9, bold=True, color=NEG))
    els.append(line(b2_x + 40, b2_y + 171, b2_x + 40, b2_y + 195, color=INK, sw=1.5))
    els.append(line(b2_x + 30, b2_y + 195, b2_x + 50, b2_y + 195, color=INK, sw=1.5))
    els.append(text(b2_x + 40, b2_y + 215, "ESD-захист", size=10, color=MUTED))

    # Фільтровий резистор R_f
    els.append(line(b2_x + 40, b2_y + 115, b2_x + 75, b2_y + 115, color=INK, sw=2))
    els.append(rect(b2_x + 75, b2_y + 103, 38, 24, fill=BG, stroke=INK, sw=1.5))
    els.append(text(b2_x + 94, b2_y + 119, "R_f", size=12, bold=True))
    els.append(text(b2_x + 94, b2_y + 95, "1 кОм", size=10, color=MUTED))

    # Конденсатор C_f
    els.append(line(b2_x + 113, b2_y + 115, b2_x + 175, b2_y + 115, color=INK, sw=2))
    els.append(circle(b2_x + 175, b2_y + 115, 3, fill=INK, stroke=INK))
    els.append(line(b2_x + 175, b2_y + 115, b2_x + 175, b2_y + 145, color=INK, sw=1.5))
    # Обкладки конденсатора
    els.append(line(b2_x + 162, b2_y + 145, b2_x + 188, b2_y + 145, color=INK, sw=2))
    els.append(line(b2_x + 162, b2_y + 152, b2_x + 188, b2_y + 152, color=INK, sw=2))
    els.append(line(b2_x + 175, b2_y + 152, b2_x + 175, b2_y + 195, color=INK, sw=1.5))
    els.append(line(b2_x + 165, b2_y + 195, b2_x + 185, b2_y + 195, color=INK, sw=1.5))
    els.append(text(b2_x + 205, b2_y + 150, "C_f", size=12, bold=True, anchor="start"))
    els.append(text(b2_x + 205, b2_y + 165, "100 нФ", size=10, color=MUTED, anchor="start"))
    els.append(text(b2_x + 175, b2_y + 215, "ФНЧ f_c ≈ 1.6 кГц", size=10, color=MUTED))

    # Вихід фільтра до АЦП
    els.append(line(b2_x + 175, b2_y + 115, b2_x + b2_w, b2_y + 115, color=INK, sw=2))
    els.append(arrow(b2_x + b2_w, b2_y + 115, b2_x + b2_w + 25, b2_y + 115, color=INK, sw=2))

    # Блок 3: Мікроконтролер та АЦП
    b3_x, b3_y, b3_w, b3_h = 555, 55, 295, 230
    els.append(rect(b3_x, b3_y, b3_w, b3_h, fill="#eef3f8", stroke="#2457d6", sw=1.5, rx=6))
    els.append(text(b3_x + b3_w / 2, b3_y + 22, "3. Мікроконтролер (SAR АЦП)", size=13, bold=True, color=NEG))

    # Пін входу
    els.append(circle(b3_x + 15, b3_y + 115, 4, fill=BG, stroke=INK, sw=1.5))
    els.append(text(b3_x + 15, b3_y + 98, "AINx", size=11, bold=True))

    # Семпл-холд всередині АЦП
    els.append(line(b3_x + 19, b3_y + 115, b3_x + 45, b3_y + 115, color=INK, sw=1.5))
    # Ключ S_sample
    els.append(circle(b3_x + 45, b3_y + 115, 2.5, fill=INK, stroke=INK))
    els.append(line(b3_x + 45, b3_y + 115, b3_x + 72, b3_y + 100, color=POS, sw=2))
    els.append(circle(b3_x + 75, b3_y + 115, 2.5, fill=INK, stroke=INK))
    els.append(text(b3_x + 58, b3_y + 88, "S_sample", size=10, color=POS, bold=True))

    # Внутрішній конденсатор C_sample
    els.append(line(b3_x + 75, b3_y + 115, b3_x + 105, b3_y + 115, color=INK, sw=1.5))
    els.append(circle(b3_x + 105, b3_y + 115, 2.5, fill=INK, stroke=INK))
    els.append(line(b3_x + 105, b3_y + 115, b3_x + 105, b3_y + 140, color=INK, sw=1.5))
    els.append(line(b3_x + 95, b3_y + 140, b3_x + 115, b3_y + 140, color=INK, sw=2))
    els.append(line(b3_x + 95, b3_y + 146, b3_x + 115, b3_y + 146, color=INK, sw=2))
    els.append(line(b3_x + 105, b3_y + 146, b3_x + 105, b3_y + 175, color=INK, sw=1.5))
    els.append(line(b3_x + 98, b3_y + 175, b3_x + 112, b3_y + 175, color=INK, sw=1.5))
    els.append(text(b3_x + 122, b3_y + 148, "C_s", size=10, bold=True, anchor="start"))
    els.append(text(b3_x + 122, b3_y + 162, "5 пФ", size=9, color=MUTED, anchor="start"))

    # Блок квантування SAR
    els.append(line(b3_x + 105, b3_y + 115, b3_x + 175, b3_y + 115, color=INK, sw=1.5))
    els.append(rect(b3_x + 175, b3_y + 85, 100, 60, fill=BG, stroke=NEG, sw=1.5, rx=4))
    els.append(text(b3_x + 225, b3_y + 108, "12-bit SAR", size=12, bold=True, color=NEG))
    els.append(text(b3_x + 225, b3_y + 125, "Ядро АЦП", size=10, color=MUTED))

    # Вихідний цифровий потік
    els.append(line(b3_x + 225, b3_y + 145, b3_x + 225, b3_y + 185, color=INK, sw=1.5))
    els.append(arrow(b3_x + 225, b3_y + 185, b3_x + 225, b3_y + 200, color=INK, sw=1.5))
    els.append(rect(b3_x + 165, b3_y + 200, 120, 22, fill="#e8f5e9", stroke=FIELD, sw=1, rx=3))
    els.append(text(b3_x + 225, b3_y + 215, "Код: 0 … 4095", size=11, bold=True, color=FIELD))

    render(os.path.join(IMG, "signal-chain-schematic.svg"), W, H, *els)


# ── 2. Логометричний вимір ──────────────────────────────────────────────────
def fig_ratiometric():
    W, H = 860, 270
    els = []

    els.append(text(W / 2, 26, "Логометричний принцип: чому шум живлення взаємно знищується", size=15, bold=True))

    # Ліва панель: Аналогове формування напруги
    p1_x, p1_y, p1_w, p1_h = 30, 50, 380, 200
    els.append(rect(p1_x, p1_y, p1_w, p1_h, fill=FILL, stroke=MUTED, sw=1.2, rx=6))
    els.append(text(p1_x + p1_w / 2, p1_y + 24, "Напруга на вході АЦП (V_in)", size=13, bold=True, color=INK))

    els.append(text(p1_x + p1_w / 2, p1_y + 55, "Дільник живиться від спільної шини V_ref:", size=12, color=MUTED))
    
    # Формула напруги в рамці
    els.append(rect(p1_x + 30, p1_y + 70, 320, 48, fill=BG, stroke=INK, sw=1.2, rx=4))
    els.append(text(p1_x + p1_w / 2, p1_y + 92, "V_in = (V_ref + ΔV) ·", size=13, bold=True, color=INK))
    els.append(text(p1_x + 280, p1_y + 86, "R_ntc", size=12, bold=True, color=POS))
    els.append(line(p1_x + 235, p1_y + 92, p1_x + 335, p1_y + 92, color=INK, sw=1.2))
    els.append(text(p1_x + 285, p1_y + 107, "R_ref + R_ntc", size=11, color=INK))

    els.append(text(p1_x + p1_w / 2, p1_y + 145, "Якщо V_ref просіла або шумить на +ΔV,", size=11, color=POS))
    els.append(text(p1_x + p1_w / 2, p1_y + 162, "вхідна напруга V_in масштабується синхронно", size=11, color=POS))
    els.append(text(p1_x + p1_w / 2, p1_y + 182, "у точно такій самій пропорції.", size=11, color=MUTED))

    # Стрілка переносу між блоками
    els.append(arrow(p1_x + p1_w + 8, p1_y + p1_h / 2, p1_x + p1_w + 32, p1_y + p1_h / 2, color=NEG, sw=3))

    # Права панель: Перетворення АЦП і скорочення
    p2_x, p2_y, p2_w, p2_h = 450, 50, 380, 200
    els.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#e8f5e9", stroke=FIELD, sw=1.2, rx=6))
    els.append(text(p2_x + p2_w / 2, p2_y + 24, "Цифровий код АЦП (Код)", size=13, bold=True, color=FIELD))

    els.append(text(p2_x + p2_w / 2, p2_y + 55, "АЦП ділить вхід на власну шкалу V_ref:", size=12, color=MUTED))

    # Формула коду
    els.append(rect(p2_x + 25, p2_y + 70, 330, 52, fill=BG, stroke=FIELD, sw=1.2, rx=4))
    els.append(text(p2_x + 75, p2_y + 100, "Код = 2ᴺ ·", size=13, bold=True))
    els.append(text(p2_x + 215, p2_y + 87, "(V_ref + ΔV) · (R_ntc / (R_ref + R_ntc))", size=11, color=POS))
    els.append(line(p2_x + 120, p2_y + 94, p2_x + 340, p2_y + 94, color=INK, sw=1.2))
    els.append(text(p2_x + 215, p2_y + 112, "(V_ref + ΔV)", size=12, bold=True, color=POS))

    # Закреслення чисельника і знаменника для демонстрації скорочення
    els.append(line(p2_x + 126, p2_y + 91, p2_x + 205, p2_y + 83, color=NEG, sw=1.8))
    els.append(line(p2_x + 175, p2_y + 116, p2_x + 255, p2_y + 107, color=NEG, sw=1.8))

    # Фінальний чистий результат
    els.append(rect(p2_x + 45, p2_y + 138, 290, 42, fill=BG, stroke=FIELD, sw=1.5, rx=4))
    els.append(text(p2_x + p2_w / 2, p2_y + 162, "Код = 2ᴺ · R_ntc / (R_ref + R_ntc)", size=13, bold=True, color=FIELD))
    els.append(text(p2_x + p2_w / 2, p2_y + 192, "✓ Дрейф опорної напруги повністю зникає з результату!", size=11, color=FIELD, bold=True))

    render(os.path.join(IMG, "ratiometric-principle.svg"), W, H, *els)


# ── 3. Заряд семпл-холду та бюджет часу ──────────────────────────────────────
def fig_sampling_settling():
    W, H = 860, 330
    els = []

    els.append(text(W / 2, 26, "Експоненційний заряд ємності C_sample: необхідний час вибірки t_sample", size=15, bold=True))

    # Координатна сітка
    ox, oy = 75, 270
    pw, ph = 480, 215

    # Осі
    els.append(line(ox, oy, ox + pw + 25, oy, color=INK, sw=1.5))
    els.append(line(ox, oy, ox, oy - ph - 10, color=INK, sw=1.5))
    els.append(text(ox + pw + 30, oy + 4, "t", size=13, bold=True, anchor="start"))
    els.append(text(ox - 10, oy - ph - 5, "V(t)", size=13, bold=True, anchor="end"))

    # Цільовий рівень V_in (100%)
    v_target_y = oy - ph + 20
    els.append(line(ox, v_target_y, ox + pw, v_target_y, color=MUTED, sw=1.2, dash="4,4"))
    els.append(text(ox - 12, v_target_y + 4, "V_in", size=12, bold=True, anchor="end"))

    # Зона похибки ½ LSB (для 12 біт це 0.012% від V_in)
    lsb_band_y = v_target_y + 12
    els.append(rect(ox, v_target_y, pw, 12, fill="#e8f5e9", stroke="none"))
    els.append(line(ox, lsb_band_y, ox + pw, lsb_band_y, color=FIELD, sw=1, dash="2,2"))
    els.append(text(ox + pw + 8, lsb_band_y + 3, "Межа ½ LSB (12-bit)", size=10, color=FIELD, anchor="start", bold=True))

    # Крива 1: Нормальний імпеданс (τ_1 = 35px) -> швидко заходить в межі
    pts1 = []
    tau1 = 35.0
    for i in range(pw):
        t = float(i)
        v = (1.0 - math.exp(-t / tau1))
        vy = oy - (ph - 20) * v
        pts1.append((ox + t, vy))

    path_d1 = "M " + " L ".join(["%.1f,%.1f" % p for p in pts1])
    els.append(path_tag(path_d1, stroke=FIELD, sw=2.5))

    # Крива 2: Високий вихідний опір (τ_2 = 140px) -> не встигає
    pts2 = []
    tau2 = 140.0
    for i in range(pw):
        t = float(i)
        v = (1.0 - math.exp(-t / tau2))
        vy = oy - (ph - 20) * v
        pts2.append((ox + t, vy))

    path_d2 = "M " + " L ".join(["%.1f,%.1f" % p for p in pts2])
    els.append(path_tag(path_d2, stroke=POS, sw=2.2, dash="5,3"))

    # Позначки часу на осі t
    t_settle_x = ox + 315
    els.append(line(t_settle_x, oy, t_settle_x, v_target_y, color=FIELD, sw=1.2, dash="3,3"))
    els.append(text(t_settle_x, oy + 18, "t = 9.01 · τ", size=11, bold=True, color=FIELD))
    els.append(circle(t_settle_x, lsb_band_y, 4, fill=FIELD, stroke=INK))

    # Вікно вибірки за замовчуванням
    t_short_x = ox + 150
    els.append(line(t_short_x, oy, t_short_x, oy - ph + 20, color=POS, sw=1.5, dash="3,3"))
    els.append(text(t_short_x, oy + 18, "t_sample (коротке)", size=10, bold=True, color=POS))
    # Похибка на короткому вікні для високого опору
    v_err_y = oy - (ph - 20) * (1.0 - math.exp(-150.0 / tau2))
    els.append(circle(t_short_x, v_err_y, 4, fill=POS, stroke=INK))
    els.append(arrow(t_short_x + 10, (v_err_y + v_target_y) / 2, t_short_x + 10, v_target_y, color=POS, sw=1.5))
    els.append(arrow(t_short_x + 10, (v_err_y + v_target_y) / 2, t_short_x + 10, v_err_y, color=POS, sw=1.5))
    els.append(text(t_short_x + 16, (v_err_y + v_target_y) / 2 + 4, "ΔV (величезна похибка)", size=10, bold=True, color=POS, anchor="start"))

    # Права інформаційна панель
    info_x, info_y, info_w, info_h = 580, 50, 260, 240
    els.append(rect(info_x, info_y, info_w, info_h, fill=FILL, stroke=MUTED, sw=1.2, rx=6))
    els.append(text(info_x + info_w / 2, info_y + 22, "Вимоги до часу вибірки", size=13, bold=True, color=INK))

    els.append(text(info_x + 15, info_y + 50, "Стала часу кола вибірки:", size=11, bold=True, anchor="start"))
    els.append(text(info_x + 15, info_y + 68, "τ = R_екв · C_sample", size=12, color=POS, bold=True, anchor="start"))
    els.append(text(info_x + 15, info_y + 84, "де R_екв = (R_ref || R_ntc) + R_f", size=10, color=MUTED, anchor="start"))

    els.append(line(info_x + 15, info_y + 98, info_x + info_w - 15, info_y + 98, color=MUTED, sw=0.8))

    els.append(text(info_x + 15, info_y + 118, "Критерій для ½ LSB залишку:", size=11, bold=True, anchor="start"))
    els.append(text(info_x + 15, info_y + 138, "• 10-bit: t_sample ≥ 7.62 · τ", size=11, anchor="start"))
    els.append(text(info_x + 15, info_y + 156, "• 12-bit: t_sample ≥ 9.01 · τ", size=11, bold=True, color=FIELD, anchor="start"))
    els.append(text(info_x + 15, info_y + 174, "• 16-bit: t_sample ≥ 11.78 · τ", size=11, anchor="start"))

    els.append(rect(info_x + 12, info_y + 190, info_w - 24, 40, fill=BG, stroke=FIELD, sw=1, rx=4))
    els.append(text(info_x + info_w / 2, info_y + 206, "R_екв = 5 кОм, C_s = 5 пФ → τ = 25 нс", size=10, color=INK))
    els.append(text(info_x + info_w / 2, info_y + 222, "t_sample ≥ 9.01 · 25 нс ≈ 225 нс", size=10, bold=True, color=FIELD))

    render(os.path.join(IMG, "sampling-settling-curve.svg"), W, H, *els)


# ── 4. Таблична кусково-лінійна інтерполяція ─────────────────────────────────
def fig_lut_interpolation():
    W, H = 860, 320
    els = []

    els.append(text(W / 2, 26, "Кусково-лінійна інтерполяція характеристики NTC за таблицею вузлів (LUT)", size=15, bold=True))

    # Графік зліва
    ox, oy = 75, 260
    pw, ph = 420, 200

    els.append(line(ox, oy, ox + pw + 25, oy, color=INK, sw=1.5))
    els.append(line(ox, oy, ox, oy - ph - 10, color=INK, sw=1.5))
    els.append(text(ox + pw + 30, oy + 4, "Код АЦП", size=12, bold=True, anchor="start"))
    els.append(text(ox - 10, oy - ph - 5, "T, °C", size=12, bold=True, anchor="end"))

    # Сітка та вузли LUT
    nodes = [
        (ox + 40, oy - 25, "-20°C", "380"),
        (ox + 100, oy - 55, "0°C", "950"),
        (ox + 180, oy - 100, "25°C", "2048"),
        (ox + 270, oy - 145, "50°C", "3120"),
        (ox + 350, oy - 175, "75°C", "3680"),
        (ox + 405, oy - 195, "100°C", "3920"),
    ]

    # Малюємо гладку істинну криву
    true_pts = []
    for i in range(40, 410, 5):
        norm_x = (i - 40) / 370.0
        norm_y = math.pow(norm_x, 0.72)
        true_pts.append((ox + i, oy - 25 - norm_y * 170))
    path_true = "M " + " L ".join(["%.1f,%.1f" % p for p in true_pts])
    els.append(path_tag(path_true, stroke=MUTED, sw=1.5, dash="4,3"))

    # Малюємо відрізки кусково-лінійної апроксимації між вузлами
    for i in range(len(nodes) - 1):
        x1, y1 = nodes[i][0], nodes[i][1]
        x2, y2 = nodes[i+1][0], nodes[i+1][1]
        els.append(line(x1, y1, x2, y2, color=NEG, sw=2))

    # Виділяємо робочий інтервал між вузлом i та i+1
    i_idx = 2
    nx1, ny1 = nodes[i_idx][0], nodes[i_idx][1]
    nx2, ny2 = nodes[i_idx+1][0], nodes[i_idx+1][1]

    # Вертикальні лінії до осі
    els.append(line(nx1, ny1, nx1, oy, color=MUTED, sw=1, dash="2,2"))
    els.append(line(nx2, ny2, nx2, oy, color=MUTED, sw=1, dash="2,2"))
    els.append(text(nx1, oy + 16, "Code[i]", size=11, bold=True, color=NEG))
    els.append(text(nx2, oy + 16, "Code[i+1]", size=11, bold=True, color=NEG))

    # Точка виміру x всередині інтервалу
    mx = nx1 + (nx2 - nx1) * 0.45
    my = ny1 + (ny2 - ny1) * 0.45
    els.append(line(mx, my, mx, oy, color=FIELD, sw=1.2, dash="3,2"))
    els.append(line(mx, my, ox, my, color=FIELD, sw=1.2, dash="3,2"))
    els.append(circle(mx, my, 4.5, fill=FIELD, stroke=INK))
    els.append(text(mx, oy + 30, "Code_x (вхід)", size=11, bold=True, color=FIELD))
    els.append(text(ox - 8, my + 4, "T_x", size=11, bold=True, color=FIELD, anchor="end"))

    # Вузлові точки
    for nx, ny, t_lbl, c_lbl in nodes:
        els.append(circle(nx, ny, 4, fill=NEG, stroke=INK))

    # Права панель з формулою інтерполяції
    p_x, p_y, p_w, p_h = 520, 50, 315, 240
    els.append(rect(p_x, p_y, p_w, p_h, fill=FILL, stroke=MUTED, sw=1.2, rx=6))
    els.append(text(p_x + p_w / 2, p_y + 22, "Формула інтерполяції в інтервалі", size=13, bold=True, color=INK))

    els.append(rect(p_x + 12, p_y + 42, p_w - 24, 60, fill=BG, stroke=NEG, sw=1.2, rx=4))
    els.append(text(p_x + (p_w - 24) / 2 + 12, p_y + 64, "T_x = T[i] + (Code_x − Code[i]) · k", size=12, bold=True, color=INK))
    els.append(text(p_x + (p_w - 24) / 2 + 12, p_y + 88, "де k = (T[i+1] − T[i]) / (Code[i+1] − Code[i])", size=11, color=NEG))

    els.append(text(p_x + 15, p_y + 122, "Переваги для мікроконтролера:", size=11, bold=True, anchor="start"))
    els.append(text(p_x + 15, p_y + 142, "• Жодних важких викликів log() та pow()", size=11, anchor="start"))
    els.append(text(p_x + 15, p_y + 160, "• 1 ділення + 1 множення або бітовий зсув", size=11, anchor="start"))
    els.append(text(p_x + 15, p_y + 178, "• Таблиця 33–65 точок дає похибку < 0.05 °C", size=11, anchor="start"))
    els.append(text(p_x + 15, p_y + 196, "• Час виконання: лічені такти процесора", size=11, color=FIELD, bold=True, anchor="start"))

    els.append(rect(p_x + 12, p_y + 208, p_w - 24, 24, fill="#e8f5e9", stroke=FIELD, sw=1, rx=3))
    els.append(text(p_x + p_w / 2, p_y + 224, "Виконується за одиниці мікросекунд", size=10, bold=True, color=FIELD))

    render(os.path.join(IMG, "lut-piecewise-linear.svg"), W, H, *els)


if __name__ == "__main__":
    fig_signal_chain()
    fig_ratiometric()
    fig_sampling_settling()
    fig_lut_interpolation()
    print("Всі фігури згенеровано успішно у ./img/")
