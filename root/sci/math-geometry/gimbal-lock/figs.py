# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def polyline(pts, color=INK, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (s, color, sw, d))


def dot(x, y, r=4.5, color=INK):
    return '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (x, y, r, color)


def ellipse(cx, cy, rx, ry, fill="none", stroke=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" '
            'stroke="%s" stroke-width="%.1f"%s/>' % (cx, cy, rx, ry, fill, stroke, sw, d))


# ───────────────────────────────────────────────────────────────────────────
# ФІГУРА 1: Складання рамок у 3-осьовому підвісі
# ───────────────────────────────────────────────────────────────────────────
def fig_gimbal_rings():
    W, H = 1020, 520
    frags = []

    # Заголовок панелей
    b1, _, _ = textbox(250, 35, "Нормальний стан: тангаж θ = 0°\nТри незалежні осі обертання (3 DOF)", size=13, bold=True, fill="#eef6ff", stroke=NEG)
    b2, _, _ = textbox(770, 35, "Складання рамок: тангаж θ = +90°\nОсі крену й рискання збіглися (2 DOF)", size=13, bold=True, fill="#fdecea", stroke=POS)
    frags.extend([b1, b2])

    # Розділювальна лінія між панелями
    frags.append(line(510, 15, 510, 505, color=MUTED, sw=1.2, dash="4 4"))

    # Ліва панель: θ = 0°
    c1x, c1y = 250, 270
    # Зовнішнє кільце (Yaw - вісь Z, синє)
    frags.append(ellipse(c1x, c1y, 150, 150, fill="none", stroke=NEG, sw=3.5))
    frags.append(line(c1x, c1y - 175, c1x, c1y + 175, color=NEG, sw=2.0, dash="5 4"))
    frags.append(arrow(c1x, c1y - 165, c1x, c1y - 190, color=NEG, sw=2.5))
    tb_z1, _, _ = textbox(c1x + 85, c1y - 175, "Вісь 1: Рискання (Z)", size=11, bold=True, fill="#ffffff", stroke=NEG)
    frags.append(tb_z1)

    # Середнє кільце (Pitch - вісь Y, зелене, нахил в ізометрії)
    frags.append(ellipse(c1x, c1y, 120, 70, fill="none", stroke=FIELD, sw=3.0))
    frags.append(line(c1x - 145, c1y, c1x + 145, c1y, color=FIELD, sw=2.0, dash="5 4"))
    frags.append(arrow(c1x + 135, c1y, c1x + 160, c1y, color=FIELD, sw=2.5))
    tb_y1, _, _ = textbox(c1x + 125, c1y + 25, "Вісь 2: Тангаж (Y)", size=11, bold=True, fill="#ffffff", stroke=FIELD)
    frags.append(tb_y1)

    # Внутрішнє кільце (Roll - вісь X, червоне, вертикальний еліпс)
    frags.append(ellipse(c1x, c1y, 60, 100, fill="none", stroke=POS, sw=3.0))
    frags.append(line(c1x - 65, c1y + 55, c1x + 65, c1y - 55, color=POS, sw=2.0, dash="5 4"))
    frags.append(arrow(c1x + 55, c1y - 45, c1x + 78, c1y - 65, color=POS, sw=2.5))
    tb_x1, _, _ = textbox(c1x - 110, c1y - 95, "Вісь 3: Крен (X)", size=11, bold=True, fill="#ffffff", stroke=POS)
    frags.append(tb_x1)

    # Центральне тіло
    frags.append(circle(c1x, c1y, 16, fill="#ffffff", stroke=INK, sw=2.0))
    frags.append(dot(c1x, c1y, 4, color=INK))

    tb_sub1, _, _ = textbox(250, 475, "Осі Z, Y, X взаємно перпендикулярні.\nБудь-який 3D поворот компенсується без перешкод.", size=11.5, fill="#f4f6f8")
    frags.append(tb_sub1)

    # Права панель: θ = +90°
    c2x, c2y = 770, 270
    # Зовнішнє кільце (Yaw - вісь Z, синє)
    frags.append(ellipse(c2x, c2y, 150, 150, fill="none", stroke=NEG, sw=3.5))

    # Середнє кільце повернуто на 90° (Pitch)
    frags.append(ellipse(c2x, c2y, 120, 120, fill="none", stroke=FIELD, sw=3.0, dash="6 4"))

    # Внутрішнє кільце лягло в площину зовнішнього!
    frags.append(ellipse(c2x, c2y, 95, 95, fill="none", stroke=POS, sw=3.5))

    # Спільна вісь колінеарності
    frags.append(line(c2x, c2y - 180, c2x, c2y + 180, color=POS, sw=2.8))
    frags.append(arrow(c2x, c2y - 165, c2x, c2y - 192, color=POS, sw=2.8))
    frags.append(arrow(c2x, c2y + 165, c2x, c2y + 192, color=NEG, sw=2.8))

    tb_align, _, _ = textbox(c2x + 110, c2y - 135, "Осі Z (рискання) та X (крен)\nПОВНІСТЮ ЗБІГЛИСЯ!", size=11, bold=True, fill="#fff5f5", stroke=POS)
    frags.append(tb_align)

    # Заблокований ступінь вільності
    frags.append(line(c2x - 130, c2y + 75, c2x + 130, c2y - 75, color=MUTED, sw=2.0, dash="3 3"))
    tb_blocked, _, _ = textbox(c2x - 95, c2y + 115, "ВТРАЧЕНИЙ СТУПІНЬ ВІЛЬНОСТІ:\nповорот навколо цієї осі заклинює підвіс", size=10.5, bold=True, fill="#fffbe6", stroke="#d48800")
    frags.append(tb_blocked)

    # Центральне тіло
    frags.append(circle(c2x, c2y, 16, fill="#ffffff", stroke=INK, sw=2.0))
    frags.append(dot(c2x, c2y, 4, color=POS))

    tb_sub2, _, _ = textbox(770, 475, "Обертання зовнішнього та внутрішнього кілець дають однаковий рух.\nПростір поворотів вироджується з 3D у 2D.", size=11.5, fill="#f4f6f8")
    frags.append(tb_sub2)

    render(os.path.join(IMG, "gimbal-rings-aligned.svg"), W, H, *frags)


# ───────────────────────────────────────────────────────────────────────────
# ФІГУРА 2: Алгебраїчне виродження матриці повороту при тангажі 90°
# ───────────────────────────────────────────────────────────────────────────
def fig_euler_matrix_singularity():
    W, H = 980, 450
    frags = []

    # Загальний заголовок
    t1, _, _ = textbox(490, 35, "Матриця повороту R_ZYX(ψ, θ, φ) та її виродження при θ = +90°", size=15, bold=True, fill="#ffffff", stroke=LINE)
    frags.append(t1)

    # Лівий блок: Загальний вигляд
    lx, ly = 245, 190
    tb_gen_t, _, _ = textbox(lx, 90, "Загальний стан: R_z(ψ) · R_y(θ) · R_x(φ)", size=12.5, bold=True, fill="#eef6ff", stroke=NEG)
    frags.append(tb_gen_t)

    gen_mat_lines = [
        "|  cψ·cθ    cψ·sθ·sφ − sψ·cφ    cψ·sθ·cφ + sψ·sφ  |",
        "|  sψ·cθ    sψ·sθ·sφ + cψ·cφ    sψ·sθ·cφ − cψ·sφ  |",
        "|   −sθ          cθ·sφ               cθ·cφ        |"
    ]
    gen_body = rect(lx - 220, 120, 440, 150, fill="#f8fafc", stroke=LINE, rx=6)
    gen_text = mtext(lx, 160, gen_mat_lines, size=12.5, color=INK, lh=2.0)
    frags.extend([gen_body, gen_text])

    tb_gen_foot, _, _ = textbox(lx, 325, "9 елементів залежать від трьох кутів (ψ, θ, φ).\nВсі три параметри визначаються однозначно.", size=11.5, fill="#ffffff", stroke=MUTED)
    frags.append(tb_gen_foot)

    # Стрілка переходу
    frags.append(line(475, 195, 505, 195, color=POS, sw=3.0))
    frags.append(arrow(495, 195, 515, 195, color=POS, sw=3.0))
    frags.append(text(495, 175, "θ = +π/2", size=12, color=POS, bold=True))
    frags.append(text(495, 218, "cos θ = 0", size=11, color=MUTED))
    frags.append(text(495, 235, "sin θ = 1", size=11, color=MUTED))

    # Правий блок: Вироджений стан
    rx, ry = 735, 190
    tb_sing_t, _, _ = textbox(rx, 90, "Вироджений стан: θ = +90° (Gimbal Lock)", size=12.5, bold=True, fill="#fdecea", stroke=POS)
    frags.append(tb_sing_t)

    sing_mat_lines = [
        "|   0    cos(ψ − φ)    sin(ψ − φ)  |",
        "|   0    sin(ψ − φ)   −cos(ψ − φ)  |",
        "|  −1        0             0       |"
    ]
    sing_body = rect(rx - 200, 120, 400, 150, fill="#fff8f8", stroke=POS, rx=6)
    sing_text = mtext(rx, 160, sing_mat_lines, size=13.5, color=POS, bold=True, lh=2.0)
    frags.extend([sing_body, sing_text])

    tb_sing_foot, _, _ = textbox(rx, 325, "Матриця залежить ЛИШЕ від різниці (ψ − φ)!\nОкремі значення ψ і φ визначити неможливо.", size=11.5, bold=True, fill="#fff5f5", stroke=POS)
    frags.append(tb_sing_foot)

    # Нижній висновок
    bot, _, _ = textbox(490, 405, "Наслідок: нескінченна кількість пар (ψ, φ) дають абсолютно однакову просторову матрицю.\nСпроба відновити окремі кути призводить до невизначеності й ділення на нуль.", size=11.5, fill="#f4f6f8")
    frags.append(bot)

    render(os.path.join(IMG, "euler-singularity-matrix.svg"), W, H, *frags)


# ───────────────────────────────────────────────────────────────────────────
# ФІГУРА 3: Графік вибуху кутових швидкостей Якобіана біля 90°
# ───────────────────────────────────────────────────────────────────────────
def fig_kinematic_divergence():
    W, H = 1040, 480
    frags = []

    # Заголовок
    t1, _, _ = textbox(520, 30, "Кінематична сингулярність: вибух швидкостей рамок dφ/dt та dψ/dt при θ → 90°", size=15, bold=True, fill="#ffffff", stroke=LINE)
    frags.append(t1)

    # Вісь графіка
    gx0, gy0 = 100, 390
    gw, gh = 420, 290

    # Зона небезпеки (75° - 90°)
    x_dang = gx0 + (75.0 / 90.0) * gw
    x_asymp = gx0 + gw
    frags.append(rect(x_dang, gy0 - gh, x_asymp - x_dang, gh, fill="rgba(192, 57, 43, 0.08)", stroke="none"))
    tb_zone, _, _ = textbox(x_dang - 55, gy0 - gh + 50, "Зона нестійкості\n(θ > 75°)", size=10.5, bold=True, fill="#ffffff", stroke=POS)
    frags.append(tb_zone)

    # Сітка
    for i in range(5):
        y = gy0 - (gh / 4) * i
        frags.append(line(gx0, y, gx0 + gw, y, color="#e5e7eb", sw=1.0))
        val_str = "%.1f" % (i * 2.5) if i > 0 else "0"
        frags.append(text(gx0 - 18, y + 4, val_str, size=11, color=MUTED, anchor="end"))

    # Вертикальні лінії для кутів θ: 0°, 30°, 60°, 75°, 85°, 90°
    angles = [(0, "0°"), (30, "30°"), (60, "60°"), (75, "75°"), (85, "85°"), (90, "90° (π/2)")]
    for deg, lbl in angles:
        x = gx0 + (deg / 90.0) * gw
        frags.append(line(x, gy0, x, gy0 - gh, color="#e5e7eb", sw=1.0))
        frags.append(text(x, gy0 + 20, lbl, size=11, color=MUTED, anchor="middle"))

    # Осі X та Y
    frags.append(line(gx0, gy0, gx0 + gw + 20, gy0, color=INK, sw=1.8))
    frags.append(arrow(gx0 + gw + 10, gy0, gx0 + gw + 25, gy0, color=INK, sw=1.8))
    frags.append(text(gx0 + gw + 35, gy0 + 4, "θ", size=13, bold=True, anchor="start"))

    frags.append(line(gx0, gy0, gx0, gy0 - gh - 20, color=INK, sw=1.8))
    frags.append(arrow(gx0, gy0 - gh - 10, gx0, gy0 - gh - 25, color=INK, sw=1.8))
    frags.append(text(gx0 - 10, gy0 - gh - 30, "Коефіцієнт підсилення (1 / cos θ)", size=11.5, bold=True, anchor="middle"))

    # Крива 1 / cos(θ)
    pts = []
    n_steps = 100
    for i in range(n_steps):
        deg = (88.5 * i) / (n_steps - 1)
        rad = math.radians(deg)
        val = 1.0 / math.cos(rad)
        if val > 10.5:
            val = 10.5
        x = gx0 + (deg / 90.0) * gw
        y = gy0 - (val / 10.0) * gh
        pts.append((x, y))

    frags.append(polyline(pts, color=POS, sw=3.2))

    # Асимптота на 90°
    frags.append(line(x_asymp, gy0, x_asymp, gy0 - gh - 15, color=POS, sw=2.0, dash="6 4"))
    tb_asymp, _, _ = textbox(x_asymp - 40, gy0 - gh - 25, "Асимптота θ = 90°: 1/cos θ → ∞", size=10.5, color=POS, bold=True, fill="#ffffff", stroke=POS)
    frags.append(tb_asymp)

    # Правий пояснювальний блок
    bx = 790
    tb_eq, _, _ = textbox(bx, 130, "Кінематичні рівняння Ейлера:\n\n[ dφ/dt ]     [ 1   sin φ·tg θ   cos φ·tg θ ] [ ω_x ]\n[ dθ/dt ]  =  [ 0     cos φ       −sin φ    ] [ ω_y ]\n[ dψ/dt ]     [ 0  sin φ/cos θ  cos φ/cos θ ] [ ω_z ]", size=11.5, fill="#f8fafc", stroke=LINE)
    frags.append(tb_eq)

    tb_desc, _, _ = textbox(bx, 285, "Фізичний парадокс:\n• Апарат обертається з помірною швидкістю ω_z.\n• Проте при θ → 90° знаменник cos θ → 0.\n• Швидкість обертання рамок dψ/dt прямує до ∞!\n• Контролер намагається крутити сервоприводи\n  з нескінченною швидкістю → зрив стабілізації.", size=11, fill="#fff8f8", stroke=POS)
    frags.append(tb_desc)

    tb_bot, _, _ = textbox(bx, 410, "У цифрових системах це викликає NaN / Inf,\nпереповнення буферів інтегрування та втрату керування.", size=11, bold=True, fill="#fff5f5", stroke=POS)
    frags.append(tb_bot)

    render(os.path.join(IMG, "kinematic-jacobian-divergence.svg"), W, H, *frags)


# ───────────────────────────────────────────────────────────────────────────
# ФІГУРА 4: Топологічне порівняння: Кути Ейлера (S2xS1) vs Кватерніони (S3)
# ───────────────────────────────────────────────────────────────────────────
def fig_quaternion_s3_topology():
    W, H = 960, 430
    frags = []

    # Заголовок
    t1, _, _ = textbox(480, 30, "Топологічна природа сингулярності: 3D координати проти 4D гіперсфери S³", size=15, bold=True, fill="#ffffff", stroke=LINE)
    frags.append(t1)

    # Ліва панель: Кути Ейлера (Сингулярна карта)
    lx = 240
    tb_l_tit, _, _ = textbox(lx, 75, "Кути Ейлера (3 параметри: ψ, θ, φ)", size=13, bold=True, fill="#fdecea", stroke=POS)
    frags.append(tb_l_tit)

    # Координатна сітка як циліндр / прямокутник з особливими краями
    frags.append(rect(lx - 160, 110, 320, 180, fill="#fff8f8", stroke=POS, sw=2.0))
    # Лінії полюсів
    frags.append(line(lx - 160, 110, lx + 160, 110, color=POS, sw=3.5))
    frags.append(text(lx, 128, "Сингулярна межа: тангаж θ = +90° (Gimbal Lock)", size=11, color=POS, bold=True))

    frags.append(line(lx - 160, 290, lx + 160, 290, color=POS, sw=3.5))
    frags.append(text(lx, 278, "Сингулярна межа: тангаж θ = −90° (Gimbal Lock)", size=11, color=POS, bold=True))

    # Внутрішня координатна сітка
    for xi in range(1, 4):
        x = lx - 160 + xi * 80
        frags.append(line(x, 110, x, 290, color="#fca5a5", sw=1.2, dash="3 3"))
    frags.append(line(lx - 160, 200, lx + 160, 200, color=FIELD, sw=1.8))
    frags.append(text(lx + 85, 192, "Екватор: θ = 0°", size=11, color=FIELD, bold=True))

    tb_l_desc, _, _ = textbox(lx, 360, "Теорема топології: простір обертань SO(3) ≅ RP³\nнеможливо покрити трьома глобальними координатами\nбез сингулярних точок або розривів (як і сферу S²).", size=11.5, fill="#ffffff", stroke=MUTED)
    frags.append(tb_l_desc)

    # Розділювач
    frags.append(line(480, 60, 480, 410, color=MUTED, sw=1.2, dash="4 4"))

    # Права панель: Кватерніони на S3
    rx = 720
    tb_r_tit, _, _ = textbox(rx, 75, "Одиничні кватерніони (Гіперсфера S³ ⊂ ℝ⁴)", size=13, bold=True, fill="#eef6ff", stroke=NEG)
    frags.append(tb_r_tit)

    # 3D проекція гіперсфери
    frags.append(circle(rx, 200, 85, fill="#f0fdf4", stroke=FIELD, sw=2.5))
    frags.append(ellipse(rx, 200, 85, 30, fill="none", stroke=FIELD, sw=1.5, dash="4 3"))

    # Точки q та -q
    frags.append(dot(rx - 45, 175, 6, color=NEG))
    frags.append(text(rx - 55, 165, "+q", size=13, bold=True, color=NEG))

    frags.append(dot(rx + 45, 225, 6, color=NEG))
    frags.append(text(rx + 58, 235, "−q", size=13, bold=True, color=NEG))

    # Стрілка зв'язку подвійного накриття
    frags.append(line(rx - 40, 180, rx + 40, 220, color=MUTED, sw=1.5, dash="3 3"))
    tb_cover, _, _ = textbox(rx, 200, "Подвійне накриття:\n+q та −q задають\nтой самий поворот", size=10.5, bold=True, fill="#ffffff", stroke=NEG)
    frags.append(tb_cover)

    tb_r_desc, _, _ = textbox(rx, 360, "Гіперсфера S³ є компактним гладким многовидом без меж.\nКінематика dq/dt = ½ q ⊗ ω є лінійною і строго регулярною:\nЖОДНИХ полюсів, кутів складання чи ділення на нуль!", size=11.5, bold=True, fill="#f0fdf4", stroke=FIELD)
    frags.append(tb_r_desc)

    render(os.path.join(IMG, "quaternion-s3-cover.svg"), W, H, *frags)


# ───────────────────────────────────────────────────────────────────────────
# ФІГУРА 5: Блок-схема безпечного алгоритму витягання кутів з кватерніона
# ───────────────────────────────────────────────────────────────────────────
def fig_safe_euler_algorithm():
    W, H = 980, 520
    frags = []

    # Заголовок
    t1, _, _ = textbox(490, 30, "Алгоритм безпечного витягання кутів Ейлера з кватерніона (Безпечний Z-Y-X)", size=15, bold=True, fill="#ffffff", stroke=LINE)
    frags.append(t1)

    # Крок 1: Вхідний кватерніон
    b_in, _, _ = textbox(490, 80, "Вхід: нормований кватерніон q = (w, x, y, z), де |q| = 1", size=13, bold=True, fill="#f8fafc", stroke=LINE)
    frags.append(b_in)
    frags.append(arrow(490, 100, 490, 130, color=LINE, sw=2.0))

    # Крок 2: Обчислення аргументу синуса тангажу
    b_calc, _, _ = textbox(490, 155, "Обчислення параметра тангажу:\ns = 2 · (w·y − x·z)", size=13, bold=True, fill="#eef6ff", stroke=NEG)
    frags.append(b_calc)
    frags.append(arrow(490, 180, 490, 210, color=LINE, sw=2.0))

    # Крок 3: Захисний clamp
    b_clamp, _, _ = textbox(490, 235, "Захист від похибок float: s_safe = clamp(s, −1.0, 1.0)", size=12.5, fill="#f0fdf4", stroke=FIELD)
    frags.append(b_clamp)
    frags.append(arrow(490, 260, 490, 290, color=LINE, sw=2.0))

    # Крок 4: Розгалуження детекції сингулярності
    b_cond, _, _ = textbox(490, 320, "Умова сингулярності (Gimbal Lock):\n|s_safe| ≥ 1.0 − ε   (де ε ≈ 10⁻⁶)?", size=13, bold=True, fill="#fffbe6", stroke="#d48800")
    frags.append(b_cond)

    # Стрілка Вправо (ТАК: Сингулярність)
    frags.append(line(635, 320, 770, 320, color=POS, sw=2.2))
    frags.append(arrow(760, 320, 780, 320, color=POS, sw=2.2))
    frags.append(text(700, 310, "ТАК (Gimbal Lock)", size=12, bold=True, color=POS))

    # Стрілка Вліво (НІ: Регулярний стан)
    frags.append(line(345, 320, 210, 320, color=FIELD, sw=2.2))
    frags.append(arrow(220, 320, 200, 320, color=FIELD, sw=2.2))
    frags.append(text(280, 310, "НІ (Регулярно)", size=12, bold=True, color=FIELD))

    # Блок РЕГУЛЯРНОГО обчислення (Зліва)
    reg_lines = [
        "Тангаж:  θ = asin(s_safe)",
        "Крен:    φ = atan2(2(w·x + y·z), 1 − 2(x² + y²))",
        "Рискання: ψ = atan2(2(w·z + x·y), 1 − 2(y² + z²))"
    ]
    b_reg, _, _ = textbox(200, 415, "\n".join(reg_lines), size=12, fill="#f0fdf4", stroke=FIELD)
    frags.append(b_reg)

    # Блок СИНГУЛЯРНОГО обчислення (Справа)
    sing_lines = [
        "Тангаж:  θ = copysign(π / 2, s_safe)",
        "Крен:    φ = 0.0  (фіксація свободи)",
        "Рискання: ψ = −2 · sign(s_safe) · atan2(x, w)"
    ]
    b_sing, _, _ = textbox(780, 415, "\n".join(sing_lines), size=12, bold=True, fill="#fff8f8", stroke=POS)
    frags.append(b_sing)

    # Фінальні стрілки вниз
    frags.append(line(200, 465, 200, 485, color=FIELD, sw=1.8))
    frags.append(line(780, 465, 780, 485, color=POS, sw=1.8))
    frags.append(line(200, 485, 780, 485, color=LINE, sw=1.8))
    frags.append(arrow(490, 485, 490, 505, color=LINE, sw=2.2))

    b_out, _, _ = textbox(490, 505, "Результат: однозначні й неперервні кути (φ, θ, ψ) без падінь і NaN", size=12, bold=True, fill="#f8fafc", stroke=LINE)
    frags.append(b_out)

    render(os.path.join(IMG, "safe-euler-extraction-flow.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_gimbal_rings()
    fig_euler_matrix_singularity()
    fig_kinematic_divergence()
    fig_quaternion_s3_topology()
    fig_safe_euler_algorithm()
    print("All figures generated successfully.")
