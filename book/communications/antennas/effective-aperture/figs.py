# -*- coding: utf-8 -*-
"""Фігури до теми «Ефективна апертура антени».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

import math

# Додаткові відтінки
WAVE = "#c0392b"       # Електромагнітна хвиля / Вектор Пойнтінга S
CAP_BG = "#e8f8f0"     # Заливка ефективної зони перехоплення
CAP_BORDER = "#27ae60" # Межа ефективної апертури
DISH_COLOR = "#34495e" # Метал антени / рефлектора
LOSS_COLOR = "#e74c3c" # Втрати / розсіювання

def _sine_wave(x0, y0, length, amp, cycles, color=WAVE, sw=2.0, n=100):
    pts = []
    for i in range(n + 1):
        t = i / float(n)
        x = x0 + t * length
        y = y0 - amp * math.sin(2 * math.pi * cycles * t)
        pts.append("%.1f,%.1f" % (x, y))
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round"/>' % (" ".join(pts), color, sw))


# ── 1. Фізична концепція ефективної апертури ─────────────────────────────────
def fig_aperture_concept():
    W, H = 740, 360
    f = [text(W / 2, 24, "Фізичний зміст ефективної апертури антени", size=16, bold=True)]

    # Ліва частина: Падаюча плоска хвиля з густиною S
    f.append(text(110, 55, "Падаюча хвиля", size=13, color=WAVE, bold=True))
    f.append(text(110, 72, "Густина потужності S [Вт/м²]", size=11, color=MUTED))

    # Кілька ліній плоского фронту з векторами Пойнтінга
    for y in (110, 160, 210, 260, 310):
        f.append(_sine_wave(30, y, 120, 8, 2.5, color=WAVE, sw=1.5))
        f.append(arrow(155, y, 220, y, color=WAVE, sw=2.0))

    # Зона ефективного перехоплення A_e (віртуальний прямокутник/вирва)
    ap_top = 110
    ap_bottom = 260
    ap_h = ap_bottom - ap_top
    ap_w = 40
    ap_x = 240

    # Заливка апертури
    f.append(rect(ap_x, ap_top, ap_w, ap_h, fill=CAP_BG, stroke=CAP_BORDER, sw=2.0, rx=4))
    f.append(text(ap_x + ap_w / 2, ap_top - 12, "Апертура A_e", size=13, color=CAP_BORDER, bold=True))

    # Рупорна антена
    horn_x1 = ap_x + ap_w
    horn_y1 = ap_top - 15
    horn_y2 = ap_bottom + 15
    horn_x2 = horn_x1 + 110
    horn_cy = (ap_top + ap_bottom) / 2

    # Контур рупора
    horn_path = ('M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z' %
                 (horn_x1, horn_y1, horn_x2, horn_cy - 20,
                  horn_x2, horn_cy + 20, horn_x1, horn_y2))
    f.append('<path d="%s" fill="%s" stroke="%s" stroke-width="2"/>' %
             (horn_path, FILL, DISH_COLOR))

    # Хвилевід та навантаження
    f.append(rect(horn_x2, horn_cy - 20, 70, 40, fill="#eaeded", stroke=DISH_COLOR, sw=2.0, rx=3))
    f.append(text(horn_x2 + 35, horn_cy - 4, "Приймач", size=12, bold=True))
    f.append(text(horn_x2 + 35, horn_cy + 12, "Z_L", size=11, color=MUTED))

    # Потік енергії у приймач
    f.append(arrow(horn_x2 + 70, horn_cy, horn_x2 + 130, horn_cy, color=FIELD, sw=2.5))
    
    # Вихідний блок результату
    res_b, rw, rh = textbox(horn_x2 + 175, horn_cy, "Прийнята\nпотужність\nP_r = S · A_e",
                            size=12, pad=10, fill="#eafaf1", stroke=FIELD, sw=2.0, bold=True)
    f.append(res_b)

    # Пояснювальний підпис знизу
    f.append(text(W / 2, 342, "Антена вихоплює з простору енергію з площі A_e і спрямовує її в приймач",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "aperture-concept.svg"), W, H, *f)


# ── 2. Дріт проти Дзеркала (Диполь проти Тарілки) ───────────────────────────
def fig_wire_vs_dish():
    W, H = 740, 340
    f = [text(W / 2, 24, "Фізична площа проти ефективної: тонкий дріт і парабола", size=16, bold=True)]

    # Ліва панель: Диполь
    cxL = 200
    cy = 180
    f.append(text(cxL, 55, "Півхвильовий диполь", size=14, bold=True))
    
    # Фізичний дріт диполя (товщина ~2 мм, площа майже 0)
    f.append(line(cxL, cy - 70, cxL, cy + 70, color=DISH_COLOR, sw=4.0))
    f.append(circle(cxL, cy, 4, fill=POS, stroke=POS, sw=1.0)) # кабель живлення
    f.append(text(cxL, cy + 90, "Фізична перетинкова площа:", size=11, color=MUTED))
    f.append(text(cxL, cy + 106, "A_phys ≈ 0.0005 м² (майже 0)", size=11, bold=True))

    # Зона ефективного перехоплення навколо диполя (невидима вирва)
    f.append(circle(cxL, cy, 65, fill=CAP_BG, stroke=CAP_BORDER, sw=1.8))
    # Перемальовуємо дріт поверх заливки
    f.append(line(cxL, cy - 70, cxL, cy + 70, color=DISH_COLOR, sw=4.0))
    f.append(circle(cxL, cy, 4, fill=POS, stroke=POS, sw=1.0))
    f.append(text(cxL + 12, cy - 15, "Невидима вирва", size=11, color=CAP_BORDER, anchor="start", italic=True))
    f.append(text(cxL + 12, cy + 5, "A_e ≈ 0.13 λ²", size=12, color=CAP_BORDER, anchor="start", bold=True))
    f.append(text(cxL + 12, cy + 22, "(на 144 МГц A_e ≈ 0.56 м²)", size=10, color=CAP_BORDER, anchor="start"))

    # Розділювач
    f.append(line(W / 2, 50, W / 2, 300, color="#d5dbdb", sw=1.5, dash="4,4"))

    # Права панель: Параболічне дзеркало
    cxR = 540
    f.append(text(cxR, 55, "Параболічна тарілка", size=14, bold=True))

    # Фізичний апертурний прямокутник / овал дзеркала
    f.append(rect(cxR - 90, cy - 75, 180, 150, fill="#f4f6f7", stroke=DISH_COLOR, sw=2.0, rx=8))
    f.append(text(cxR, cy - 50, "Фізична апертура A_phys", size=12, color=DISH_COLOR, bold=True))
    f.append(text(cxR, cy - 35, "A_phys = π D² / 4", size=11, color=MUTED))

    # Ефективна площа всередині фізичної
    f.append(rect(cxR - 70, cy - 10, 140, 70, fill=CAP_BG, stroke=CAP_BORDER, sw=2.0, rx=6))
    f.append(text(cxR, cy + 15, "Ефективна апертура A_e", size=12, color=CAP_BORDER, bold=True))
    f.append(text(cxR, cy + 35, "A_e = η_a · A_phys  (η_a ≈ 55…70%)", size=11, color=CAP_BORDER, bold=True))

    f.append(text(cxR, cy + 106, "A_e трохи менша за фізичний розмір", size=11, color=MUTED))

    render(os.path.join(IMG, "wire-vs-dish.svg"), W, H, *f)


# ── 3. Масштабування від частоти (1/f²) ──────────────────────────────────────
def fig_frequency_scaling():
    W, H = 740, 340
    f = [text(W / 2, 24, "Масштабування апертури від частоти при сталому підсиленні G = 10 дБі", size=15, bold=True)]

    # 3 колонки: 300 МГц, 3 ГГц, 30 ГГц
    cols = [
        (140, "300 МГц (λ = 1 м)", "A_e ≈ 8000 см²", "0.8 м²", 70, "#e8f8f0", CAP_BORDER),
        (370, "3 ГГц (λ = 10 см)", "A_e ≈ 80 см²", "0.008 м²", 35, "#fef9e7", "#f39c12"),
        (600, "30 ГГц (λ = 1 см)", "A_e ≈ 0.8 см²", "0.00008 м²", 12, "#fadbd8", POS)
    ]

    cy = 170
    for cx, title, area_str, area_m, r_size, bg_col, border_col in cols:
        f.append(text(cx, 60, title, size=13, bold=True))
        
        # Квадрат/коло що ілюструє відносний розмір апертури
        f.append(circle(cx, cy, r_size, fill=bg_col, stroke=border_col, sw=2.0))
        
        f.append(text(cx, cy + r_size + 24, area_str, size=13, color=border_col, bold=True))
        f.append(text(cx, cy + r_size + 42, "(" + area_m + ")", size=11, color=MUTED))

    # Стрілка динаміки падіння апертури
    f.append(arrow(100, 300, 640, 300, color=POS, sw=2.0))
    f.append(text(W / 2, 320, "При зростанні частоти у 100 разів ефективна апертура зменшується у 10 000 разів (∝ 1/f²)",
                  size=11, color=POS, bold=True))

    render(os.path.join(IMG, "frequency-scaling.svg"), W, H, *f)


# ── 4. Еквівалентна схема приймальної антени ──────────────────────────────────
def fig_equivalent_circuit():
    W, H = 740, 340
    f = [text(W / 2, 24, "Еквівалентна схема Тевеніна приймальної антени та розсіювання потужності", size=15, bold=True)]

    # Схема ліворуч (генератор і опори)
    x0 = 60
    y_top = 80
    y_bot = 240

    # Генератор напруги V_oc
    f.append(circle(x0, 160, 22, fill=FILL, stroke=INK, sw=2.0))
    f.append(text(x0, 165, "V_oc", size=12, bold=True))
    f.append(text(x0 - 45, 165, "Е·h_eff", size=11, color=MUTED))

    # Лінії контуру антени
    f.append(line(x0, y_top, x0, 138, color=INK, sw=2.0))
    f.append(line(x0, 182, x0, y_bot, color=INK, sw=2.0))

    # Опір випромінювання R_r
    f.append(rect(x0 + 40, y_top - 15, 50, 30, fill="#ebf5fb", stroke=NEG, sw=1.8, rx=2))
    f.append(text(x0 + 65, y_top + 4, "R_r", size=12, color=NEG, bold=True))

    # Опір втрат R_L
    f.append(rect(x0 + 110, y_top - 15, 50, 30, fill="#fdebd0", stroke="#d35400", sw=1.8, rx=2))
    f.append(text(x0 + 135, y_top + 4, "R_loss", size=12, color="#d35400", bold=True))

    # Реактивність антени X_A
    f.append(rect(x0 + 180, y_top - 15, 50, 30, fill=FILL, stroke=MUTED, sw=1.8, rx=2))
    f.append(text(x0 + 205, y_top + 4, "j X_A", size=12, color=MUTED, bold=True))

    # З'єднання
    f.append(line(x0, y_top, x0 + 40, y_top, color=INK, sw=2.0))
    f.append(line(x0 + 90, y_top, x0 + 110, y_top, color=INK, sw=2.0))
    f.append(line(x0 + 160, y_top, x0 + 180, y_top, color=INK, sw=2.0))
    f.append(line(x0 + 230, y_top, x0 + 290, y_top, color=INK, sw=2.0))
    f.append(line(x0, y_bot, x0 + 290, y_bot, color=INK, sw=2.0))

    # Клеми підключення навантаження
    f.append(circle(x0 + 290, y_top, 4, fill=INK, stroke=INK, sw=1.0))
    f.append(circle(x0 + 290, y_bot, 4, fill=INK, stroke=INK, sw=1.0))

    # Навантаження Z_load
    f.append(rect(x0 + 290, y_top + 30, 70, 100, fill="#e8f8f0", stroke=FIELD, sw=2.0, rx=4))
    f.append(text(x0 + 325, y_top + 70, "Z_load", size=13, color=FIELD, bold=True))
    f.append(text(x0 + 325, y_top + 90, "R_L + j X_L", size=10, color=MUTED))

    f.append(line(x0 + 290, y_top, x0 + 325, y_top, color=INK, sw=2.0))
    f.append(line(x0 + 325, y_top, x0 + 325, y_top + 30, color=INK, sw=2.0))
    f.append(line(x0 + 290, y_bot, x0 + 325, y_bot, color=INK, sw=2.0))
    f.append(line(x0 + 325, y_bot, x0 + 325, y_top + 130, color=INK, sw=2.0))

    # Права частина: Баланс потужності при сопряженій узгодженості (Z_load = Z_A*)
    cxR = 560
    b1, w1, h1 = textbox(cxR, 100, "Корисна потужність у навантаженні:\nP_L = |V_oc|² / (4 R_r)",
                         size=12, pad=8, fill="#eafaf1", stroke=FIELD, sw=1.8, bold=True)
    f.append(b1)

    b2, w2, h2 = textbox(cxR, 185, "Перевипромінена (розсіяна) потужність:\nP_scat = |V_oc|² / (4 R_r)",
                         size=12, pad=8, fill="#fdedec", stroke=LOSS_COLOR, sw=1.8, bold=True)
    f.append(b2)

    f.append(text(cxR, 260, "За ідеального узгодження антена віддає 50% енергії", size=11, bold=True))
    f.append(text(cxR, 276, "у навантаження, а інші 50% перевипромінює в простір!", size=11, color=LOSS_COLOR, bold=True))

    render(os.path.join(IMG, "equivalent-circuit.svg"), W, H, *f)


# ── 5. Компоненти коефіцієнта ефективності апертури (η_a) ────────────────────
def fig_efficiency_breakdown():
    W, H = 740, 360
    f = [text(W / 2, 24, "Структура коефіцієнта ефективності апертури η_a = η_s · η_t · η_b · η_r · η_o", size=14, bold=True)]

    # Схема дзеркала з опромінювачем
    cxDish = 140
    cyDish = 190

    # Дуга параболи
    f.append('<path d="M %d,%d Q %d,%d %d,%d" fill="none" stroke="%s" stroke-width="4.0"/>' %
             (cxDish - 70, cyDish - 100, cxDish + 30, cyDish, cxDish - 70, cyDish + 100, DISH_COLOR))

    # Обпромінювач (Horn feed) в фокусі
    f.append(rect(cxDish + 50, cyDish - 12, 30, 24, fill=FILL, stroke=INK, sw=1.8, rx=2))
    f.append(line(cxDish + 10, cyDish, cxDish + 50, cyDish, color=MUTED, sw=1.5, dash="3,3")) # штанга

    # Промені та втрати
    # 1. Spillover (переливання)
    f.append(arrow(cxDish + 50, cyDish - 10, cxDish - 90, cyDish - 120, color=LOSS_COLOR, sw=1.5))
    f.append(text(cxDish - 60, cyDish - 130, "Spillover (повз край) η_s", size=11, color=LOSS_COLOR, bold=True))

    # 2. Illumination taper (нерівномірність)
    f.append(arrow(cxDish + 50, cyDish - 5, cxDish - 40, cyDish - 50, color=FIELD, sw=1.5))
    f.append(arrow(cxDish - 40, cyDish - 50, cxDish + 140, cyDish - 50, color=FIELD, sw=1.5))

    # 3. Blockage (затінення опромінювачем)
    f.append(rect(cxDish + 80, cyDish - 20, 40, 40, fill="#fadbd8", stroke=POS, sw=1.2, rx=2))
    f.append(text(cxDish + 100, cyDish + 35, "Затінення η_b", size=11, color=POS, bold=True))

    # 4. Шорсткість (Ruze loss)
    f.append(text(cxDish - 80, cyDish + 120, "Неточність поверхні η_r", size=11, color=MUTED))

    # Блоки відсотків праворуч
    factors = [
        ("η_t (Спадок амплітуди / Taper)", "80…92%", "Нерівномірне поле по центру та краях"),
        ("η_s (Переливання / Spillover)", "85…95%", "Частина променів пролітає повз дзеркало"),
        ("η_b (Затінення / Blockage)", "90…98%", "Тінь від опромінювача та розтяжок"),
        ("η_r (Точність поверхні / Surface)", "90…99%", "Відхилення форма профілю від параболи"),
        ("η_o (Омічні втрати / Ohmic)", "95…99%", "Теплові втрати в металі та кабелі")
    ]

    xR = 280
    yR = 60
    for idx, (title, val, desc) in enumerate(factors):
        y_curr = yR + idx * 54
        # Рамка фактора
        f.append(rect(xR, y_curr, 430, 46, fill="#fdfefe", stroke="#cbd5e1", sw=1.5, rx=4))
        f.append(text(xR + 15, y_curr + 20, title, size=12, anchor="start", bold=True))
        f.append(text(xR + 415, y_curr + 20, val, size=12, color=FIELD, anchor="end", bold=True))
        f.append(text(xR + 15, y_curr + 37, desc, size=10, color=MUTED, anchor="start"))

    f.append(text(xR + 215, 342, "Типова підсумкова ефективність параболи: η_a ≈ 55% … 70%",
                  size=12, color=CAP_BORDER, bold=True))

    render(os.path.join(IMG, "efficiency-breakdown.svg"), W, H, *f)


def main():
    fig_aperture_concept()
    fig_wire_vs_dish()
    fig_frequency_scaling()
    fig_equivalent_circuit()
    fig_efficiency_breakdown()
    print("Згенеровано 5 фігур SVG у folder img/")

if __name__ == "__main__":
    main()
