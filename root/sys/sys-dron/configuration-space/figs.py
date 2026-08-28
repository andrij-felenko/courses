# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_cspace_point_reduction():
    W, H = 860, 430
    p = []

    # Розділювач
    p.append(line(430, 20, 430, 410, color="#e5e7eb", sw=1.5, dash="4,4"))

    # Ліва панель: Робочий простір W = R²
    tb_l, _, _ = textbox(215, 35, "Робочий простір W (геометричне тіло)", size=13, bold=True, fill="#fff3f0", stroke=POS)
    p.append(tb_l)
    p.append(text(215, 68, "Робот має розмір, орієнтацію та складну форму", size=11, color=MUTED, anchor="middle", italic=True))

    # Рамка робочого простору
    p.append(rect(45, 85, 340, 245, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=4))

    # Перешкода B у робочому просторі
    poly_obs = [(150, 160), (250, 140), (280, 220), (190, 260), (130, 210)]
    pts_obs = " ".join("%.1f,%.1f" % pt for pt in poly_obs)
    p.append('<polygon points="%s" fill="#94a3b8" stroke="%s" stroke-width="2.0"/>' % (pts_obs, LINE))
    p.append(text(200, 200, "Перешкода B", size=11, color="#ffffff", anchor="middle", bold=True))

    # Робот A у початковій позиції
    r_pos1 = (90, 120)
    poly_rob1 = [(75, 130), (105, 130), (105, 110), (75, 110)]
    pts_rob1 = " ".join("%.1f,%.1f" % pt for pt in poly_rob1)
    p.append('<polygon points="%s" fill="#fed7aa" stroke="#ea580c" stroke-width="1.8"/>' % pts_rob1)
    p.append(circle(90, 120, 3.5, fill="#ea580c", stroke="none"))
    p.append(text(90, 102, "A(q₁)", size=10, color="#ea580c", anchor="middle", bold=True))

    # Робот A в момент дотику до перешкоди
    poly_rob2 = [(125, 235), (155, 235), (155, 215), (125, 215)]
    pts_rob2 = " ".join("%.1f,%.1f" % pt for pt in poly_rob2)
    p.append('<polygon points="%s" fill="#fecaca" stroke="%s" stroke-width="1.8" stroke-dasharray="3,3"/>' % (pts_rob2, POS))
    p.append(circle(140, 225, 3.5, fill=POS, stroke="none"))
    p.append(text(120, 252, "Колізія: A(q) ∩ B ≠ ∅", size=10, color=POS, anchor="middle", bold=True))

    # Складна перевірка
    fb_l = fitbox(55, 345, 320, 60, "Складна геометрія:\nПеревірка перетину контурів O(N · M)\nдля кожної конфігурації траєкторії", size=11, fill="#fff7ed", stroke="#fdba74")
    p.append(fb_l)

    # Права панель: Конфігураційний простір C
    tb_r, _, _ = textbox(645, 35, "Конфігураційний простір C (рух точки)", size=13, bold=True, fill="#f0fdf4", stroke=FIELD)
    p.append(tb_r)
    p.append(text(645, 68, "Робот стиснуто в точку q, перешкоду роздуто в C_obs", size=11, color=MUTED, anchor="middle", italic=True))

    # Рамка конфігураційного простору
    p.append(rect(475, 85, 340, 245, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=4))

    # Розширена C-перешкода C_obs = B ⊕ (-A)
    poly_c_obs = [(565, 140), (695, 120), (730, 225), (630, 280), (545, 225)]
    pts_c_obs = " ".join("%.1f,%.1f" % pt for pt in poly_c_obs)
    p.append('<polygon points="%s" fill="#fee2e2" stroke="%s" stroke-width="2.0"/>' % (pts_c_obs, POS))
    p.append('<polygon points="%s" fill="#94a3b8" stroke="%s" stroke-width="1.2" stroke-dasharray="3,3"/>' % (
        " ".join("%.1f,%.1f" % (pt[0] + 430, pt[1]) for pt in poly_obs), LINE))
    p.append(text(630, 200, "C_obs = B ⊕ (−A)", size=11, color=POS, anchor="middle", bold=True))

    # Точковий робот q і траєкторія
    p.append(circle(520, 120, 5.0, fill=FIELD, stroke="#ffffff", sw=2.0))
    p.append(text(520, 102, "q₁ (точка)", size=10, color=FIELD, anchor="middle", bold=True))

    # Безпечний шлях точки q у C_free
    path_q = [(520, 120), (530, 160), (520, 240), (560, 300), (670, 305), (760, 260)]
    for i in range(len(path_q) - 1):
        p.append(line(path_q[i][0], path_q[i][1], path_q[i+1][0], path_q[i+1][1], color=FIELD, sw=2.5))
        p.append(circle(path_q[i+1][0], path_q[i+1][1], 3.0, fill=FIELD, stroke="none"))
    p.append(text(760, 280, "Шлях у C_free", size=10, color=FIELD, anchor="middle", bold=True))

    # Проста перевірка
    fb_r = fitbox(485, 345, 320, 60, "Елементарна перевірка:\nКолізія ⇔ точка q ∈ C_obs\nШлях для точки шукається стандартним графом", size=11, fill="#f0fdf4", stroke="#86efac")
    p.append(fb_r)

    render(os.path.join(OUT, "cspace-point-reduction.svg"), W, H, *p)


def fig_minkowski_sum_expansion():
    W, H = 880, 430
    p = []

    # Заголовок
    tb, _, _ = textbox(440, 28, "Побудова C-перешкоди через суму Мінковського B ⊕ (−A)", size=13, bold=True, fill="#f8fafc", stroke=LINE)
    p.append(tb)

    # 4 кроки
    step_w = 195
    step_h = 290
    step_y = 65

    # Крок 1: Тіло A та перешкода B
    p.append(rect(30, step_y, step_w, step_h, fill="#ffffff", stroke="#e2e8f0", rx=6))
    p.append(text(127, 85, "1. Геометрія у W", size=12, color=INK, anchor="middle", bold=True))
    
    # Робот A
    p.append('<polygon points="90,135 155,135 122,175" fill="#fed7aa" stroke="#ea580c" stroke-width="1.8"/>')
    p.append(circle(122, 148, 3.5, fill="#ea580c", stroke="none"))
    p.append(text(122, 122, "Робот A", size=10, color="#ea580c", anchor="middle", bold=True))
    p.append(text(122, 192, "Центр q = (0,0)", size=9, color=MUTED, anchor="middle"))

    # Перешкода B
    p.append('<polygon points="65,260 160,230 180,290 85,310" fill="#94a3b8" stroke="%s" stroke-width="1.8"/>' % LINE)
    p.append(text(122, 275, "Перешкода B", size=10, color="#ffffff", anchor="middle", bold=True))
    p.append(text(127, 340, "Оригінальні форми", size=10, color=MUTED, anchor="middle", italic=True))

    # Стрілка 1->2
    p.append(arrow(228, 200, 248, 200, color="#94a3b8", sw=2.0))

    # Крок 2: Інверсія робота -A
    p.append(rect(255, step_y, step_w, step_h, fill="#ffffff", stroke="#e2e8f0", rx=6))
    p.append(text(352, 85, "2. Відбиття −A", size=12, color=INK, anchor="middle", bold=True))

    # Оригінальний A пунктиром
    p.append('<polygon points="315,135 380,135 347,175" fill="none" stroke="#ea580c" stroke-width="1.2" stroke-dasharray="3,3"/>')
    # Інвертований -A відносно (347, 185)
    p.append('<polygon points="380,235 315,235 347,195" fill="#fee2e2" stroke="%s" stroke-width="1.8"/>' % POS)
    p.append(circle(347, 222, 3.5, fill=POS, stroke="none"))
    p.append(text(347, 255, "−A = { −a : a ∈ A }", size=10, color=POS, anchor="middle", bold=True))
    p.append(text(352, 340, "Інверсія координат", size=10, color=MUTED, anchor="middle", italic=True))

    # Стрілка 2->3
    p.append(arrow(453, 200, 473, 200, color="#94a3b8", sw=2.0))

    # Крок 3: Обкатування B фігурою -A
    p.append(rect(480, step_y, step_w, step_h, fill="#ffffff", stroke="#e2e8f0", rx=6))
    p.append(text(577, 85, "3. Згортка контурів", size=12, color=INK, anchor="middle", bold=True))

    # Перешкода B по центру
    p.append('<polygon points="530,220 605,195 625,255 550,270" fill="#94a3b8" stroke="%s" stroke-width="1.8"/>' % LINE)
    # Кілька положень -A на вершинах B
    p.append('<polygon points="555,185 505,185 530,150" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="2,2"/>' % POS)
    p.append('<polygon points="630,160 580,160 605,125" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="2,2"/>' % POS)
    p.append('<polygon points="650,220 600,220 625,185" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="2,2"/>' % POS)
    p.append('<polygon points="575,235 525,235 550,200" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="2,2"/>' % POS)
    p.append(text(577, 235, "B", size=11, color="#ffffff", anchor="middle", bold=True))
    p.append(text(577, 340, "Обхід периметра B", size=10, color=MUTED, anchor="middle", italic=True))

    # Стрілка 3->4
    p.append(arrow(678, 200, 698, 200, color="#94a3b8", sw=2.0))

    # Крок 4: Результуюча C-перешкода
    p.append(rect(705, step_y, step_w, step_h, fill="#ffffff", stroke="#e2e8f0", rx=6))
    p.append(text(802, 85, "4. C-перешкода", size=12, color=INK, anchor="middle", bold=True))

    # Опукла оболонка роздутої фігури
    c_poly = [(750, 150), (825, 125), (850, 200), (825, 290), (750, 305), (715, 235)]
    pts_c = " ".join("%.1f,%.1f" % pt for pt in c_poly)
    p.append('<polygon points="%s" fill="#fee2e2" stroke="%s" stroke-width="2.0"/>' % (pts_c, POS))
    p.append('<polygon points="755,220 830,195 850,255 775,270" fill="#94a3b8" stroke="%s" stroke-width="1.2" stroke-dasharray="3,3"/>' % LINE)
    p.append(text(795, 215, "C_obs", size=12, color=POS, anchor="middle", bold=True))
    p.append(circle(730, 130, 4.0, fill=FIELD, stroke="#ffffff", sw=1.5))
    p.append(text(730, 115, "q (вільний)", size=9, color=FIELD, anchor="middle", bold=True))
    p.append(text(802, 340, "Готова C_obs у C-просторі", size=10, color=POS, anchor="middle", bold=True))

    # Підсумок знизу
    tb_bot, _, _ = textbox(440, 395, "Теорема колізії: Робот A(q) перетинає перешкоду B  ⇔  Точка q потрапляє всередину C_obs = B ⊕ (−A)", size=11, bold=True, fill="#eff6ff", stroke=NEG)
    p.append(tb_bot)

    render(os.path.join(OUT, "minkowski-sum-expansion.svg"), W, H, *p)


def fig_cspace_topology_se2():
    W, H = 860, 430
    p = []

    # Розділювач
    p.append(line(430, 20, 430, 410, color="#e5e7eb", sw=1.5, dash="4,4"))

    # Ліва панель: SE(2) = R² x S¹
    tb_l, _, _ = textbox(215, 35, "Топологія SE(2) = ℝ² × S¹ (дрон / ровер)", size=13, bold=True, fill="#eff6ff", stroke=NEG)
    p.append(tb_l)
    p.append(text(215, 68, "Циліндричний простір: періодичність кута θ ∈ [−π, π)", size=11, color=MUTED, anchor="middle", italic=True))

    # Візуалізація шарів SE(2) по куту theta
    p.append(rect(60, 95, 310, 220, fill="#f8fafc", stroke="#cbd5e1", rx=6))

    # Три зрізи по куту
    p.append(rect(80, 235, 270, 60, fill="#ffffff", stroke="#94a3b8", rx=4))
    p.append(text(95, 255, "θ = −π/2", size=10, color=NEG, anchor="start", bold=True))
    p.append('<polygon points="190,265 240,250 250,280 200,285" fill="#fecaca" stroke="%s" stroke-width="1.2"/>' % POS)

    p.append(rect(80, 165, 270, 60, fill="#ffffff", stroke="#94a3b8", rx=4))
    p.append(text(95, 185, "θ = 0", size=10, color=NEG, anchor="start", bold=True))
    p.append('<polygon points="180,185 245,185 245,215 180,215" fill="#fecaca" stroke="%s" stroke-width="1.2"/>' % POS)

    p.append(rect(80, 105, 270, 60, fill="#ffffff", stroke="#94a3b8", rx=4))
    p.append(text(95, 125, "θ = +π/2", size=10, color=NEG, anchor="start", bold=True))
    p.append('<polygon points="195,115 225,115 235,155 205,155" fill="#fecaca" stroke="%s" stroke-width="1.2"/>' % POS)

    # Періодичне замикання кута
    p.append(line(360, 115, 380, 115, color=NEG, sw=1.5))
    p.append(line(380, 115, 380, 285, color=NEG, sw=1.5, dash="3,3"))
    p.append(arrow(380, 285, 360, 285, color=NEG, sw=1.5))
    p.append(text(385, 200, "Замикання: +π ≡ −π", size=9, color=NEG, anchor="middle", bold=True))

    fb_l = fitbox(60, 330, 310, 75, "Метрика з урахуванням періодичності:\nd_S1(θ₁, θ₂) = min(|θ₁ − θ₂|, 2π − |θ₁ − θ₂|)\nd_SE2 = √(w_xy · Δp² + w_θ · d_S1²)", size=10, fill="#f0f9ff", stroke="#bae6fd")
    p.append(fb_l)

    # Права панель: Тор T² = S¹ x S¹ (дволанковий маніпулятор)
    tb_r, _, _ = textbox(645, 35, "Топологія тора T² = S¹ × S¹ (маніпулятор 2R)", size=13, bold=True, fill="#f0fdf4", stroke=FIELD)
    p.append(tb_r)
    p.append(text(645, 68, "Розгортка тора на площину кутів зчленувань (θ₁, θ₂)", size=11, color=MUTED, anchor="middle", italic=True))

    # Розгортка тора [-pi, pi] x [-pi, pi]
    p.append(rect(490, 95, 220, 220, fill="#f8fafc", stroke=LINE, sw=1.8, rx=4))

    # Осі координат
    p.append(line(490, 205, 710, 205, color="#94a3b8", sw=1.0, dash="2,2"))
    p.append(line(600, 95, 600, 315, color="#94a3b8", sw=1.0, dash="2,2"))
    p.append(text(600, 328, "θ₁ ∈ [−π, π)", size=10, color=INK, anchor="middle", bold=True))
    p.append(text(475, 205, "θ₂", size=10, color=INK, anchor="middle", bold=True))

    # Стрілки ототожнення меж тора
    p.append(arrow(540, 95, 660, 95, color=FIELD, sw=2.0))
    p.append(arrow(540, 315, 660, 315, color=FIELD, sw=2.0))
    p.append(arrow(490, 260, 490, 150, color=FIELD, sw=2.0))
    p.append(arrow(710, 260, 710, 150, color=FIELD, sw=2.0))

    # C-перешкода на торі, що розривається на межах
    p.append('<path d="M 490,140 Q 530,150 560,180 Q 540,210 490,200 Z" fill="#fee2e2" stroke="%s" stroke-width="1.5"/>' % POS)
    p.append('<path d="M 710,140 Q 670,150 640,180 Q 660,210 710,200 Z" fill="#fee2e2" stroke="%s" stroke-width="1.5"/>' % POS)
    p.append(text(600, 160, "C_obs", size=11, color=POS, anchor="middle", bold=True))

    # Безперервна траєкторія крізь межу
    p.append(line(520, 270, 490, 250, color=FIELD, sw=2.0))
    p.append(line(710, 250, 660, 230, color=FIELD, sw=2.0))
    p.append(circle(520, 270, 3.5, fill=FIELD, stroke="none"))
    p.append(circle(660, 230, 3.5, fill=FIELD, stroke="none"))
    p.append(text(725, 240, "Перехід межі", size=9, color=FIELD, anchor="start", bold=True))

    fb_r = fitbox(490, 345, 310, 60, "Топологічні властивості тора:\nТраєкторія, перетинаючи праву межу θ₁=+π,\nбезперервно продовжується з лівої межі θ₁=−π", size=10, fill="#f0fdf4", stroke="#86efac")
    p.append(fb_r)

    render(os.path.join(OUT, "cspace-topology-se2.svg"), W, H, *p)


def fig_cspace_representations():
    W, H = 880, 430
    p = []

    # Заголовок
    tb, _, _ = textbox(440, 28, "Три форми представлення вільного простору C_free в автономних системах", size=13, bold=True, fill="#f8fafc", stroke=LINE)
    p.append(tb)

    panel_w = 260
    panel_h = 320
    panel_y = 65

    # Панель 1: Сітка зайнятості та інфляція
    p.append(rect(30, panel_y, panel_w, panel_h, fill="#ffffff", stroke="#e2e8f0", rx=6))
    p.append(text(160, 85, "1. Сітка та інфляція", size=12, color=INK, anchor="middle", bold=True))
    p.append(text(160, 102, "Occupancy Grid & Costmap", size=10, color=MUTED, anchor="middle", italic=True))

    # Візуалізація сітки з шарами вартості
    gx0, gy0 = 55, 120
    cw = 21
    for r in range(8):
        for c in range(10):
            cx, cy = gx0 + c * cw, gy0 + r * cw
            # Центр - перешкода (r: 3..4, c: 4..5)
            if (3 <= r <= 4) and (4 <= c <= 5):
                fill_c = "#1e293b" # Смертельна зона (Lethal)
            elif (2 <= r <= 5) and (3 <= c <= 6):
                fill_c = "#ef4444" # Інфляція робота (Robot radius)
            elif (1 <= r <= 6) and (2 <= c <= 7):
                fill_c = "#fde047" # Зона спадання вартості (Decay)
            else:
                fill_c = "#f8fafc" # Вільний простір
            p.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="#e2e8f0" stroke-width="0.8"/>' % (cx, cy, cw, cw, fill_c))

    # Легенда
    p.append(rect(45, 295, 12, 12, fill="#1e293b", stroke="none"))
    p.append(text(62, 305, "Lethal", size=9, color=INK, anchor="start"))
    p.append(rect(110, 295, 12, 12, fill="#ef4444", stroke="none"))
    p.append(text(127, 305, "R_robot", size=9, color=INK, anchor="start"))
    p.append(rect(175, 295, 12, 12, fill="#fde047", stroke="none"))
    p.append(text(192, 305, "Decay", size=9, color=INK, anchor="start"))

    fb1 = fitbox(40, 325, 240, 50, "Дискретний растр вартостей.\nШвидкий пошук: A*, Dijkstra,\nD* Lite у навігаційному стеку", size=10, fill="#fefce8", stroke="#fef08a")
    p.append(fb1)

    # Панель 2: Клітинна декомпозиція
    p.append(rect(310, panel_y, panel_w, panel_h, fill="#ffffff", stroke="#e2e8f0", rx=6))
    p.append(text(440, 85, "2. Декомпозиція на клітинки", size=12, color=INK, anchor="middle", bold=True))
    p.append(text(440, 102, "Exact & Convex Decomposition", size=10, color=MUTED, anchor="middle", italic=True))

    # Опуклі комірки та перешкода
    p.append(rect(335, 120, 210, 168, fill="#f8fafc", stroke=LINE, sw=1.5))
    # Перешкода
    p.append('<polygon points="410,180 470,180 470,230 410,230" fill="#94a3b8" stroke="%s" stroke-width="1.5"/>' % LINE)
    p.append(text(440, 208, "C_obs", size=10, color="#ffffff", anchor="middle", bold=True))

    # Розрізи декомпозиції
    p.append(line(410, 120, 410, 288, color=POS, sw=1.2, dash="3,3"))
    p.append(line(470, 120, 470, 288, color=POS, sw=1.2, dash="3,3"))

    # Назви комірок
    p.append(text(372, 205, "C₁", size=11, color=FIELD, anchor="middle", bold=True))
    p.append(text(440, 150, "C₂", size=11, color=FIELD, anchor="middle", bold=True))
    p.append(text(440, 260, "C₃", size=11, color=FIELD, anchor="middle", bold=True))
    p.append(text(508, 205, "C₄", size=11, color=FIELD, anchor="middle", bold=True))

    # Граф суміжності
    p.append(circle(372, 205, 12, fill="#ffffff", stroke=FIELD, sw=1.8))
    p.append(text(372, 209, "C₁", size=10, color=FIELD, anchor="middle", bold=True))
    p.append(circle(440, 150, 12, fill="#ffffff", stroke=FIELD, sw=1.8))
    p.append(text(440, 154, "C₂", size=10, color=FIELD, anchor="middle", bold=True))
    p.append(circle(440, 260, 12, fill="#ffffff", stroke=FIELD, sw=1.8))
    p.append(text(440, 264, "C₃", size=10, color=FIELD, anchor="middle", bold=True))
    p.append(circle(508, 205, 12, fill="#ffffff", stroke=FIELD, sw=1.8))
    p.append(text(508, 209, "C₄", size=10, color=FIELD, anchor="middle", bold=True))

    p.append(line(384, 205, 428, 155, color=FIELD, sw=1.5))
    p.append(line(384, 205, 428, 255, color=FIELD, sw=1.5))
    p.append(line(452, 155, 496, 205, color=FIELD, sw=1.5))
    p.append(line(452, 255, 496, 205, color=FIELD, sw=1.5))

    fb2 = fitbox(320, 325, 240, 50, "Аналітичне розбиття на опуклі полігони.\nГарантована опуклість комірок,\nідеально для безперервної оптимізації", size=10, fill="#f0fdf4", stroke="#bbf7d0")
    p.append(fb2)

    # Панель 3: Поле відстаней зі знаком (ESDF / SDF)
    p.append(rect(590, panel_y, panel_w, panel_h, fill="#ffffff", stroke="#e2e8f0", rx=6))
    p.append(text(720, 85, "3. Карти відстаней (ESDF)", size=12, color=INK, anchor="middle", bold=True))
    p.append(text(720, 102, "Euclidean Signed Distance Field", size=10, color=MUTED, anchor="middle", italic=True))

    # Ізолінії відстані навколо перешкоди
    p.append(rect(615, 120, 210, 168, fill="#f8fafc", stroke="#cbd5e1", rx=4))
    
    # Концентричні ізолінії (d = +30, d = +15)
    p.append('<rect x="670" y="160" width="100" height="88" rx="14" fill="#eff6ff" stroke="#93c5fd" stroke-width="1.2"/>')
    p.append('<rect x="685" y="175" width="70" height="58" rx="8" fill="#dbeafe" stroke="#60a5fa" stroke-width="1.2"/>')
    
    # Сама перешкода (d <= 0)
    p.append('<rect x="700" y="190" width="40" height="28" rx="4" fill="#1e293b" stroke="%s" stroke-width="1.5"/>' % LINE)
    p.append(text(720, 207, "d ≤ 0", size=9, color="#ffffff", anchor="middle", bold=True))

    p.append(text(720, 170, "d = +15 см", size=9, color=NEG, anchor="middle"))
    p.append(text(720, 145, "d = +30 см", size=9, color=NEG, anchor="middle"))

    # Вектори градієнта ∇d
    p.append(arrow(660, 204, 635, 204, color=POS, sw=2.0))
    p.append(arrow(780, 204, 805, 204, color=POS, sw=2.0))
    p.append(arrow(720, 140, 720, 125, color=POS, sw=2.0))
    p.append(text(645, 192, "∇d", size=10, color=POS, anchor="middle", bold=True))

    fb3 = fitbox(600, 325, 240, 50, "Неперервне скалярне поле відстані.\nДає аналітичний градієнт ∇d для\nградієнтного виштовхування траєкторій", size=10, fill="#eff6ff", stroke="#bfdbfe")
    p.append(fb3)

    render(os.path.join(OUT, "cspace-representations.svg"), W, H, *p)


if __name__ == "__main__":
    fig_cspace_point_reduction()
    fig_minkowski_sum_expansion()
    fig_cspace_topology_se2()
    fig_cspace_representations()
    print("OK: generated 4 figures")
