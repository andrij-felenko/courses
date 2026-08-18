# -*- coding: utf-8 -*-
"""Генератор фігур для теми «Сегнетоелектричний тунельний перехід (FTJ)»."""

import os
import sys

# Підключаємо svgkit з scripts/ (4 рівні вгору від теми до кореня)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def make_fig1():
    """Фігура 1: Структура FTJ та потенціальний бар'єр у станах ON і OFF."""
    w, h = 800, 420
    frags = []

    # Заголовок
    frags.append(text(w / 2, 25, "Сегнетоелектричний тунельний перехід: Стан ON проти Стан OFF", size=16, bold=True))

    # Ліва панель — Стан ON (Низький опір)
    x1, y1, pw, ph = 30, 55, 355, 340
    frags.append(rect(x1, y1, pw, ph, fill="#ffffff", stroke="#cccccc", sw=1.5, rx=8))
    frags.append(text(x1 + pw / 2, y1 + 25, "Стан ON (Логічна «1»)", size=15, bold=True, color=POS))
    frags.append(text(x1 + pw / 2, y1 + 45, "Поляризація P ↓ (до BE)", size=12, color=MUTED, italic=True))

    # Схема шарів ON
    sy = y1 + 75
    frags.append(rect(x1 + 30, sy, 70, 40, fill="#e1e8ed", stroke="#4a5568", sw=1.5, rx=4))
    frags.append(text(x1 + 65, sy + 24, "TE (Pt)", size=12, bold=True))

    frags.append(rect(x1 + 100, sy, 155, 40, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
    frags.append(text(x1 + 177, sy + 18, "HZO (2 нм)", size=12, bold=True, color="#b45309"))
    frags.append(text(x1 + 177, sy + 33, "P ↓↓↓", size=13, bold=True, color=POS))

    frags.append(rect(x1 + 255, sy, 70, 40, fill="#e1e8ed", stroke="#4a5568", sw=1.5, rx=4))
    frags.append(text(x1 + 290, sy + 24, "BE (TiN)", size=12, bold=True))

    # Зонна діаграма ON
    by = sy + 70
    frags.append(line(x1 + 20, by + 120, x1 + 335, by + 120, color="#94a3b8", sw=1, dash="4 4"))
    frags.append(text(x1 + 310, by + 112, "E_F", size=11, color="#64748b"))

    # Потенціальний бар'єр φ_ON (нижча середня висота)
    path_on = f"M {x1+30} {by+120} L {x1+100} {by+120} L {x1+100} {by+45} L {x1+255} {by+75} L {x1+255} {by+120} L {x1+325} {by+120}"
    frags.append(f'<path d="{path_on}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    # Затінення бар'єра
    path_fill_on = f"M {x1+100} {by+120} L {x1+100} {by+45} L {x1+255} {by+75} L {x1+255} {by+120} Z"
    frags.append(f'<path d="{path_fill_on}" fill="#fde8e8" opacity="0.6"/>')

    # Тунельний струм J_ON (товста стрілка)
    frags.append(arrow(x1 + 50, by + 80, x1 + 285, by + 80, color=POS, sw=3.0))
    frags.append(text(x1 + 177, by + 70, "Високий струм J_ON", size=12, bold=True, color=POS))
    frags.append(text(x1 + 177, by + 145, "Низький опір R_ON", size=13, bold=True, color=INK))
    frags.append(text(x1 + 177, by + 165, "Середня висота φ_ON мала", size=11, color=MUTED))


    # Права панель — Стан OFF (Високий опір)
    x2 = 415
    frags.append(rect(x2, y1, pw, ph, fill="#ffffff", stroke="#cccccc", sw=1.5, rx=8))
    frags.append(text(x2 + pw / 2, y1 + 25, "Стан OFF (Логічний «0»)", size=15, bold=True, color=NEG))
    frags.append(text(x2 + pw / 2, y1 + 45, "Поляризація P ↑ (до TE)", size=12, color=MUTED, italic=True))

    # Схема шарів OFF
    frags.append(rect(x2 + 30, sy, 70, 40, fill="#e1e8ed", stroke="#4a5568", sw=1.5, rx=4))
    frags.append(text(x2 + 65, sy + 24, "TE (Pt)", size=12, bold=True))

    frags.append(rect(x2 + 100, sy, 155, 40, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
    frags.append(text(x2 + 177, sy + 18, "HZO (2 нм)", size=12, bold=True, color="#b45309"))
    frags.append(text(x2 + 177, sy + 33, "P ↑↑↑", size=13, bold=True, color=NEG))

    frags.append(rect(x2 + 255, sy, 70, 40, fill="#e1e8ed", stroke="#4a5568", sw=1.5, rx=4))
    frags.append(text(x2 + 290, sy + 24, "BE (TiN)", size=12, bold=True))

    # Зонна діаграма OFF
    frags.append(line(x2 + 20, by + 120, x2 + 335, by + 120, color="#94a3b8", sw=1, dash="4 4"))
    frags.append(text(x2 + 310, by + 112, "E_F", size=11, color="#64748b"))

    # Потенціальний бар'єр φ_OFF (висока середня висота)
    path_off = f"M {x2+30} {by+120} L {x2+100} {by+120} L {x2+100} {by+15} L {x2+255} {by+45} L {x2+255} {by+120} L {x2+325} {by+120}"
    frags.append(f'<path d="{path_off}" fill="none" stroke="{NEG}" stroke-width="2.5"/>')

    # Затінення бар'єра
    path_fill_off = f"M {x2+100} {by+120} L {x2+100} {by+15} L {x2+255} {by+45} L {x2+255} {by+120} Z"
    frags.append(f'<path d="{path_fill_off}" fill="#e8f0fe" opacity="0.6"/>')

    # Тунельний струм J_OFF (тонка стрілка)
    frags.append(arrow(x2 + 50, by + 80, x2 + 285, by + 80, color=NEG, sw=1.2))
    frags.append(text(x2 + 177, by + 70, "Низький струм J_OFF", size=12, bold=True, color=NEG))
    frags.append(text(x2 + 177, by + 145, "Високий опір R_OFF", size=13, bold=True, color=INK))
    frags.append(text(x2 + 177, by + 165, "Середня висота φ_OFF велика", size=11, color=MUTED))

    render(os.path.join(IMG_DIR, "ftj-structure-and-ter.svg"), w, h, *frags)


def make_fig2():
    """Фігура 2: Електростатичний профіль потенціалу на межах розділу FTJ."""
    w, h = 760, 380
    frags = []

    frags.append(text(w / 2, 25, "Анатомія асиметрії: Екранування Томаса — Фермі у гетероструктурі FTJ", size=15, bold=True))

    # Осі координат
    ox, oy = 80, 310
    frags.append(arrow(ox, oy, ox + 620, oy, color=LINE, sw=1.5))
    frags.append(text(ox + 630, oy + 4, "x (напрямок транспорту)", size=12, anchor="start"))

    frags.append(arrow(ox, oy, ox, oy - 260, color=LINE, sw=1.5))
    frags.append(text(ox, oy - 270, "Енергія U(x)", size=12))

    # Вертикальні границі шарів
    x_fe1 = ox + 160
    x_fe2 = ox + 440

    frags.append(line(x_fe1, oy - 250, x_fe1, oy + 20, color="#cbd5e1", sw=1.5, dash="5 5"))
    frags.append(line(x_fe2, oy - 250, x_fe2, oy + 20, color="#cbd5e1", sw=1.5, dash="5 5"))

    # Підписи областей
    frags.append(text(ox + 80, oy + 35, "Верхній електрод (TE)", size=12, bold=True))
    frags.append(text(ox + 80, oy + 50, "Робота виходу Φ1, λ1_TF", size=11, color=MUTED))

    frags.append(text(x_fe1 + 140, oy + 35, "Сегнетоелектрик (FE)", size=12, bold=True, color="#b45309"))
    frags.append(text(x_fe1 + 140, oy + 50, "Товщина d ~ 2 нм", size=11, color=MUTED))

    frags.append(text(x_fe2 + 100, oy + 35, "Нижній електрод (BE)", size=12, bold=True))
    frags.append(text(x_fe2 + 100, oy + 50, "Робота виходу Φ2, λ2_TF", size=11, color=MUTED))

    # Шар екранування в металах
    frags.append(rect(x_fe1 - 40, oy - 240, 40, 240, fill="#fee2e2", stroke="none"))
    frags.append(text(x_fe1 - 20, oy - 220, "λ1", size=12, bold=True, color=POS))
    frags.append(text(x_fe1 - 20, oy - 205, "-σ_P", size=11, color=POS))

    frags.append(rect(x_fe2, oy - 240, 25, 240, fill="#dbeafe", stroke="none"))
    frags.append(text(x_fe2 + 12, oy - 220, "λ2", size=12, bold=True, color=NEG))
    frags.append(text(x_fe2 + 12, oy - 205, "+σ_P", size=11, color=NEG))

    # Рівні Фермі E_F1 та E_F2
    frags.append(line(ox, oy - 70, x_fe1, oy - 70, color=LINE, sw=2))
    frags.append(text(ox + 40, oy - 80, "E_F1 (TE)", size=12, bold=True))

    frags.append(line(x_fe2, oy - 110, ox + 600, oy - 110, color=LINE, sw=2))
    frags.append(text(ox + 520, oy - 120, "E_F2 (BE)", size=12, bold=True))

    # Дно зони провідності E_c(x)
    # Потенціальні зсуви на межах через Thomas-Fermi screening: δV1 та δV2
    path_band = f"M {x_fe1-40} {oy-70} Q {x_fe1} {oy-70} {x_fe1} {oy-210} L {x_fe2} {oy-160} Q {x_fe2} {oy-110} {x_fe2+25} {oy-110}"
    frags.append(f'<path d="{path_band}" fill="none" stroke="{FIELD}" stroke-width="3"/>')

    frags.append(text(x_fe1 + 140, oy - 210, "Дно зони провідності U(x)", size=12, bold=True, color=FIELD))
    frags.append(arrow(x_fe1 + 40, oy - 70, x_fe1 + 40, oy - 200, color=POS, sw=1.5))
    frags.append(text(x_fe1 + 55, oy - 135, "φ1", size=12, bold=True, color=POS))

    frags.append(arrow(x_fe2 - 40, oy - 110, x_fe2 - 40, oy - 165, color=NEG, sw=1.5))
    frags.append(text(x_fe2 - 55, oy - 135, "φ2", size=12, bold=True, color=NEG))

    render(os.path.join(IMG_DIR, "asymmetric-barrier-electrostatics.svg"), w, h, *frags)


def make_fig3():
    """Фігура 3: Порівняння механізмів зчитування FeRAM та FTJ."""
    w, h = 800, 360
    frags = []

    frags.append(text(w / 2, 25, "Порівняння принципу зчитування: FeRAM проти FTJ", size=16, bold=True))

    # Лівий блок — FeRAM (Руйнівне читання)
    x1, y1, pw, ph = 30, 55, 355, 280
    frags.append(rect(x1, y1, pw, ph, fill="#fff5f5", stroke="#fca5a5", sw=1.5, rx=8))
    frags.append(text(x1 + pw / 2, y1 + 25, "FeRAM (Конденсаторна пам'ять)", size=15, bold=True, color="#991b1b"))
    frags.append(text(x1 + pw / 2, y1 + 48, "Товщина сегнетоелектрика d = 50–100 нм", size=11, color=MUTED))

    # Гістерезисна петля FeRAM
    cx1, cy1 = x1 + 177, y1 + 135
    frags.append(line(cx1 - 80, cy1, cx1 + 80, cy1, color="#94a3b8", sw=1))
    frags.append(line(cx1, cy1 - 55, cx1, cy1 + 55, color="#94a3b8", sw=1))
    frags.append(text(cx1 + 85, cy1 + 4, "Напруга V", size=10, color=MUTED))
    frags.append(text(cx1 + 5, cy1 - 60, "Заряд Q / P", size=10, color=MUTED))

    # Схематичний гістерезис
    p_hyst = f"M {cx1-50} {cy1+35} C {cx1-10} {cy1+35} {cx1+40} {cy1+20} {cx1+50} {cy1-35} C {cx1+10} {cy1-35} {cx1-40} {cy1-20} {cx1-50} {cy1+35}"
    frags.append(f'<path d="{p_hyst}" fill="none" stroke="#dc2626" stroke-width="2"/>')

    # Великий імпульс читання V_read > V_coercive
    frags.append(arrow(cx1, cy1, cx1 + 60, cy1, color=POS, sw=2))
    frags.append(text(cx1 + 30, cy1 - 12, "V_read > V_c", size=11, bold=True, color=POS))

    # Висновок FeRAM
    frags.append(textbox(x1 + pw / 2, y1 + 235, "РУЙНІВНЕ ЗЧИТАННЯ (Destructive Read)\nПереполяризація генерує струм зсуву.\nВимагає обов'язкового перезапису!", size=11, color="#7f1d1d", fill="#fee2e2", stroke="#f87171")[0])


    # Правий блок — FTJ (Неруйнівне читання)
    x2 = 415
    frags.append(rect(x2, y1, pw, ph, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(x2 + pw / 2, y1 + 25, "FTJ (Тунельний перехід)", size=15, bold=True, color="#166534"))
    frags.append(text(x2 + pw / 2, y1 + 48, "Товщина бар'єра d = 1–2 нм", size=11, color=MUTED))

    # ВАХ характеристика FTJ (тунелювання)
    cx2, cy2 = x2 + 177, y1 + 135
    frags.append(line(cx2 - 80, cy2, cx2 + 80, cy2, color="#94a3b8", sw=1))
    frags.append(line(cx2, cy2 - 55, cx2, cy2 + 55, color="#94a3b8", sw=1))
    frags.append(text(cx2 + 85, cy2 + 4, "Напруга V", size=10, color=MUTED))
    frags.append(text(cx2 + 5, cy2 - 60, "Струм J_tunnel", size=10, color=MUTED))

    # Дві ВАХ криві (ON - стрімка, OFF - полога)
    p_iv_on = f"M {cx2-60} {cy2+45} Q {cx2} {cy2} {cx2+60} {cy2-45}"
    p_iv_off = f"M {cx2-60} {cy2+15} Q {cx2} {cy2} {cx2+60} {cy2-15}"
    frags.append(f'<path d="{p_iv_on}" fill="none" stroke="{POS}" stroke-width="2.5"/>')
    frags.append(f'<path d="{p_iv_off}" fill="none" stroke="{NEG}" stroke-width="2.5"/>')

    # Малий імпульс читання V_read << V_coercive
    frags.append(line(cx2 + 25, cy2 - 50, cx2 + 25, cy2 + 40, color="#15803d", sw=1.5, dash="3 3"))
    frags.append(text(cx2 + 25, cy2 + 48, "V_read << V_c", size=11, bold=True, color="#15803d"))

    # Висновок FTJ
    frags.append(textbox(x2 + pw / 2, y1 + 235, "НЕРУЙНІВНЕ ЗЧИТАННЯ (Non-Destructive)\nВимірювання опіру R_ON / R_OFF тунельним струмом.\nПоляризація P залишається недоторканою!", size=11, color="#14532d", fill="#dcfce7", stroke="#4ade80")[0])

    render(os.path.join(IMG_DIR, "ftj-vs-feram-readout.svg"), w, h, *frags)


if __name__ == "__main__":
    make_fig1()
    make_fig2()
    make_fig3()
    print("Усі фігури успішно згенеровано у", IMG_DIR)
