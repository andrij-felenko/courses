# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми teplovizor:
1. fig-microbolometer-pixel.svg — Будова пікселя неохолоджуваного мікроболометра
2. fig-fpa-roic-readout.svg — Архітектура FPA та колоночний тракт зчитування ROIC
3. fig-nuc-shutter-principle.svg — Неоднорідність пікселів та калібрування NUC
4. fig-thermal-pipeline.svg — Повний конвеєр цифрової обробки тепловізійного кадру
"""

import sys
import os

# Підключення svgkit із кореня scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def draw_microbolometer_pixel():
    w, h = 880, 520
    frags = []

    # Загальна рамка
    frags.append(rect(10, 10, 860, 500, fill="#ffffff", stroke="#d0d5dd", sw=1.5, rx=8))

    # Секція 1: Кремнієва підкладка з інтегральною схемою ROIC
    frags.append(rect(40, 410, 800, 80, fill="#e5e7eb", stroke="#4b5563", sw=2, rx=4))
    b, _, _ = textbox(440, 450, "Кремнієва підкладка (CMOS ROIC): комутатори рядків, колоночні інтегратори CTIA, АЦП", size=13, pad=8, fill="#ffffff", stroke="#9ca3af", bold=True)
    frags.append(b)

    # Дзеркальний відбивач на підкладці
    frags.append(rect(180, 396, 520, 14, fill="#fbbf24", stroke="#d97706", sw=1.5, rx=2))
    frags.append(text(440, 406, "Нижнє дзеркало (Ti / Al) для створення чвертьхвильового оптичного резонатора", size=11, color="#78350f", bold=True))

    # Оптична порожнина (вакуумний зазор d = λ/4 ≈ 2.5 мкм)
    frags.append(line(140, 240, 140, 396, color="#0284c7", sw=1.5, dash="4,4"))
    frags.append(line(740, 240, 740, 396, color="#0284c7", sw=1.5, dash="4,4"))
    frags.append(line(150, 320, 170, 320, color="#0284c7", sw=1.5))
    frags.append(line(710, 320, 730, 320, color="#0284c7", sw=1.5))
    b, _, _ = textbox(440, 320, "Вакуумний резонансний проміжок d = λ / 4 ≈ 2.5 мкм (інтерференція на довжині хвилі 10 мкм)", size=12, pad=6, fill="#f0f9ff", stroke="#0284c7")
    frags.append(b)

    # Опорні мікроніжки (Suspension legs)
    # Ліва ніжка
    frags.append(rect(100, 360, 60, 50, fill="#94a3b8", stroke="#475569", sw=1.5, rx=2))
    frags.append(text(130, 390, "Контакт", size=11, color="#1e293b", bold=True))
    frags.append(line(130, 360, 130, 240, color="#ea580c", sw=4))
    frags.append(line(130, 240, 200, 240, color="#ea580c", sw=4))

    # Права ніжка
    frags.append(rect(720, 360, 60, 50, fill="#94a3b8", stroke="#475569", sw=1.5, rx=2))
    frags.append(text(750, 390, "Контакт", size=11, color="#1e293b", bold=True))
    frags.append(line(750, 360, 750, 240, color="#ea580c", sw=4))
    frags.append(line(750, 240, 680, 240, color="#ea580c", sw=4))

    # Підвішена мембрана (Microbridge absorber + VOx thermistor)
    frags.append(rect(200, 200, 480, 80, fill="#fee2e2", stroke="#b91c1c", sw=2, rx=6))
    
    # Шари мембрани
    frags.append(rect(210, 210, 460, 20, fill="#fca5a5", stroke="#dc2626", sw=1, rx=2))
    frags.append(text(440, 224, "Поглинач ІЧ-випромінювання (тонкий металевий шар NiCr, узгоджений хвильовий опір 377 Ом/кв)", size=11, color="#7f1d1d", bold=True))
    
    frags.append(rect(210, 235, 460, 22, fill="#fef08a", stroke="#ca8a04", sw=1, rx=2))
    frags.append(text(440, 250, "Термочутливий шар: оксид ванадію (VOx) або a-Si з високим TCR (α ≈ -2% ... -3% / K)", size=11, color="#713f12", bold=True))

    frags.append(rect(210, 260, 460, 15, fill="#cbd5e1", stroke="#64748b", sw=1, rx=2))
    frags.append(text(440, 271, "Опорна несуча мембрана з нітриду кремнію (Si3N4)", size=10, color="#334155"))

    # Падаюче ІЧ-випромінювання
    for x in (280, 380, 500, 600):
        frags.append(arrow(x, 70, x, 195, color="#dc2626", sw=2.5))
    b, _, _ = textbox(440, 50, "Падаючий потік довгохвильового ІЧ-випромінювання (LWIR 8–14 мкм, поглинання P_rad)", size=13, pad=8, fill="#fef2f2", stroke="#ef4444", color="#991b1b", bold=True)
    frags.append(b)

    # Виноски параметрів мікроніжок
    b1, _, _ = textbox(110, 140, "Довгі тонкі мікроніжки:\n• Високий R_th ≈ 10^7 К/Вт\n• Малий стік тепла G_th\n• Електричний контакт", size=11, pad=6, fill="#fff7ed", stroke="#f97316")
    frags.append(b1)
    frags.append(arrow(110, 185, 130, 235, color="#ea580c", sw=1.5))

    b2, _, _ = textbox(770, 140, "Тепловий баланс:\n• Ємність C_th ≈ 10^-9 Дж/К\n• Час реакції τ = C/G ≈ 10 мс\n• Вакуум < 10^-2 мбар", size=11, pad=6, fill="#f0fdf4", stroke="#16a34a")
    frags.append(b2)
    frags.append(arrow(770, 185, 750, 235, color="#16a34a", sw=1.5))

    return render(os.path.join(IMG_DIR, "fig-microbolometer-pixel.svg"), w, h, *frags)


def draw_fpa_roic_readout():
    w, h = 900, 480
    frags = []

    frags.append(rect(10, 10, 880, 460, fill="#ffffff", stroke="#d0d5dd", sw=1.5, rx=8))

    # Блок піксельної матриці FPA (ліворуч)
    frags.append(rect(30, 40, 360, 400, fill="#f8fafc", stroke="#64748b", sw=1.8, rx=6))
    frags.append(text(210, 65, "Матриця у фокальній площині (FPA)", size=14, color="#0f172a", bold=True))

    # Активний піксель
    frags.append(rect(50, 90, 320, 150, fill="#fee2e2", stroke="#ef4444", sw=1.5, rx=4))
    frags.append(text(210, 115, "Активний піксель (R_pix, підвішений VOx)", size=12, color="#991b1b", bold=True))
    frags.append(text(210, 135, "Отримує P_rad від сцени, нагрівається на ΔT", size=11, color="#7f1d1d"))
    frags.append(rect(130, 155, 160, 35, fill="#ffffff", stroke="#b91c1c", sw=1.2, rx=3))
    frags.append(text(210, 177, "R_pix(T) = R0 · [1 + α·ΔT]", size=11, color="#991b1b", bold=True))
    frags.append(text(210, 220, "Ключ рядкового вибору (Row Switch, t_int ≈ 50 мкс)", size=10, color="#6b7280"))

    # Сліпий еталонний піксель (Blind Reference Bolometer)
    frags.append(rect(50, 260, 320, 160, fill="#e0e7ff", stroke="#6366f1", sw=1.5, rx=4))
    frags.append(text(210, 285, "Сліпий еталонний піксель (Blind Bolometer)", size=12, color="#3730a3", bold=True))
    frags.append(text(210, 305, "Екранований від ІЧ-випромінювання Al-шаром", size=11, color="#312e81"))
    frags.append(text(210, 325, "Термозв'язаний з кремнієвою підкладкою (T_sub)", size=11, color="#312e81"))
    frags.append(rect(130, 345, 160, 35, fill="#ffffff", stroke="#4338ca", sw=1.2, rx=3))
    frags.append(text(210, 367, "R_blind(T_sub) ≈ R0(T_sub)", size=11, color="#3730a3", bold=True))
    frags.append(text(210, 400, "Компенсує підкладковий дрейф і самонагрів", size=10, color="#4338ca"))

    # Стрілки передачі струмів до інтегратора
    frags.append(arrow(370, 165, 450, 165, color="#dc2626", sw=2))
    frags.append(text(410, 155, "I_act", size=12, color="#dc2626", bold=True))

    frags.append(arrow(370, 340, 450, 235, color="#4338ca", sw=2))
    frags.append(text(410, 290, "I_blind", size=12, color="#4338ca", bold=True))

    # Блок колоночного зчитування ROIC (праворуч)
    frags.append(rect(450, 40, 420, 400, fill="#f0fdf4", stroke="#16a34a", sw=1.8, rx=6))
    frags.append(text(660, 65, "Колоночний тракт зчитування (ROIC Column Unit)", size=14, color="#14532d", bold=True))

    # Інтегратор струму CTIA
    frags.append(rect(470, 90, 380, 170, fill="#ffffff", stroke="#22c55e", sw=1.5, rx=4))
    frags.append(text(660, 115, "Диференційний інтегратор заряду CTIA", size=13, color="#15803d", bold=True))
    frags.append(text(660, 135, "Віднімає базовий струм підкладки: ΔI = I_act − I_blind", size=11, color="#166534"))
    
    # Схема зворотного зв'язку CTIA
    frags.append(rect(540, 155, 240, 45, fill="#dcfce7", stroke="#16a34a", sw=1.2, rx=4))
    frags.append(text(660, 175, "Інтегруючий конденсатор C_int", size=11, color="#14532d", bold=True))
    frags.append(text(660, 192, "V_out = (1 / C_int) · ∫ ΔI(t) dt", size=11, color="#15803d"))
    
    frags.append(text(660, 235, "Імпульсне зміщення V_bias синхронно з ключем скидання RST", size=10, color="#4b5563"))

    # Блок вибірки-зберігання (S&H) та АЦП
    frags.append(arrow(660, 260, 660, 290, color="#16a34a", sw=2))
    
    frags.append(rect(470, 290, 380, 60, fill="#ffffff", stroke="#0284c7", sw=1.5, rx=4))
    frags.append(text(660, 315, "Корельована подвійна вибірка (CDS) та S&H", size=12, color="#0369a1", bold=True))
    frags.append(text(660, 335, "Усуває шум скидання інтегратора kTC та 1/f зміщення", size=10, color="#0284c7"))

    frags.append(arrow(660, 350, 660, 375, color="#0284c7", sw=2))

    frags.append(rect(470, 375, 380, 50, fill="#0284c7", stroke="#0369a1", sw=1.5, rx=4))
    frags.append(text(660, 405, "14-бітний / 16-бітний колоночний АЦП (Raw DN)", size=13, color="#ffffff", bold=True))

    return render(os.path.join(IMG_DIR, "fig-fpa-roic-readout.svg"), w, h, *frags)


def draw_nuc_shutter_principle():
    w, h = 900, 500
    frags = []

    frags.append(rect(10, 10, 880, 480, fill="#ffffff", stroke="#d0d5dd", sw=1.5, rx=8))

    # Секція 1: Проблема Non-Uniformity (Зліва)
    frags.append(rect(30, 40, 260, 420, fill="#fff1f2", stroke="#e11d48", sw=1.5, rx=6))
    frags.append(text(160, 65, "1. Неоднорідність (NU)", size=13, color="#9f1239", bold=True))
    frags.append(text(160, 85, "Сирий відгук пікселів матриці", size=11, color="#be123c"))

    # Графік відгуку пікселів (розкид зсувів і нахилів)
    frags.append(rect(50, 105, 220, 200, fill="#ffffff", stroke="#fda4af", sw=1.2, rx=4))
    frags.append(line(70, 280, 250, 280, color="#475569", sw=1.5)) # вісь X
    frags.append(line(70, 280, 70, 120, color="#475569", sw=1.5))  # вісь Y
    frags.append(text(230, 295, "T_сцени", size=10, color="#475569"))
    frags.append(text(60, 125, "DN", size=10, color="#475569"))

    # Різні лінії відгуку
    frags.append(line(70, 250, 240, 140, color="#dc2626", sw=2)) # піксель A
    frags.append(line(70, 220, 240, 160, color="#2563eb", sw=2)) # піксель B
    frags.append(line(70, 190, 240, 130, color="#16a34a", sw=2)) # піксель C

    frags.append(text(160, 325, "• Розкид R0: ±5%...10%", size=11, color="#881337"))
    frags.append(text(160, 345, "• Розкид чутливості (TCR): ±3%", size=11, color="#881337"))
    frags.append(text(160, 365, "• Розкид теплопровідності G_th", size=11, color="#881337"))
    frags.append(text(160, 395, "FPN (просторово-фіксований", size=11, color="#9f1239", bold=True))
    frags.append(text(160, 412, "шум) перекриває корисний", size=11, color="#9f1239", bold=True))
    frags.append(text(160, 429, "тепловий сигнал у 50+ разів!", size=11, color="#9f1239", bold=True))

    frags.append(arrow(290, 250, 320, 250, color="#e11d48", sw=2))

    # Секція 2: Механічна шторка і 1-точкова NUC (По центру)
    frags.append(rect(320, 40, 260, 420, fill="#f0f9ff", stroke="#0284c7", sw=1.5, rx=6))
    frags.append(text(450, 65, "2. Калібрування шторкою", size=13, color="#075985", bold=True))
    frags.append(text(450, 85, "Одноточкова корекція зміщення", size=11, color="#0369a1"))

    # Малюнок шторки
    frags.append(rect(350, 110, 200, 100, fill="#ffffff", stroke="#38bdf8", sw=1.2, rx=4))
    frags.append(rect(370, 130, 160, 60, fill="#334155", stroke="#0f172a", sw=1.5, rx=3))
    frags.append(text(450, 155, "Механічна заслінка", size=11, color="#ffffff", bold=True))
    frags.append(text(450, 172, "Ізотермічне тіло T_shutter", size=10, color="#94a3b8"))

    frags.append(rect(340, 225, 220, 110, fill="#ffffff", stroke="#0284c7", sw=1.2, rx=4))
    frags.append(text(450, 245, "Зняття кадру зміщення:", size=11, color="#0c4a6e", bold=True))
    frags.append(text(450, 268, "Offset[i] = Y_shutter[i]", size=11, color="#0369a1", bold=True))
    frags.append(text(450, 292, "Корекція в реальному часі:", size=11, color="#0c4a6e", bold=True))
    frags.append(text(450, 315, "Y_corr[i] = Y[i] − Offset[i] + S0", size=11, color="#0284c7", bold=True))

    frags.append(text(450, 360, "• Шторка перекриває FPA", size=11, color="#0369a1"))
    frags.append(text(450, 380, "  на 100–300 мс кожні 2–5 хв", size=11, color="#0369a1"))
    frags.append(text(450, 400, "• Компенсує тепловий", size=11, color="#0369a1"))
    frags.append(text(450, 417, "  дрейф корпусу сенсора", size=11, color="#0369a1"))

    frags.append(arrow(580, 250, 610, 250, color="#0284c7", sw=2))

    # Секція 3: Двоточкове калібрування Flat-Field (Справа)
    frags.append(rect(610, 40, 260, 420, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=6))
    frags.append(text(740, 65, "3. Двоточкова FFC", size=13, color="#14532d", bold=True))
    frags.append(text(740, 85, "Корекція підсилення й зсуву", size=11, color="#15803d"))

    # Графік після 2-точкової корекції (ідеально узгоджені лінії)
    frags.append(rect(630, 105, 220, 200, fill="#ffffff", stroke="#86efac", sw=1.2, rx=4))
    frags.append(line(650, 280, 830, 280, color="#475569", sw=1.5)) # вісь X
    frags.append(line(650, 280, 650, 120, color="#475569", sw=1.5)) # вісь Y
    frags.append(text(810, 295, "T_сцени", size=10, color="#475569"))
    frags.append(text(640, 125, "DN", size=10, color="#475569"))

    # Точки T1 (холодна) і T2 (гаряча)
    frags.append(line(690, 280, 690, 120, color="#94a3b8", sw=1, dash="3,3"))
    frags.append(text(690, 295, "T_cold", size=9, color="#0284c7", bold=True))

    frags.append(line(780, 280, 780, 120, color="#94a3b8", sw=1, dash="3,3"))
    frags.append(text(780, 295, "T_hot", size=9, color="#dc2626", bold=True))

    # Єдина калібрована пряма
    frags.append(line(650, 260, 820, 135, color="#16a34a", sw=3))
    frags.append(circle(690, 230, 4, fill="#0284c7", stroke="#0369a1", sw=1.5))
    frags.append(circle(780, 165, 4, fill="#dc2626", stroke="#b91c1c", sw=1.5))

    frags.append(rect(625, 320, 230, 70, fill="#ffffff", stroke="#16a34a", sw=1.2, rx=4))
    frags.append(text(740, 340, "Gain[i] = ΔDN_target / (Y_h[i] − Y_c[i])", size=9, color="#14532d", bold=True))
    frags.append(text(740, 365, "Y_out[i] = Gain[i] · (Y[i] − Y_c[i]) + C0", size=9, color="#15803d", bold=True))

    frags.append(text(740, 410, "Результат: однорідне поле,", size=11, color="#14532d", bold=True))
    frags.append(text(740, 427, "NETD < 40 мК, чиста термограма", size=11, color="#16a34a", bold=True))

    return render(os.path.join(IMG_DIR, "fig-nuc-shutter-principle.svg"), w, h, *frags)


def draw_thermal_pipeline():
    w, h = 920, 380
    frags = []

    frags.append(rect(10, 10, 900, 360, fill="#ffffff", stroke="#d0d5dd", sw=1.5, rx=8))
    frags.append(text(460, 35, "Конвеєр цифрової обробки тепловізійного кадру (Thermal Vision ISP)", size=16, color="#0f172a", bold=True))

    stages = [
        ("1. Сирий кадр FPA", "14-бітний потік\nМасив 16384 рівнів\nСильний шум FPN", "#fee2e2", "#ef4444", "#991b1b"),
        ("2. NUC + Шторка", "Flat-Field Correction\nGain[i] · (Raw[i] − Off[i])\nВидалення смуг і зсуву", "#fef3c7", "#f59e0b", "#92400e"),
        ("3. Заміна дефектів", "Bad Pixel Replacement\nВиявлення «мертвих»\nМедіана 3×3 сусідів", "#e0e7ff", "#6366f1", "#3730a3"),
        ("4. Фільтрація шуму", "Temporal IIR + Spatial\nДвосторонній фільтр\nЗниження шуму до NETD", "#f0fdf4", "#22c55e", "#15803d"),
        ("5. Стиснення AGC", "Plateau Equalization / DDE\nДинамічний діапазон\n14 біт → 8 біт (0–255)", "#f0f9ff", "#0284c7", "#075985"),
        ("6. Ironbow Палітра", "Псевдокольорова LUT\nЧорний → Червоний →\nЖовтий → Білий (RGB888)", "#fdf4ff", "#d946ef", "#86198f"),
    ]

    box_w = 130
    box_h = 190
    spacing = 16
    start_x = 30
    y = 65

    for i, (title, desc, fill_c, stroke_c, text_c) in enumerate(stages):
        x = start_x + i * (box_w + spacing)
        frags.append(rect(x, y, box_w, box_h, fill=fill_c, stroke=stroke_c, sw=1.6, rx=6))
        frags.append(fitbox(x + 5, y + 10, box_w - 10, 35, title, size=11, pad=2, fill="#ffffff", stroke=stroke_c, color=text_c, bold=True))
        
        # Опис блоку
        lines = desc.split("\n")
        for j, line_txt in enumerate(lines):
            frags.append(text(x + box_w / 2, y + 70 + j * 24, line_txt, size=10, color=text_c))

        # Стрілка переходу
        if i < len(stages) - 1:
            arrow_x1 = x + box_w
            arrow_x2 = arrow_x1 + spacing
            frags.append(arrow(arrow_x1, y + box_h / 2, arrow_x2, y + box_h / 2, color="#64748b", sw=2))

    # Нижня панель виводу результату
    frags.append(rect(30, 275, 860, 75, fill="#0f172a", stroke="#334155", sw=1.5, rx=6))
    frags.append(text(460, 305, "Фінальний вихід: термограма 24-біт RGB (30–60 к/с) з роздільною здатністю температури до 0.04 °C", size=13, color="#f8fafc", bold=True))
    frags.append(text(460, 330, "Готовий потік для виведення на екран, тепловізійного машинного бачення та радіометричного вимірювання", size=11, color="#94a3b8"))

    return render(os.path.join(IMG_DIR, "fig-thermal-pipeline.svg"), w, h, *frags)


if __name__ == "__main__":
    print("Генерація SVG фігур для teplovizor...")
    draw_microbolometer_pixel()
    draw_fpa_roic_readout()
    draw_nuc_shutter_principle()
    draw_thermal_pipeline()
    print("Готово!")
