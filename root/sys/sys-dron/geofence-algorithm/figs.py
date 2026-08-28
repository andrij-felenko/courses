# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Алгоритм геозони».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(REPO_ROOT, 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(SCRIPT_DIR, "img")
os.makedirs(IMG_DIR, exist_ok=True)


# ── Фігура 1: Метод променя (Ray-Casting) та обробка ребер ──────────────────
def fig_ray_casting_edges():
    W, H = 980, 480
    P = []
    P.append(text(W / 2, 28, "Алгоритм пускання променя (Ray-Casting) та обробка ребер полігона",
                  size=16, bold=True))

    # Полігон (неопуклий контур)
    poly = [(140, 360), (140, 140), (320, 240), (480, 100), (600, 260), (460, 400), (300, 340)]
    pts = " ".join("%.0f,%.0f" % (x, y) for x, y in poly)
    P.append('<polygon points="%s" fill="#f4fbf7" stroke="%s" stroke-width="2.5"/>' % (pts, FIELD))

    # Вершини та їхні позначення
    v_labels = ["V0", "V1", "V2", "V3", "V4", "V5", "V6"]
    v_offsets = [(-16, 12), (-16, -8), (14, -12), (0, -14), (16, 4), (14, 16), (-12, 18)]
    for (vx, vy), lbl, (ox, oy) in zip(poly, v_labels, v_offsets):
        P.append(circle(vx, vy, 4.5, fill="#ffffff", stroke=FIELD, sw=2))
        P.append(text(vx + ox, vy + oy, lbl, size=11, color=FIELD, bold=True))

    # Точка P_in (всередині): 3 перетини
    p_in_x, p_in_y = 190, 200
    P.append(circle(p_in_x, p_in_y, 5.5, fill="#2b6cb0", stroke="#1a365d", sw=2))
    P.append(text(p_in_x - 12, p_in_y - 12, "P_in (всередині)", size=11, color="#2b6cb0", bold=True))
    P.append(line(p_in_x, p_in_y, 630, p_in_y, color="#2b6cb0", sw=1.6, dash="5 4"))
    P.append(arrow(p_in_x, p_in_y, 635, p_in_y, color="#2b6cb0", sw=1.6))

    int_pts = [(248, 200), (366, 200), (555, 200)]
    for idx, (ix, iy) in enumerate(int_pts, 1):
        P.append(circle(ix, iy, 4.5, fill=POS, stroke="#9b2c2c", sw=1.5))
        P.append(text(ix, iy - 10, f"#{idx}", size=10, color=POS, bold=True))

    # Точка P_out (зовні): 2 перетини
    p_out2_x, p_out2_y = 60, 280
    P.append(circle(p_out2_x, p_out2_y, 5.5, fill="#718096", stroke="#2d3748", sw=2))
    P.append(text(p_out2_x, p_out2_y - 12, "P_out (зовні)", size=11, color="#4a5568", bold=True))
    P.append(line(p_out2_x, p_out2_y, 630, p_out2_y, color="#718096", sw=1.6, dash="5 4"))
    P.append(arrow(p_out2_x, p_out2_y, 635, p_out2_y, color="#718096", sw=1.6))

    P.append(circle(140, 280, 4.5, fill="#718096", stroke="#2d3748", sw=1.5))
    P.append(text(140, 280 - 10, "#1", size=10, color="#4a5568", bold=True))

    P.append(circle(580, 280, 4.5, fill="#718096", stroke="#2d3748", sw=1.5))
    P.append(text(580, 280 - 10, "#2", size=10, color="#4a5568", bold=True))

    # Права інформаційна панель
    rx = 690
    P.append(fitbox(rx, 70, 270, 160,
                    "Правило парності (Even-Odd)\n"
                    "• Лічильник перетинів k = 0\n"
                    "• Кожен перетин променя x ≥ P.x\n"
                    "  інвертує статус: k = k + 1\n"
                    "• k непарне (1, 3, ...) → ВСЕРЕДИНІ\n"
                    "• k парне (0, 2, 4, ...) → ЗОВНІ",
                    size=12, fill="#f7fafc", stroke=INK, sw=1.4))

    P.append(fitbox(rx, 250, 270, 190,
                    "Обробка крайових умов\n"
                    "• Напіввідкритий інтервал:\n"
                    "  (V_i.y ≤ P.y < V_j.y) або\n"
                    "  (V_j.y ≤ P.y < V_i.y)\n"
                    "• Вершина рахується РІВНО 1 раз\n"
                    "• Горизонтальні ребра: V_i.y == V_j.y\n"
                    "  автоматично ігноруються\n"
                    "• Без ділення: порівняння знака",
                    size=11.5, fill="#ebf8ff", stroke="#3182ce", sw=1.4))

    render(os.path.join(IMG_DIR, "ray-casting-edges.svg"), W, H, *P)


# ── Фігура 2: Композиція зон Keep-In та Keep-Out + AABB фільтр ──────────────
def fig_inclusion_exclusion_composite():
    W, H = 980, 470
    P = []
    P.append(text(W / 2, 28, "Композиція геозон Keep-In (дозволені) та Keep-Out (заборонені) з AABB",
                  size=16, bold=True))

    # Зовнішній AABB габаритний контейнер (пунктир)
    aabb_x, aabb_y, aabb_w, aabb_h = 70, 70, 560, 360
    P.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" fill="none" stroke="#a0aec0" stroke-width="1.5" stroke-dasharray="6 5"/>' % (aabb_x, aabb_y, aabb_w, aabb_h))
    P.append(text(aabb_x + 150, aabb_y + 18, "AABB Bounding Box (O(1) швидка відбраковка)", size=10.5, color="#718096", bold=True))

    # Keep-In Полігон (велика дозволена зона польоту)
    poly_in = [(100, 140), (320, 90), (580, 130), (600, 380), (360, 410), (120, 360)]
    pts_in = " ".join("%.0f,%.0f" % (x, y) for x, y in poly_in)
    P.append('<polygon points="%s" fill="#e6fffa" stroke="%s" stroke-width="2.6"/>' % (pts_in, FIELD))
    P.append(text(340, 125, "Зона дозволеного польоту (Keep-In #1)", size=12, color=FIELD, bold=True))

    # Keep-Out Полігон (заборонена зона всередині)
    poly_out1 = [(170, 200), (290, 180), (310, 270), (190, 290)]
    pts_out1 = " ".join("%.0f,%.0f" % (x, y) for x, y in poly_out1)
    P.append('<polygon points="%s" fill="#fff5f5" stroke="%s" stroke-width="2.2"/>' % (pts_out1, POS))
    P.append(text(240, 238, "Keep-Out (Заборона)", size=10.5, color=POS, bold=True))
    P.append(text(240, 254, "Склад / Вежа зв'язку", size=10, color=POS))

    # Keep-Out Циліндр (кругла заборонена зона)
    c_out_x, c_out_y, c_out_r = 460, 270, 65
    P.append(circle(c_out_x, c_out_y, c_out_r, fill="#fff5f5", stroke=POS, sw=2.2))
    P.append(text(c_out_x, c_out_y - 8, "Keep-Out Циліндр", size=10.5, color=POS, bold=True))
    P.append(text(c_out_x, c_out_y + 8, "R = 150 м, H = 0..100 м", size=10, color=POS))
    P.append(text(c_out_x, c_out_y + 24, "Охоронна зона", size=9.5, color=MUTED))

    # Дрон та його траєкторія
    P.append(circle(200, 360, 6, fill="#3182ce", stroke="#1a365d", sw=2))
    P.append(text(200, 382, "Дрон (безпечна зона)", size=10.5, color="#2b6cb0", bold=True))

    # Траєкторія польоту (стрілка між заборонами)
    traj = [(200, 360), (280, 340), (380, 360), (480, 380)]
    for i in range(len(traj) - 1):
        P.append(line(traj[i][0], traj[i][1], traj[i+1][0], traj[i+1][1], color="#3182ce", sw=2, dash="5 4"))
    P.append(arrow(380, 360, 480, 380, color="#3182ce", sw=2))
    P.append(text(340, 348, "Планований маршрут", size=10, color="#3182ce"))

    # Права панель: Булева алгебра зон
    rx = 660
    P.append(fitbox(rx, 70, 290, 175,
                    "Булева логіка перевірки\n"
                    "Положення P валідне тоді і лише тоді, коли:\n\n"
                    "1. P ∈ ⋃ (Keep-In полігони)\n"
                    "   (якщо є хоча б одна зона впуску,\n"
                    "   апарат мусить бути всередині однієї)\n\n"
                    "2. P ∉ ⋃ (Keep-Out полігони/кола)\n"
                    "   (апарат не повинен бути в ЖОДНІЙ\n"
                    "   із заборонених зон)",
                    size=11, fill="#f7fafc", stroke=INK, sw=1.4))

    P.append(fitbox(rx, 260, 290, 170,
                    "Дворівнева фільтрація на MCU\n"
                    "• Рівень 1: Оцінка AABB (2-4 порівняння).\n"
                    "  Якщо точка поза прямокутником межі,\n"
                    "  полігон відкидається миттєво (O(1)).\n\n"
                    "• Рівень 2: Точний Ray-Casting (O(N))\n"
                    "  викликається лише для зон, AABB яких\n"
                    "  містить координати апарата.",
                    size=11, fill="#f0fff4", stroke=FIELD, sw=1.4))

    render(os.path.join(IMG_DIR, "inclusion-exclusion-composite.svg"), W, H, *P)


# ── Фігура 3: Прогнозування порушення та гальмівний шлях ────────────────────
def fig_predictive_breach_braking():
    W, H = 980, 470
    P = []
    P.append(text(W / 2, 28, "Динамічне прогнозування порушення: швидкість, затримка та гальмівний шлях",
                  size=16, bold=True))

    # Стіна геозони (вертикальний бар'єр праворуч)
    fence_x = 760
    P.append(line(fence_x, 70, fence_x, 410, color=POS, sw=3.5))
    P.append(text(fence_x - 12, 90, "Межа геозони (Hard Fence)", size=12, color=POS, bold=True, anchor="end"))

    # Смуга статичного запасу (FENCE_MARGIN)
    margin_static_w = 70
    margin_x = fence_x - margin_static_w
    P.append(line(margin_x, 70, margin_x, 410, color="#d69e2e", sw=2, dash="6 5"))
    P.append(rect(margin_x, 70, margin_static_w, 340, fill="#fefcbf", stroke="none"))
    P.append(text(margin_x + 35, 395, "Статичний запас", size=10, color="#b7791f", bold=True))

    # Початкова точка дрона
    p0_x, p0_y = 120, 240
    P.append(circle(p0_x, p0_y, 7, fill="#3182ce", stroke="#1a365d", sw=2))
    P.append(text(p0_x, p0_y - 18, "Поточна позиція P", size=11, color="#2b6cb0", bold=True))
    P.append(text(p0_x, p0_y + 20, "V = 18 м/с", size=10.5, color="#2b6cb0"))

    # Відрізок реакції системи: d_react = V * t_react
    d_react_w = 120
    p_react_x = p0_x + d_react_w
    P.append(line(p0_x, p0_y, p_react_x, p0_y, color="#4299e1", sw=3))
    P.append(circle(p_react_x, p0_y, 4.5, fill="#ffffff", stroke="#4299e1", sw=2))
    P.append(arrow(p0_x, p0_y, p_react_x, p0_y, color="#4299e1", sw=2.5))
    P.append(text(p0_x + d_react_w / 2, p0_y - 10, "d_react = V · t_delay", size=10.5, color="#2b6cb0"))
    P.append(text(p0_x + d_react_w / 2, p0_y + 16, "(затримка EKF + фільтр)", size=9.5, color=MUTED))

    # Відрізок гальмування: d_brake = V^2 / (2 * a_max)
    d_brake_w = 260
    p_stop_x = p_react_x + d_brake_w
    P.append(line(p_react_x, p0_y, p_stop_x, p0_y, color="#ed8936", sw=3))
    P.append(arrow(p_react_x, p0_y, p_stop_x, p0_y, color="#ed8936", sw=2.5))
    P.append(circle(p_stop_x, p0_y, 5, fill="#dd6b20", stroke="#7b341e", sw=2))
    P.append(text(p_react_x + d_brake_w / 2, p0_y - 10, "d_brake = V² / (2 · a_max)", size=10.5, color="#c05621", bold=True))
    P.append(text(p_react_x + d_brake_w / 2, p0_y + 16, "(гальмування з a_max)", size=9.5, color=MUTED))

    # Прогнозована точка зупинки (Lookahead point)
    P.append(text(p_stop_x, p0_y - 18, "P_pred (зупинка)", size=11, color="#c05621", bold=True))

    # Залишковий дистанційний запас до межі
    P.append(line(p_stop_x, p0_y, margin_x, p0_y, color=FIELD, sw=2, dash="4 4"))
    P.append(circle(margin_x, p0_y, 4, fill=FIELD, stroke=FIELD))
    P.append(text((p_stop_x + margin_x) / 2, p0_y - 10, "Запас безпеки > 0", size=10, color=FIELD, bold=True))

    # Нижня розмірна шкала повного зупинного шляху
    dim_y = 310
    P.append(line(p0_x, dim_y, p_stop_x, dim_y, color=INK, sw=1.4))
    P.append(line(p0_x, dim_y - 6, p0_x, dim_y + 6, color=INK, sw=1.4))
    P.append(line(p_stop_x, dim_y - 6, p_stop_x, dim_y + 6, color=INK, sw=1.4))
    P.append(text((p0_x + p_stop_x) / 2, dim_y + 18, "Повний динамічний дистанційний поріг D_stop = d_react + d_brake",
                  size=10.5, color=INK, bold=True))

    # Верхня інформаційна картка
    P.append(fitbox(70, 70, 420, 110,
                    "Кінематика попередження порушення\n"
                    "• Time-to-Breach (TTB) = dist_to_fence / V_perp\n"
                    "• Якщо TTB ≤ t_react + V_perp / a_max → аварійне гальмування!\n"
                    "• Без упередження апарат на швидкості 18 м/с пробиває\n"
                    "  статичну межу на 65+ метрів до повної зупинки.",
                    size=11, fill="#f7fafc", stroke=INK, sw=1.4))

    render(os.path.join(IMG_DIR, "predictive-breach-braking.svg"), W, H, *P)


# ── Фігура 4: Скінченний автомат стану геозонування та ескалація дій ────────
def fig_geofence_state_machine():
    W, H = 980, 480
    P = []
    P.append(text(W / 2, 28, "Скінченний автомат стану (FSM) та ієрархія захисних дій автопілота",
                  size=16, bold=True))

    # Стан 1: SAFE (Нормальний політ)
    s1_x, s1_y, s1_w, s1_h = 70, 170, 200, 120
    P.append(rect(s1_x, s1_y, s1_w, s1_h, rx=8, fill="#f0fff4", stroke=FIELD, sw=2.2))
    P.append(text(s1_x + s1_w / 2, s1_y + 26, "GEOFENCE_SAFE", size=13, color=FIELD, bold=True))
    P.append(text(s1_x + s1_w / 2, s1_y + 50, "P ∈ Keep-In && P ∉ Keep-Out", size=10, color=INK))
    P.append(text(s1_x + s1_w / 2, s1_y + 70, "Дистанція > D_stop + Margin", size=10, color=MUTED))
    P.append(text(s1_x + s1_w / 2, s1_y + 94, "Режим: ШТАТНИЙ ПОЛІТ", size=10, color=FIELD, bold=True))

    # Стан 2: WARNING (Наближення до межі / Динамічне упередження)
    s2_x, s2_y, s2_w, s2_h = 390, 70, 210, 130
    P.append(rect(s2_x, s2_y, s2_w, s2_h, rx=8, fill="#fffaf0", stroke="#dd6b20", sw=2.2))
    P.append(text(s2_x + s2_w / 2, s2_y + 26, "GEOFENCE_WARNING", size=13, color="#c05621", bold=True))
    P.append(text(s2_x + s2_w / 2, s2_y + 50, "TTB ≤ T_warn || d < D_margin", size=10, color=INK))
    P.append(text(s2_x + s2_w / 2, s2_y + 72, "Дія: MAVLink WARN на GCS", size=10, color="#c05621", bold=True))
    P.append(text(s2_x + s2_w / 2, s2_y + 92, "Обмеження швидкості до межі", size=10, color=MUTED))
    P.append(text(s2_x + s2_w / 2, s2_y + 110, "Підготовка до гальмування", size=10, color=MUTED))

    # Стан 3: BREACH (Порушення / Неминуче пробиття)
    s3_x, s3_y, s3_w, s3_h = 390, 270, 210, 130
    P.append(rect(s3_x, s3_y, s3_w, s3_h, rx=8, fill="#fff5f5", stroke=POS, sw=2.5))
    P.append(text(s3_x + s3_w / 2, s3_y + 26, "GEOFENCE_BREACH", size=13, color=POS, bold=True))
    P.append(text(s3_x + s3_w / 2, s3_y + 50, "P ∉ Keep-In || P ∈ Keep-Out", size=10, color=INK))
    P.append(text(s3_x + s3_w / 2, s3_y + 70, "Або TTB ≤ T_react + T_brake", size=10, color=POS))
    P.append(text(s3_x + s3_w / 2, s3_y + 94, "Перехоплення навігації", size=10.5, color=POS, bold=True))
    P.append(text(s3_x + s3_w / 2, s3_y + 112, "Failsafe Ladder Recovery", size=10, color=POS))

    # Стан 4: Ескалація захисних дій (Драбина Failsafe)
    s4_x, s4_y, s4_w, s4_h = 710, 110, 210, 290
    P.append(rect(s4_x, s4_y, s4_w, s4_h, rx=8, fill="#edf2f7", stroke="#4a5568", sw=2))
    P.append(text(s4_x + s4_w / 2, s4_y + 26, "Ієрархія реакцій (Actions)", size=12, color=INK, bold=True))

    actions = [
        ("1. HOLD / BRAKE", "Зупинка / зависання", "#2b6cb0"),
        ("2. SMART-RTL", "Повернення чистим треком", FIELD),
        ("3. RTL to SAFE", "Політ до точки зльоту", "#d69e2e"),
        ("4. EMERGENCY LAND", "Негайна посадка на місці", "#dd6b20"),
        ("5. TERMINATION", "Парашут / відсічка моторів", POS)
    ]
    for idx, (title, desc, col) in enumerate(actions):
        ay = s4_y + 55 + idx * 45
        P.append(rect(s4_x + 10, ay, s4_w - 20, 36, rx=4, fill="#ffffff", stroke=col, sw=1.4))
        P.append(text(s4_x + 18, ay + 15, title, size=10, color=col, bold=True, anchor="start"))
        P.append(text(s4_x + 18, ay + 29, desc, size=9.5, color=MUTED, anchor="start"))

    # Стрілки переходів
    # SAFE -> WARNING
    P.append(line(s1_x + s1_w, s1_y + 30, s2_x, s2_y + 60, color="#dd6b20", sw=1.8))
    P.append(arrow(s1_x + s1_w, s1_y + 30, s2_x, s2_y + 60, color="#dd6b20", sw=1.8))
    P.append(text(300, 110, "TTB < T_warn", size=10, color="#c05621"))

    # WARNING -> SAFE (відліт від межі)
    P.append(line(s2_x, s2_y + 90, s1_x + s1_w, s1_y + 60, color=FIELD, sw=1.6, dash="4 4"))
    P.append(arrow(s2_x, s2_y + 90, s1_x + s1_w, s1_y + 60, color=FIELD, sw=1.6))
    P.append(text(300, 145, "Відновлення дистанції", size=10, color=FIELD))

    # SAFE -> BREACH (миттєвий викид / супутниковий стрибок)
    P.append(line(s1_x + s1_w, s1_y + 80, s3_x, s3_y + 40, color=POS, sw=1.8))
    P.append(arrow(s1_x + s1_w, s1_y + 80, s3_x, s3_y + 40, color=POS, sw=1.8))

    # WARNING -> BREACH (продовження руху на стіну)
    P.append(line(s2_x + s2_w / 2, s2_y + s2_h, s3_x + s3_w / 2, s3_y, color=POS, sw=2))
    P.append(arrow(s2_x + s2_w / 2, s2_y + s2_h, s3_x + s3_w / 2, s3_y, color=POS, sw=2))
    P.append(text(s2_x + s2_w / 2 + 55, (s2_y + s2_h + s3_y) / 2, "Не зупинився", size=10, color=POS))

    # BREACH -> ACTIONS
    P.append(line(s3_x + s3_w, s3_y + 65, s4_x, s4_y + 145, color=POS, sw=2))
    P.append(arrow(s3_x + s3_w, s3_y + 65, s4_x, s4_y + 145, color=POS, sw=2))
    P.append(text(655, 275, "Виклик Failsafe", size=10, color=POS, bold=True))

    render(os.path.join(IMG_DIR, "geofence-state-machine.svg"), W, H, *P)


if __name__ == "__main__":
    fig_ray_casting_edges()
    fig_inclusion_exclusion_composite()
    fig_predictive_breach_braking()
    fig_geofence_state_machine()
    print("All figures generated successfully.")
