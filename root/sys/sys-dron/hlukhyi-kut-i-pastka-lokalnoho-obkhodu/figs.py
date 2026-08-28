# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_local_minima_u_obstacle():
    W, H = 880, 440
    p = []

    # Заголовок
    tb_title, _, _ = textbox(440, 26, "Пастка локального мінімуму в U-подібній перешкоді та механізм зависання", size=13, bold=True, fill="#f8fafc", stroke=LINE)
    p.append(tb_title)

    # Ліва частина: Геометрія сил та рівновага у пастці (W_left: 450)
    p.append(rect(30, 55, 470, 365, fill="#ffffff", stroke="#cbd5e1", rx=6))
    p.append(text(265, 78, "Векторне поле сил всередині увігнутої перешкоди", size=12, color=INK, anchor="middle", bold=True))

    # U-подібна перешкода (полігон)
    poly_u = [
        (100, 115), (140, 115), (140, 245), (390, 245), (390, 115), (430, 115),
        (430, 280), (100, 280)
    ]
    pts_u = " ".join("%.1f,%.1f" % pt for pt in poly_u)
    p.append('<polygon points="%s" fill="#94a3b8" stroke="%s" stroke-width="2.0"/>' % (pts_u, LINE))
    p.append(text(265, 266, "U-подібна будівля / перешкода", size=10, color="#ffffff", anchor="middle", bold=True))

    # Ціль (Goal) позаду перешкоди
    p.append(circle(265, 335, 9, fill="#22c55e", stroke="#15803d", sw=2.0))
    p.append(circle(265, 335, 3.5, fill="#ffffff", stroke="none"))
    p.append(text(265, 362, "Ціль p_goal", size=11, color="#15803d", anchor="middle", bold=True))

    # Дрон у положенні рівноваги всередині "кишені"
    drone_x, drone_y = 265, 175
    p.append(circle(drone_x, drone_y, 8.0, fill="#f97316", stroke="#c2410c", sw=2.0))
    p.append(circle(drone_x, drone_y, 3.0, fill="#ffffff", stroke="none"))
    p.append(text(265, 155, "Дрон p(t)", size=11, color="#c2410c", anchor="middle", bold=True))

    # Вектор притягання F_att (спрямований до цілі, вниз)
    p.append(arrow(drone_x, drone_y + 8, drone_x, drone_y + 55, color="#16a34a", sw=2.5))
    p.append(text(drone_x + 35, drone_y + 36, "F_att", size=11, color="#16a34a", anchor="start", bold=True))

    # Вектори відштовхування від стін
    # F_rep від дна (вгору)
    p.append(arrow(drone_x, drone_y - 8, drone_x, drone_y - 48, color=POS, sw=2.2))
    p.append(text(drone_x + 28, drone_y - 28, "F_rep,дно", size=10, color=POS, anchor="start", bold=True))

    # F_rep від лівої стінки (вправо)
    p.append(arrow(drone_x + 8, drone_y, drone_x + 40, drone_y, color=POS, sw=1.8))
    p.append(text(drone_x + 45, drone_y + 12, "F_rep,ліва", size=9, color=POS, anchor="start"))

    # F_rep від правої стінки (вліво)
    p.append(arrow(drone_x - 8, drone_y, drone_x - 40, drone_y, color=POS, sw=1.8))
    p.append(text(drone_x - 45, drone_y + 12, "F_rep,права", size=9, color=POS, anchor="end"))

    # Підсумок векторів
    fb_forces = fitbox(45, 305, 175, 100, "Рівновага сил:\nF_att + ∑ F_rep = 0\n∇U(p) = 0, p ≠ p_goal\nШвидкість v → 0\n(Зависання у пастці)", size=10, fill="#fef2f2", stroke="#fca5a5")
    p.append(fb_forces)

    # Права частина: Траєкторії та коливальні цикли (W_right: 330)
    p.append(rect(520, 55, 330, 365, fill="#ffffff", stroke="#cbd5e1", rx=6))
    p.append(text(685, 78, "Динаміка граничного циклу (Limit Cycle)", size=12, color=INK, anchor="middle", bold=True))

    # Міні-схема коливань між стінками
    p.append(rect(545, 98, 280, 160, fill="#f8fafc", stroke="#e2e8f0", rx=4))
    # Стінки кишені
    p.append(line(575, 110, 575, 235, color=LINE, sw=3.0))
    p.append(line(795, 110, 795, 235, color=LINE, sw=3.0))
    p.append(line(575, 235, 795, 235, color=LINE, sw=3.0))
    p.append(text(685, 250, "Дно кишені", size=9, color=MUTED, anchor="middle"))

    # Траєкторія коливань дзиґою / вісімкою
    osc_pts = [
        (685, 125), (635, 155), (735, 185), (635, 205),
        (725, 215), (685, 175), (645, 145), (685, 125)
    ]
    for i in range(len(osc_pts) - 1):
        p.append(line(osc_pts[i][0], osc_pts[i][1], osc_pts[i+1][0], osc_pts[i+1][1], color=POS, sw=1.8, dash="3,2"))
        p.append(circle(osc_pts[i][0], osc_pts[i][1], 2.5, fill=POS, stroke="none"))
    p.append(text(685, 140, "Коливальний цикл", size=10, color=POS, anchor="middle", bold=True))

    # Пояснення симптомів
    fb_diag = fitbox(535, 275, 300, 130, "Діагностика пастки на борту:\n• Інтеграл наближення до цілі:\n  ∫ v_prog dt < 0.2 м за 3 с\n• Радіус зміщення: R_disp < 1.0 м\n• Пройдений шлях: L_path > 4.0 м\n• Висновок: автопілот у глухому куті", size=10, fill="#eff6ff", stroke="#93c5fd")
    p.append(fb_diag)

    render(os.path.join(OUT, "local-minima-u-obstacle.svg"), W, H, *p)


def fig_escape_strategies_overview():
    W, H = 880, 440
    p = []

    # Заголовок
    tb_title, _, _ = textbox(440, 26, "Три стратегії виходу з пастки локального мінімуму", size=13, bold=True, fill="#f8fafc", stroke=LINE)
    p.append(tb_title)

    panel_w = 260
    panel_h = 365
    panel_y = 55

    # 1. Відкат по історії (Breadcrumb Backtracking)
    p.append(rect(30, panel_y, panel_w, panel_h, fill="#ffffff", stroke="#cbd5e1", rx=6))
    p.append(text(160, 78, "1. Відкат по історії (Backtrack)", size=11, color=INK, anchor="middle", bold=True))

    # Схема U-кишені для панелі 1
    p.append('<polygon points="65,150 90,150 90,230 230,230 230,150 255,150 255,250 65,250" fill="#94a3b8" stroke="%s" stroke-width="1.5"/>' % LINE)
    
    # Хлібні крихти (історія точок)
    crumbs = [(60, 110), (95, 120), (140, 135), (160, 175), (160, 205)]
    for pt in crumbs:
        p.append(circle(pt[0], pt[1], 3.0, fill=NEG, stroke="none"))
    # Траєкторія відкату назад (зелена пунктирна)
    p.append(arrow(160, 205, 160, 175, color=FIELD, sw=2.0))
    p.append(arrow(160, 175, 140, 135, color=FIELD, sw=2.0))
    p.append(arrow(140, 135, 85, 115, color=FIELD, sw=2.0))
    p.append(circle(160, 205, 5.0, fill=POS, stroke="none"))
    p.append(text(160, 220, "Тупик", size=9, color=POS, anchor="middle", bold=True))
    p.append(text(80, 100, "Точка виходу", size=9, color=FIELD, anchor="middle", bold=True))

    fb_s1 = fitbox(40, 280, 240, 125, "Механізм:\n• Збереження кінематичної історії\n• Відкат назад по вейпоінтах буфера\n• Вихід із зони дії увігнутості\n• Запуск глобального A* з чистої точки", size=10, fill="#f0fdf4", stroke="#86efac")
    p.append(fb_s1)

    # 2. Обхід контуру (Wall-Following / Bug2)
    p.append(rect(310, panel_y, panel_w, panel_h, fill="#ffffff", stroke="#cbd5e1", rx=6))
    p.append(text(440, 78, "2. Обхід контуру (Wall-Following)", size=11, color=INK, anchor="middle", bold=True))

    # Схема U-кишені для панелі 2
    p.append('<polygon points="345,150 370,150 370,230 510,230 510,150 535,150 535,250 345,250" fill="#94a3b8" stroke="%s" stroke-width="1.5"/>' % LINE)
    
    # Траєкторія обходу вздовж внутрішнього та зовнішнього периметра
    p.append(circle(440, 205, 5.0, fill=POS, stroke="none"))
    p.append(text(440, 195, "Hit-point", size=9, color=POS, anchor="middle", bold=True))
    p.append(arrow(440, 205, 390, 205, color=FIELD, sw=2.0))
    p.append(arrow(390, 205, 390, 135, color=FIELD, sw=2.0))
    p.append(arrow(390, 135, 335, 135, color=FIELD, sw=2.0))
    p.append(arrow(335, 135, 335, 265, color=FIELD, sw=2.0))
    p.append(arrow(335, 265, 440, 265, color=FIELD, sw=2.0))
    p.append(text(465, 275, "До цілі", size=9, color=FIELD, anchor="start", bold=True))

    fb_s2 = fitbox(320, 280, 240, 125, "Механізм:\n• Перемикання в режим слідування стіні\n• Вектор швидкості вздовж дотичної\n• Рух по периметру до умови виходу\n• Перетин прямої m-line ближче до цілі", size=10, fill="#eff6ff", stroke="#93c5fd")
    p.append(fb_s2)

    # 3. Вертикальний набір висоти (3D Altitude Escape)
    p.append(rect(590, panel_y, panel_w, panel_h, fill="#ffffff", stroke="#cbd5e1", rx=6))
    p.append(text(720, 78, "3. Набір висоти (3D-манєвр)", size=11, color=INK, anchor="middle", bold=True))

    # Схема будівлі у 3D-профілі (вид збоку)
    p.append(rect(650, 160, 140, 90, fill="#94a3b8", stroke=LINE, sw=1.5))
    p.append(text(720, 210, "Перешкода (висота H)", size=9, color="#ffffff", anchor="middle", bold=True))

    # Траєкторія підйому та перельоту
    p.append(circle(625, 220, 5.0, fill=POS, stroke="none"))
    p.append(text(625, 238, "Тупик", size=9, color=POS, anchor="middle", bold=True))
    p.append(arrow(625, 220, 625, 130, color=FIELD, sw=2.2))
    p.append(arrow(625, 130, 805, 130, color=FIELD, sw=2.2))
    p.append(line(610, 130, 640, 130, color=NEG, sw=1.0, dash="2,2"))
    p.append(text(720, 118, "H + Δz_escape", size=9, color=NEG, anchor="middle", bold=True))

    fb_s3 = fitbox(600, 280, 240, 125, "Механізм:\n• Перевірка висоти стелі за 3D-картою\n• Вертикальний підйом на безпечний ешелон\n• 2D-мінімум зникає у 3D-просторі\n• Прямий проліт над перешкодою", size=10, fill="#fefce8", stroke="#fde047")
    p.append(fb_s3)

    render(os.path.join(OUT, "escape-strategies-overview.svg"), W, H, *p)


if __name__ == "__main__":
    fig_local_minima_u_obstacle()
    fig_escape_strategies_overview()
    print("OK: generated 2 figures")
