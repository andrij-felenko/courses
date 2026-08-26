# -*- coding: utf-8 -*-
"""Фігури до теми «Підробні й перемарковані компоненти»
П'ять інженерних фігур:
  counterfeit-categories.svg    — чотири базові механізми контрафакту напівпровідників
  optical-inspection-defects.svg— дефекти поверхні та маркування при blacktopping під мікроскопом
  vi-curve-tracing.svg          — сигнатурний аналіз V-I (Pin-to-Ground) та форми кривих
  xray-die-bond-comparison.svg  — рентгенографічна інспекція: еталон проти контрафакту
  inbound-inspection-funnel.svg — багаторівнева вирва вхідного контролю якості (IQC)
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_counterfeit_categories():
    """Чотири базові типи контрафакту: перемаркування, відбраковка, порожній макет, клон."""
    W, H = 780, 420
    p = []
    
    # 4 колонки для кожного типу
    cols = [
        ("Чорне перемаркування", "(Blacktopping)", 
         "Зішліфовування маркування,\nнанесення шару епоксидного лаку\nі підробного лазерного напису.\nДешевий чип видають за дорогий.",
         POS, "#fdf2f2"),
        ("Кремнієва відбраковка", "(B-Grade / Scrap)",
         "Кристали, що провалили тести\nна заводі (витоки, шуми, збій PLL),\nвикрадені з утилізації та\nзапаковані в корпуси без тесту.",
         "#d97706", "#fffbeb"),
        ("Порожні макети", "(Dummy Packages)",
         "Пластиковий корпус з рамкою,\nале всередині немає кристала\nабо з'єднувальних провідників.\nІмітація ваги без функції.",
         MUTED, "#f3f4f6"),
        ("Урізані клони", "(Degraded Clones)",
         "Стороння топологія зі спрощеною\nсхемотехнікою: тонший метал,\nгірший ESD-захист, термодрейф\nта невідповідність даташиту.",
         NEG, "#eff6ff")
    ]
    
    cw = 175
    gap = 15
    start_x = 20
    top_y = 55
    card_h = 240
    
    for i, (title_ua, title_en, desc, border_col, bg_col) in enumerate(cols):
        x = start_x + i * (cw + gap)
        # Карточка
        p.append(rect(x, top_y, cw, card_h, fill=bg_col, stroke=border_col, sw=1.8, rx=8))
        # Заголовок
        p.append(text(x + cw / 2, top_y + 24, title_ua, size=12, bold=True, color=border_col))
        p.append(text(x + cw / 2, top_y + 40, title_en, size=11, italic=True, color=MUTED))
        p.append(line(x + 12, top_y + 50, x + cw - 12, top_y + 50, color=border_col, sw=1.0))
        
        # Текстовий опис
        lines = desc.split("\n")
        for line_idx, ltext in enumerate(lines):
            p.append(text(x + cw / 2, top_y + 75 + line_idx * 20, ltext, size=11, color=INK))
            
        # Піктограма внизу картки
        icon_y = top_y + 195
        if i == 0:
            # Шліфований корпус з напливом
            p.append(rect(x + 40, icon_y - 20, 95, 38, fill="#ffffff", stroke=border_col, sw=1.5, rx=3))
            p.append(line(x + 40, icon_y - 8, x + 135, icon_y - 8, color=POS, sw=2, dash="3 2"))
            p.append(text(x + 87, icon_y + 6, "Лак + лазер", size=10, bold=True, color=POS))
        elif i == 1:
            # Кристал з дефектом
            p.append(rect(x + 45, icon_y - 20, 85, 38, fill="#ffffff", stroke=border_col, sw=1.5, rx=3))
            p.append(circle(x + 87, icon_y - 1, 9, fill="#fdecea", stroke="#d97706", sw=1.5))
            p.append(text(x + 87, icon_y + 3, "✖", size=11, bold=True, color="#d97706"))
        elif i == 2:
            # Порожній чіп
            p.append(rect(x + 45, icon_y - 20, 85, 38, fill="#ffffff", stroke=border_col, sw=1.5, rx=3))
            p.append(text(x + 87, icon_y + 4, "ПОРОЖНЬО", size=10, bold=True, color=MUTED))
        else:
            # Клон
            p.append(rect(x + 45, icon_y - 20, 85, 38, fill="#ffffff", stroke=border_col, sw=1.5, rx=3))
            p.append(text(x + 87, icon_y + 4, "Ersatz Die", size=11, bold=True, color=NEG))

    # Підсумковий інформаційний блок
    b, _, _ = textbox(W / 2, 355,
                      "Контрафакт — це не лише підробка бренду, а насамперед невідповідність фізичної структури заявленим\n"
                      "характеристикам надійності, діапазону температур, стійкості до перенапруг та довговічності кристала.",
                      size=12, fill="#f8fafc", stroke=LINE)
    p.append(b)

    render(os.path.join(OUT, 'counterfeit-categories.svg'), W, H, *p,
           title="Базові категорії контрафактних напівпровідникових компонентів")


def fig_optical_inspection():
    """Оптична інспекція: оригінальний корпус проти перемаркованого під мікроскопом."""
    W, H = 760, 390
    p = []
    
    # Ліва половина: Оригінальний чіп
    p.append(rect(30, 45, 335, 270, fill="#f9fafb", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(197, 70, "ОРИГІНАЛ (OEM)", size=13, bold=True, color=FIELD))
    
    # Креслення чіпа зліва
    p.append(rect(75, 90, 245, 140, fill="#374151", stroke="#111827", sw=2, rx=4))
    # Лунка Pin 1
    p.append(circle(100, 115, 8, fill="#1f2937", stroke="#4b5563", sw=1.5))
    p.append(text(100, 118, "•", size=10, color="#9ca3af"))
    # Заводське маркування
    p.append(text(197, 135, "STM32F407", size=12, bold=True, color="#e5e7eb"))
    p.append(text(197, 155, "VGT6  990AA", size=11, color="#d1d5db"))
    p.append(text(197, 175, "MYS 22 41", size=10, color="#9ca3af"))
    # Виводи зліва/справа
    for y_lead in range(105, 220, 18):
        p.append(line(50, y_lead, 75, y_lead, color="#9ca3af", sw=3))
        p.append(line(320, y_lead, 345, y_lead, color="#9ca3af", sw=3))
        
    p.append(text(197, 252, "• Матова рівномірна текстура компаунда", size=11, color=INK))
    p.append(text(197, 272, "• Чіткі глибокі фаски та чиста лунка Pin 1", size=11, color=INK))
    p.append(text(197, 292, "• Однорідне лазерне травлення (абляція)", size=11, color=INK))

    # Права половина: Підробний чіп
    p.append(rect(395, 45, 335, 270, fill="#fdf2f2", stroke=POS, sw=1.8, rx=8))
    p.append(text(562, 70, "ПЕРЕМАРКУВАННЯ (Blacktopping)", size=13, bold=True, color=POS))
    
    # Креслення чіпа справа
    p.append(rect(440, 90, 245, 140, fill="#1e293b", stroke=POS, sw=2, rx=4))
    # Сліди шліфування (діагональні смуги)
    p.append(line(445, 105, 520, 93, color="#475569", sw=1, dash="4 3"))
    p.append(line(560, 105, 635, 93, color="#475569", sw=1, dash="4 3"))
    p.append(line(450, 215, 530, 203, color="#475569", sw=1, dash="4 3"))
    # Затоплена лунка
    p.append(circle(465, 115, 8, fill="#0f172a", stroke=POS, sw=1.8))
    p.append(text(465, 118, "~", size=11, bold=True, color=POS))
    # Фальшиве маркування
    p.append(text(562, 135, "STM32F407", size=12, bold=True, color="#ffffff"))
    p.append(text(562, 155, "VGT6  990AA", size=11, color="#fca5a5"))
    p.append(text(562, 175, "CHN 25 88", size=10, color="#f87171"))
    # Виводи з напливами
    for y_lead in range(105, 220, 18):
        p.append(line(415, y_lead, 440, y_lead, color="#cbd5e1", sw=3))
        p.append(line(685, y_lead, 710, y_lead, color="#cbd5e1", sw=3))
        p.append(circle(418, y_lead, 2.5, fill=POS, stroke=POS))
        
    p.append(text(562, 252, "• Сліди шліфування під тонким шаром лаку", size=11, color=POS))
    p.append(text(562, 272, "• Лак затікає в лунку Pin 1 (частково залита)", size=11, color=POS))
    p.append(text(562, 292, "• Нерівні виводи зі слідами повторного паяння", size=11, color=POS))

    # Пояснення
    b, _, _ = textbox(W / 2, 350,
                      "Під мікроскопом вторинне покриття видає себе мікропухирцями повітря в лаку, закругленими краями фасок\n"
                      "та невідповідністю шрифтів офіційному вектору виробника (Date Code / Plant Code).",
                      size=12, fill="#f8fafc", stroke=LINE)
    p.append(b)

    render(os.path.join(OUT, 'optical-inspection-defects.svg'), W, H, *p,
           title="Оптична мікроскопія: анатомія дефектів перемаркованого корпусу")


def fig_vi_curve_tracing():
    """Сигнатурний аналіз V-I (Pin-to-Ground Curve Tracing) та форми кривих."""
    W, H = 780, 420
    p = []
    
    # ── Ліва частина: вимірювальна схема ──
    p.append(rect(25, 50, 310, 270, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(180, 72, "Схема вимірювання сигнатури", size=12, bold=True))
    
    # Генератор
    p.append(circle(80, 130, 22, fill="#ffffff", stroke=LINE, sw=1.8))
    p.append(text(80, 134, "~", size=22, bold=True, color=NEG))
    p.append(text(80, 165, "V_test (±5 В)", size=10, color=MUTED))
    
    # Резистор R_limit
    p.append(line(102, 130, 135, 130, color=LINE, sw=1.8))
    p.append(rect(135, 120, 50, 20, fill="#ffffff", stroke=LINE, sw=1.6, rx=3))
    p.append(text(160, 134, "R_lim", size=10, bold=True))
    p.append(text(160, 155, "1 кОм", size=10, color=MUTED))
    
    # Вузол до досліджуваного виводу
    p.append(line(185, 130, 235, 130, color=LINE, sw=1.8))
    p.append(circle(235, 130, 4, fill=INK, stroke=INK))
    p.append(text(235, 115, "Pin DUT", size=11, bold=True, color=POS))
    
    # Вхід мікросхеми (DUT)
    p.append(rect(235, 120, 80, 120, fill="#e2e8f0", stroke="#475569", sw=1.6, rx=4))
    p.append(text(275, 140, "DUT IC", size=11, bold=True))
    # Діоди всередині DUT
    p.append(line(235, 175, 275, 175, color=LINE, sw=1.4))
    p.append(text(275, 170, "ESD Diodes", size=9, color=MUTED))
    p.append(line(275, 175, 275, 225, color=LINE, sw=1.4))
    p.append(line(275, 225, 235, 225, color=LINE, sw=1.4))
    p.append(text(255, 237, "GND", size=10, bold=True))
    
    # Земляна лінія від генератора
    p.append(line(80, 152, 80, 225, color=LINE, sw=1.8))
    p.append(line(80, 225, 235, 225, color=LINE, sw=1.8))
    
    # Зняття V та I на АЦП
    p.append(line(200, 130, 200, 270, color=NEG, sw=1.5, dash="3 3"))
    p.append(text(200, 285, "Канал V (напруга) / Канал I (струм)", size=10, color=NEG))

    # ── Права частина: 4 характерні сигнатури ──
    sig_x0 = 360
    sig_w = 180
    sig_h = 115
    
    signatures = [
        ("Справний пін (ESD-діод)", "#f0fdf4", FIELD, 0, 0,
         "Пряме падіння ~0.65 В,\nзворотний пробій >12 В"),
        ("Обрив (Порожній корпус)", "#fef2f2", POS, 1, 0,
         "Струм відсутній: I = 0\n(горизонтальна лінія)"),
        ("Коротке замикання (КЗ)", "#fef2f2", POS, 0, 1,
         "Напруга відсутня: V = 0\n(вертикальна лінія)"),
        ("Дефект / Інший кристал", "#fffbeb", "#d97706", 1, 1,
         "Витік струму / зсув порогу\nінша структура захисту")
    ]
    
    for title_s, bg_s, col_s, gx, gy, note_s in signatures:
        cx = sig_x0 + gx * (sig_w + 20)
        cy = 50 + gy * (sig_h + 35)
        
        # Рамка графіка
        p.append(rect(cx, cy, sig_w, sig_h, fill=bg_s, stroke=col_s, sw=1.5, rx=6))
        p.append(text(cx + sig_w / 2, cy + 16, title_s, size=10, bold=True, color=col_s))
        
        # Осі координат
        ox, oy = cx + sig_w / 2, cy + sig_h / 2 + 6
        p.append(line(cx + 15, oy, cx + sig_w - 15, oy, color=MUTED, sw=1.0))
        p.append(line(ox, cy + 26, ox, cy + sig_h - 10, color=MUTED, sw=1.0))
        p.append(text(cx + sig_w - 12, oy - 3, "V", size=9, color=MUTED))
        p.append(text(ox + 5, cy + 34, "I", size=9, color=MUTED))
        
        # Сама крива
        if title_s.startswith("Справний"):
            # Коліно діода справа вгору і загин зліва вниз
            p.append('<path d="M%.1f %.1f L%.1f %.1f Q%.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="2.2"/>'
                     % (cx + 25, oy, ox + 25, oy, ox + 35, oy - 2, ox + 45, cy + 30, col_s))
        elif title_s.startswith("Обрив"):
            # Горизонтальна пряма (нульовий струм)
            p.append(line(cx + 25, oy, cx + sig_w - 25, oy, color=col_s, sw=2.5))
        elif title_s.startswith("Коротке"):
            # Вертикальна пряма (нульова напруга)
            p.append(line(ox, cy + 32, ox, cy + sig_h - 12, color=col_s, sw=2.5))
        else:
            # Нахилений еліпс/петля витоку
            p.append('<ellipse cx="%.1f" cy="%.1f" rx="35" ry="18" fill="none" stroke="%s" stroke-width="2" transform="rotate(-25 %.1f %.1f)"/>'
                     % (ox, oy, col_s, ox, oy))
                     
        p.append(text(cx + sig_w / 2, cy + sig_h + 14, note_s.split("\n")[0], size=9, color=MUTED))

    # Нижній блок
    b, _, _ = textbox(W / 2, 380,
                      "V-I сигнатура пін-земля фіксує електричний «відбиток пальця» кристала без його вмикання.\n"
                      "Будь-яка невідповідність техпроцесу чи відсутність кристала миттєво змінює ВАХ захисних кіл.",
                      size=12, fill="#f8fafc", stroke=LINE)
    p.append(b)

    render(os.path.join(OUT, 'vi-curve-tracing.svg'), W, H, *p,
           title="Сигнатурний аналіз V-I (Pin-to-Ground Curve Tracing)")


def fig_xray_inspection():
    """Рентгенографічний аналіз: еталон проти підробки (розмір кристала і розварювання)."""
    W, H = 760, 390
    p = []
    
    # Ліва колонка: Еталонний чіп (OEM Golden Sample)
    p.append(rect(30, 45, 335, 275, fill="#0f172a", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(197, 70, "РЕНТГЕН: ЕТАЛОН (OEM)", size=12, bold=True, color="#4ade80"))
    
    # Зовнішній контур корпусу
    p.append(rect(75, 90, 245, 145, fill="#1e293b", stroke="#334155", sw=1.5, rx=4))
    # Теплорозподільна пластина (Die Paddle)
    p.append(rect(130, 115, 135, 95, fill="#334155", stroke="#475569", sw=1.2))
    # Кремнієвий кристал (великий)
    p.append(rect(145, 125, 105, 75, fill="#64748b", stroke="#94a3b8", sw=1.5))
    p.append(text(197, 165, "Кристал 4.2 × 3.0 мм", size=10, bold=True, color="#f8fafc"))
    
    # Вивідна рамка та золоті провідники (Bond wires)
    for i, y_p in enumerate(range(105, 225, 20)):
        # Ліві виводи
        p.append(line(55, y_p, 105, y_p, color="#94a3b8", sw=2.5))
        # Золоті дроти (висококонтрастні жовті)
        p.append(line(105, y_p, 145, 135 + i * 10, color="#fbbf24", sw=1.8))
        # Праві виводи
        p.append(line(290, y_p, 340, y_p, color="#94a3b8", sw=2.5))
        p.append(line(250, 135 + i * 10, 290, y_p, color="#fbbf24", sw=1.8))
        
    p.append(text(197, 255, "• Великий кристал відповідає тепловому розрахунку", size=10, color="#cbd5e1"))
    p.append(text(197, 275, "• 100% розварювання виводів золотим дротом (Au)", size=10, color="#cbd5e1"))
    p.append(text(197, 295, "• Рівномірний шар приклеювання кристала", size=10, color="#cbd5e1"))

    # Права колонка: Контрафактний чіп
    p.append(rect(395, 45, 335, 275, fill="#0f172a", stroke=POS, sw=1.8, rx=8))
    p.append(text(562, 70, "РЕНТГЕН: КОНТРАФАКТ", size=12, bold=True, color="#f87171"))
    
    # Зовнішній контур
    p.append(rect(440, 90, 245, 145, fill="#1e293b", stroke="#334155", sw=1.5, rx=4))
    # Мала пластина
    p.append(rect(510, 130, 105, 65, fill="#334155", stroke="#475569", sw=1.2))
    # Маленький кристал (чужий)
    p.append(rect(530, 140, 65, 45, fill="#64748b", stroke=POS, sw=1.5))
    p.append(text(562, 165, "Кристал 2.0 × 1.4 мм", size=9, bold=True, color="#fca5a5"))
    
    # Вивідна рамка з пропущеними провідниками
    for i, y_p in enumerate(range(105, 225, 20)):
        p.append(line(420, y_p, 470, y_p, color="#94a3b8", sw=2.5))
        p.append(line(655, y_p, 705, y_p, color="#94a3b8", sw=2.5))
        if i in [1, 2, 4]:
            # Тонкі або алюмінієві дроти (слабка контрастність)
            p.append(line(470, y_p, 530, 145 + (i - 1) * 12, color="#f87171", sw=1.2, dash="3 2"))
            p.append(line(595, 145 + (i - 1) * 12, 655, y_p, color="#f87171", sw=1.2, dash="3 2"))
        else:
            # Пропущені виводи (NC або обрив живлення)
            p.append(circle(470, y_p, 3, fill=POS, stroke=POS))
            p.append(circle(655, y_p, 3, fill=POS, stroke=POS))
            
    p.append(text(562, 255, "• Площа кристала в 4.5 рази менша за норму", size=10, color="#fca5a5"))
    p.append(text(562, 275, "• Пропущені розварювальні дроти на пінах живлення", size=10, color="#fca5a5"))
    p.append(text(562, 295, "• Каверни та пустоти в компаунді (кустарна збірка)", size=10, color="#fca5a5"))

    # Пояснення
    b, _, _ = textbox(W / 2, 355,
                      "Рентген дозволяє за секунди виявити підробку без руйнування корпусу: зменшений кристал\n"
                      "не витримає номінальної розсіюваної потужності, а пропущені зв'язки позбавляють чип функціоналу.",
                      size=12, fill="#f8fafc", stroke=LINE)
    p.append(b)

    render(os.path.join(OUT, 'xray-die-bond-comparison.svg'), W, H, *p,
           title="Рентгенографічний контроль: розмір кристала та розварювання виводів")


def fig_inbound_inspection_funnel():
    """Багаторівнева вирва вхідного контролю компонентів (IQC)."""
    W, H = 760, 410
    p = []
    
    stages = [
        ("Рівень 0: Валідація джерела", "Перевірка ланцюжка постачання (AVL, CoC від франшизи, сертифікати AS6081)", 
         "#eff6ff", NEG, 700),
        ("Рівень 1: Візуальний контроль (100% пакування, AQL)", "Огляд упаковки MSL, DataMatrix, відсутність слідів окислення та blacktopping під оптикою", 
         "#f0fdf4", FIELD, 580),
        ("Рівень 2: Хімічний та V-I скринінг", "Ацетоновий тест на стійкість маркування + вибіркове зняття V-I сигнатур захисних діодів", 
         "#fffbeb", "#d97706", 460),
        ("Рівень 3: Рентгенографічний аналіз (X-Ray)", "Перевірка геометрії кристала, відповідності підкладки та топології розварювання провідників", 
         "#fdf2f2", POS, 340),
        ("Рівень 4: Декапсуляція та кліматичні тести", "Розчинення компаунда кислотою, верифікація маски кристала та стрес-тест у камері", 
         "#f3e8ff", "#9333ea", 240)
    ]
    
    top_y = 55
    h_step = 62
    
    for idx, (st_name, st_desc, bg_c, stroke_c, width_s) in enumerate(stages):
        cur_y = top_y + idx * h_step
        cx = W / 2
        p.append(rect(cx - width_s / 2, cur_y, width_s, 50, fill=bg_c, stroke=stroke_c, sw=1.6, rx=6))
        p.append(text(cx, cur_y + 19, st_name, size=11, bold=True, color=stroke_c))
        p.append(text(cx, cur_y + 37, st_desc, size=10, color=INK))
        
        # Стрілка вниз між рівнями
        if idx < len(stages) - 1:
            arrow_y = cur_y + 50
            p.append(arrow(cx, arrow_y, cx, arrow_y + 11, color=LINE, sw=1.5))
            
    # Нижній висновок
    b, _, _ = textbox(W / 2, 380,
                      "Кожен наступний рівень вимагає дорожчого обладнання, але відсікає глибші рівні підробок.\n"
                      "Для критичних виробництв комбінація рівнів 1–3 є обов'язковим бар'єром перед виходом на лінію SMT.",
                      size=11, fill="#f8fafc", stroke=LINE)
    p.append(b)

    render(os.path.join(OUT, 'inbound-inspection-funnel.svg'), W, H, *p,
           title="Ієрархія системи вхідного контролю якості компонентів (IQC)")


if __name__ == '__main__':
    fig_counterfeit_categories()
    fig_optical_inspection()
    fig_vi_curve_tracing()
    fig_xray_inspection()
    fig_inbound_inspection_funnel()
    print("OK: 5 figures ->", OUT)
