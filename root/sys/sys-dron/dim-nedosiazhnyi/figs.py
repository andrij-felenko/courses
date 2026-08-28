# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def svg_ellipse(cx, cy, rx, ry, fill="none", stroke=LINE, sw=1.5, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" stroke-width="%.1f"%s/>' %
            (cx, cy, rx, ry, fill, stroke, sw, d))


def svg_path(d, fill="none", stroke=LINE, sw=1.5):
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (d, fill, stroke, sw)


def fig_wind_energy_reachability():
    W, H = 860, 440
    p = []

    # Заголовок та підзаголовок
    tb_hdr, _, _ = textbox(430, 26, "Енергетична недосяжність Home Point за зустрічного вітру", size=14, bold=True, fill="#f8fafc", stroke="#94a3b8")
    p.append(tb_hdr)
    p.append(text(430, 54, "Асиметрія радіуса досяжності та порятунок через запасні майданчики (Rally Points)", size=11, color=MUTED, italic=True))

    # Ліва панель: Просторова карта та еліпс досяжності
    p.append(rect(30, 72, 410, 350, fill="none", stroke="#cbd5e1", rx=6))
    tb_l_hdr, _, _ = textbox(235, 94, "Карта досяжності (Airspeed = 16 м/с, Вітер = 12 м/с)", size=11, bold=True, fill="#eff6ff", stroke=NEG)
    p.append(tb_l_hdr)

    # Вітер стрілка (із Заходу на Схід: зліва направо)
    p.append(rect(45, 116, 150, 32, fill="#f1f5f9", stroke="#94a3b8", sw=1.0, rx=4))
    p.append(arrow(55, 132, 105, 132, color=NEG, sw=2.0))
    p.append(text(115, 136, "Вітер: 12 м/с", size=10, color=NEG, anchor="start", bold=True))

    # Асиметричний овал досяжності (витягнутий за вітром праворуч)
    p.append(svg_ellipse(275, 260, 135, 95, fill="#f0fdf4", stroke=FIELD, sw=1.5, dash="5,4"))
    p.append(text(340, 195, "Зона досяжності", size=10, color=FIELD, anchor="middle", bold=True))
    p.append(text(340, 210, "(запас заряду > 20%)", size=9, color=FIELD, anchor="middle"))

    # Поточна позиція дрона (Центр)
    p.append(circle(210, 260, 7, fill="#0f172a", stroke="#ffffff", sw=2.0))
    p.append(text(210, 242, "БПЛА (поточна точка)", size=10, color=INK, anchor="middle", bold=True))
    p.append(text(210, 280, "Заряд: 28% (350 Вт·год)", size=9, color=MUTED, anchor="middle"))

    # Home Point (Ліворуч, проти вітру)
    p.append(rect(45, 235, 80, 52, fill="#fef2f2", stroke=POS, sw=1.5, rx=4))
    p.append(circle(85, 252, 4, fill=POS, stroke=INK, sw=1.0))
    p.append(text(85, 268, "Home Point", size=10, color=POS, anchor="middle", bold=True))
    p.append(text(85, 280, "d = 7.5 км", size=9, color=POS, anchor="middle"))

    # Траєкторія до Home: червона пунктирна стрілка
    p.append(line(200, 258, 130, 258, color=POS, sw=2.0, dash="4,3"))
    p.append(text(165, 248, "Vг = 4 м/с", size=9, color=POS, anchor="middle", bold=True))

    # Зона аварії (хрестик) недольоту до Home
    p.append(text(135, 258, "✕", size=13, color=POS, anchor="middle", bold=True))
    p.append(text(135, 228, "Виснаження АКБ", size=9, color=POS, anchor="middle", bold=True))

    # Rally Point 1 (Збоку / Північ)
    p.append(rect(175, 138, 85, 48, fill="#eff6ff", stroke=NEG, sw=1.5, rx=4))
    p.append(circle(217, 154, 4, fill=NEG, stroke=INK, sw=1.0))
    p.append(text(217, 168, "Rally Point 1", size=10, color=NEG, anchor="middle", bold=True))
    p.append(text(217, 180, "d = 4.2 км", size=9, color=NEG, anchor="middle"))
    p.append(arrow(210, 250, 217, 190, color=NEG, sw=2.0))
    p.append(text(245, 220, "Vг = 10.6 м/с", size=9, color=NEG, anchor="start", bold=True))

    # Rally Point 2 (Праворуч / За вітром)
    p.append(rect(340, 236, 85, 48, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=4))
    p.append(circle(382, 252, 4, fill=FIELD, stroke=INK, sw=1.0))
    p.append(text(382, 266, "Rally Point 2", size=10, color=FIELD, anchor="middle", bold=True))
    p.append(text(382, 278, "d = 6.8 км", size=9, color=FIELD, anchor="middle"))
    p.append(arrow(220, 260, 335, 260, color=FIELD, sw=2.0))
    p.append(text(280, 274, "Vг = 28 м/с", size=9, color=FIELD, anchor="middle", bold=True))

    # Пояснення внизу лівої панелі
    p.append(rect(40, 372, 390, 38, fill="#f8fafc", stroke="#e2e8f0", sw=1.0, rx=4))
    p.append(text(235, 387, "До Home проти вітру треба 31 хв (бракує 160 Вт·год).", size=9, color=POS, anchor="middle", bold=True))
    p.append(text(235, 401, "До RP1 треба 6.6 хв (витрата 85 Вт·год), до RP2 — 4.0 хв (48 Вт·год).", size=9, color=FIELD, anchor="middle"))

    # Права панель: Графік розряду та просідання напруги
    p.append(rect(460, 72, 370, 350, fill="none", stroke="#cbd5e1", rx=6))
    tb_r_hdr, _, _ = textbox(645, 94, "Профіль напруги АКБ під час польоту", size=11, bold=True, fill="#fef2f2", stroke=POS)
    p.append(tb_r_hdr)

    # Осі графіка
    p.append(line(510, 340, 800, 340, color="#64748b", sw=1.5)) # Вісь X (час, хв)
    p.append(line(510, 340, 510, 130, color="#64748b", sw=1.5)) # Вісь Y (напруга, В)
    p.append(arrow(510, 135, 510, 125, color="#64748b", sw=1.5))
    p.append(arrow(795, 340, 805, 340, color="#64748b", sw=1.5))

    p.append(text(805, 355, "Час (хв)", size=9, color=MUTED, anchor="end"))
    p.append(text(505, 126, "U (В)", size=9, color=MUTED, anchor="end"))

    # Позначки шкали Y (6S LiPo: 22.2V, 20.5V, 19.2V)
    p.append(text(500, 155, "22.2В", size=9, color=MUTED, anchor="end"))
    p.append(line(506, 152, 514, 152, color="#94a3b8", sw=1.0))
    p.append(text(500, 225, "20.5В", size=9, color=MUTED, anchor="end"))
    p.append(line(506, 222, 514, 222, color="#94a3b8", sw=1.0))
    p.append(text(500, 285, "19.2В", size=9, color=POS, anchor="end", bold=True))
    p.append(line(506, 282, 800, 282, color=POS, sw=1.0, dash="3,3"))
    p.append(text(790, 276, "Критичний поріг (Cutoff)", size=9, color=POS, anchor="end", bold=True))

    # Позначки шкали X (0, 5, 10, 15, 20, 25)
    p.append(text(510, 355, "0", size=9, color=MUTED, anchor="middle"))
    p.append(text(560, 355, "5", size=9, color=MUTED, anchor="middle"))
    p.append(text(610, 355, "10", size=9, color=MUTED, anchor="middle"))
    p.append(text(660, 355, "15", size=9, color=MUTED, anchor="middle"))
    p.append(text(710, 355, "20", size=9, color=MUTED, anchor="middle"))
    p.append(text(760, 355, "25", size=9, color=MUTED, anchor="middle"))

    # Крива повернення до Home (просідання та колапс на 12-й хв)
    p.append(svg_path("M 510 160 Q 580 210 610 270 T 630 335", stroke=POS, sw=2.5))
    p.append(circle(628, 330, 4, fill=POS, stroke=INK, sw=1.0))
    p.append(text(640, 325, "Колапс на 12 хв", size=9, color=POS, anchor="start", bold=True))

    # Крива перельоту до RP2 (посадка на 4-й хвилині)
    p.append(svg_path("M 510 160 L 550 185", stroke=FIELD, sw=2.5))
    p.append(circle(550, 185, 4, fill=FIELD, stroke=INK, sw=1.0))
    p.append(text(558, 182, "Посадка RP2 (4 хв, U=21.4В)", size=9, color=FIELD, anchor="start", bold=True))

    # Крива перельоту до RP1 (посадка на 7-й хвилині)
    p.append(svg_path("M 510 160 Q 545 185 577 210", stroke=NEG, sw=2.5))
    p.append(circle(577, 210, 4, fill=NEG, stroke=INK, sw=1.0))
    p.append(text(585, 208, "Посадка RP1 (6.6 хв, U=20.8В)", size=9, color=NEG, anchor="start", bold=True))

    # Висновок під графіком
    p.append(rect(470, 372, 350, 38, fill="#f8fafc", stroke="#e2e8f0", sw=1.0, rx=4))
    p.append(text(645, 387, "Форсований політ проти вітру викликає Voltage Sag.", size=9, color=INK, anchor="middle", bold=True))
    p.append(text(645, 401, "Перехід на Rally Point рятує літак від раптового знеструмлення.", size=9, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, "wind-energy-reachability.svg"), W, H, *p)


def fig_rally_point_selection_pipeline():
    W, H = 860, 420
    p = []

    # Заголовок та підзаголовок
    tb_hdr, _, _ = textbox(430, 26, "Конвеєр вибору та ранжування запасних майданчиків (Rally Points)", size=14, bold=True, fill="#f8fafc", stroke="#94a3b8")
    p.append(tb_hdr)
    p.append(text(430, 52, "Поетапна фільтрація реєстру, розрахунок витрат та запобігання хибним перемиканням", size=11, color=MUTED, italic=True))

    # Блоки конвеєра (5 кроків горизонтально)
    # Крок 1: Реєстр та фільтрація
    p.append(rect(20, 75, 145, 270, fill="none", stroke="#cbd5e1", rx=6))
    tb_s1, _, _ = textbox(92, 95, "1. Фільтрація", size=11, bold=True, fill="#f1f5f9", stroke="#64748b")
    p.append(tb_s1)
    p.append(text(92, 125, "Реєстр майданчиків", size=10, color=INK, anchor="middle", bold=True))
    p.append(text(92, 140, "(Статичні + Динамічні)", size=9, color=MUTED, anchor="middle"))

    p.append(rect(30, 158, 125, 42, fill="#fef2f2", stroke=POS, sw=1.0, rx=4))
    p.append(text(92, 174, "Перевірка Geofence", size=9, color=POS, anchor="middle", bold=True))
    p.append(text(92, 190, "Відсікання No-Fly зон", size=9, color=POS, anchor="middle"))

    p.append(rect(30, 210, 125, 42, fill="#f8fafc", stroke="#94a3b8", sw=1.0, rx=4))
    p.append(text(92, 226, "Радіус підходу", size=9, color=INK, anchor="middle", bold=True))
    p.append(text(92, 242, "R_clearance > R_min", size=9, color=MUTED, anchor="middle"))

    p.append(rect(30, 262, 125, 42, fill="#f8fafc", stroke="#94a3b8", sw=1.0, rx=4))
    p.append(text(92, 278, "Статус доступності", size=9, color=INK, anchor="middle", bold=True))
    p.append(text(92, 294, "is_active == true", size=9, color=MUTED, anchor="middle"))

    p.append(text(92, 328, "N кандидатів", size=9, color=FIELD, anchor="middle", bold=True))

    # Стрілка 1->2
    p.append(arrow(168, 200, 186, 200, color="#64748b", sw=2.0))

    # Крок 2: Аеродинаміка та вітер
    p.append(rect(188, 75, 150, 270, fill="none", stroke="#cbd5e1", rx=6))
    tb_s2, _, _ = textbox(263, 95, "2. Вітровий трикутник", size=11, bold=True, fill="#eff6ff", stroke=NEG)
    p.append(tb_s2)
    p.append(text(263, 125, "Вектор вітру (V_w, ψ_w)", size=10, color=NEG, anchor="middle", bold=True))
    p.append(text(263, 140, "з бортового EKF", size=9, color=MUTED, anchor="middle"))

    p.append(rect(198, 158, 130, 42, fill="#f8fafc", stroke="#94a3b8", sw=1.0, rx=4))
    p.append(text(263, 174, "Кут упередження δ", size=9, color=INK, anchor="middle", bold=True))
    p.append(text(263, 190, "sin(δ) = (Vw/Va)·sin(θ)", size=9, color=MUTED, anchor="middle"))

    p.append(rect(198, 210, 130, 42, fill="#f8fafc", stroke="#94a3b8", sw=1.0, rx=4))
    p.append(text(263, 226, "Шляхова швидкість V_g", size=9, color=INK, anchor="middle", bold=True))
    p.append(text(263, 242, "V_g = Va·cos(δ)+Vw·cos(θ)", size=9, color=MUTED, anchor="middle"))

    p.append(rect(198, 262, 130, 42, fill="#fef2f2", stroke=POS, sw=1.0, rx=4))
    p.append(text(263, 278, "Перевірка просування", size=9, color=POS, anchor="middle", bold=True))
    p.append(text(263, 294, "V_g > V_g_min (> 2 м/с)", size=9, color=POS, anchor="middle"))

    p.append(text(263, 328, "Час підльоту T_fl", size=9, color=FIELD, anchor="middle", bold=True))

    # Стрілка 2->3
    p.append(arrow(340, 200, 358, 200, color="#64748b", sw=2.0))

    # Крок 3: Рельєф та енергія
    p.append(rect(360, 75, 150, 270, fill="none", stroke="#cbd5e1", rx=6))
    tb_s3, _, _ = textbox(435, 95, "3. Рельєф та Енергія", size=11, bold=True, fill="#fef2f2", stroke=POS)
    p.append(tb_s3)
    p.append(text(435, 125, "Профіль висот маршруту", size=10, color=INK, anchor="middle", bold=True))
    p.append(text(435, 140, "SRTM / Terrain Protocol", size=9, color=MUTED, anchor="middle"))

    p.append(rect(370, 158, 130, 42, fill="#f8fafc", stroke="#94a3b8", sw=1.0, rx=4))
    p.append(text(435, 174, "Безпечний ешелон", size=9, color=INK, anchor="middle", bold=True))
    p.append(text(435, 190, "H_safe = H_terr + H_clear", size=9, color=MUTED, anchor="middle"))

    p.append(rect(370, 210, 130, 42, fill="#f8fafc", stroke="#94a3b8", sw=1.0, rx=4))
    p.append(text(435, 226, "Потужність P(Va, Vz)", size=9, color=INK, anchor="middle", bold=True))
    p.append(text(435, 242, "Гориз. + Набір висоти", size=9, color=MUTED, anchor="middle"))

    p.append(rect(370, 262, 130, 42, fill="#fef2f2", stroke=POS, sw=1.0, rx=4))
    p.append(text(435, 278, "Енергетичний бюджет", size=9, color=POS, anchor="middle", bold=True))
    p.append(text(435, 294, "E_req + E_margin < E_rem", size=9, color=POS, anchor="middle"))

    p.append(text(435, 328, "Валідні за енергією", size=9, color=FIELD, anchor="middle", bold=True))

    # Стрілка 3->4
    p.append(arrow(512, 200, 528, 200, color="#64748b", sw=2.0))

    # Крок 4: Функція оцінки (Scoring)
    p.append(rect(530, 75, 150, 270, fill="none", stroke="#cbd5e1", rx=6))
    tb_s4, _, _ = textbox(605, 95, "4. Розрахунок Score", size=11, bold=True, fill="#f0fdf4", stroke=FIELD)
    p.append(tb_s4)
    p.append(text(605, 125, "Багатокритеріальний бал", size=10, color=FIELD, anchor="middle", bold=True))
    p.append(text(605, 140, "J = ∑ (w_i · Cost_i)", size=9, color=MUTED, anchor="middle"))

    p.append(rect(540, 158, 130, 42, fill="#f8fafc", stroke="#94a3b8", sw=1.0, rx=4))
    p.append(text(605, 174, "Вага енергії (w_e)", size=9, color=INK, anchor="middle", bold=True))
    p.append(text(605, 190, "E_req / E_remaining", size=9, color=MUTED, anchor="middle"))

    p.append(rect(540, 210, 130, 42, fill="#f8fafc", stroke="#94a3b8", sw=1.0, rx=4))
    p.append(text(605, 226, "Захід проти вітру", size=9, color=INK, anchor="middle", bold=True))
    p.append(text(605, 242, "Збіг курсу посадки", size=9, color=MUTED, anchor="middle"))

    p.append(rect(540, 262, 130, 42, fill="#f8fafc", stroke="#94a3b8", sw=1.0, rx=4))
    p.append(text(605, 278, "Пріоритет бази (w_p)", size=9, color=INK, anchor="middle", bold=True))
    p.append(text(605, 294, "Тактична важливість", size=9, color=MUTED, anchor="middle"))

    p.append(text(605, 328, "Ранжований список", size=9, color=FIELD, anchor="middle", bold=True))

    # Стрілка 4->5
    p.append(arrow(682, 200, 698, 200, color="#64748b", sw=2.0))

    # Крок 5: Гістерезис та фіксація
    p.append(rect(700, 75, 138, 270, fill="none", stroke="#cbd5e1", rx=6))
    tb_s5, _, _ = textbox(769, 95, "5. Вибір цілі", size=11, bold=True, fill="#fef3c7", stroke="#d97706")
    p.append(tb_s5)
    p.append(text(769, 125, "Фільтр гістерезису", size=10, color=INK, anchor="middle", bold=True))
    p.append(text(769, 140, "Захист від флапінгу", size=9, color=MUTED, anchor="middle"))

    p.append(rect(708, 158, 122, 52, fill="#fef2f2", stroke=POS, sw=1.0, rx=4))
    p.append(text(769, 175, "Поріг зміни цілі", size=9, color=POS, anchor="middle", bold=True))
    p.append(text(769, 190, "J_new < J_cur - ΔJ", size=9, color=POS, anchor="middle"))
    p.append(text(769, 202, "Таймаут утримання", size=9, color=MUTED, anchor="middle"))

    p.append(rect(708, 220, 122, 70, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(769, 240, "АКТИВНИЙ RALLY", size=9, color=FIELD, anchor="middle", bold=True))
    p.append(text(769, 256, "Формування місії:", size=9, color=INK, anchor="middle"))
    p.append(text(769, 270, "1. Набір ешелону", size=9, color=MUTED, anchor="middle"))
    p.append(text(769, 282, "2. Транзитний політ", size=9, color=MUTED, anchor="middle"))

    p.append(text(769, 328, "Виконання RTL", size=9, color=FIELD, anchor="middle", bold=True))

    # Загальний підсумок внизу
    p.append(rect(20, 360, 818, 42, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=4))
    p.append(text(429, 378, "Автопілот безперервно перераховує баланс енергії: якщо Home стає енергетично недосяжним,", size=9, color=INK, anchor="middle", bold=True))
    p.append(text(429, 394, "алгоритм автоматично та без коливань перемикає вектор порятунку на оптимальний Rally Point.", size=9, color=FIELD, anchor="middle", bold=True))

    render(os.path.join(OUT, "rally-point-selection-pipeline.svg"), W, H, *p)


if __name__ == "__main__":
    fig_wind_energy_reachability()
    fig_rally_point_selection_pipeline()
    print("Figures generated successfully in", OUT)
