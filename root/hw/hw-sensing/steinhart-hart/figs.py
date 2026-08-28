# -*- coding: utf-8 -*-
"""Фігури до теми «Лінеаризація термістора».
Запуск: python figs.py  → генерує SVG у ./img/
"""
import os
import sys
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

WARM = "#e08a3c"


# ── 1. Фізика NTC: активація носіїв та стрибкова провідність ──────────────
def fig_ntc_physics():
    W, H = 760, 360
    f = [text(W / 2, 28, "Стрибкова провідність у напівпровідниковому NTC-оксиді", size=16, bold=True)]

    # Ліва панель: низька температура
    f.append(rect(24, 55, 340, 275, fill="#f4f8fc", stroke=MUTED, sw=1.3, rx=8))
    f.append(text(194, 82, "Холодний оксид (низька T)", size=14, bold=True, color=NEG))
    f.append(text(194, 102, "Теплової енергії k_B·T замало для подолання бар'єра", size=11, color=MUTED))

    # Спрощена ґратка іонів Mn3+ / Mn4+
    ions_left = [
        (80, 150, "Mn³⁺", "#d9e2ec"), (160, 150, "Mn⁴⁺", "#bcccdc"), (240, 150, "Mn³⁺", "#d9e2ec"), (310, 150, "Mn³⁺", "#d9e2ec"),
        (80, 205, "Mn⁴⁺", "#bcccdc"), (160, 205, "Mn³⁺", "#d9e2ec"), (240, 205, "Mn⁴⁺", "#bcccdc"), (310, 205, "Mn³⁺", "#d9e2ec"),
    ]
    for cx, cy, label, fill_col in ions_left:
        f.append(circle(cx, cy, 18, fill=fill_col, stroke=MUTED, sw=1.2))
        f.append(text(cx, cy + 4, label, size=11, bold=True, color=INK))

    # Зв'язаний локалізований електрон
    f.append(circle(120, 150, 6, fill=NEG, stroke=INK, sw=1))
    f.append(text(120, 137, "e⁻ (локалізований)", size=9.5, color=NEG))
    f.append(line(126, 150, 142, 150, color=MUTED, sw=1.2, dash="3,3"))

    b1, _, _ = textbox(194, 275, "Електрон локалізований біля іона Mn³⁺\nСтрибки рідкісні → Опір R ВЕЛИКИЙ",
                       size=11, fill=BG, stroke=MUTED)
    f.append(b1)

    # Права панель: висока температура
    f.append(rect(396, 55, 340, 275, fill="#fdf6f0", stroke=MUTED, sw=1.3, rx=8))
    f.append(text(566, 82, "Нагрітий оксид (висока T)", size=14, bold=True, color=POS))
    f.append(text(566, 102, "Теплові фонони активують тунелювання поляронів", size=11, color=MUTED))

    ions_right = [
        (450, 150, "Mn⁴⁺", "#bcccdc"), (530, 150, "Mn³⁺", "#d9e2ec"), (610, 150, "Mn⁴⁺", "#bcccdc"), (680, 150, "Mn³⁺", "#d9e2ec"),
        (450, 205, "Mn³⁺", "#d9e2ec"), (530, 205, "Mn⁴⁺", "#bcccdc"), (610, 205, "Mn³⁺", "#d9e2ec"), (680, 205, "Mn⁴⁺", "#bcccdc"),
    ]
    for cx, cy, label, fill_col in ions_right:
        f.append(circle(cx, cy, 18, fill=fill_col, stroke=MUTED, sw=1.2))
        f.append(text(cx, cy + 4, label, size=11, bold=True, color=INK))

    # Стрибки електронів між іонами
    f.append(arrow(468, 150, 510, 150, color=POS, sw=1.8))
    f.append(arrow(548, 150, 590, 150, color=POS, sw=1.8))
    f.append(arrow(468, 205, 510, 205, color=POS, sw=1.8))
    f.append(arrow(548, 205, 590, 205, color=POS, sw=1.8))
    f.append(circle(489, 142, 5, fill=POS, stroke=INK, sw=1))
    f.append(circle(569, 142, 5, fill=POS, stroke=INK, sw=1))
    f.append(text(566, 130, "висока частота стрибків", size=10, bold=True, color=POS))

    b2, _, _ = textbox(566, 275, "Інтенсивний дрейф носіїв (Mn³⁺ ⇄ Mn⁴⁺)\nПровідність σ росте → Опір R ПАДАЄ",
                       size=11, fill=BG, stroke=MUTED)
    f.append(b2)

    render(os.path.join(IMG, "ntc-physics-bandgap.svg"), W, H, *f)


# ── 2. Порівняння похибок: модель Beta проти рівняння Стейнгарта-Гарта ────────
def fig_model_comparison():
    W, H = 760, 420
    f = [text(W / 2, 26, "Залишкова похибка розрахунку температури: Beta-модель vs Стейнгарт–Гарт", size=15, bold=True)]

    ox, oy = 85, 230
    ax_w, ax_h = 600, 150

    # Осі координат (нуль похибки посередині)
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.5))
    f.append(line(ox, oy - ax_h, ox, oy + ax_h, color=INK, sw=1.5))
    f.append(text(ox + ax_w - 40, oy + 24, "Температура, °C", size=11, color=INK))
    f.append(mtext(ox - 55, oy - 60, ["Похибка", "ΔT, °C"], size=11, color=INK))

    def X(t):
        return ox + (t - (-40)) / (125 - (-40)) * ax_w

    def Y(err):
        # масштаб: 1 °C = 40 px
        return oy - err * 40.0

    # Сітка та позначки
    for t in (-40, -20, 0, 25, 50, 75, 100, 125):
        f.append(line(X(t), oy - ax_h, X(t), oy + ax_h, color="#e5e7eb", sw=1, dash="3,3"))
        f.append(line(X(t), oy - 4, X(t), oy + 4, color=INK, sw=1.2))
        f.append(text(X(t), oy + 18, str(t), size=10, color=MUTED))

    for err in (-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0):
        f.append(line(ox - 4, Y(err), ox + 4, Y(err), color=INK, sw=1.2))
        if abs(err) > 0.01:
            f.append(text(ox - 10, Y(err) + 4, "%+.1f" % err, size=10, color=MUTED, anchor="end"))

    # Крива Beta-моделі (калібрована на 25 °C та 85 °C)
    beta_pts = []
    for t in range(-40, 126, 2):
        # Реалістична форма похибки бета-моделі (кубічно-параболічна форма)
        err = -0.0000035 * (t - 25) * (t - 85) * (t + 30)
        beta_pts.append((X(t), Y(err)))

    poly_beta = " ".join("%.1f,%.1f" % pt for pt in beta_pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (poly_beta, POS))

    # Крива Стейнгарта-Гарта (калібрована на 0 °C, 25 °C, 85 °C) — майже нуль
    sh_pts = []
    for t in range(-40, 126, 2):
        err = 0.00000015 * (t - 0) * (t - 25) * (t - 85)
        sh_pts.append((X(t), Y(err)))

    poly_sh = " ".join("%.1f,%.1f" % pt for pt in sh_pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (poly_sh, FIELD))

    # Точки калібрування Стейнгарта-Гарта
    for t_cal in (0, 25, 85):
        f.append(circle(X(t_cal), Y(0), 4.5, fill=BG, stroke=FIELD, sw=2))

    # Підписи та пояснювальні блоки
    b1, _, _ = textbox(190, 95, "Beta-модель: похибка зростає до ±2.5 °C\nчерез дрейф енергії активації",
                       size=11, fill="#fdf0ed", stroke=POS)
    f.append(b1)

    b2, _, _ = textbox(530, 350, "Стейнгарт–Гарт: похибка < ±0.01 °C\nу каліброваному вікні (точки 0, 25, 85 °C)",
                       size=11, fill="#eef8f1", stroke=FIELD)
    f.append(b2)

    render(os.path.join(IMG, "model-comparison-error.svg"), W, H, *f)


# ── 3. Апаратна лінеаризація: дільник напруги та точка перегину ──────────────
def fig_divider_linearization():
    W, H = 760, 390
    f = [text(W / 2, 26, "Апаратна лінеаризація: взаємна компенсація нелінійностей у дільнику", size=15, bold=True)]

    # Схема дільника зліва
    f.append(rect(24, 55, 230, 310, fill=FILL, stroke=MUTED, sw=1.2, rx=8))
    f.append(text(139, 82, "Вимірювальний дільник", size=13, bold=True))

    # Джерела живлення та елементи
    f.append(line(139, 105, 139, 130, color=INK, sw=1.8))
    f.append(circle(139, 100, 4, fill=POS, stroke=INK, sw=1.5))
    f.append(text(139, 92, "V_ref (3.3 В)", size=11, bold=True, color=POS))

    # Опорний резистор R_ref
    f.append(rect(121, 130, 36, 48, fill=BG, stroke=INK, sw=1.6))
    f.append(text(139, 158, "R_ref", size=11, bold=True))
    f.append(text(185, 158, "10 кОм", size=10.5, color=MUTED))

    # Середня точка
    f.append(line(139, 178, 139, 230, color=INK, sw=1.8))
    f.append(circle(139, 204, 4.5, fill=BG, stroke=FIELD, sw=2))
    f.append(arrow(139, 204, 215, 204, color=FIELD, sw=2))
    f.append(text(205, 192, "V_out → АЦП", size=11, bold=True, color=FIELD))

    # NTC термістор знизу
    f.append(rect(121, 230, 36, 48, fill=BG, stroke=INK, sw=1.6))
    f.append(line(115, 282, 163, 226, color=INK, sw=1.5))
    f.append(line(112, 282, 118, 282, color=INK, sw=1.5))
    f.append(text(139, 258, "R_ntc", size=11, bold=True))
    f.append(text(185, 258, "NTC", size=10.5, color=MUTED))

    # Земля
    f.append(line(139, 278, 139, 310, color=INK, sw=1.8))
    f.append(line(125, 310, 153, 310, color=INK, sw=1.8))
    f.append(line(130, 315, 148, 315, color=INK, sw=1.4))
    f.append(line(135, 320, 143, 320, color=INK, sw=1.1))

    b_note, _, _ = textbox(139, 345, "NTC внизу: гарячіше → V_out нижча", size=10, fill=BG, stroke=MUTED)
    f.append(b_note)

    # Графік перехідної характеристики справа
    gx, gy = 330, 320
    gw, gh = 390, 240
    f.append(line(gx, gy, gx + gw, gy, color=INK, sw=1.6))
    f.append(line(gx, gy, gx, gy - gh, color=INK, sw=1.6))
    f.append(text(gx + gw / 2, gy + 32, "Температура навколишнього середовища, °C", size=11, color=INK))
    f.append(mtext(gx - 45, gy - gh / 2, ["Напруга", "V_out, В"], size=11, color=INK))

    # Позначки осі X
    for t in (0, 25, 50, 75, 100):
        xt = gx + (t / 100.0) * gw
        f.append(line(xt, gy - 3, xt, gy + 3, color=INK, sw=1.2))
        f.append(text(xt, gy + 16, str(t), size=10, color=MUTED))

    # Позначки осі Y
    for v in (0.0, 1.0, 1.65, 2.0, 3.0, 3.3):
        yv = gy - (v / 3.3) * gh
        f.append(line(gx - 3, yv, gx + 3, yv, color=INK, sw=1.2))
        f.append(text(gx - 8, yv + 4, "%.1f" % v if v != 1.65 else "1.65", size=9.5, color=MUTED, anchor="end"))

    # Обчислення S-подібної кривої V_out(T)
    R25, B_val, T25 = 10000.0, 3950.0, 298.15
    R_ref = 10000.0
    V_ref = 3.3
    pts = []
    for t in range(0, 101, 2):
        Tk = t + 273.15
        R_ntc = R25 * math.exp(B_val * (1.0 / Tk - 1.0 / T25))
        V_out = V_ref * R_ntc / (R_ref + R_ntc)
        xt = gx + (t / 100.0) * gw
        yv = gy - (V_out / V_ref) * gh
        pts.append((xt, yv))

    poly_s = " ".join("%.1f,%.1f" % pt for pt in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (poly_s, POS))

    # Дотична лінія в точці перегину (25 °C)
    t_inf = 25
    xt_inf = gx + (t_inf / 100.0) * gw
    yv_inf = gy - (1.65 / 3.3) * gh
    f.append(circle(xt_inf, yv_inf, 5, fill=BG, stroke=FIELD, sw=2.2))

    # Лінійна ділянка
    f.append(line(xt_inf - 70, yv_inf + 55, xt_inf + 70, yv_inf - 55, color=FIELD, sw=1.5, dash="4,3"))

    b_tangent, _, _ = textbox(525, 115, "Точка перегину (R_ntc ≈ R_ref):\nквадратична кривина d²V/dT² = 0\nМаксимальна лінійність передачі",
                              size=10.5, fill="#eef8f1", stroke=FIELD)
    f.append(b_tangent)

    render(os.path.join(IMG, "divider-linearization-inflection.svg"), W, H, *f)


# ── 4. Самонагрів та імпульсне опитування ────────────────────────────────────
def fig_self_heating_pulsed():
    W, H = 760, 360
    f = [text(W / 2, 26, "Мінімізація самонагріву: імпульсне живлення дільника замість постійного", size=15, bold=True)]

    # Ліва частина: постійний нагрів
    f.append(rect(24, 55, 340, 280, fill="#fdf0ed", stroke=POS, sw=1.3, rx=8))
    f.append(text(194, 82, "Постійне живлення (DC)", size=13.5, bold=True, color=POS))
    f.append(text(194, 102, "P = V² / (4·R) постійно виділяється в кристалі", size=10.5, color=MUTED))

    # Графік постійної потужності
    f.append(rect(45, 120, 298, 75, fill=BG, stroke=MUTED, sw=1))
    f.append(line(55, 175, 330, 175, color=INK, sw=1.2))
    f.append(line(55, 140, 330, 140, color=POS, sw=2.2))
    f.append(text(60, 134, "Потужність P_dc = 0.27 мВт (100% часу)", size=9.5, bold=True, color=POS, anchor="start"))
    f.append(text(310, 186, "час t", size=9.5, color=MUTED))

    b_err, _, _ = textbox(194, 255, "Самонагрів: ΔT = P / δ\nДля δ = 1.5 мВт/°C:\nΔT_self ≈ +0.18 °C (постійна похибка!)",
                          size=11, fill=BG, stroke=POS)
    f.append(b_err)

    # Права частина: імпульсне опитування (Pulsed Excitation)
    f.append(rect(396, 55, 340, 280, fill="#eef8f1", stroke=FIELD, sw=1.3, rx=8))
    f.append(text(566, 82, "Імпульсне опитування (Pulsed)", size=13.5, bold=True, color=FIELD))
    f.append(text(566, 102, "Живлення подається лише на час перетворення АЦП", size=10.5, color=MUTED))

    # Графік імпульсної потужності
    f.append(rect(417, 120, 298, 75, fill=BG, stroke=MUTED, sw=1))
    f.append(line(427, 175, 702, 175, color=INK, sw=1.2))

    # Короткі імпульси
    for px in (450, 530, 610):
        f.append(rect(px, 138, 12, 37, fill=FIELD, stroke=FIELD, sw=1.2))
        f.append(line(px + 6, 130, px + 6, 138, color=MUTED, sw=1))
        f.append(text(px + 6, 125, "50 мкс", size=10, color=MUTED))

    f.append(text(432, 134, "P_pulse", size=9.5, bold=True, color=FIELD, anchor="start"))
    f.append(text(685, 186, "час t", size=9.5, color=MUTED))

    b_pulsed_gain, _, _ = textbox(566, 255, "Коефіцієнт заповнення D = 0.05%\nСередня потужність P_avg = 0.14 мкВт\nΔT_self < 0.0001 °C (повне усунення похибки)",
                                  size=11, fill=BG, stroke=FIELD)
    f.append(b_pulsed_gain)

    render(os.path.join(IMG, "self-heating-pulsed.svg"), W, H, *f)


# ── 5. Конвеєр LUT-інтерполяції ─────────────────────────────────────────────
def fig_lut_pipeline():
    W, H = 760, 320
    f = [text(W / 2, 26, "Конвеєр швидкого обчислення температури: LUT із лінійною інтерполяцією", size=15, bold=True)]

    # Крок 1: Вхідний код АЦП
    b1, _, _ = textbox(110, 95, "Сирий відлік АЦП\nraw (12 біт, 0..4095)", size=11.5, bold=True, fill="#eef2f8", stroke=NEG)
    f.append(b1)
    f.append(arrow(185, 95, 235, 95, color=INK, sw=1.8))

    # Крок 2: Швидке бітове розділення індексу та залишку
    b2, _, _ = textbox(340, 95, "Бітовий поділ (крок 128)\nidx = raw >> 7  (0..31)\nrem = raw & 0x7F (0..127)",
                       size=11, fill="#fef9e7", stroke=WARM)
    f.append(b2)
    f.append(arrow(445, 95, 495, 95, color=INK, sw=1.8))

    # Крок 3: Вибірка з таблиці Flash
    b3, _, _ = textbox(620, 95, "Таблиця LUT у Flash\nT_low = lut[idx]\nT_high = lut[idx+1]",
                       size=11, fill="#f4f8fc", stroke=MUTED)
    f.append(b3)

    # Стрілка вниз до обчислювального блоку
    f.append(arrow(620, 140, 620, 185, color=INK, sw=1.8))
    f.append(arrow(340, 140, 340, 185, color=INK, sw=1.8))

    # Крок 4: Фіксована цілочисельна інтерполяція
    b4, _, _ = textbox(480, 230, "Цілочисельна лінійна інтерполяція (без ділення):\n"
                                 "T = T_low + (((T_high - T_low) * rem) >> 7)\n"
                                 "Час виконання: 15–25 тактів CPU замість 800+ у logf()",
                       size=12, bold=True, fill="#eef8f1", stroke=FIELD)
    f.append(b4)

    # Вихід
    f.append(arrow(270, 230, 185, 230, color=FIELD, sw=2.2))
    b_out, _, _ = textbox(105, 230, "Температура\n(0.01 °C / int16)", size=12, bold=True, fill=BG, stroke=FIELD)
    f.append(b_out)

    render(os.path.join(IMG, "lut-interpolation-pipeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_ntc_physics()
    fig_model_comparison()
    fig_divider_linearization()
    fig_self_heating_pulsed()
    fig_lut_pipeline()
    print("Всі фігури згенеровано успішно.")
