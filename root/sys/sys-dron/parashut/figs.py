# -*- coding: utf-8 -*-
"""figs.py — ілюстрації до статті «Парашут: опір і швидкість спуску».
Генерує SVG-фігури за допомогою svgkit у теку ./img/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), "img"), exist_ok=True)


def fig_aerodynamics():
    W, H = 940, 520
    P = []
    P.append(text(W / 2, 28, "Аеродинамічний баланс сил і розрахунок швидкості спуску", size=17, bold=True))

    # Ліва колонка: фізична схема купола й дрона
    cx = 260
    # Купол (арка/дуга)
    P.append('<path d="M 80 180 C 80 80, 440 80, 440 180 C 380 165, 320 185, 260 170 C 200 185, 140 165, 80 180 Z" fill="#eaf0fd" stroke="#2457d6" stroke-width="2.5"/>')
    # Зони надлишкового тиску під куполом (текст усередині без перетинання ліній)
    P.append(fitbox(150, 115, 220, 38, "Зона гальмування потоку\n(високий тиск +Δp)", size=11, fill="#ffffff", stroke="#2457d6", color="#2457d6", bold=True))
    
    # Вихори на кромках купола
    P.append('<path d="M 75 190 C 60 205, 55 225, 70 235 C 85 245, 95 225, 85 210" fill="none" stroke="#6b7280" stroke-width="1.5" stroke-dasharray="3,3"/>')
    P.append('<path d="M 445 190 C 460 205, 465 225, 450 235 C 435 245, 425 225, 435 210" fill="none" stroke="#6b7280" stroke-width="1.5" stroke-dasharray="3,3"/>')
    P.append(text(60, 252, "крайові вихори", size=10.5, color=MUTED, italic=True))
    P.append(text(460, 252, "крайові вихори", size=10.5, color=MUTED, italic=True))

    # Стропи (лінії від кромок купола до центральної вуздечки)
    bridle_x, bridle_y = cx, 310
    P.append(line(85, 180, bridle_x, bridle_y, color="#333333", sw=1.2))
    P.append(line(170, 172, bridle_x, bridle_y, color="#333333", sw=1.2))
    P.append(line(260, 170, bridle_x, bridle_y, color="#333333", sw=1.2))
    P.append(line(350, 172, bridle_x, bridle_y, color="#333333", sw=1.2))
    P.append(line(435, 180, bridle_x, bridle_y, color="#333333", sw=1.2))

    # Вуздечка та точка кріплення (bridle / swivel)
    P.append(circle(bridle_x, bridle_y, 4, fill="#333333", stroke="#1a1a1a", sw=1.5))
    P.append(line(bridle_x, bridle_y, cx, 345, color="#333333", sw=2.5))

    # Корпус дрона
    drone_w, drone_h = 160, 44
    P.append(rect(cx - drone_w / 2, 345, drone_w, drone_h, fill="#f4f6f8", stroke="#1a1a1a", sw=2, rx=6))
    P.append(text(cx, 368, "Безпілотник (маса m)", size=12, bold=True))
    # Пропелери (зупинені)
    P.append(line(cx - 95, 350, cx - 65, 350, color="#6b7280", sw=2))
    P.append(line(cx + 65, 350, cx + 95, 350, color="#6b7280", sw=2))
    P.append(circle(cx - 80, 350, 2.5, fill="#1a1a1a", stroke="#1a1a1a"))
    P.append(circle(cx + 80, 350, 2.5, fill="#1a1a1a", stroke="#1a1a1a"))

    # Вектори сил
    # Сила лобового опору F_d вгору (зелена) — стартує над верхівкою купола
    P.append(arrow(cx, 80, cx, 40, color=FIELD, sw=3))
    P.append(textbox(cx + 105, 52, "F_d = 0.5 · ρ · V² · S_p · C_d\n(сила опору)", size=10.5, bold=True, color=FIELD, fill="#e9f7ef", stroke=FIELD)[0])

    # Сила тяжіння F_g вниз (червона)
    P.append(arrow(cx, 390, cx, 480, color=POS, sw=3))
    P.append(textbox(cx + 70, 455, "F_g = m · g\n(вага апарата)", size=11, bold=True, color=POS, fill="#fdecea", stroke=POS)[0])

    # Права колонка: розрахункові формули та критерії безпеки
    rx = 540
    rw = 360
    
    # Блок 1: Рівновага та усталена швидкість
    b1_h = 175
    P.append(rect(rx, 60, rw, b1_h, fill="#ffffff", stroke="#d0d5dd", sw=1.5, rx=8))
    P.append(text(rx + rw / 2, 85, "Усталений спуск (рівновага сил)", size=13, bold=True, color=INK))
    P.append(line(rx + 20, 96, rx + rw - 20, 96, color="#e5e7eb", sw=1))
    
    P.append(fitbox(rx + 20, 106, rw - 40, 115,
                    "F_d = F_g  ⇒  прискорення a = 0\n"
                    "0.5 · ρ · V_term² · S_p · C_d = m · g\n"
                    "V_term = √( (2 · m · g) / (ρ · S_p · C_d) )\n"
                    "ρ ≈ 1.225 кг/м³ (густина повітря на рівні моря)\n"
                    "C_d ≈ 1.5–1.75 (хрестоподібний купол)",
                    size=11, pad=6, fill="#f8fafc", stroke="#cbd5e1", bold=False))

    # Блок 2: Критерії безпеки удару (ASTM F3322 / FAA / EASA)
    b2_y = 250
    b2_h = 240
    P.append(rect(rx, b2_y, rw, b2_h, fill="#ffffff", stroke="#d0d5dd", sw=1.5, rx=8))
    P.append(text(rx + rw / 2, b2_y + 25, "Нормативні критерії безпеки приземлення", size=13, bold=True, color=POS))
    P.append(line(rx + 20, b2_y + 36, rx + rw - 20, b2_y + 36, color="#e5e7eb", sw=1))

    P.append(fitbox(rx + 20, b2_y + 46, rw - 40, 178,
                    "Кінетична енергія удару:\n"
                    "E_k = 0.5 · m · V_term²\n\n"
                    "• Безпечна швидкість: V_term ≤ 3.0–4.5 м/с\n"
                    "• Ліміт енергії для людей: E_k < 80 Дж\n"
                    "  (критичний поріг важких травм голови)\n"
                    "• Жорсткий поріг (OOP Cat 2): E_k < 34 Дж\n"
                    "• Приклад (дрон 4.0 кг при V = 3.5 м/с):\n"
                    "  E_k = 0.5 · 4.0 · 3.5² = 24.5 Дж  (безпечно)",
                    size=10.5, pad=6, fill="#fdf2f2", stroke="#fca5a5", bold=False))

    render(os.path.join(os.path.dirname(__file__), "img", "parashut-descent-aerodynamics.svg"), W, H, *P)


def fig_ejection_mechanisms():
    W, H = 940, 480
    P = []
    P.append(text(W / 2, 28, "Порівняння механізмів примусового викиду купола", size=17, bold=True))

    col_w = 280
    gap = 25
    x_start = 35

    # 3 типи: Пружинний, Пневматичний (CO2), Піротехнічний
    types = [
        {
            "title": "Механічна пружина",
            "subtitle": "Spring-Loaded Ejection",
            "color": "#2457d6",
            "bg": "#eaf0fd",
            "scheme": "Пружина стиснута в тубусі,\nутримується замком сервоприводу",
            "v0": "V₀ ≈ 10–16 м/с",
            "t_ej": "t_eject ≈ 60–90 мс",
            "h_min": "h_min ≈ 18–25 м",
            "pros": "• Багаторазове зведення вручну\n• Немає піротехніки (вільний IATA)\n• Просте обслуговування",
            "cons": "• Більша маса та габарити\n• Повільніше наповнення\n• Втома металу при зберіганні"
        },
        {
            "title": "Стиснений газ (CO₂)",
            "subtitle": "Pneumatic Piston Ejection",
            "color": "#27ae60",
            "bg": "#e9f7ef",
            "scheme": "Балончик CO₂ 16г (55 бар),\nпробійник на серво/електромагніті",
            "v0": "V₀ ≈ 18–26 м/с",
            "t_ej": "t_eject ≈ 30–50 мс",
            "h_min": "h_min ≈ 14–18 м",
            "pros": "• Висока енергія викиду\n• Немає відкритого вогню\n• Дозволено для перевезень",
            "cons": "• Потребує заміни балона CO₂\n• Чутливий до морозу (тиск CO₂)\n• Складніша герметизація"
        },
        {
            "title": "Балістичний піропатрон",
            "subtitle": "Pyrotechnic Squib Ejection",
            "color": "#c0392b",
            "bg": "#fdecea",
            "scheme": "Пороховий мікрозаряд (Squib),\nпідпал електроімпульсом 2 А",
            "v0": "V₀ ≈ 30–45 м/с",
            "t_ej": "t_eject ≈ 10–20 мс",
            "h_min": "h_min ≈ 10–14 м",
            "pros": "• Миттєвий надшвидкий викид\n• Мінімальна висота порятунку\n• Найлегший компактний тубус",
            "cons": "• Одноразовий змінний заряд\n• Обмеження перевезень (IATA)\n• Вимагає ліцензій/сертифікації"
        }
    ]

    for i, t in enumerate(types):
        x = x_start + i * (col_w + gap)
        P.append(rect(x, 60, col_w, 395, fill="#ffffff", stroke=t["color"], sw=1.8, rx=8))
        # Шапка
        P.append(rect(x, 60, col_w, 54, fill=t["bg"], stroke=t["color"], sw=1.8, rx=8))
        P.append(text(x + col_w / 2, 82, t["title"], size=13.5, bold=True, color=t["color"]))
        P.append(text(x + col_w / 2, 102, t["subtitle"], size=10.5, color=MUTED, italic=True))

        # Схема роботи
        P.append(fitbox(x + 10, 122, col_w - 20, 52, t["scheme"], size=10.5, fill="#f8fafc", stroke="#e2e8f0"))

        # Ключові метрики
        my = 182
        P.append(rect(x + 10, my, col_w - 20, 72, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=5))
        P.append(text(x + 20, my + 20, "Швидкість викиду:", size=10.5, color=INK, bold=True, anchor="start"))
        P.append(text(x + col_w - 20, my + 20, t["v0"], size=10.5, color=t["color"], bold=True, anchor="end"))
        P.append(text(x + 20, my + 40, "Час спрацьовування:", size=10.5, color=INK, bold=True, anchor="start"))
        P.append(text(x + col_w - 20, my + 40, t["t_ej"], size=10.5, color=t["color"], bold=True, anchor="end"))
        P.append(text(x + 20, my + 60, "Мін. висота розкриття:", size=10.5, color=INK, bold=True, anchor="start"))
        P.append(text(x + col_w - 20, my + 60, t["h_min"], size=10.5, color=t["color"], bold=True, anchor="end"))

        # Переваги та недоліки
        P.append(text(x + 15, 272, "Переваги:", size=11, bold=True, color=FIELD, anchor="start"))
        P.append(fitbox(x + 10, 280, col_w - 20, 68, t["pros"], size=9.5, fill="#f0fdf4", stroke="#bbf7d0"))

        P.append(text(x + 15, 360, "Недоліки та обмеження:", size=11, bold=True, color=POS, anchor="start"))
        P.append(fitbox(x + 10, 368, col_w - 20, 75, t["cons"], size=9.5, fill="#fef2f2", stroke="#fecaca"))

    render(os.path.join(os.path.dirname(__file__), "img", "ejection-mechanisms-comparison.svg"), W, H, *P)


def fig_ptu_safety_chain():
    W, H = 960, 530
    P = []
    P.append(text(W / 2, 26, "Автономна система PTU та часова послідовність порятунку", size=17, bold=True))

    # Верхня частина: Апаратна архітектура PTU
    P.append(text(35, 58, "1. АПАРАТНА АРХІТЕКТУРА АВТОНОМНОГО БЛОКУ (PTU)", size=12.5, bold=True, color=INK, anchor="start"))

    # Блок автономного живлення
    P.append(fitbox(35, 70, 160, 95, "Резервне живлення\n1S LiPo (3.7 В)\n+\nСуперконденсатор\n(незалежно від борту)", size=10.5, pad=6, fill="#fdf6e3", stroke="#b08900", bold=True))
    P.append(arrow(195, 117, 240, 117, color=MUTED, sw=1.5))

    # Центральний мікроконтролер PTU
    P.append(fitbox(240, 70, 240, 95, "Мікроконтролер PTU\n(STM32 Bare-Metal / RTOS)\n• Виділений 6-DOF IMU (1 кГц)\n• Фільтр вільного падіння / tumble\n• Захист від помилкового запуску", size=10.5, pad=6, fill="#eef2f7", stroke="#2457d6", bold=True))

    # Два виходи: Motor Cutoff (FTS) та Ejection Trigger
    P.append(arrow(480, 95, 535, 95, color=POS, sw=2))
    P.append(text(507, 85, "1. FTS", size=10, bold=True, color=POS))
    P.append(fitbox(535, 70, 185, 45, "Motor Cutoff (FTS)\nОптрони / DShot переривач\n(миттєва зупинка моторів)", size=10, pad=4, fill="#fdecea", stroke=POS, bold=True))

    P.append(arrow(480, 140, 535, 140, color=FIELD, sw=2))
    P.append(text(507, 130, "2. Eject", size=10, bold=True, color=FIELD))
    P.append(fitbox(535, 120, 185, 45, "Ejection Actuator\nMOSFET-ключ підпалу\n(піропатрон / CO₂ / серво)", size=10, pad=4, fill="#e9f7ef", stroke=FIELD, bold=True))

    # Безпечний контур від головного FC (MAVLink Heartbeat & Arming status)
    P.append(fitbox(750, 70, 175, 95, "Зв'язок з автопілотом\n(MAVLink / GPIO Arm)\n• Статус Arm/Disarm\n• Блокування на землі\n(ручний спуск з GCS)", size=10, pad=5, fill="#f8fafc", stroke="#94a3b8"))
    P.append(line(750, 117, 720, 117, color=MUTED, sw=1.2, dash="3,3"))

    # Нижня частина: Часова шкала послідовності «Cut Before Deploy»
    P.append(text(35, 195, "2. ЧАСОВА ШКАЛА АВАРІЙНОЇ ПОСЛІДОВНОСТІ (CUT BEFORE DEPLOY)", size=12.5, bold=True, color=INK, anchor="start"))

    timeline_y = 310
    P.append(line(50, timeline_y, 910, timeline_y, color="#333333", sw=2.5))

    events = [
        (60, "0 мс", "Аварія", "Вільне падіння a<0.2g\nабо зрив ω>350°/с", POS, "#fdecea"),
        (180, "+80 мс", "Детекція PTU", "Підтвердження аварії\n(фільтр шуму IMU)", "#b08900", "#fdf6e3"),
        (320, "+90 мс", "Motor Cutoff", "FTS: вимкнення ESC\nАктивне гальмування", POS, "#fdecea"),
        (470, "+140 мс", "Викид купола", "Мотори зупинено!\nПідпал піропатрона", FIELD, "#e9f7ef"),
        (640, "+320 мс", "Line Stretch", "Повний вихід строп\nПочаток наповнення", "#2457d6", "#eaf0fd"),
        (820, "+650 мс", "Full Inflation", "Купол розкрито!\nУсталений спуск V_term", FIELD, "#e9f7ef")
    ]

    for x, t_str, title, desc, col, bg in events:
        # Мітка на осі часу
        P.append(circle(x, timeline_y, 5, fill=col, stroke="#1a1a1a", sw=1.5))
        P.append(text(x, timeline_y + 20, t_str, size=11, bold=True, color=col))
        
        # Картка над віссю
        card_h = 68
        card_y = timeline_y - 25 - card_h
        P.append(line(x, timeline_y, x, card_y + card_h, color=col, sw=1.2, dash="2,2"))
        
        P.append(rect(x - 60, card_y, 120, card_h, fill=bg, stroke=col, sw=1.5, rx=5))
        P.append(text(x, card_y + 16, title, size=11, bold=True, color=col))
        P.append(fitbox(x - 55, card_y + 22, 110, 42, desc, size=9, fill=bg, stroke=bg, color=INK))

    # Нижній висновок-підсумок
    P.append(rect(50, 375, 860, 125, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    P.append(text(70, 400, "Критичне правило безпеки: FTS (Motor Cutoff) ЗАВЖДИ передує викиду купола", size=12, bold=True, color=POS, anchor="start"))
    P.append(fitbox(70, 412, 820, 75,
                    "Якщо викинути парашут до повної зупинки моторів, стропи намотуються на пропелери за 5–15 мс.\n"
                    "Це призводить до перерізання строп карбоновими лопатями, блокування розкриття купола та пожежі моторів.\n"
                    "Затримка між FTS та підпалом (50 мс) з активним DShot-гальмуванням гарантує чистий вихід купола вбік або вгору.",
                    size=10.5, pad=4, fill="#ffffff", stroke="#e2e8f0"))

    render(os.path.join(os.path.dirname(__file__), "img", "ptu-architecture-and-safety-chain.svg"), W, H, *P)


if __name__ == "__main__":
    fig_aerodynamics()
    fig_ejection_mechanisms()
    fig_ptu_safety_chain()
    print("Figures generated successfully.")
