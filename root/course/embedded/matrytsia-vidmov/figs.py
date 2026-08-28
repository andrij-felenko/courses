# -*- coding: utf-8 -*-
"""Генератор векторних діаграм для теми 'Матриця відмов'."""
import sys
import os

# scripts/ лежить на 4 рівні вгору від root/course/embedded/matrytsia-vidmov
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_failsafe_fsm():
    """Скінченний автомат переходів станів аварійного захисту (Failsafe FSM)."""
    w, h = 980, 530
    frags = []

    frags.append(text(w / 2, 28, "Скінченний автомат аварійних станів автопілота (Failsafe FSM)", size=16, bold=True))

    # Стан 1: Штатний політ
    b_norm, _, _ = textbox(160, 110, "NORMAL_FLIGHT\nШтатне виконання місії\nабо ручне керування", size=13, pad=12, fill="#e8f8f0", stroke=FIELD, sw=2, bold=True)
    frags.append(b_norm)

    # Проміжний стан: Оцінка та фільтрація тривоги (Debounce)
    b_eval, _, _ = textbox(500, 110, "EVALUATION / DEBOUNCE\nТаймери підтвердження відмови\n(RC 1.5 с, GNSS 3.0 с, Batt 1.0 с)", size=12, pad=12, fill="#fef9e7", stroke="#d4ac0d", sw=2, bold=True)
    frags.append(b_eval)

    # Аварійний стан 2: Повернення додому (RTL)
    b_rtl, _, _ = textbox(820, 110, "FS_ACTION_RTL\nАвтономне повернення\nЄ GNSS + Є батарея", size=12, pad=12, fill="#ebf5fb", stroke=NEG, sw=2, bold=True)
    frags.append(b_rtl)

    # Аварійний стан 3: Безпечний висотний спуск (AltHold / Land)
    b_land, _, _ = textbox(820, 310, "FS_ACTION_LAND\nКероване зниження на місці\nНемає GNSS або мало заряду", size=12, pad=12, fill="#fbeee6", stroke="#e67e22", sw=2, bold=True)
    frags.append(b_land)

    # Аварійний стан 4: Екстрене вимкнення / Термінація
    b_term, _, _ = textbox(820, 460, "FS_ACTION_TERMINATE\nВимкнення моторів (Disarm)\nабо викид парашута", size=12, pad=12, fill="#fdedec", stroke=POS, sw=2, bold=True)
    frags.append(b_term)

    # Стан відновлення зв'язку
    b_rec, _, _ = textbox(160, 310, "RECOVERY_HOLD\nОчікування стабільного сигналу\n(Гістерезис 2.0 с)", size=12, pad=12, fill="#f4f6f8", stroke=MUTED, sw=1.8, bold=True)
    frags.append(b_rec)

    # Стрілки та підписи
    # 1. Normal -> Evaluation
    frags.append(arrow(265, 110, 370, 110, color=LINE, sw=2))
    frags.append(text(318, 96, "Детекція аномалії", size=11, color=MUTED))

    # 2. Evaluation -> Normal (якщо відновилось до таймауту)
    frags.append(arrow(370, 130, 265, 130, color=FIELD, sw=1.8))
    frags.append(text(318, 148, "Короткий збій < таймаут", size=10, color=FIELD))

    # 3. Evaluation -> RTL
    frags.append(arrow(630, 110, 715, 110, color=NEG, sw=2))
    frags.append(text(672, 96, "RC Loss + GNSS OK", size=11, color=NEG, bold=True))

    # 4. Evaluation -> Land
    frags.append(arrow(580, 155, 730, 270, color="#e67e22", sw=2))
    frags.append(text(620, 220, "GNSS Glitch або Low Batt", size=11, color="#e67e22", bold=True))

    # 5. Evaluation -> Terminate
    frags.append(arrow(530, 155, 715, 440, color=POS, sw=2))
    frags.append(text(540, 370, "Crit Batt / Fatal Fail", size=11, color=POS, bold=True))

    # 6. RTL -> Land (деградація в польоті)
    frags.append(arrow(820, 155, 820, 260, color="#e67e22", sw=2))
    frags.append(text(868, 205, "GNSS Lost у польоті", size=10, color="#e67e22"))

    # 7. Land -> Terminate (торкання землі або критичний стан)
    frags.append(arrow(820, 360, 820, 420, color=POS, sw=2))
    frags.append(text(868, 390, "Детекція посадки", size=10, color=POS))

    # 8. RTL -> Recovery Hold (відновлення RC)
    frags.append(line(725, 140, 245, 270, color=MUTED, sw=1.5, dash="4,4"))
    frags.append(text(460, 240, "RC відновлено: перевірка зв'язку", size=11, color=MUTED))

    # 9. Recovery Hold -> Normal
    frags.append(arrow(160, 265, 160, 155, color=FIELD, sw=2))
    frags.append(text(105, 210, "Сигнал стабільний", size=10, color=FIELD))

    render(os.path.join(OUT, "failsafe-fsm.svg"), w, h, *frags)


def fig_conflict_matrix():
    """Матриця пріоритетів і розв'язання конфліктів одночасних відмов."""
    w, h = 980, 500
    frags = []

    frags.append(text(w / 2, 28, "Ієрархія та матриця розв'язання конфліктів одночасних відмов", size=16, bold=True))

    # Ліва колонка: Піраміда пріоритетів безпеки
    frags.append(text(230, 68, "Ієрархія пріоритетів безпеки", size=14, bold=True, color=INK))

    p1, _, _ = textbox(230, 115, "РІВЕНЬ 1 (Найвищий): Безпека людей\nЗапобігання некерованому падінню в натовп\nДія: Негайний Disarm / Викид парашута", size=11, pad=10, fill="#fdedec", stroke=POS, sw=2, bold=True)
    p2, _, _ = textbox(230, 195, "РІВЕНЬ 2: Межі дозволеного простору\nПорушення Geofence (периметр / стеля)\nДія: Зупинка біля кордону / Примусовий Land", size=11, pad=10, fill="#fef5e7", stroke="#d35400", sw=1.8, bold=True)
    p3, _, _ = textbox(230, 275, "РІВЕНЬ 3: Енергетична невідворотність\nКритична напруга акумулятора (Batt Critical)\nДія: Термінова вертикальна посадка Land", size=11, pad=10, fill="#fef9e7", stroke="#f39c12", sw=1.8, bold=True)
    p4, _, _ = textbox(230, 355, "РІВЕНЬ 4: Навігаційна достовірність\nВтрата / глушіння / спуфінг GNSS\nДія: Спуск в AltHold або оптичне утримання", size=11, pad=10, fill="#ebf5fb", stroke=NEG, sw=1.8, bold=True)
    p5, _, _ = textbox(230, 435, "РІВЕНЬ 5: Канал зв'язку оператора\nВтрата RC або телеметрії GCS\nДія: Автономний RTL або продовження місії", size=11, pad=10, fill="#e8f8f0", stroke=FIELD, sw=1.8, bold=True)

    frags.extend([p1, p2, p3, p4, p5])

    # Права колонка: Таблиця типових конфліктних комбінацій
    frags.append(text(710, 68, "Розв'язання конфліктів одночасних відмов", size=14, bold=True, color=INK))

    cases = [
        ("Комбінація: Втрата зв'язку (RC Loss) + Втрата супутників (GNSS Glitch)",
         "Конфлікт: RTL вимагає навігації, але координати недостовірні\nАрбітраж: Заборона RTL -> Перехід у Land або AltHold спуск",
         "#ebf5fb", NEG),
        ("Комбінація: Втрата зв'язку (RC Loss) + Критична батарея (Batt Crit)",
         "Конфлікт: Часу дольоту до Home більше, ніж запасу енергії комірок\nАрбітраж: Скасування RTL -> Негайна вертикальна посадка на місці",
         "#fef9e7", "#d35400"),
        ("Комбінація: Вихід за Geofence + Втрата зв'язку (RC Loss)",
         "Конфлікт: RTL летить через заборонену зону / продовжує виліт\nАрбітраж: Пріоритет Geofence -> Гальмування на межі та посадка",
         "#fdedec", POS),
        ("Комбінація: Відмова 1 мотора (Гексакоптер) + Спуфінг GNSS",
         "Конфлікт: Обмежена тяга та відсутність зовнішньої позиції\nАрбітраж: Деградація кутів нахилу + Екстрений спуск на тязі 5 моторів",
         "#f4f6f8", LINE)
    ]

    for idx, (title_c, desc_c, fill_c, strk_c) in enumerate(cases):
        cy = 125 + idx * 92
        bx, _, _ = textbox(710, cy, title_c + "\n" + desc_c, size=11, pad=8, fill=fill_c, stroke=strk_c, sw=1.5, bold=False, min_w=460)
        frags.append(bx)

    render(os.path.join(OUT, "conflict-matrix.svg"), w, h, *frags)


def fig_voltage_sag_hysteresis():
    """Крива просадки напруги під навантаженням та часовий гістерезис фільтрації."""
    w, h = 960, 480
    frags = []

    frags.append(text(w / 2, 28, "Динамічна просадка напруги (Sag), фільтрація та спрацьовування захисту", size=16, bold=True))

    x0, y0 = 90, 400
    xw, yh = 800, 320

    # Осі
    frags.append(line(x0, y0, x0 + xw, y0, color=INK, sw=2))
    frags.append(line(x0, y0, x0, y0 - yh, color=INK, sw=2))

    frags.append(text(x0 + xw, y0 + 26, "Час польоту (t) →", size=11, color=MUTED, anchor="end"))
    frags.append(text(x0 - 15, y0 - yh - 10, "Напруга комірки LiPo (В)", size=11, color=MUTED, anchor="start"))

    # Рівні напруги
    voltages = [
        (4.2, "4.20 В (Повний заряд)", "#27ae60", True),
        (3.7, "3.70 В (Номінал)", "#7f8c8d", False),
        (3.5, "3.50 В (Поріг FS Warning)", "#f39c12", True),
        (3.3, "3.30 В (Поріг FS Critical Land)", "#e74c3c", True),
        (3.0, "3.00 В (Апаратна відсічка BMS)", "#900c3f", True)
    ]

    def vy(v):
        return y0 - (v - 2.9) / (4.3 - 2.9) * yh

    for v, lab, col, dash_flag in voltages:
        yy = vy(v)
        frags.append(line(x0, yy, x0 + xw, yy, color=col, sw=1.2, dash="4,4" if dash_flag else None))
        frags.append(text(x0 - 8, yy + 4, lab, size=10, color=col, anchor="end", bold=dash_flag))

    pts_voc = [(x0 + 20, vy(4.15)), (x0 + 150, vy(3.85)), (x0 + 320, vy(3.75)),
               (x0 + 480, vy(3.68)), (x0 + 620, vy(3.52)), (x0 + 740, vy(3.35))]

    pts_vload = [
        (x0 + 20, vy(4.10)), (x0 + 150, vy(3.75)),
        (x0 + 220, vy(3.70)), (x0 + 240, vy(3.28)), (x0 + 280, vy(3.25)), (x0 + 300, vy(3.68)),
        (x0 + 400, vy(3.62)), (x0 + 520, vy(3.54)),
        (x0 + 620, vy(3.40)), (x0 + 680, vy(3.28)), (x0 + 740, vy(3.15))
    ]

    s_voc = " ".join("%.1f,%.1f" % (pt[0], pt[1]) for pt in pts_voc)
    frags.append('<polyline points="%s" fill="none" stroke="#27ae60" stroke-width="2" stroke-dasharray="6,4"/>' % s_voc)

    s_vload = " ".join("%.1f,%.1f" % (pt[0], pt[1]) for pt in pts_vload)
    frags.append('<polyline points="%s" fill="none" stroke="#2457d6" stroke-width="2.2"/>' % s_vload)

    # Пояснення імпульсу струму (просадки)
    bx_sag, _, _ = textbox(x0 + 260, vy(3.26) + 48, "Короткочасний пік газу (Sag)\nТривалість < t_debounce\nFailsafe НЕ спрацьовує", size=10, pad=6, fill="#fef9e7", stroke="#d4ac0d", sw=1.2)
    frags.append(bx_sag)
    frags.append(arrow(x0 + 260, vy(3.26) + 26, x0 + 260, vy(3.26) + 4, color="#d4ac0d", sw=1.5))

    # Пояснення стійкого вичерпання
    bx_crit, _, _ = textbox(x0 + 690, vy(3.28) - 45, "Стійка просадка > t_debounce\nПідтвердження вичерпання\nСпрацьовує FS_ACTION_LAND", size=10, pad=6, fill="#fdedec", stroke=POS, sw=1.5, bold=True)
    frags.append(bx_crit)
    frags.append(arrow(x0 + 690, vy(3.28) - 22, x0 + 690, vy(3.28) - 4, color=POS, sw=1.8))

    # Легенда
    frags.append(line(x0 + 440, y0 - yh + 20, x0 + 480, y0 - yh + 20, color="#27ae60", sw=2, dash="6,4"))
    frags.append(text(x0 + 490, y0 - yh + 24, "ЕРС батареї (Voc)", size=10, color=INK, anchor="start"))

    frags.append(line(x0 + 640, y0 - yh + 20, x0 + 680, y0 - yh + 20, color="#2457d6", sw=2.2))
    frags.append(text(x0 + 690, y0 - yh + 24, "Напруга на клемах під струмом (Vload)", size=10, color=INK, anchor="start"))

    render(os.path.join(OUT, "voltage-sag-hysteresis.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_failsafe_fsm()
    fig_conflict_matrix()
    fig_voltage_sag_hysteresis()
    print("Векторні фігури успішно згенеровано у img/.")
