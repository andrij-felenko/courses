# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_kinodynamic_stitching():
    W, H = 880, 460
    p = []

    # Заголовок панелей
    tb_l, _, _ = textbox(225, 30, "Фізичний простір та траєкторія склеювання", size=13, bold=True, fill="#f8fafc", stroke=LINE)
    p.append(tb_l)
    tb_r, _, _ = textbox(665, 30, "Профілі неперервності C²: p(t), v(t), a(t)", size=13, bold=True, fill="#f8fafc", stroke=LINE)
    p.append(tb_r)

    # Розділювач
    p.append(line(450, 15, 450, 445, color="#e2e8f0", sw=1.5, dash="4,4"))

    # --- Ліва панель: Просторовий маневр ---
    p.append(rect(25, 60, 400, 375, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))

    # Перешкода
    p.append(rect(230, 130, 85, 90, fill="#fee2e2", stroke=POS, sw=1.8, rx=4))
    p.append(text(272, 170, "Нова", size=11, color=POS, bold=True))
    p.append(text(272, 186, "перешкода", size=11, color=POS, bold=True))

    # Стара траєкторія (пунктир через перешкоду)
    p.append(line(50, 290, 140, 240, color=MUTED, sw=2.0))
    p.append(line(140, 240, 210, 200, color=MUTED, sw=2.0))
    p.append(line(210, 200, 310, 150, color=POS, sw=2.0, dash="4,4"))
    p.append(line(310, 150, 390, 110, color=MUTED, sw=2.0, dash="4,4"))
    p.append(text(345, 120, "Старий шлях (колізія)", size=10, color=POS, italic=True))

    # Точка t_now (виявлення перешкоди)
    p.append(circle(140, 240, 5, fill=NEG, stroke="#ffffff", sw=1.5))
    p.append(text(125, 268, "t_now (виявлення)", size=10, color=NEG, bold=True))

    # Час обчислення t_plan (сегмент польоту під час рахунку)
    p.append(circle(210, 200, 5, fill=FIELD, stroke="#ffffff", sw=1.5))
    p.append(text(175, 175, "t_stitch = t_now + t_plan", size=10, color=FIELD, bold=True))
    p.append(text(175, 189, "[p, v, a] склеювання", size=9, color=FIELD))

    # Вектор швидкості v(t_stitch)
    p.append(arrow(210, 200, 255, 175, color=FIELD, sw=2.0))
    p.append(text(275, 172, "v_stitch", size=10, color=FIELD, bold=True))

    # Нова перепланована траєкторія ухилення
    p.append('<path d="M 210 200 C 250 250, 310 270, 360 250 S 390 180, 405 130" fill="none" stroke="%s" stroke-width="2.8"/>' % FIELD)
    p.append(text(330, 285, "Нова траєкторія (C²)", size=11, color=FIELD, bold=True))

    # Пояснення внизу лівої панелі
    fb_l = fitbox(35, 335, 380, 90, "Фатальна помилка наївного алгоритму:\n1. Планування від точки t_now ігнорує зсув за час рахунку t_plan.\n2. Спроба рушити з v=0 дає стрибок прискорення Δa та зрив кутів.\n3. Склеювання вимагає старту з S(t_now + t_plan) по старій траєкторії.", size=10, fill="#f8fafc", stroke="#e2e8f0")
    p.append(fb_l)

    # --- Права панель: Графіки p(t), v(t), a(t) ---
    p.append(rect(475, 60, 380, 375, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))

    # Графік 1: Позиція p(t)
    p.append(rect(490, 75, 350, 70, fill="#f8fafc", stroke="#e2e8f0", rx=4))
    p.append(line(540, 130, 820, 130, color="#94a3b8", sw=1.0))
    p.append(line(540, 85, 540, 135, color="#94a3b8", sw=1.0))
    p.append(text(515, 110, "p(t)", size=11, color=INK, bold=True))
    p.append(line(650, 80, 650, 140, color="#cbd5e1", sw=1.0, dash="3,3"))
    p.append('<path d="M 540 125 Q 600 115, 650 105 T 760 90 T 820 85" fill="none" stroke="%s" stroke-width="2.2"/>' % FIELD)
    p.append(text(650, 78, "t_stitch", size=9, color=MUTED))
    p.append(text(780, 102, "C⁰ неперервність", size=9, color=FIELD))

    # Графік 2: Швидкість v(t)
    p.append(rect(490, 155, 350, 70, fill="#f8fafc", stroke="#e2e8f0", rx=4))
    p.append(line(540, 210, 820, 210, color="#94a3b8", sw=1.0))
    p.append(line(540, 165, 540, 215, color="#94a3b8", sw=1.0))
    p.append(text(515, 190, "v(t)", size=11, color=INK, bold=True))
    p.append(line(650, 160, 650, 220, color="#cbd5e1", sw=1.0, dash="3,3"))
    p.append('<path d="M 540 195 C 590 195, 620 185, 650 185 C 680 185, 720 175, 820 175" fill="none" stroke="%s" stroke-width="2.2"/>' % NEG)
    p.append(text(780, 195, "C¹ неперервність", size=9, color=NEG))

    # Графік 3: Прискорення a(t)
    p.append(rect(490, 235, 350, 85, fill="#f8fafc", stroke="#e2e8f0", rx=4))
    p.append(line(540, 280, 820, 280, color="#94a3b8", sw=1.0))
    p.append(line(540, 245, 540, 310, color="#94a3b8", sw=1.0))
    p.append(text(515, 275, "a(t)", size=11, color=INK, bold=True))
    p.append(line(650, 240, 650, 315, color="#cbd5e1", sw=1.0, dash="3,3"))
    p.append('<path d="M 540 280 Q 600 275, 650 265 Q 700 250, 750 280 T 820 280" fill="none" stroke="%s" stroke-width="2.2"/>' % POS)
    p.append(line(650, 265, 650, 305, color=MUTED, sw=1.5, dash="2,2"))
    p.append(line(650, 305, 720, 290, color=MUTED, sw=1.5, dash="2,2"))
    p.append(text(750, 305, "Без C²: стрибок тяги", size=9, color=MUTED, italic=True))
    p.append(text(760, 255, "C²: плавна тяга", size=9, color=POS, bold=True))

    # Текстова плашка внизу правої панелі
    fb_r = fitbox(490, 335, 350, 90, "Кінодинамічна сумісність (Kinodynamic Feasibility):\n• C⁰: позиція не має просторових телепортацій.\n• C¹: швидкість збігається за напрямком і величиною.\n• C²: вектор прискорення неперервний (немає миттєвих змін кута крену/тангажу й тяги моторів).", size=10, fill="#f8fafc", stroke="#e2e8f0")
    p.append(fb_r)

    render(os.path.join(OUT, "kinodynamic-stitching.svg"), W, H, *p)


def fig_replanning_pipeline():
    W, H = 880, 420
    p = []

    # Головний заголовок
    tb_title, _, _ = textbox(440, 28, "Архітектура трирівневого динамічного перепланування на борту БПЛА", size=13, bold=True, fill="#f8fafc", stroke=LINE)
    p.append(tb_title)

    # 4 етапи конвеєра: Сенсори -> Фронтенд -> Бекенд -> Контролер
    col_w = 190
    col_h = 320
    y_top = 65

    # Етап 1: Сенсорне оновлення карти
    p.append(rect(25, y_top, col_w, col_h, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(rect(35, y_top + 10, col_w - 20, 32, fill="#f1f5f9", stroke="#94a3b8", sw=1.0, rx=4))
    p.append(text(120, y_top + 31, "1. Сенсорика та карта", size=11, color=INK, bold=True))
    
    fb1 = fitbox(35, y_top + 55, col_w - 20, 245, "Джерела даних:\n• Стереокамера / Лідар\n• IMU + Одометрія (VIO/GNSS)\n\nЛокальна карта:\n• Voxel Grid (OctoMap)\n• Dynamic ESDF (3D поле знакових відстаней)\n• Ring-Buffer оновлення\n\nЧастота: 20–50 Гц\nЗатримка: < 15 мс", size=10, fill="#f8fafc", stroke="#e2e8f0")
    p.append(fb1)

    # Стрілка 1 -> 2
    p.append(arrow(215, y_top + 160, 243, y_top + 160, color=LINE, sw=2.0))

    # Етап 2: Фронтенд (Топологічний пошук)
    p.append(rect(245, y_top, col_w, col_h, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(rect(255, y_top + 10, col_w - 20, 32, fill="#e0f2fe", stroke="#0284c7", sw=1.0, rx=4))
    p.append(text(340, y_top + 31, "2. Дискретний пошук", size=11, color="#0369a1", bold=True))

    fb2 = fitbox(255, y_top + 55, col_w - 20, 245, "Алгоритми пошуку:\n• D* Lite (інкрементний граф)\n• Kinodynamic A*\n• Jump Point Search (JPS)\n\nРезультат:\n• Безпечний коридор (SFC)\n• Опорні шляхові точки\n• Ініціалізація для бекенду\n\nЧас пошуку: 1–5 мс", size=10, fill="#f8fafc", stroke="#e2e8f0")
    p.append(fb2)

    # Стрілка 2 -> 3
    p.append(arrow(435, y_top + 160, 463, y_top + 160, color=LINE, sw=2.0))

    # Етап 3: Бекенд (Неперервна оптимізація)
    p.append(rect(465, y_top, col_w, col_h, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(rect(475, y_top + 10, col_w - 20, 32, fill="#fef3c7", stroke="#d97706", sw=1.0, rx=4))
    p.append(text(560, y_top + 31, "3. Оптимізація траєкторії", size=11, color="#b45309", bold=True))

    fb3 = fitbox(475, y_top + 55, col_w - 20, 245, "Математичний апарат:\n• Градієнтна деформація B-сплайнів у полі ESDF\n• Minimum Snap / Jerk QP\n• Часова репараметризація\n\nОбмеження:\n• v_max, a_max, j_max\n• C²-склеювання в t_stitch\n\nЧас розрахунку: 2–8 мс", size=10, fill="#f8fafc", stroke="#e2e8f0")
    p.append(fb3)

    # Стрілка 3 -> 4
    p.append(arrow(655, y_top + 160, 683, y_top + 160, color=LINE, sw=2.0))

    # Етап 4: Виконавчий трекінг (Автопілот)
    p.append(rect(685, y_top, col_w, col_h, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(rect(695, y_top + 10, col_w - 20, 32, fill="#dcfce7", stroke="#16a34a", sw=1.0, rx=4))
    p.append(text(780, y_top + 31, "4. Трекінг та уставки", size=11, color="#15803d", bold=True))

    fb4 = fitbox(695, y_top + 55, col_w - 20, 245, "Вихідний потік:\n• Уставки p_ref, v_ref, a_ref\n• Курс yaw, yaw_rate\n\nВиконавчий контур:\n• Geometric Attitude Tracking (SO3)\n• Motor Mixer / Allocation\n\nЧастота: 250–500 Гц\nПрямий зв'язок (Feedforward)", size=10, fill="#f8fafc", stroke="#e2e8f0")
    p.append(fb4)

    # Загальний нижній рядок зворотного зв'язку
    p.append(line(780, y_top + col_h + 10, 120, y_top + col_h + 10, color=MUTED, sw=1.2, dash="3,3"))
    p.append(arrow(120, y_top + col_h + 10, 120, y_top + col_h + 2, color=MUTED, sw=1.2))
    p.append(text(450, y_top + col_h + 22, "Замкнений контур: реальний стан БПЛА постійно передається у генератор уставок та планувальник", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "replanning-algorithms-pipeline.svg"), W, H, *p)


if __name__ == "__main__":
    fig_kinodynamic_stitching()
    fig_replanning_pipeline()
    print("Figures generated successfully.")
