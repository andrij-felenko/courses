# -*- coding: utf-8 -*-
"""Фігури до теми «Коефіцієнт відбиття».
Запуск: python figs.py  → створює SVG у ./img/
Стиль та помічники — зі спільного svgkit.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

import math

# Кольорова палітра для ВЧ хвильових явищ
WAVE_INC  = "#2457d6"  # Падаюча хвиля V+ (синій)
WAVE_REF  = "#c0392b"  # Відбита хвиля V- (червоний)
LOAD_COLOR = "#8e44ad" # Навантаження Z_L (пурпуровий)
LINE_COLOR = "#2c3e50" # Лінія передачі Z_0
AXIS_COLOR = "#7f8c8d" # Осі координат


# ── 1. Фізичний механізм виникнення відбитої хвилі ───────────────────────────
def fig_gamma_concept():
    W, H = 840, 430
    f = [text(W / 2, 28, "Межа розділу лінії передачі Z₀ та навантаження Z_L", size=16, bold=True)]

    # Головний блок лінії передачі
    f.append(rect(40, 60, 480, 230, fill="#f8fafc", stroke=LINE_COLOR, sw=2, rx=8))
    f.append(text(280, 90, "Двопровідна лінія передачі (хвильовий опір Z₀)", size=13, bold=True, color=LINE_COLOR))

    # Провідники лінії
    f.append(line(60, 130, 520, 130, color=LINE_COLOR, sw=3))
    f.append(line(60, 230, 520, 230, color=LINE_COLOR, sw=3))

    # Падаюча хвиля V+
    f.append(arrow(100, 160, 360, 160, color=WAVE_INC, sw=3))
    f.append(text(230, 150, "Падаюча хвиля V⁺ = V₀ e⁻ʲᵇᶻ", size=13, bold=True, color=WAVE_INC))

    # Відбита хвиля V-
    f.append(arrow(360, 200, 100, 200, color=WAVE_REF, sw=3))
    f.append(text(230, 220, "Відбита хвиля V⁻ = Γ · V⁺ = V₀ Γ e⁺ʲᵇᶻ", size=13, bold=True, color=WAVE_REF))

    # Навантаження Z_L
    f.append(rect(520, 110, 140, 140, fill="#f5eeed", stroke=LOAD_COLOR, sw=2.5, rx=6))
    f.append(text(590, 165, "Навантаження", size=13, bold=True, color=LOAD_COLOR))
    f.append(text(590, 190, "Z_L = R_L + j X_L", size=13, bold=True, color=LOAD_COLOR))

    # З'єднання навантаження
    f.append(line(520, 130, 550, 130, color=LINE_COLOR, sw=3))
    f.append(line(520, 230, 550, 230, color=LINE_COLOR, sw=3))
    f.append(circle(520, 130, 4, fill=LINE_COLOR, stroke=LINE_COLOR))
    f.append(circle(520, 230, 4, fill=LINE_COLOR, stroke=LINE_COLOR))

    # Граничні умови та формульний підсумок (внизу)
    box_txt = (
        "Гранична умова на межі z = 0 (безперервність напруги та струму):\n"
        "V(0) = V⁺ + V⁻,   I(0) = (V⁺ − V⁻) / Z₀ = V(0) / Z_L\n"
        "Формула коефіцієнта відбиття:  Γ_L = V⁻ / V⁺ = (Z_L − Z₀) / (Z_L + Z₀)"
    )
    f.append(fitbox(40, 310, 760, 95, box_txt, size=13, fill="#eef2f7", stroke=LINE_COLOR, bold=True))

    render(os.path.join(IMG, 'gamma-concept.svg'), W, H, *f)


# ── 2. Комплексна площина коефіцієнта відбиття ──────────────────────────────
def fig_gamma_complex_plane():
    W, H = 820, 520
    f = [text(W / 2, 28, "Комплексна площина Г = Re(Г) + j Im(Г) та одиничне коло", size=16, bold=True)]

    # Центр системи координат
    cx, cy = 340, 270
    R = 190  # радіус одиничного кола |Γ| = 1

    # Одиничне коло |Γ| = 1
    f.append(circle(cx, cy, R, fill="#fdfefe", stroke=LINE_COLOR, sw=2))

    # Осі координат
    f.append(line(cx - R - 40, cy, cx + R + 40, cy, color=AXIS_COLOR, sw=1.5))
    f.append(line(cx, cy - R - 40, cx, cy + R + 40, color=AXIS_COLOR, sw=1.5))
    f.append(text(cx + R + 55, cy + 4, "Re(Γ)", size=13, bold=True, color=AXIS_COLOR))
    f.append(text(cx, cy - R - 50, "Im(Γ)", size=13, bold=True, color=AXIS_COLOR))

    # Ключові точки на комплексному колі
    # 1. Центр: Г = 0 (Z_L = Z_0)
    f.append(circle(cx, cy, 6, fill=FIELD, stroke=FIELD))
    f.append(text(cx + 25, cy - 25, "Г = 0 (Z_L = Z₀)", size=11, bold=True, color=FIELD))
    f.append(text(cx + 25, cy - 10, "Узгоджено", size=10, color=FIELD))

    # 2. Правий край: Г = +1 (Z_L = ∞, Розрив)
    f.append(circle(cx + R, cy, 6, fill=WAVE_REF, stroke=WAVE_REF))
    f.append(text(cx + R - 10, cy - 15, "Г = +1 (Z_L = ∞)", size=11, bold=True, color=WAVE_REF, anchor="end"))
    f.append(text(cx + R - 10, cy + 18, "Холостий хід", size=10, color=WAVE_REF, anchor="end"))

    # 3. Лівий край: Г = -1 (Z_L = 0, КЗ)
    f.append(circle(cx - R, cy, 6, fill=WAVE_INC, stroke=WAVE_INC))
    f.append(text(cx - R + 10, cy - 15, "Г = −1 (Z_L = 0)", size=11, bold=True, color=WAVE_INC, anchor="start"))
    f.append(text(cx - R + 10, cy + 18, "Коротке замикання", size=10, color=WAVE_INC, anchor="start"))

    # 4. Верхній край: Г = +j (Z_L = +j Z_0, Індуктивне КЗ)
    f.append(circle(cx, cy - R, 5, fill=LOAD_COLOR, stroke=LOAD_COLOR))
    f.append(text(cx + 12, cy - R - 5, "Г = +j (Z_L = +jZ₀)", size=11, bold=True, color=LOAD_COLOR, anchor="start"))

    # 5. Нижній край: Г = -j (Z_L = -j Z_0, Ємнісне КЗ)
    f.append(circle(cx, cy + R, 5, fill=LOAD_COLOR, stroke=LOAD_COLOR))
    f.append(text(cx + 12, cy + R + 15, "Г = −j (Z_L = −jZ₀)", size=11, bold=True, color=LOAD_COLOR, anchor="start"))

    # Довільний комплексний вектор Г
    px, py = cx + 110, cy - 100
    f.append(line(cx, cy, px, py, color=LOAD_COLOR, sw=2.5))
    f.append(circle(px, py, 5, fill=LOAD_COLOR, stroke=LOAD_COLOR))
    f.append(text(px + 10, py - 10, "Г = |Г| eʲᶲ", size=12, bold=True, color=LOAD_COLOR))
    f.append(text(px + 10, py + 8, "(Z_L = R + jX)", size=10, color=LOAD_COLOR))

    # Дуга фазового кута phi
    f.append(text(cx + 45, cy - 20, "φ", size=13, bold=True, color=LOAD_COLOR))

    # Пояснювальна інфографіка праворуч
    info_txt = (
        "Області комплексного кола:\n\n"
        "• Внутрішність кола (|Γ| < 1):\n"
        "  Пасивні навантаження (R_L > 0)\n\n"
        "• Верхня півплощина (Im(Γ) > 0):\n"
        "  Індуктивний характер (X_L > 0)\n\n"
        "• Нижня півплощина (Im(Γ) < 0):\n"
        "  Ємнісний характер (X_L < 0)\n\n"
        "• Одиничне коло (|Γ| = 1):\n"
        "  Реактивні навантаження (R_L = 0)"
    )
    f.append(fitbox(580, 80, 220, 380, info_txt, size=11.5, fill="#f8fafc", stroke=LINE_COLOR, bold=False))

    render(os.path.join(IMG, 'gamma-complex-plane.svg'), W, H, *f)


# ── 3. Трансформація коефіцієнта відбиття вздовж лінії ───────────────────────
def fig_gamma_transformation_line():
    W, H = 840, 440
    f = [text(W / 2, 28, "Трансформація Г(l) = Г_L e⁻²ʲᵇˡ при русі вздовж лінії передачі", size=16, bold=True)]

    # Верхня частина: Фізична лінія з відстанню l
    f.append(rect(40, 60, 760, 110, fill="#f8fafc", stroke=LINE_COLOR, sw=1.5, rx=6))
    f.append(line(60, 95, 680, 95, color=LINE_COLOR, sw=2.5))
    f.append(line(60, 135, 680, 135, color=LINE_COLOR, sw=2.5))
    
    # Навантаження Z_L праворуч
    f.append(rect(680, 80, 100, 70, fill="#f5eeed", stroke=LOAD_COLOR, sw=2, rx=4))
    f.append(text(730, 120, "Z_L (Г_L)", size=12, bold=True, color=LOAD_COLOR))

    # Стрілка напрямку до генератора
    f.append(arrow(650, 155, 150, 155, color=WAVE_INC, sw=2))
    f.append(text(400, 160, "Відстань l від навантаження до генератора (рух за годинниковою стрілкою на Г-площині)", size=11, bold=True, color=WAVE_INC))

    # Нижня частина: Коло обертання вектора Г
    cx, cy = 250, 310
    R = 90

    # Коло постійного модуля |Г|
    f.append(circle(cx, cy, R, fill="#ffffff", stroke=LINE_COLOR, sw=1.5))
    f.append(line(cx - R - 20, cy, cx + R + 20, cy, color=AXIS_COLOR, sw=1))
    f.append(line(cx, cy - R - 20, cx, cy + R + 20, color=AXIS_COLOR, sw=1))

    # Вектор навантаження Г_L
    ang1 = -math.pi / 4
    x1, y1 = cx + R * math.cos(ang1), cy + R * math.sin(ang1)
    f.append(line(cx, cy, x1, y1, color=LOAD_COLOR, sw=2))
    f.append(circle(x1, y1, 4, fill=LOAD_COLOR, stroke=LOAD_COLOR))
    f.append(text(x1 + 15, y1 - 5, "Г_L (l = 0)", size=11, bold=True, color=LOAD_COLOR))

    # Вектор після трансформації Г(l)
    ang2 = ang1 + 2.2  # обертання за годинниковою
    x2, y2 = cx + R * math.cos(ang2), cy + R * math.sin(ang2)
    f.append(line(cx, cy, x2, y2, color=WAVE_INC, sw=2))
    f.append(circle(x2, y2, 4, fill=WAVE_INC, stroke=WAVE_INC))
    f.append(text(x2 - 15, y2 + 15, "Г(l) = Г_L e⁻²ʲᵇˡ", size=11, bold=True, color=WAVE_INC, anchor="end"))

    # Дуга обертання
    f.append(text(cx + 40, cy + 40, "2βl", size=12, bold=True, color=WAVE_INC))

    # Пояснення ключових періодів (праворуч)
    box_txt = (
        "Ключові властивості трансформації Г(l):\n\n"
        "1. Періодичність λ/2 (180° по довжині = 360° на площині):\n"
        "   Г(l + λ/2) = Г(l) e⁻²ʲ⁽²ᵖ/ˡ⁾⁽ˡ⁺ˡ/²⁾ = Г(l) e⁻²ʲᵖ = Г(l)\n"
        "   Імпеданс лінії повторюється кожні пів хвилі.\n\n"
        "2. Чвертьхвильовий трансформатор λ/4 (90° по довжині = 180° на площині):\n"
        "   Г(l + λ/4) = −Г(l)\n"
        "   Інверсія імпедансу: Z_in = Z₀² / Z_L (коротке стає розривом).\n\n"
        "3. Втрати в лінії (α > 0):\n"
        "   Модуль спадає: |Г(l)| = |Г_L| e⁻²ᵃˡ (спіраль до центру Г = 0)."
    )
    f.append(fitbox(420, 200, 390, 220, box_txt, size=11, fill="#edf2f7", stroke=LINE_COLOR, bold=False))

    render(os.path.join(IMG, 'gamma-transformation-line.svg'), W, H, *f)


# ── 4. Взаємозв'язок |Г|, КСХ, Втрат на відбиття та Потужності ────────────────
def fig_gamma_vs_vswr_rl():
    W, H = 840, 440
    f = [text(W / 2, 28, "Шкала співвідношення параметрів неузгодження ВЧ-тракту", size=16, bold=True)]

    # Таблична шкала режимів
    cols = [
        ("Режим", "|Г|", "КСХ (SWR)", "Return Loss", "Пропущена P", "Оцінка якості"),
        ("Ідеал (Узгоджено)", "0.00", "1.00 : 1", "∞ дБ", "100.0 %", "Відмінно"),
        ("Чудове узгодження", "0.05", "1.11 : 1", "26.0 дБ", "99.7 %", "Відмінно"),
        ("Стандарт ВЧ-техніки", "0.10", "1.22 : 1", "20.0 дБ", "99.0 %", "Добре"),
        ("Межа прийнятного", "0.33", "2.00 : 1", "9.5 дБ", "88.9 %", "Прийнятно"),
        ("Сильне відбиття", "0.50", "3.00 : 1", "6.0 дБ", "75.0 %", "Погано (ризик)"),
        ("Повне відбиття (КЗ/ХХ)", "1.00", "∞ : 1", "0.0 дБ", "0.0 %", "Критично"),
    ]

    y_start = 70
    row_h = 36
    col_w = [180, 80, 120, 120, 130, 130]

    for r_idx, row in enumerate(cols):
        y = y_start + r_idx * row_h
        is_head = (r_idx == 0)
        bg_col = "#2c3e50" if is_head else ("#ffffff" if r_idx % 2 == 1 else "#f8fafc")
        txt_col = "#ffffff" if is_head else INK
        
        x_curr = 40
        for c_idx, val in enumerate(row):
            w = col_w[c_idx]
            sw = 1.5 if is_head else 1
            strk = "#1a252f" if is_head else "#e2e8f0"
            f.append(rect(x_curr, y, w, row_h, fill=bg_col, stroke=strk, sw=sw, rx=0))
            f.append(text(x_curr + w / 2, y + row_h / 2 + 4, val, size=11, bold=is_head, color=txt_col))
            x_curr += w

    # Нижня частина: Точні математичні формули зв'язку
    eq_txt = (
        "Математичні формули взаємоперерахунку:\n"
        "• КСХ = (1 + |Γ|) / (1 − |Γ|)    ⇄    |Γ| = (КСХ − 1) / (КСХ + 1)\n"
        "• Return Loss (дБ) = −20 log₁₀ |Γ|    ⇄    |Γ| = 10⁻⁽ᴿᴸ ⁾²⁰⁾\n"
        "• Частка відбитої потужності P_ref / P_inc = |Γ|²\n"
        "• Частка пропущеної потужності P_trans / P_inc = 1 − |Γ|²"
    )
    f.append(fitbox(40, y_start + len(cols) * row_h + 20, 760, 100, eq_txt, size=11.5, fill="#edf2f7", stroke=LINE_COLOR, bold=False))

    render(os.path.join(IMG, 'gamma-vs-vswr-rl.svg'), W, H, *f)


if __name__ == '__main__':
    fig_gamma_concept()
    fig_gamma_complex_plane()
    fig_gamma_transformation_line()
    fig_gamma_vs_vswr_rl()
    print("Успішно згенеровано 4 фігури у ./img/")
