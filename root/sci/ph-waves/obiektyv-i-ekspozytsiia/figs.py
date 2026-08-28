# -*- coding: utf-8 -*-
"""Генератор векторних SVG-фігур для теми:
Об'єктив і експозиція: поле зору, діафрагма, витримка, підсилення.
"""

import os
import sys

# Додаємо scripts/ до шляху пошуку модулів для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_exposure_triangle():
    """Фігура 1: Трикутник експозиції та фізичні компроміси параметрів зйомки."""
    w, h = 860, 520
    frags = []

    # Вершини трикутника
    # Верхня вершина: Діафрагма
    # Ліва нижня: Витримка
    # Права нижня: Чутливість ISO
    top_x, top_y = 430, 80
    left_x, left_y = 150, 410
    right_x, right_y = 710, 410

    # Заливка внутрішньої площини трикутника
    frags.append(
        '<polygon points="%d,%d %d,%d %d,%d" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>'
        % (top_x, top_y, left_x, left_y, right_x, right_y)
    )

    # Лінії трикутника з кольоровими акцентами
    frags.append(line(top_x, top_y, left_x, left_y, color=POS, sw=2.5))
    frags.append(line(top_x, top_y, right_x, right_y, color=NEG, sw=2.5))
    frags.append(line(left_x, left_y, right_x, right_y, color=FIELD, sw=2.5))

    # Центральний інформаційний блок: Експозиція сенсора
    b_ev, _, _ = textbox(
        430, 290,
        "Фотометрична експозиція сенсора\n"
        "H = E_v · t_exp  (люкс · с)\n"
        "EV = log₂(N² / t_exp) - log₂(ISO / 100)\n"
        "Цільовий динамічний діапазон",
        size=12, pad=12, fill="#ffffff", stroke="#475569", sw=1.8, bold=False
    )
    frags.append(b_ev)

    # Вершина 1: ДІАФРАГМА (Aperture, F-number N = f / D)
    b_ap, _, _ = textbox(
        top_x, top_y - 20,
        "ДІАФРАГМА (F-number N = f / D)\n"
        "Вхідна оптична зіниця · Світлосила",
        size=13, pad=10, fill="#fef2f2", stroke=POS, sw=2, bold=True, color=POS
    )
    frags.append(b_ap)

    # Текстовий блок ліворуч від діафрагми: фізичний ефект
    b_ap_desc, _, _ = textbox(
        430, top_y + 70,
        "Відкрита (f/1.4): багато світла · мала глибина DoF · аберації\n"
        "Закрита (f/16): мало світла · велика DoF · дифракційне розмиття",
        size=11, pad=8, fill="#ffffff", stroke=POS, sw=1.2, color=INK
    )
    frags.append(b_ap_desc)

    # Вершина 2: ВИТРИМКА (Shutter Speed t_exp)
    b_sh, _, _ = textbox(
        left_x - 10, left_y + 40,
        "ВИТРИМКА (Час інтеграції t_exp)\n"
        "Накопичення заряду пікселів Q = I_ph · t",
        size=13, pad=10, fill="#eff6ff", stroke=NEG, sw=2, bold=True, color=NEG
    )
    frags.append(b_sh)

    # Опис витримки
    b_sh_desc, _, _ = textbox(
        left_x + 50, left_y - 65,
        "Коротка (1/2000 с): чіткий рух · мало фотонів\n"
        "Довга (1/10 с): багато фотонів · змаз руху (Motion Blur)",
        size=11, pad=8, fill="#ffffff", stroke=NEG, sw=1.2, color=INK
    )
    frags.append(b_sh_desc)

    # Вершина 3: ПІДСИЛЕННЯ (ISO Gain / Чутливість)
    b_iso, _, _ = textbox(
        right_x + 10, right_y + 40,
        "ПІДСИЛЕННЯ (ISO Gain)\n"
        "Аналогове підсилення G_ana · АЦП",
        size=13, pad=10, fill="#f0fdf4", stroke=FIELD, sw=2, bold=True, color=FIELD
    )
    frags.append(b_iso)

    # Опис підсилення
    b_iso_desc, _, _ = textbox(
        right_x - 50, right_y - 65,
        "Низьке (ISO 100): високий SNR · чистий сигнал\n"
        "Високе (ISO 6400): робота в темряві · високий шум",
        size=11, pad=8, fill="#ffffff", stroke=FIELD, sw=1.2, color=INK
    )
    frags.append(b_iso_desc)

    return render(os.path.join(IMG_DIR, "exposure-triangle.svg"), w, h, *frags)


def fig_dof_geometry_coc():
    """Фігура 2: Геометрія глибини різкості, кружок розмиття (CoC) та гіперфокальна відстань."""
    w, h = 860, 460
    frags = []

    # Головна оптична вісь
    y_axis = 220
    frags.append(line(30, y_axis, 830, y_axis, color=MUTED, sw=1.5, dash="6,4"))
    frags.append(text(820, y_axis - 10, "Оптична вісь", size=11, color=MUTED, anchor="end"))

    # Положення елементів
    x_lens = 380
    x_sensor = 680
    aperture_d = 140  # Діаметр зіниці D

    # Тонка лінза / апертурна діафрагма
    frags.append(line(x_lens, y_axis - aperture_d / 2 - 30, x_lens, y_axis + aperture_d / 2 + 30, color=NEG, sw=2))
    # Обмеження апертури (отвір діафрагми)
    frags.append(line(x_lens - 8, y_axis - aperture_d / 2, x_lens + 8, y_axis - aperture_d / 2, color=POS, sw=3))
    frags.append(line(x_lens - 8, y_axis + aperture_d / 2, x_lens + 8, y_axis + aperture_d / 2, color=POS, sw=3))
    frags.append(text(x_lens, y_axis - aperture_d / 2 - 40, "Діафрагма (D = f / N)", size=12, color=POS, bold=True))

    # Сенсор (площина зображення)
    frags.append(line(x_sensor, y_axis - 120, x_sensor, y_axis + 120, color=LINE, sw=3))
    frags.append(text(x_sensor, y_axis - 130, "Площина сенсора", size=12, color=LINE, bold=True))

    # Сфокусований предмет (на відстані s): точка фокусування на сенсорі
    # Промені від сфокусованого предмета сходяться точно на сенсорі в точці (x_sensor, y_axis)
    frags.append(line(x_lens, y_axis - aperture_d / 2, x_sensor, y_axis, color="#2563eb", sw=1.8))
    frags.append(line(x_lens, y_axis + aperture_d / 2, x_sensor, y_axis, color="#2563eb", sw=1.8))

    # Близький предмет (Dn): сходиться за сенсором у точці x_focus_near = 760
    x_focus_near = 760
    frags.append(line(x_lens, y_axis - aperture_d / 2, x_focus_near, y_axis, color=POS, sw=1.5, dash="4,3"))
    frags.append(line(x_lens, y_axis + aperture_d / 2, x_focus_near, y_axis, color=POS, sw=1.5, dash="4,3"))

    # Далекий предмет (Df): сходиться перед сенсором у точці x_focus_far = 620
    x_focus_far = 620
    frags.append(line(x_lens, y_axis - aperture_d / 2, x_focus_far, y_axis, color=FIELD, sw=1.5, dash="4,3"))
    frags.append(line(x_lens, y_axis + aperture_d / 2, x_focus_far, y_axis, color=FIELD, sw=1.5, dash="4,3"))
    # Продовження променів за точку перетину до сенсора
    frags.append(line(x_focus_far, y_axis, x_sensor, y_axis + 18, color=FIELD, sw=1.5, dash="4,3"))
    frags.append(line(x_focus_far, y_axis, x_sensor, y_axis - 18, color=FIELD, sw=1.5, dash="4,3"))

    # Кружок розмиття CoC на сенсорі
    coc_h = 36
    frags.append(line(x_sensor - 4, y_axis - coc_h / 2, x_sensor + 4, y_axis - coc_h / 2, color=POS, sw=2))
    frags.append(line(x_sensor - 4, y_axis + coc_h / 2, x_sensor + 4, y_axis + coc_h / 2, color=POS, sw=2))
    frags.append(line(x_sensor + 16, y_axis - coc_h / 2, x_sensor + 16, y_axis + coc_h / 2, color=POS, sw=1.5))
    frags.append(text(x_sensor + 24, y_axis + 4, "Кружок розмиття (c)", size=11, color=POS, anchor="start", bold=True))

    # Предмети у просторі предметів (ліворуч)
    x_obj_near = 120
    x_obj_focus = 180
    x_obj_far = 270

    # Маркери об'єктів
    frags.append(circle(x_obj_near, y_axis, 5, fill=POS, stroke=POS))
    frags.append(text(x_obj_near, y_axis + 22, "D_near", size=11, color=POS, bold=True))

    frags.append(circle(x_obj_focus, y_axis, 5, fill="#2563eb", stroke="#2563eb"))
    frags.append(text(x_obj_focus, y_axis + 22, "s (фокус)", size=11, color="#2563eb", bold=True))

    frags.append(circle(x_obj_far, y_axis, 5, fill=FIELD, stroke=FIELD))
    frags.append(text(x_obj_far, y_axis + 22, "D_far", size=11, color=FIELD, bold=True))

    # Зона різкості (DoF)
    frags.append(line(x_obj_near, y_axis - 40, x_obj_far, y_axis - 40, color=FIELD, sw=3))
    frags.append(line(x_obj_near, y_axis - 48, x_obj_near, y_axis - 32, color=FIELD, sw=2))
    frags.append(line(x_obj_far, y_axis - 48, x_obj_far, y_axis - 32, color=FIELD, sw=2))
    frags.append(text((x_obj_near + x_obj_far) / 2, y_axis - 52, "Глибина різкості (DoF)", size=12, color=FIELD, bold=True))

    # Інформаційна плашка знизу
    b_info, _, _ = textbox(
        430, 400,
        "Гіперфокальна відстань: H = f² / (N · c)\n"
        "Ближня межа різкості: D_n = (s · H) / (H + s)    |    Дальня межа: D_f = (s · H) / (H - s)\n"
        "При фокусуванні на H різким є весь простір від H / 2 до нескінченності (∞)",
        size=12, pad=10, fill="#f8fafc", stroke="#64748b", sw=1.5
    )
    frags.append(b_info)

    return render(os.path.join(IMG_DIR, "dof-geometry-coc.svg"), w, h, *frags)


def fig_vignetting_cos4():
    """Фігура 3: Закон спадання освітленості cos⁴ θ, геометрія похилих пучків та віньєтування."""
    w, h = 860, 480
    frags = []

    # Центр оптичної системи (зіниця лінзи)
    x_pupil = 240
    y_pupil = 240
    pupil_r = 50

    # Площина сенсора
    x_sens = 620
    y_sens_center = 240
    sens_h = 320

    # Оптична вісь (осьовий промінь θ = 0)
    frags.append(line(x_pupil - 80, y_pupil, x_sens + 80, y_pupil, color=MUTED, sw=1.5, dash="6,4"))
    frags.append(text(x_sens + 70, y_pupil - 10, "Оптична вісь", size=11, color=MUTED, anchor="end"))

    # Апертурна зіниця
    frags.append(line(x_pupil, y_pupil - pupil_r - 20, x_pupil, y_pupil + pupil_r + 20, color=NEG, sw=2))
    frags.append(line(x_pupil - 6, y_pupil - pupil_r, x_pupil + 6, y_pupil - pupil_r, color=POS, sw=3))
    frags.append(line(x_pupil - 6, y_pupil + pupil_r, x_pupil + 6, y_pupil + pupil_r, color=POS, sw=3))
    frags.append(text(x_pupil, y_pupil - pupil_r - 30, "Вхідна зіниця (площа A₀)", size=12, color=POS, bold=True))

    # Сенсор
    frags.append(line(x_sens, y_sens_center - sens_h / 2, x_sens, y_sens_center + sens_h / 2, color=LINE, sw=3.5))
    frags.append(text(x_sens, y_sens_center - sens_h / 2 - 15, "Сенсор зображення", size=12, color=LINE, bold=True))

    # Центральна точка сенсора (E₀)
    frags.append(circle(x_sens, y_sens_center, 4, fill=POS, stroke=POS))
    frags.append(text(x_sens + 15, y_sens_center + 4, "Центр: E₀", size=12, color=POS, anchor="start", bold=True))

    # Крайова точка сенсора (кутовий промінь під кутом θ = 30°)
    y_edge = y_sens_center - 130
    frags.append(circle(x_sens, y_edge, 4, fill=NEG, stroke=NEG))
    frags.append(text(x_sens + 15, y_edge + 4, "Край: E(θ) = E₀ · cos⁴ θ", size=12, color=NEG, anchor="start", bold=True))

    # Похилий головний промінь під кутом θ
    frags.append(line(x_pupil, y_pupil, x_sens, y_edge, color=NEG, sw=2))

    # Дуга кута θ
    frags.append(
        '<path d="M %d,%d A 70 70 0 0 0 %d,%d" fill="none" stroke="%s" stroke-width="1.8"/>'
        % (x_pupil + 70, y_pupil, x_pupil + 64, y_pupil - 27, NEG)
    )
    frags.append(text(x_pupil + 85, y_pupil - 12, "θ", size=13, color=NEG, bold=True))

    # 4 геометричні фактори спадання світла (інформаційні блоки)
    factors_text = (
        "Чотири множники закону cos⁴ θ:\n"
        "1. Проекція зіниці на похилий пучок: A(θ) = A₀ · cos θ\n"
        "2. Збільшення відстані до краю: r(θ) = d / cos θ  →  1 / r² ∝ cos² θ\n"
        "3. Закон Ламберта (кут падіння променів на сенсор): ∝ cos θ\n"
        "Підсумок природного віньєтування: E(θ) = E₀ · cos⁴ θ"
    )
    b_factors, _, _ = textbox(
        430, 400, factors_text,
        size=12, pad=10, fill="#f8fafc", stroke="#64748b", sw=1.5
    )
    frags.append(b_factors)

    # Профіль освітленості сенсора вгорі
    frags.append(text(430, 45, "Профіль природного спадання освітленості E(θ)", size=13, color=INK, bold=True))
    frags.append(line(240, 70, 620, 70, color=MUTED, sw=1.2))
    # Крива падіння освітленості
    curve_pts = "240,110 335,80 430,70 525,80 620,110"
    frags.append(
        '<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>'
        % (curve_pts, POS)
    )
    frags.append(text(430, 92, "100% (Центр)", size=11, color=POS, bold=True))
    frags.append(text(240, 125, "56% (θ=30°)", size=11, color=MUTED))
    frags.append(text(620, 125, "56% (θ=30°)", size=11, color=MUTED))

    return render(os.path.join(IMG_DIR, "vignetting-cos4-law.svg"), w, h, *frags)


def fig_aec_control_loop():
    """Фігура 4: Архітектура контуру автоматичного керування експозицією (AEC/AGC)."""
    w, h = 860, 460
    frags = []

    # Блоки контуру керування
    # 1. Сенсор CMOS (Raw кадр)
    b_sensor, _, _ = textbox(
        130, 150,
        "CMOS Сенсор\n"
        "Формування кадру\n"
        "Raw Bayer Data",
        size=12, pad=10, fill="#eff6ff", stroke=NEG, sw=2, bold=True, color=NEG
    )
    frags.append(b_sensor)

    # 2. Модуль збору статистики
    b_stats, _, _ = textbox(
        360, 150,
        "Аналіз яскравості\n"
        "Гістограма + ROI\n"
        "Y_mean = ∑ w_i · Y_i",
        size=12, pad=10, fill="#f8fafc", stroke=LINE, sw=1.8, bold=True
    )
    frags.append(b_stats)

    # 3. PID-регулятор експозиції
    b_pid, _, _ = textbox(
        600, 150,
        "AEC / AGC Регулятор\n"
        "Помилка e = Y_tgt - Y\n"
        "Розрахунок цільового EV",
        size=12, pad=10, fill="#fef2f2", stroke=POS, sw=2, bold=True, color=POS
    )
    frags.append(b_pid)

    # 4. Розподіл параметрів (State Machine)
    b_split, _, _ = textbox(
        600, 320,
        "Політика розподілу\n"
        "1. Anti-Flicker (10/8.33 мс)\n"
        "2. Витримка t_exp (пріоритет)\n"
        "3. Аналогове підсилення G_ana\n"
        "4. Цифрове підсилення G_dig",
        size=11, pad=10, fill="#f0fdf4", stroke=FIELD, sw=1.8, bold=True, color=FIELD
    )
    frags.append(b_split)

    # 5. Драйвер сенсора (I2C / SPI регістри)
    b_driver, _, _ = textbox(
        240, 320,
        "Драйвер сенсора (I2C)\n"
        "Запис регістрів витримки\n"
        "і аналогового підсилення",
        size=12, pad=10, fill="#f8fafc", stroke=LINE, sw=1.8, bold=True
    )
    frags.append(b_driver)

    # З'єднувальні стрілки
    frags.append(arrow(210, 150, 275, 150, color=LINE, sw=2))
    frags.append(arrow(445, 150, 505, 150, color=LINE, sw=2))
    frags.append(arrow(600, 205, 600, 255, color=LINE, sw=2))
    frags.append(arrow(480, 320, 360, 320, color=LINE, sw=2))

    # Зворотний зв'язок від драйвера до сенсора
    frags.append(line(130, 320, 130, 210, color=NEG, sw=2))
    frags.append(arrow(130, 210, 130, 205, color=NEG, sw=2))

    # Підписи до стрілок
    frags.append(text(242, 138, "Кадр", size=11, color=MUTED))
    frags.append(text(475, 138, "Y_mean", size=11, color=MUTED))
    frags.append(text(645, 230, "ΔEV", size=11, color=MUTED))
    frags.append(text(420, 308, "t_exp, Gain", size=11, color=MUTED))
    frags.append(text(85, 260, "Регістри", size=11, color=NEG, anchor="middle"))

    # Заголовок зверху
    frags.append(text(430, 40, "Замкнений контур автоекспозиції (AEC) та автопідсилення (AGC)", size=14, color=INK, bold=True))

    return render(os.path.join(IMG_DIR, "aec-control-loop.svg"), w, h, *frags)


def main():
    fig_exposure_triangle()
    fig_dof_geometry_coc()
    fig_vignetting_cos4()
    fig_aec_control_loop()
    print("Фігури успішно згенеровано у %s" % IMG_DIR)


if __name__ == "__main__":
    main()
