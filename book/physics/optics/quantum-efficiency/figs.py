# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — Зв'язок EQE та IQE у фотодетекторі
# Описує шлях фотонів від падіння на поверхню до збору носіїв:
# - Вхідний потік фотонів N_γ
# - Відбиття R (відбиті фотони R · N_γ)
# - Поглинання в пасивному шарі (втрати (1-R)(1-ζ))
# - Поглинання в активній зоні N_abs
# - Рекомбінаційні втрати носіїв (1 - η_coll)
# - Зібрані електрони N_e (EQE = N_e / N_γ)
# ═══════════════════════════════════════════════════════════════════════════
def fig_eqe_vs_iqe():
    W, H = 720, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Зв\'язок EQE та IQE у фотодетекторі', 16, INK, 'middle', bold=True))

    # Схема детектора зліва (шари)
    x0, y0 = 60, 60
    dw, dh = 240, 240

    # Шари фотодіода
    # 1. Антивідбивальне покриття / Поверхня
    f.append(rect(x0, y0, dw, 24, fill="#e1f5fe", stroke=LINE, sw=1.2))
    f.append(text(x0 + dw / 2, y0 + 16, 'Поверхня / Антивідбивальний шар (R)', 11, INK, 'middle'))

    # 2. Мертвий верхній шар (пасивне поглинання)
    f.append(rect(x0, y0 + 24, dw, 36, fill="#ffe0b2", stroke=LINE, sw=1.2))
    f.append(text(x0 + dw / 2, y0 + 46, 'Пасивний шар (поглинання без збору)', 11, INK, 'middle'))

    # 3. Активна зона (область збіднення)
    f.append(rect(x0, y0 + 60, dw, 120, fill="#e8f5e9", stroke=FIELD, sw=1.8))
    f.append(text(x0 + dw / 2, y0 + 115, 'Активна зона (генерація e⁻/h⁺)', 12, FIELD, 'middle', bold=True))
    f.append(text(x0 + dw / 2, y0 + 135, 'Внутрішня ефективність IQE', 11, MUTED, 'middle'))

    # 4. Підкладка / Нижні контакти
    f.append(rect(x0, y0 + 180, dw, 60, fill="#f5f5f5", stroke=LINE, sw=1.2))
    f.append(text(x0 + dw / 2, y0 + 215, 'Нижній контакт (збір носіїв)', 11, MUTED, 'middle'))

    # Стрілка фотонів зверху
    f.append(arrow(x0 + 60, y0 - 25, x0 + 60, y0 - 2, color=POS, sw=2.5))
    f.append(text(x0 + 60, y0 - 30, 'Падаючі фотони N_γ (100%)', 11, POS, 'middle', bold=True))

    # Відбитий пучок
    f.append(arrow(x0 + 60, y0, x0 + 10, y0 - 25, color=NEG, sw=1.8))
    f.append(text(x0 + 5, y0 - 30, 'Відбиття R', 10, NEG, 'end'))

    # Втрати в пасивному шарі
    f.append(arrow(x0 + 180, y0 + 40, x0 + 230, y0 + 40, color=MUTED, sw=1.5))
    f.append(text(x0 + 235, y0 + 44, 'Пасивні втрати (1−ζ)', 10, MUTED, 'start'))

    # Рекомбінація в активній зоні
    f.append(arrow(x0 + 180, y0 + 120, x0 + 230, y0 + 120, color=POS, sw=1.5))
    f.append(text(x0 + 235, y0 + 124, 'Рекомбінація (1−η_coll)', 10, POS, 'start'))

    # Зібраний струм знизу
    f.append(arrow(x0 + 60, y0 + 240, x0 + 60, y0 + 275, color=FIELD, sw=2.5))
    f.append(text(x0 + 60, y0 + 290, 'Зібраний струм N_e (EQE)', 11, FIELD, 'middle', bold=True))

    # Права частина — Блок математичного підсумку
    bx, by = 350, 70
    bw, bh = 340, 230
    f.append(rect(bx, by, bw, bh, fill="#f8f9fa", stroke=LINE, sw=1.5, rx=8))

    f.append(text(bx + bw / 2, by + 28, 'Формули співвідношення', 14, INK, 'middle', bold=True))

    f.append(text(bx + 20, by + 65, 'Зовнішня квантова ефективність (EQE):', 12, INK, 'start', bold=True))
    f.append(text(bx + 35, by + 88, 'EQE = N_e / N_γ', 13, POS, 'start', bold=True))

    f.append(text(bx + 20, by + 120, 'Внутрішня квантова ефективність (IQE):', 12, INK, 'start', bold=True))
    f.append(text(bx + 35, by + 143, 'IQE = N_e / N_abs', 13, FIELD, 'start', bold=True))

    f.append(text(bx + 20, by + 175, 'Повний розклад втрат:', 12, INK, 'start', bold=True))
    f.append(text(bx + 35, by + 200, 'EQE = (1 − R) · ζ · IQE', 14, INK, 'start', bold=True))

    f.append(text(W / 2, H - 12,
                  'EQE враховує оптичні та рекомбінаційні втрати; IQE показує ефективність поглинутої частки світла',
                  11, MUTED, 'middle'))

    render(os.path.join(IMG, 'eqe-vs-iqe.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Спектральна квантова ефективність η(λ) та чутливість R_λ (А/Вт)
# ═══════════════════════════════════════════════════════════════════════════
def fig_spectral_responsivity():
    W, H = 720, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Спектральна квантова ефективність η(λ) та чутливість R_λ', 16, INK, 'middle', bold=True))

    # Осі координат
    ox, oy = 80, 280
    gx_w, gy_h = 560, 210

    # Графічні осі
    f.append(line(ox, oy, ox + gx_w, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - gy_h, color=FIELD, sw=1.8))
    f.append(line(ox + gx_w, oy, ox + gx_w, oy - gy_h, color=POS, sw=1.8))

    # Підписи осей
    f.append(text(ox + gx_w / 2, oy + 42, 'Довжина хвилі λ (нм)', 12, INK, 'middle', bold=True))
    f.append(text(ox - 45, oy - gy_h / 2, 'Квантова ефективність EQE (%)', 11, FIELD, 'middle', bold=True))
    f.append(text(ox + gx_w + 45, oy - gy_h / 2, 'Чутливість R_λ (А/Вт)', 11, POS, 'middle', bold=True))

    # Позначки довжин хвиль на осі X: 300, 500, 700, 900, 1100 (для кремнію)
    ticks = [
        (300, '300 (УФ)'),
        (500, '500'),
        (700, '700'),
        (900, '900 (ІЧ)'),
        (1100, '1100 (λ_c)'),
    ]
    for w_nm, label in ticks:
        tx = ox + (w_nm - 300) / (1150 - 300) * gx_w
        f.append(line(tx, oy, tx, oy + 5, color=INK, sw=1.2))
        f.append(text(tx, oy + 20, label, 10, MUTED, 'middle'))
        # Вертикальна сітка
        f.append(line(tx, oy, tx, oy - gy_h, color="#e0e0e0", sw=1, dash="3,3"))

    # Побудова кривих:
    eqe_pts = []
    resp_pts = []

    # Генерація точок кривих
    for w in range(300, 1150, 10):
        tx = ox + (w - 300) / (1150 - 300) * gx_w

        if w < 400:
            eta = 0.35 + (w - 300) / 100.0 * 0.45
        elif w <= 850:
            eta = 0.80 + 0.10 * math.sin((w - 400) / 450.0 * math.pi)
        elif w <= 1100:
            eta = 0.90 * math.pow((1100 - w) / 250.0, 0.7)
        else:
            eta = 0.0

        resp = eta * (w / 1240.0)

        ty_eqe = oy - eta * (gy_h * 0.9)
        ty_resp = oy - (resp / 0.7) * (gy_h * 0.9)

        eqe_pts.append((tx, ty_eqe))
        resp_pts.append((tx, ty_resp))

    # Малювання кривої EQE (Зелений/Field)
    path_eqe = "M " + " L ".join(["%.1f %.1f" % (x, y) for x, y in eqe_pts])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_eqe, FIELD))

    # Малювання кривої Responsivity (Червоний/Pos)
    path_resp = "M " + " L ".join(["%.1f %.1f" % (x, y) for x, y in resp_pts])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="6,3"/>' % (path_resp, POS))

    # Пояснювальні виноси
    f.append(text(ox + 120, oy - 140, 'Квантова ефективність η(λ)', 12, FIELD, 'start', bold=True))
    f.append(text(ox + 320, oy - 200, 'Спектральна чутливість R_λ (лінійне зростання)', 12, POS, 'start', bold=True))

    # Позначка довжини хвилі відсічки
    tc_x = ox + (1100 - 300) / (1150 - 300) * gx_w
    f.append(line(tc_x, oy - gy_h, tc_x, oy, color=POS, sw=1.5, dash="4,4"))
    f.append(text(tc_x - 10, oy - gy_h + 20, 'Відсічка: λ_c = hc / E_g', 11, POS, 'end', bold=True))

    f.append(text(W / 2, H - 10,
                  'Чутливість R_λ зростає з λ навіть за сталого η, бо довші хвилі несуть більше фотонів на 1 Ват потужності',
                  11, MUTED, 'middle'))

    render(os.path.join(IMG, 'spectral-responsivity.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — Профіль поглинання фотонів та збору носіїв у p-i-n фотодіоді
# ═══════════════════════════════════════════════════════════════════════════
def fig_pin_absorption_profile():
    W, H = 720, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Профіль поглинання світла та збір носіїв у p-i-n фотодіоді', 16, INK, 'middle', bold=True))

    # Шари диода
    ox, oy = 80, 80
    w_p, w_i, w_n = 70, 320, 150
    h_layer = 180

    # P+ шар
    f.append(rect(ox, oy, w_p, h_layer, fill="#ffebee", stroke=LINE, sw=1.2))
    f.append(text(ox + w_p / 2, oy + 25, 'p+ шар', 12, POS, 'middle', bold=True))
    f.append(text(ox + w_p / 2, oy + 45, '(тонка віконна зона)', 10, MUTED, 'middle'))

    # Intrinsic (i) шар - область збіднення
    f.append(rect(ox + w_p, oy, w_i, h_layer, fill="#e8f5e9", stroke=FIELD, sw=1.8))
    f.append(text(ox + w_p + w_i / 2, oy + 25, 'i-шар (Область збіднення W)', 13, FIELD, 'middle', bold=True))
    f.append(text(ox + w_p + w_i / 2, oy + 45, 'Сильне електричне поле E (швидкий дрейф, η_coll ≈ 1)', 11, INK, 'middle'))

    # N+ шар
    f.append(rect(ox + w_p + w_i, oy, w_n, h_layer, fill="#e3f2fd", stroke=LINE, sw=1.2))
    f.append(text(ox + w_p + w_i + w_n / 2, oy + 25, 'n+ підкладка', 12, NEG, 'middle', bold=True))

    # Експоненціальна крива інтенсивності світла I(x) = I_0 * exp(-alpha * x)
    exp_pts = []
    alpha = 0.008
    for x_rel in range(0, w_p + w_i + w_n, 5):
        val = math.exp(-alpha * x_rel)
        px = ox + x_rel
        py = oy + h_layer - (val * (h_layer - 40) + 10)
        exp_pts.append((px, py))

    path_exp = "M " + " L ".join(["%.1f %.1f" % (x, y) for x, y in exp_pts])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_exp, POS))
    f.append(text(ox + 90, oy + 120, 'Інтенсивність I(x) = I₀ · e⁻ᵃˣ', 12, POS, 'start', bold=True))

    # Стрілка світла
    f.append(arrow(ox - 40, oy + h_layer / 2, ox - 5, oy + h_layer / 2, color=POS, sw=3))
    f.append(text(ox - 45, oy + h_layer / 2 - 10, 'Світло I₀', 11, POS, 'end', bold=True))

    # Дрейф носіїв в i-шарі
    cx_i = ox + w_p + w_i / 2
    f.append(circle(cx_i - 30, oy + 120, 10, fill=NEG, stroke=NEG, sw=1))
    f.append(text(cx_i - 30, oy + 124, 'e⁻', 11, "#ffffff", 'middle', bold=True))
    f.append(arrow(cx_i - 20, oy + 120, cx_i + 40, oy + 120, color=NEG, sw=2))

    f.append(circle(cx_i + 30, oy + 150, 10, fill=POS, stroke=POS, sw=1))
    f.append(text(cx_i + 30, oy + 154, 'h⁺', 11, "#ffffff", 'middle', bold=True))
    f.append(arrow(cx_i + 20, oy + 150, cx_i - 40, oy + 150, color=POS, sw=2))

    f.append(text(W / 2, H - 15,
                  'Фотони, поглинуті у виснаженому i-шарі, дають майже 100% збір носіїв завдяки дрейфу в сильному полі',
                  11, MUTED, 'middle'))

    render(os.path.join(IMG, 'pin-absorption-profile.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 4 — FSI vs BSI у матрицях CMOS
# ═══════════════════════════════════════════════════════════════════════════
def fig_fsi_vs_bsi():
    W, H = 720, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Порівняння сенсорів FSI та BSI (Front-Side vs Back-Side Illumination)', 16, INK, 'middle', bold=True))

    # Ліва панель: FSI
    p1_cx = 190
    f.append(rect(30, 50, 320, 260, fill="#fafafa", stroke=LINE, sw=1.2, rx=6))
    f.append(text(p1_cx, 75, 'FSI (Пряме підсвічування)', 14, INK, 'middle', bold=True))
    f.append(text(p1_cx, 95, 'Квантова ефективність EQE ~ 40–50%', 12, POS, 'middle'))

    # Шари FSI:
    f.append(rect(p1_cx - 80, 115, 160, 18, fill="#e1f5fe", stroke=LINE, sw=1, rx=8))
    f.append(text(p1_cx, 128, 'Мікролінза', 10, INK, 'middle'))

    f.append(rect(p1_cx - 100, 140, 200, 70, fill="#efebe9", stroke=LINE, sw=1))
    f.append(rect(p1_cx - 80, 150, 40, 15, fill="#78909c", stroke=LINE, sw=1))
    f.append(rect(p1_cx + 40, 150, 40, 15, fill="#78909c", stroke=LINE, sw=1))
    f.append(rect(p1_cx - 60, 180, 40, 15, fill="#78909c", stroke=LINE, sw=1))
    f.append(rect(p1_cx + 20, 180, 40, 15, fill="#78909c", stroke=LINE, sw=1))
    f.append(text(p1_cx, 172, 'Металеві шари шин', 11, INK, 'middle', bold=True))

    f.append(rect(p1_cx - 100, 220, 200, 60, fill="#e8f5e9", stroke=FIELD, sw=1.5))
    f.append(text(p1_cx, 255, 'Кремнієвий фотодіод', 12, FIELD, 'middle', bold=True))

    f.append(arrow(p1_cx - 30, 105, p1_cx - 30, 220, color=POS, sw=2))
    f.append(arrow(p1_cx + 50, 105, p1_cx + 50, 150, color=MUTED, sw=2))
    f.append(text(p1_cx + 85, 148, 'блокування', 10, MUTED, 'start'))

    # Права панель: BSI
    p2_cx = 530
    f.append(rect(370, 50, 320, 260, fill="#fafafa", stroke=LINE, sw=1.2, rx=6))
    f.append(text(p2_cx, 75, 'BSI (Зворотне підсвічування)', 14, INK, 'middle', bold=True))
    f.append(text(p2_cx, 95, 'Квантова ефективність EQE ~ 80–95%', 12, FIELD, 'middle', bold=True))

    f.append(rect(p2_cx - 80, 115, 160, 18, fill="#e1f5fe", stroke=LINE, sw=1, rx=8))
    f.append(text(p2_cx, 128, 'Мікролінза', 10, INK, 'middle'))

    f.append(rect(p2_cx - 100, 140, 200, 65, fill="#e8f5e9", stroke=FIELD, sw=1.8))
    f.append(text(p2_cx, 175, 'Кремнієвий фотодіод (100% апертура)', 12, FIELD, 'middle', bold=True))

    f.append(rect(p2_cx - 100, 215, 200, 70, fill="#efebe9", stroke=LINE, sw=1))
    f.append(rect(p2_cx - 80, 230, 40, 15, fill="#78909c", stroke=LINE, sw=1))
    f.append(rect(p2_cx + 40, 230, 40, 15, fill="#78909c", stroke=LINE, sw=1))
    f.append(text(p2_cx, 260, 'Металеві провідники (знизу)', 11, INK, 'middle'))

    f.append(arrow(p2_cx - 40, 105, p2_cx - 40, 140, color=FIELD, sw=2.2))
    f.append(arrow(p2_cx + 40, 105, p2_cx + 40, 140, color=FIELD, sw=2.2))

    f.append(text(W / 2, H - 12,
                  'Перевертання кристаллу у BSI прибирає затінення металевими шинами та подвоює квантовий вихід',
                  11, MUTED, 'middle'))

    render(os.path.join(IMG, 'fsi-vs-fsi.svg' if False else 'fsi-vs-bsi.svg'), W, H, *f)


fig_eqe_vs_iqe()
fig_spectral_responsivity()
fig_pin_absorption_profile()
fig_fsi_vs_bsi()
print('Generated all figures for quantum-efficiency.')
