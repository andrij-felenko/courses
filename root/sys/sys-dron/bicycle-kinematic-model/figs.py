# -*- coding: utf-8 -*-
"""figs.py — генератор SVG-фігур для теми «Кінематична велосипедна модель».
svgkit імпортуємо зі scripts/, вивід у ./img/."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── Допоміжна функція: малювання колеса під кутом ─────────────────────────────
def draw_wheel(cx, cy, deg, w=18, h=44, fill="#3a3f45", stroke=INK):
    rad = math.radians(deg)
    hw, hh = w / 2.0, h / 2.0
    pts = []
    for dx, dy in [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]:
        rx = cx + dx * math.cos(rad) - dy * math.sin(rad)
        ry = cy + dx * math.sin(rad) + dy * math.cos(rad)
        pts.append("%.1f,%.1f" % (rx, ry))
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="1.5"/>'
            % (" ".join(pts), fill, stroke))


# ── Фігура 1: зведення 4-колісного шасі до 2-колісної велосипедної моделі ──────
def fig_bicycle_reduction():
    W, H = 960, 480
    parts = []

    # ЛІВОРУЧ: 4-колісне шасі Аккермана
    lx = 240
    ly = 240
    bw, bh = 140, 220

    # Контур рами автомобіля
    parts.append(rect(lx - bw / 2, ly - bh / 2, bw, bh, fill="#f0f4f8", stroke="#94a3b8", sw=2, rx=12))
    parts.append(line(lx, ly - bh / 2 - 15, lx, ly + bh / 2 + 15, color="#cbd5e1", sw=1.5, dash="5,5"))
    parts.append(text(lx, 42, "Чотириколісне шасі (Аккерман)", size=16, bold=True))
    parts.append(text(lx, 64, "різні кути вивороту лівого й правого коліс", size=12, color=MUTED))

    # Задні колеса (прямо)
    y_rear = ly + bh / 2 - 30
    w_track = bw / 2 + 14
    parts.append(draw_wheel(lx - w_track, y_rear, 0))
    parts.append(draw_wheel(lx + w_track, y_rear, 0))
    parts.append(line(lx - w_track, y_rear, lx + w_track, y_rear, color=INK, sw=2))
    parts.append(circle(lx, y_rear, 4, fill=POS, stroke=INK))

    # Передні колеса (вивернуті вліво)
    y_front = ly - bh / 2 + 30
    parts.append(draw_wheel(lx - w_track, y_front, -28)) # внутрішнє
    parts.append(draw_wheel(lx + w_track, y_front, -18)) # зовнішнє
    parts.append(line(lx - w_track, y_front, lx + w_track, y_front, color=INK, sw=2))
    parts.append(circle(lx, y_front, 4, fill=NEG, stroke=INK))

    # Підписи кутів і колії
    parts.append(text(lx - w_track - 26, y_front - 28, "δ_i", size=13, color=POS, bold=True))
    parts.append(text(lx + w_track + 26, y_front - 28, "δ_o", size=13, color=NEG, bold=True))
    parts.append(text(lx, y_rear + 24, "задня вісь (колія W)", size=11, color=MUTED))
    parts.append(text(lx - bw/2 - 28, ly, "база L", size=11.5, color=INK, bold=True))
    parts.append(line(lx - bw/2 - 12, y_front, lx - bw/2 - 12, y_rear, color=INK, sw=1.2, dash="3,3"))

    # СТРІЛКА СПРОЩЕННЯ ПОСЕРЕДИНІ
    cx = W / 2
    parts.append(arrow(cx - 35, ly, cx + 35, ly, color=FIELD, sw=3))
    box_trans, _, _ = textbox(cx, ly - 35, "Зведення до осі симетрії:\nколія W → 0", size=12, pad=8, fill="#e8f5e9", stroke=FIELD, bold=True)
    parts.append(box_trans)

    # ПРАВОРУЧ: Двоколісна велосипедна модель (Single-Track)
    rx = W - 240
    ry = ly
    parts.append(text(rx, 42, "Еквівалентна велосипедна модель", size=16, bold=True))
    parts.append(text(rx, 64, "одне віртуальне колесо на кожній осі", size=12, color=MUTED))

    # Поздовжня балка шасі
    parts.append(line(rx, ry - bh / 2 + 30, rx, ry + bh / 2 - 30, color=LINE, sw=4))
    parts.append(rect(rx - 16, ry - 35, 32, 70, fill="#f0f4f8", stroke="#94a3b8", sw=1.5, rx=6))

    # Заднє колесо
    parts.append(draw_wheel(rx, y_rear, 0, w=20, h=50))
    parts.append(circle(rx, y_rear, 5, fill=POS, stroke=INK))
    parts.append(text(rx + 36, y_rear + 4, "Заднє (x_r, y_r)", size=12, bold=True, anchor="start"))
    parts.append(text(rx + 36, y_rear + 20, "кут кочення = 0", size=11, color=MUTED, anchor="start"))

    # Центр мас CoM
    y_com = ry + 15
    parts.append(circle(rx, y_com, 6, fill="#f59e0b", stroke=INK))
    parts.append(text(rx - 22, y_com + 4, "CoM", size=12, bold=True, anchor="end"))

    # Переднє колесо (віртуальне з кутом delta)
    parts.append(draw_wheel(rx, y_front, -23, w=20, h=50))
    parts.append(circle(rx, y_front, 5, fill=NEG, stroke=INK))
    parts.append(text(rx + 36, y_front - 6, "Переднє (x_f, y_f)", size=12, bold=True, anchor="start"))
    parts.append(text(rx + 36, y_front + 10, "еквівалентний кут δ", size=11, color=NEG, bold=True, anchor="start"))

    # Пунктирний орієнтир кута керма
    parts.append(line(rx, y_front, rx, y_front - 55, color="#94a3b8", sw=1.2, dash="3,3"))
    parts.append(line(rx, y_front, rx - 24, y_front - 55, color=NEG, sw=1.5))
    parts.append(text(rx - 18, y_front - 40, "δ", size=13, color=NEG, bold=True))

    # Розміри L, lf, lr
    parts.append(line(rx - 55, y_front, rx - 55, y_rear, color=INK, sw=1.2))
    parts.append(line(rx - 60, y_front, rx - 50, y_front, color=INK, sw=1.2))
    parts.append(line(rx - 60, y_rear, rx - 50, y_rear, color=INK, sw=1.2))
    parts.append(text(rx - 68, (y_front + y_rear) / 2, "L", size=13, bold=True, anchor="end"))

    box_bot, _, _ = textbox(W / 2, H - 25,
                            "Велосипедна модель усуває надлишковість 4 коліс при малій бічній силі,\n"
                            "зберігаючи точну геометрію колісної бази L і віртуального кута керма δ",
                            size=12, pad=10, fill=FILL, bold=False)
    parts.append(box_bot)

    render("img/bicycle-reduction.svg", W, H, *parts,
           title="Зведення чотириколісного шасі до велосипедної моделі")


# ── Фігура 2: миттєвий центр обертання (ICR) та геометрія швидкостей ──────────
def fig_icr_geometry():
    W, H = 960, 560
    parts = []

    # Положення миттєвого центру обертання (ICR) ліворуч
    icr_x = 180
    icr_y = 380

    # Центр задньої осі
    rear_x = 680
    rear_y = 380

    # База L і довжини lf, lr
    L_px = 240
    lr_px = 90
    lf_px = 150
    front_x = rear_x
    front_y = rear_y - L_px
    com_x = rear_x
    com_y = rear_y - lr_px

    # ICR точка
    parts.append(circle(icr_x, icr_y, 7, fill=POS, stroke=INK, sw=2))
    parts.append(text(icr_x - 14, icr_y + 24, "МЦО (ICR)", size=14, color=POS, bold=True, anchor="middle"))
    parts.append(text(icr_x - 14, icr_y + 42, "миттєвий центр\nобертання", size=11, color=MUTED, anchor="middle"))

    # Радіуси обертання від ICR
    # До задньої осі (R_r)
    parts.append(line(icr_x, icr_y, rear_x, rear_y, color="#94a3b8", sw=1.8, dash="4,4"))
    parts.append(text((icr_x + rear_x) / 2, rear_y + 20, "R = L / tan(δ)", size=13, color=INK, bold=True))

    # До центру мас CoM (R_cg)
    parts.append(line(icr_x, icr_y, com_x, com_y, color="#f59e0b", sw=1.5, dash="4,4"))
    parts.append(text((icr_x + com_x) / 2 - 20, (icr_y + com_y) / 2 + 18, "R_cg", size=12, color="#d97706", bold=True))

    # До переднього колеса (R_f)
    parts.append(line(icr_x, icr_y, front_x, front_y, color="#3b82f6", sw=1.8, dash="4,4"))
    parts.append(text((icr_x + front_x) / 2 - 30, (icr_y + front_y) / 2 - 10, "R_f = L / sin(δ)", size=12, color=NEG, bold=True))

    # Корпус / балка
    parts.append(line(rear_x, rear_y, front_x, front_y, color=INK, sw=4))

    # Заднє колесо
    parts.append(draw_wheel(rear_x, rear_y, 0, w=22, h=54))
    parts.append(circle(rear_x, rear_y, 5, fill=POS, stroke=INK))
    # Вектор швидкості v_r (строго вздовж осі корпусу)
    parts.append(arrow(rear_x, rear_y, rear_x, rear_y - 75, color=POS, sw=3))
    parts.append(text(rear_x + 18, rear_y - 50, "v_r", size=14, color=POS, bold=True, anchor="start"))

    # CoM
    parts.append(circle(com_x, com_y, 6, fill="#f59e0b", stroke=INK))
    # Вектор швидкості CoM повернутий на кут бета вліво від курсу
    beta_deg = math.degrees(math.atan2(lr_px, (rear_x - icr_x))) # кут зсуву
    vx_com = com_x - 80 * math.sin(math.radians(beta_deg))
    vy_com = com_y - 80 * math.cos(math.radians(beta_deg))
    parts.append(arrow(com_x, com_y, vx_com, vy_com, color="#d97706", sw=3))
    parts.append(text(vx_com - 10, vy_com - 10, "v_cg", size=14, color="#d97706", bold=True, anchor="end"))
    # Кут beta
    parts.append(line(com_x, com_y, com_x, com_y - 70, color="#cbd5e1", sw=1.2, dash="3,3"))
    parts.append(text(com_x - 14, com_y - 45, "β", size=14, color="#d97706", bold=True))

    # Переднє колесо вивернуте на кут delta
    delta_deg = math.degrees(math.atan2(L_px, (rear_x - icr_x)))
    parts.append(draw_wheel(front_x, front_y, -delta_deg, w=22, h=54))
    parts.append(circle(front_x, front_y, 5, fill=NEG, stroke=INK))
    # Вектор швидкості v_f (перпендикулярний до R_f)
    vx_f = front_x - 85 * math.sin(math.radians(delta_deg))
    vy_f = front_y - 85 * math.cos(math.radians(delta_deg))
    parts.append(arrow(front_x, front_y, vx_f, vy_f, color=NEG, sw=3))
    parts.append(text(vx_f - 12, vy_f - 10, "v_f", size=14, color=NEG, bold=True, anchor="end"))
    # Кут керма delta
    parts.append(line(front_x, front_y, front_x, front_y - 75, color="#cbd5e1", sw=1.2, dash="3,3"))
    parts.append(text(front_x - 18, front_y - 50, "δ", size=14, color=NEG, bold=True))

    # Розміри праворуч
    parts.append(line(rear_x + 60, rear_y, rear_x + 60, front_y, color=LINE, sw=1.2))
    parts.append(line(rear_x + 55, rear_y, rear_x + 65, rear_y, color=LINE, sw=1.2))
    parts.append(line(rear_x + 55, front_y, rear_x + 65, front_y, color=LINE, sw=1.2))
    parts.append(line(rear_x + 55, com_y, rear_x + 65, com_y, color=LINE, sw=1.2))
    parts.append(text(rear_x + 75, (rear_y + com_y) / 2, "l_r", size=12, bold=True, anchor="start"))
    parts.append(text(rear_x + 75, (com_y + front_y) / 2, "l_f", size=12, bold=True, anchor="start"))
    parts.append(text(rear_x + 105, (rear_y + front_y) / 2, "L = l_f + l_r", size=12, color=MUTED, anchor="start"))

    # Дуга кутової швидкості omega навколо ICR
    parts.append('<path d="M %d %d A 70 70 0 0 1 %d %d" fill="none" stroke="%s" stroke-width="2.5" marker-end="url(#arrow)"/>'
                 % (icr_x + 65, icr_y - 25, icr_x + 25, icr_y - 65, FIELD))
    parts.append(text(icr_x + 75, icr_y - 65, "ω = θ̇", size=14, color=FIELD, bold=True))

    box_note, _, _ = textbox(W / 2, H - 25,
                             "Миттєвий центр обертання утворюється на перетині перпендикулярів до коліс.\n"
                             "Кутова швидкість всього тіла єдина: ω = v_r / R = v_cg / R_cg = v_f / R_f",
                             size=12, pad=10, fill=FILL, bold=False)
    parts.append(box_note)

    render("img/icr-geometry.svg", W, H, *parts,
           title="Геометрія повороту та миттєвий центр обертання (ICR)")


# ── Фігура 3: неголономні в'язі та розклад швидкостей ─────────────────────────
def fig_nonholonomic_constraints():
    W, H = 940, 460
    parts = []

    # ЛІВОРУЧ: в'язь кочення окремого колеса
    lx = 240
    ly = 210

    parts.append(text(lx, 40, "Неголономна в'язь кочення", size=16, bold=True))
    parts.append(text(lx, 62, "нульова швидкість поперек площини колеса", size=12, color=MUTED))

    # Пляма контакту і колесо
    parts.append(draw_wheel(lx, ly, -25, w=28, h=90, fill="#e2e8f0", stroke=INK))
    parts.append(circle(lx, ly, 6, fill=POS, stroke=INK))

    # Дозволена поздовжня швидкість v_long
    rad = math.radians(-25)
    v_long_x = lx - 110 * math.sin(rad)
    v_long_y = ly - 110 * math.cos(rad)
    parts.append(arrow(lx, ly, v_long_x, v_long_y, color=FIELD, sw=3.5))
    parts.append(text(v_long_x - 10, v_long_y - 12, "v_поздовжнє (вільне кочення)", size=12, color=FIELD, bold=True, anchor="end"))

    # Заборонена бічна швидкість v_lat (перекреслена)
    v_lat_x = lx + 85 * math.cos(rad)
    v_lat_y = ly - 85 * math.sin(rad)
    parts.append(arrow(lx, ly, v_lat_x, v_lat_y, color=POS, sw=2.5))
    parts.append(line(v_lat_x - 12, v_lat_y - 12, v_lat_x + 12, v_lat_y + 12, color=POS, sw=3))
    parts.append(line(v_lat_x - 12, v_lat_y + 12, v_lat_x + 12, v_lat_y - 12, color=POS, sw=3))
    parts.append(text(v_lat_x + 18, v_lat_y + 6, "v_поперечне = 0\n(бокове ковзання заборонене)", size=11.5, color=POS, bold=True, anchor="start"))

    box_pfaff, _, _ = textbox(lx, ly + 140,
                              "Рівняння в'язі Пфаффа:\n"
                              "−ẋ·sin(θ) + ẏ·cos(θ) = 0",
                              size=12.5, pad=9, fill="#fef2f2", stroke=POS, bold=True)
    parts.append(box_pfaff)

    # ПРАВОРУЧ: світова система координат vs орієнтація робота
    rx = W - 240
    ry = 210

    parts.append(text(rx, 40, "Проєкції на світові осі (X, Y)", size=16, bold=True))
    parts.append(text(rx, 62, "перехід від швидкості корпусу v до (ẋ, ẏ)", size=12, color=MUTED))

    # Світові осі
    ox, oy = rx - 90, ry + 70
    parts.append(arrow(ox, oy, ox + 180, oy, color=LINE, sw=2))
    parts.append(text(ox + 185, oy + 4, "X (світ)", size=12, bold=True, anchor="start"))
    parts.append(arrow(ox, oy, ox, oy - 180, color=LINE, sw=2))
    parts.append(text(ox, oy - 190, "Y (світ)", size=12, bold=True, anchor="middle"))

    # Вектор швидкості робота
    theta_deg = 38
    theta_rad = math.radians(theta_deg)
    vec_len = 140
    vx = ox + vec_len * math.cos(theta_rad)
    vy = oy - vec_len * math.sin(theta_rad)

    parts.append(arrow(ox, oy, vx, vy, color=NEG, sw=3.5))
    parts.append(text(vx + 12, vy - 8, "v (вектор швидкості)", size=13, color=NEG, bold=True, anchor="start"))

    # Проєкції x_dot, y_dot
    parts.append(line(vx, vy, vx, oy, color="#94a3b8", sw=1.5, dash="3,3"))
    parts.append(line(vx, vy, ox, vy, color="#94a3b8", sw=1.5, dash="3,3"))
    parts.append(text(vx, oy + 18, "ẋ = v·cos(θ + β)", size=12, color=INK, bold=True, anchor="middle"))
    parts.append(text(ox - 10, vy, "ẏ = v·sin(θ + β)", size=12, color=INK, bold=True, anchor="end"))

    # Кут курсу theta
    parts.append('<path d="M %d %d A 55 55 0 0 0 %d %d" fill="none" stroke="%s" stroke-width="2"/>'
                 % (ox + 55, oy, ox + 55 * math.cos(theta_rad), oy - 55 * math.sin(theta_rad), INK))
    parts.append(text(ox + 65, oy - 18, "θ + β", size=13, bold=True))

    box_sum, _, _ = textbox(rx, ly + 140,
                            "Диференціальний зв'язок:\n"
                            "ẋ = v·cos(θ + β),  ẏ = v·sin(θ + β)",
                            size=12.5, pad=9, fill="#eff6ff", stroke=NEG, bold=True)
    parts.append(box_sum)

    box_bot, _, _ = textbox(W / 2, H - 25,
                            "Неголономна в'язь обмежує миттєвий простір швидкостей до 2 ступенів (v, δ),\n"
                            "але дозволяє роботу досягти будь-якої точки конфігураційного простору (x, y, θ)",
                            size=12, pad=10, fill=FILL, bold=False)
    parts.append(box_bot)

    render("img/nonholonomic-constraints.svg", W, H, *parts,
           title="Неголономне кінематичне обмеження та розклад швидкостей")


# ── Фігура 4: порівняння методів чисельного інтегрування позиції ───────────────
def fig_integration_comparison():
    W, H = 940, 470
    parts = []

    # Центр дуги повороту
    cx = 470
    cy = 440
    R = 260

    # Початкова точка t0
    a0 = 145
    rad0 = math.radians(a0)
    p0_x = cx + R * math.cos(rad0)
    p0_y = cy - R * math.sin(rad0)

    # Кінцева точна точка t1 (істинна дуга)
    a1 = 75
    rad1 = math.radians(a1)
    p1_x = cx + R * math.cos(rad1)
    p1_y = cy - R * math.sin(rad1)

    # Малюємо істинну дугу кола (Exact Arc)
    parts.append('<path d="M %.1f %.1f A %d %d 0 0 1 %.1f %.1f" fill="none" stroke="%s" stroke-width="4"/>'
                 % (p0_x, p0_y, R, R, p1_x, p1_y, FIELD))
    parts.append(text((p0_x + p1_x) / 2 + 10, (p0_y + p1_y) / 2 - 25, "Істинна дуга (Exact Arc / RK4)", size=13, color=FIELD, bold=True))

    # 1. Прямий Ейлер (Forward Euler): рух по прямій дотичній початкового курсу
    # Дотична в точці p0 має кут a0 - 90 = 55 градусів
    tang_rad = math.radians(a0 - 90)
    arc_len = R * math.radians(a0 - a1)
    euler_x = p0_x + arc_len * math.cos(tang_rad)
    euler_y = p0_y - arc_len * math.sin(tang_rad)

    parts.append(line(p0_x, p0_y, euler_x, euler_y, color=POS, sw=2.5, dash="5,4"))
    parts.append(circle(euler_x, euler_y, 6, fill=POS, stroke=INK))
    parts.append(text(euler_x + 14, euler_y - 6, "Метод Ейлера (1-й порядок)\nдрейф за межі повороту", size=12, color=POS, bold=True, anchor="start"))

    # Вектор помилки Ейлера
    parts.append(arrow(p1_x, p1_y, euler_x, euler_y, color=POS, sw=1.8))
    parts.append(text((p1_x + euler_x) / 2 - 12, (p1_y + euler_y) / 2 - 10, "Помилка O(Δt)", size=11, color=POS, bold=True, anchor="end"))

    # Початкова точка
    parts.append(circle(p0_x, p0_y, 7, fill=INK, stroke=INK))
    parts.append(text(p0_x - 16, p0_y + 20, "Стан (x_0, y_0, θ_0)", size=13, bold=True, anchor="end"))

    # Кінцева точна точка
    parts.append(circle(p1_x, p1_y, 7, fill=FIELD, stroke=INK))
    parts.append(text(p1_x, p1_y - 20, "Точний стан (x_1, y_1, θ_1)", size=13, color=FIELD, bold=True, anchor="middle"))

    # Блоки-порівняння внизу ліворуч і праворуч
    b1, _, _ = textbox(220, 100,
                       "Прямий Ейлер (Forward Euler):\n"
                       "x_{k+1} = x_k + v·cos(θ_k)·Δt\n"
                       "y_{k+1} = y_k + v·sin(θ_k)·Δt\n"
                       "θ_{k+1} = θ_k + ω·Δt\n"
                       "Помилка накопичується на кожному кроці кривини",
                       size=11.5, pad=9, fill="#fef2f2", stroke=POS)
    parts.append(b1)

    b2, _, _ = textbox(720, 100,
                       "Інтегратор кругової дуги (Exact Arc):\n"
                       "Δθ = ω·Δt,  R = v / ω\n"
                       "Δx = R·(sin(θ + Δθ) − sin(θ))\n"
                       "Δy = R·(cos(θ) − cos(θ + Δθ))\n"
                       "Точний результат для постійних v та δ",
                       size=11.5, pad=9, fill="#f0fdf4", stroke=FIELD)
    parts.append(b2)

    box_bot, _, _ = textbox(W / 2, H - 25,
                            "При великих кроках дискретизації Δt простий Ейлер 'вистрілює' по дотичній.\n"
                            "Інтеграція дугою або метод Рунге-Кутти (RK4) зберігають точність траєкторії",
                            size=12, pad=10, fill=FILL, bold=False)
    parts.append(box_bot)

    render("img/integration-comparison.svg", W, H, *parts,
           title="Порівняння схем чисельного інтегрування кінематики")


if __name__ == "__main__":
    fig_bicycle_reduction()
    fig_icr_geometry()
    fig_nonholonomic_constraints()
    fig_integration_comparison()
    print("All figures generated successfully.")
