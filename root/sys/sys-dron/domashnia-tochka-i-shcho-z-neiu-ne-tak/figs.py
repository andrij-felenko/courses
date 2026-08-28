# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_home_drift_at_arming():
    W, H = 860, 430
    p = []

    # Заголовок та підзаголовок
    tb_hdr, _, _ = textbox(430, 28, "Анатомія помилки Home Point при передчасному Arming", size=14, bold=True, fill="#f8fafc", stroke="#94a3b8")
    p.append(tb_hdr)
    p.append(text(430, 58, "Холодний старт GNSS та несходжений EKF зміщують точку повернення у перешкоду", size=11, color=MUTED, italic=True))

    # Ліва панель: Хронологія запуску та схід EKF
    p.append(rect(30, 80, 380, 330, fill="#ffffff", stroke="#cbd5e1", rx=6))
    tb_l_hdr, _, _ = textbox(220, 102, "Хронологія ініціалізації навігації", size=12, bold=True, fill="#eff6ff", stroke=NEG)
    p.append(tb_l_hdr)

    # Етапи по осі часу
    p.append(line(70, 135, 70, 375, color="#94a3b8", sw=2.0))
    
    # Точка 1: Подача живлення (0 с)
    p.append(circle(70, 145, 5, fill="#64748b", stroke=INK, sw=1.5))
    p.append(text(85, 142, "0 с: Подача живлення (Power ON)", size=11, color=INK, anchor="start", bold=True))
    p.append(text(85, 158, "Холодний старт GNSS, пошук супутників, шум", size=10, color=MUTED, anchor="start"))

    # Точка 2: Перший 3D Fix (15 с)
    p.append(circle(70, 205, 5, fill=POS, stroke=INK, sw=1.5))
    p.append(text(85, 202, "15 с: Перший 3D Fix (HDOP = 2.8, 6 супутників)", size=11, color=POS, anchor="start", bold=True))
    p.append(text(85, 218, "Похибка псевдодальностей: σ = 20–30 м", size=10, color=POS, anchor="start"))

    # Помилка: Ранній Arming
    p.append(rect(80, 235, 315, 52, fill="#fef2f2", stroke=POS, sw=1.2, rx=4))
    p.append(text(237, 252, "⚠ ПЕРЕДЧАСНИЙ ARMING ТА ФІКСАЦІЯ HOME", size=10, color=POS, anchor="middle", bold=True))
    p.append(text(237, 270, "Координата Home зафіксована зі зміщенням 25 м!", size=10, color=POS, anchor="middle"))

    # Точка 3: Повне сходження EKF (50 с)
    p.append(circle(70, 315, 5, fill=FIELD, stroke=INK, sw=1.5))
    p.append(text(85, 312, "50 с: Сходження EKF (HDOP = 0.8, 18 супутників)", size=11, color=FIELD, anchor="start", bold=True))
    p.append(text(85, 328, "Коваріація P_pos < 1.2 м, стабільний розв'язок", size=10, color=MUTED, anchor="start"))

    # Точка 4: Реальний стан під час польоту
    p.append(circle(70, 365, 5, fill=NEG, stroke=INK, sw=1.5))
    p.append(text(85, 362, "Політ: EKF знає точне місце, але Home спотворено", size=10, color=INK, anchor="start", bold=True))
    p.append(text(85, 378, "Автопілот повертає борт на координату 15-ї секунди", size=10, color=MUTED, anchor="start"))

    # Права панель: Просторова карта посадки
    p.append(rect(430, 80, 400, 330, fill="#f8fafc", stroke="#cbd5e1", rx=6))
    tb_r_hdr, _, _ = textbox(630, 102, "Просторові наслідки при Return-to-Launch", size=12, bold=True, fill="#fef2f2", stroke=POS)
    p.append(tb_r_hdr)

    # Реальна галявина старту
    p.append(rect(460, 240, 110, 110, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=6))
    p.append(circle(515, 295, 6, fill=FIELD, stroke=INK, sw=1.5))
    p.append(text(515, 280, "Реальний старт", size=10, color=FIELD, anchor="middle", bold=True))
    p.append(text(515, 312, "(Оператор / Стіл)", size=9, color=MUTED, anchor="middle"))

    # Водойма / Ліс поруч
    p.append(rect(630, 220, 180, 140, fill="#e0f2fe", stroke=NEG, sw=1.5, rx=6))
    p.append(text(720, 245, "Водойма / Лісосмуга", size=11, color=NEG, anchor="middle", bold=True))
    p.append(text(720, 262, "Високі дерева 15–20 м", size=10, color=MUTED, anchor="middle"))

    # Хибна домашня точка всередині водойми/лісу
    p.append(circle(715, 305, 8, fill=POS, stroke=INK, sw=2.0))
    p.append(text(715, 292, "Хибний Home Point", size=10, color=POS, anchor="middle", bold=True))
    p.append(text(715, 325, "(Зміщення Δ = 26.4 м)", size=9, color=POS, anchor="middle", bold=True))

    # Траєкторія повернення дрона (RTL)
    p.append(arrow(680, 140, 715, 290, color=POS, sw=2.5))
    p.append(text(650, 155, "Траєкторія RTL", size=10, color=POS, anchor="end", bold=True))

    # Стрілка помилки між стартом і хибним домом
    p.append(line(525, 295, 705, 305, color="#94a3b8", sw=1.5, dash="4,3"))
    p.append(text(615, 288, "Вектор дрейфу GNSS", size=10, color=POS, anchor="middle", bold=True))

    # Пояснювальний висновок внизу карти
    p.append(rect(450, 365, 360, 34, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    p.append(text(630, 386, "Наслідок: посадка у воду або зіткнення з деревом на висоті 15 м", size=10, color=POS, anchor="middle", bold=True))

    render(os.path.join(OUT, "home-drift-at-arming.svg"), W, H, *p)


def fig_moving_home_telemetry():
    W, H = 860, 420
    p = []

    # Заголовок
    tb_hdr, _, _ = textbox(430, 28, "Динамічна домашня точка (Moving Home / Follow-Me RTL)", size=14, bold=True, fill="#f8fafc", stroke="#94a3b8")
    p.append(tb_hdr)
    p.append(text(430, 58, "Екстраполяція швидкості бази та безпека при затримках і втратах телеметрії MAVLink", size=11, color=MUTED, italic=True))

    # Судно в початковий момент t0
    p.append(rect(60, 280, 140, 70, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=6))
    p.append(text(130, 305, "Судно / База t = 0", size=11, color=INK, anchor="middle", bold=True))
    p.append(text(130, 325, "Точка зльоту БПЛА", size=10, color=MUTED, anchor="middle"))

    # Траєкторія судна
    p.append(arrow(205, 315, 595, 315, color=NEG, sw=2.5))
    p.append(text(400, 300, "Швидкість судна v_ship = 15 вузлів (~7.7 м/с)", size=11, color=NEG, anchor="middle", bold=True))

    # Судно в момент RTL (t = 40 хв)
    p.append(rect(600, 280, 160, 70, fill="#eff6ff", stroke=NEG, sw=1.8, rx=6))
    p.append(text(680, 305, "Позиція бази t = 40 хв", size=11, color=NEG, anchor="middle", bold=True))
    p.append(text(680, 325, "Зміщення ΔL = 18.5 км", size=10, color=NEG, anchor="middle", bold=True))

    # Дрон у повітрі на місії
    p.append(rect(360, 95, 140, 55, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(430, 118, "БПЛА на місії", size=11, color=POS, anchor="middle", bold=True))
    p.append(text(430, 136, "Спрацював Failsafe / RTL", size=9, color=MUTED, anchor="middle"))

    # Помилковий шлях: повернення на статичний Home t=0
    p.append(arrow(390, 155, 150, 275, color=POS, sw=2.0))
    p.append(text(210, 205, "Хибний статичний RTL:", size=10, color=POS, anchor="middle", bold=True))
    p.append(text(210, 222, "падіння у відкрите море", size=10, color=POS, anchor="middle"))

    # Правильний шлях: Dynamic Moving Home
    p.append(arrow(470, 155, 660, 275, color=FIELD, sw=2.5))
    p.append(text(610, 195, "Динамічний RTL:", size=10, color=FIELD, anchor="middle", bold=True))
    p.append(text(610, 212, "наведення на рухомий док", size=10, color=FIELD, anchor="middle"))

    # Блок телеметрії та фільтрації
    p.append(rect(240, 365, 380, 42, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=4))
    p.append(text(430, 383, "MAVLink HOME_POSITION + Kalman/Alpha-Beta фільтр екстраполяції затримки", size=10, color=INK, anchor="middle", bold=True))
    p.append(text(430, 399, "Компенсація латентності каналу зв'язку (0.5–2.0 с) та курсового кута", size=9, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, "moving-home-telemetry.svg"), W, H, *p)


def fig_rally_points_selection():
    W, H = 860, 430
    p = []

    # Заголовок
    tb_hdr, _, _ = textbox(430, 28, "Мережа точок безпечного збору (Rally Points) та оцінка вартості", size=14, bold=True, fill="#f8fafc", stroke="#94a3b8")
    p.append(tb_hdr)
    p.append(text(430, 58, "Вибір майданчика за відстанню, вектором зустрічного вітру та залишком батареї", size=11, color=MUTED, italic=True))

    # Дрон на позиції інциденту
    p.append(circle(430, 220, 12, fill="#fef2f2", stroke=POS, sw=2.0))
    p.append(text(430, 195, "Позиція БПЛА", size=12, color=POS, anchor="middle", bold=True))
    p.append(text(430, 245, "Батарея 22 % (RTL)", size=10, color=POS, anchor="middle", bold=True))

    # Вектор вітру
    p.append(rect(340, 85, 180, 45, fill="#eff6ff", stroke=NEG, sw=1.2, rx=4))
    p.append(arrow(360, 107, 440, 107, color=NEG, sw=2.2))
    p.append(text(475, 105, "Вітер: 12 м/с (Східний)", size=10, color=NEG, anchor="middle", bold=True))
    p.append(text(430, 122, "Створює сильний встречний опір на захід", size=9, color=MUTED, anchor="middle"))

    # Варіант 1: Точка Home (на Захід, 8 км, проти сильного вітру)
    p.append(rect(50, 180, 170, 85, fill="#fff1f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(135, 205, "Базовий Home Point", size=11, color=POS, anchor="middle", bold=True))
    p.append(text(135, 223, "Відстань: 8.0 км", size=10, color=INK, anchor="middle"))
    p.append(text(135, 240, "Проти вітру (V_g = 4 м/с)", size=9, color=POS, anchor="middle", bold=True))
    p.append(text(135, 255, "Ціна J = 85.4 (Брак заряду!)", size=9, color=POS, anchor="middle", bold=True))
    p.append(arrow(415, 220, 225, 220, color=POS, sw=1.8))

    # Варіант 2: Rally Point 1 (на Північ, 4.5 км, боковий вітер)
    p.append(rect(330, 310, 200, 85, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=6))
    p.append(text(430, 332, "Rally Point 1 (Північ)", size=11, color=INK, anchor="middle", bold=True))
    p.append(text(430, 350, "Відстань: 4.5 км | Боковий вітер", size=10, color=MUTED, anchor="middle"))
    p.append(text(430, 367, "Висота майданчика: 120 м", size=9, color=MUTED, anchor="middle"))
    p.append(text(430, 382, "Ціна J = 42.1 (Запасний)", size=9, color=MUTED, anchor="middle"))
    p.append(arrow(430, 235, 430, 305, color="#64748b", sw=1.5))

    # Варіант 3: Rally Point 2 (на Схід, 5.5 км, попутний вітер) - ОПТИМАЛЬНИЙ
    p.append(rect(640, 180, 175, 85, fill="#f0fdf4", stroke=FIELD, sw=2.0, rx=6))
    p.append(text(727, 205, "★ Rally Point 2 (Схід)", size=11, color=FIELD, anchor="middle", bold=True))
    p.append(text(727, 223, "Відстань: 5.5 км", size=10, color=INK, anchor="middle"))
    p.append(text(727, 240, "Попутний вітер (V_g = 28 м/с)", size=9, color=FIELD, anchor="middle", bold=True))
    p.append(text(727, 255, "Ціна J = 18.2 (ОБРАНО!)", size=9, color=FIELD, anchor="middle", bold=True))
    p.append(arrow(445, 220, 635, 220, color=FIELD, sw=2.5))

    # Висновок алгоритму
    p.append(rect(180, 395, 500, 26, fill="#ffffff", stroke="#cbd5e1", rx=4))
    p.append(text(430, 412, "Рішення FSM: Перенаправлення на Rally Point 2 гарантує посадку із залишком 14 % АКБ", size=10, color=FIELD, anchor="middle", bold=True))

    render(os.path.join(OUT, "rally-points-selection.svg"), W, H, *p)


def fig_barometric_ground_drift():
    W, H = 860, 430
    p = []

    # Заголовок
    tb_hdr, _, _ = textbox(430, 28, "Барометричний дрейф висоти та комплексування з далекоміром", size=14, bold=True, fill="#f8fafc", stroke="#94a3b8")
    p.append(tb_hdr)
    p.append(text(430, 58, "Тепловий розігрів сенсора та синоптичний дрейф зміщують віртуальну лінію 0 м", size=11, color=MUTED, italic=True))

    # Лінія реальної поверхні землі
    p.append(line(60, 350, 800, 350, color=FIELD, sw=2.5))
    p.append(text(120, 368, "Реальна поверхня землі (h = 0 м)", size=11, color=FIELD, anchor="start", bold=True))

    # Лінія дрейфу 1: Розігрів корпусу (Барометр думає, що земля вище)
    p.append(line(60, 280, 800, 280, color=POS, sw=1.8, dash="5,4"))
    p.append(text(120, 270, "Хибний рівень 0 м (нагрів корпусу на +25 °C, тиск зріс): дрон роззброюється у повітрі!", size=10, color=POS, anchor="start", bold=True))

    # Лінія дрейфу 2: Падіння атмосферного тиску (Барометр думає, що земля нижче)
    p.append(line(60, 400, 800, 400, color=NEG, sw=1.8, dash="5,4"))
    p.append(text(120, 418, "Хибний рівень 0 м (синоптичне падіння тиску на -2 гПа): жорсткий удар об ґрунт без flare", size=10, color=NEG, anchor="start", bold=True))

    # Схема посадки з перемиканням на лідар
    # Маршове зниження за барометром
    p.append(arrow(700, 90, 700, 195, color="#64748b", sw=2.0))
    p.append(text(715, 145, "Маршове зниження: барометр + GNSS", size=10, color=MUTED, anchor="start"))

    # Точка перемикання на лазерний далекомір (h = 15 м)
    p.append(circle(700, 215, 6, fill=FIELD, stroke=INK, sw=1.8))
    p.append(line(450, 215, 760, 215, color="#94a3b8", sw=1.2, dash="3,3"))
    p.append(text(460, 207, "Поріг захоплення далекоміра (LiDAR AGL < 15 м)", size=10, color=FIELD, anchor="start", bold=True))

    # Конічний промінь лідара вниз (зміщено щоб не перетинати стрілку)
    p.append('<polygon points="700,221 640,350 760,350" fill="#dcfce7" opacity="0.4" stroke="#22c55e" stroke-width="1.2" stroke-dasharray="3,3"/>')
    p.append(text(625, 290, "LiDAR AGL", size=11, color=FIELD, anchor="end", bold=True))

    # Фінальне торкання землі
    p.append(arrow(700, 226, 700, 345, color=FIELD, sw=2.5))
    p.append(text(765, 335, "Точне вирівнювання (Flare)", size=10, color=FIELD, anchor="start", bold=True))

    # Блок резюме комплексування
    p.append(rect(60, 100, 360, 130, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(240, 122, "Архітектура комплексування висоти", size=11, color=INK, anchor="middle", bold=True))
    p.append(text(75, 145, "• Ешелон > 20 м: Барометр (динаміка) + GNSS (тренд)", size=10, color=MUTED, anchor="start"))
    p.append(text(75, 168, "• Зона глісади < 15 м: Активація далекоміра (LiDAR/Радар)", size=10, color=INK, anchor="start", bold=True))
    p.append(text(75, 191, "• Автовиправлення нуля: зсув барометра фіксується", size=10, color=FIELD, anchor="start"))
    p.append(text(75, 212, "• Детекція торкання: стрибок сили по осі Z + AGL < 0.1 м", size=10, color=FIELD, anchor="start", bold=True))

    render(os.path.join(OUT, "barometric-ground-drift.svg"), W, H, *p)


if __name__ == "__main__":
    fig_home_drift_at_arming()
    fig_moving_home_telemetry()
    fig_rally_points_selection()
    fig_barometric_ground_drift()
    print("Всі 4 фігури успішно згенеровано.")
