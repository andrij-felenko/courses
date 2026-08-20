# -*- coding: utf-8 -*-
"""Фігури до статті «Група SO(3) і її подвійне покриття SU(2)»."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_so3_lie_algebra():
    """Фігура 1: Група Лі SO(3), дотична алгебра Лі so(3) та експоненційне відображення."""
    W, H = 820, 440
    fr = []

    # 1. Заголовок
    fr.append(text(W / 2, 28, "Група Лі SO(3) і дотична алгебра Лі so(3)", size=17, bold=True))

    # 2. Ліва частина: многовид SO(3) та дотичний простір
    # Багатокутник многовиду (вигнута поверхня)
    m_pts = "90,320 C 120,180 240,160 380,210 C 440,230 420,380 340,400 C 220,430 80,390 90,320"
    fr.append('<path d="%s" fill="#eef2f7" stroke="#2457d6" stroke-width="2"/>' % m_pts)
    fr.append(text(350, 360, "Многовид SO(3)", size=14, color=NEG, bold=True))
    fr.append(text(350, 380, "Rᵀ R = I, det(R) = +1", size=12, color=MUTED))

    # Дотична площина у точці I (нейтральний елемент)
    t_pts = "130,190 L 320,130 L 390,210 L 200,270 Z"
    fr.append('<polygon points="%s" fill="#fdf2e9" stroke="#c0392b" stroke-width="1.8" fill-opacity="0.85"/>' % t_pts)
    fr.append(text(325, 155, "Дотичний простір: алгебра so(3)", size=13, color=POS, bold=True))

    # Точка I (тотожне перетворення)
    ix, iy = 220, 210
    fr.append(circle(ix, iy, 4.5, fill=INK, stroke=INK, sw=1.5))
    fr.append(text(ix - 16, iy + 6, "I", size=15, bold=True))

    # Дотичний вектор у площині: Omega = [omega]_x
    vx, vy = 310, 175
    fr.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2.5" marker-end="url(#arrow)"/>' % (ix, iy, vx, vy, POS))
    fr.append(text(vx - 10, vy - 12, "Ω = [ω]ₓ ∈ so(3)", size=13, color=POS, bold=True))

    # Траєкторія на многовиді: exp(t * Omega)
    traj = "M 220,210 C 250,235 280,260 305,295"
    fr.append('<path d="%s" fill="none" stroke="#27ae60" stroke-width="2.8" marker-end="url(#arrow)"/>' % traj)
    fr.append(text(285, 320, "R(t) = exp(t Ω)", size=13, color=FIELD, bold=True))

    # Пояснення стрілки exp: дуга від вектора до многовиду
    fr.append('<path d="M 285,185 C 295,210 290,230 270,245" fill="none" stroke="#6b7280" stroke-width="1.5" stroke-dasharray="4 3" marker-end="url(#arrow)"/>' % ())
    fr.append(text(315, 230, "exp(·)", size=13, color=MUTED, italic=True))

    # 3. Права частина: ізоморфізм дужки Лі та векторного добутку
    rx, ry, rw, rh = 470, 65, 320, 345
    fr.append(rect(rx, ry, rw, rh, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    fr.append(text(rx + rw/2, ry + 26, "Алгебра Лі та векторний добуток", size=15, bold=True))

    # Властивості матриць so(3)
    b1, _, _ = textbox(rx + rw/2, ry + 75, "Антисиметричні 3×3 матриці:\nΩᵀ = −Ω   (3 ступені свободи)", size=12, pad=8, fill="#ffffff", stroke="#9ca3af", min_w=280)
    fr.append(b1)

    # Капелюшкове відображення (hat map)
    b2, _, _ = textbox(rx + rw/2, ry + 155, "Ізоморфізм просторів ℝ³ ≅ so(3):\nω = (ω₁, ω₂, ω₃)ᵀ  ↦  [ω]ₓ\n[ω]ₓ v = ω × v", size=12, pad=8, fill="#ffffff", stroke="#9ca3af", min_w=280)
    fr.append(b2)

    # Дужка Лі та комутатор
    b3, _, _ = textbox(rx + rw/2, ry + 245, "Дужка Лі = матричний комутатор:\n[A, B] = A·B − B·A\n[[u]ₓ, [v]ₓ] = [u × v]ₓ", size=12, pad=8, fill="#fdf2e9", stroke=POS, min_w=280)
    fr.append(b3)

    # Генератори
    fr.append(text(rx + rw/2, ry + 315, "Базис генераторів: [J_x, J_y] = J_z", size=12, color=INK, bold=True))

    render(os.path.join(OUT, "so3-lie-algebra.svg"), W, H, *fr)


def fig_so3_rp3_topology():
    """Фігура 2: Топологія SO(3) як кулі радіуса π з ототожненням антиподів (ℝP³)."""
    W, H = 820, 430
    fr = []

    fr.append(text(W / 2, 28, "Топологія SO(3): куля радіуса π з ототожненням антиподів (ℝP³)", size=17, bold=True))

    # Ліва частина: 3D куля радіуса pi
    cx, cy, r = 230, 235, 135

    # Заливка кулі та коло межі
    fr.append(circle(cx, cy, r, fill="#f4f6f8", stroke="#2457d6", sw=2.2))
    # Екваторіальний еліпс для об'єму (пунктир ззаду, суцільний спереду)
    fr.append('<path d="M %d,%d A %d,%d 0 0 1 %d,%d" fill="none" stroke="#9ca3af" stroke-width="1.4" stroke-dasharray="4 3"/>' % (cx - r, cy, r, 45, cx + r, cy))
    fr.append('<path d="M %d,%d A %d,%d 0 0 0 %d,%d" fill="none" stroke="#9ca3af" stroke-width="1.4"/>' % (cx - r, cy, r, 45, cx + r, cy))

    # Центр (нульовий поворот, I)
    fr.append(circle(cx, cy, 4.5, fill=INK, stroke=INK, sw=1.5))
    fr.append(text(cx - 16, cy + 5, "I (θ=0)", size=12, bold=True))

    # Радіус pi - ведемо горизонтально ліворуч, щоб не перетинати шлях
    fr.append(line(cx, cy, cx - r, cy, color=MUTED, sw=1.5, dash="3 3"))
    fr.append(text(cx - r/2, cy - 8, "радіус = π", size=11, color=MUTED, italic=True))

    # Антиподальні точки на межі theta = pi
    p1x, p1y = cx + int(r * 0.5), cy - int(r * 0.866)
    p2x, p2y = cx - int(r * 0.5), cy + int(r * 0.866)
    fr.append(circle(p1x, p1y, 5.5, fill=POS, stroke=POS, sw=1.5))
    fr.append(circle(p2x, p2y, 5.5, fill=POS, stroke=POS, sw=1.5))
    fr.append(text(p1x + 12, p1y - 6, "+π u", size=13, color=POS, bold=True, anchor="start"))
    fr.append(text(p2x - 12, p2y + 16, "−π u ≡ +π u", size=13, color=POS, bold=True, anchor="end"))

    # Ототожнення межі (дуга зі стрілками)
    fr.append('<path d="M %d,%d C %d,%d %d,%d %d,%d" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="4 3"/>' %
              (p1x + 10, p1y, cx + r + 35, cy - 40, cx + r + 35, cy + 40, p2x + 10, p2y, POS))
    fr.append(text(cx + r + 30, cy, "Ототожнено!", size=12, color=POS, bold=True, anchor="start"))

    # Шлях 1: 360-градусний поворот (від I до +pi u, стрибок у -pi u, повернення до I)
    fr.append('<path d="M %d,%d L %d,%d" fill="none" stroke="%s" stroke-width="2.5" marker-end="url(#arrow)"/>' % (cx, cy, p1x - 3, p1y + 5, FIELD))
    fr.append('<path d="M %d,%d L %d,%d" fill="none" stroke="%s" stroke-width="2.5" marker-end="url(#arrow)"/>' % (p2x + 3, p2y - 5, cx - 2, cy + 3, FIELD))
    fr.append(text(cx + 45, cy - 40, "Шлях поворотів (360°)", size=11, color=FIELD, bold=True, anchor="start"))

    # Права частина: фундаментальна група pi_1(SO(3)) = Z_2
    rx, ry, rw, rh = 470, 65, 320, 345
    fr.append(rect(rx, ry, rw, rh, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    fr.append(text(rx + rw/2, ry + 26, "Фундаментальна група π₁(SO(3)) ≅ ℤ₂", size=14, bold=True))

    # Блок 1: Петля 360 градусів
    b1, _, _ = textbox(rx + rw/2, ry + 85, "Петля 1: поворот на 360° (2π)\n• Йде від I до межі +π u\n• Стрибає в антипод −π u\n• Повертається в I\n✖ Не стягується в точку!", size=12, pad=8, fill="#fdf2e9", stroke=POS, min_w=280)
    fr.append(b1)

    # Блок 2: Петля 720 градусів
    b2, _, _ = textbox(rx + rw/2, ry + 205, "Петля 2: поворот на 720° (4π)\n• Проходить петлю 1 двічі\n• Утворює подвійну траєкторію\n✔ Неперервно стягується в точку I!\nπ₁(SO(3)) має рівно 2 класи (ℤ₂)", size=12, pad=8, fill="#eafaf1", stroke=FIELD, min_w=280)
    fr.append(b2)

    # Висновок про зв'язність
    fr.append(text(rx + rw/2, ry + 300, "SO(3) не є однозв'язною!", size=13, color=POS, bold=True))
    fr.append(text(rx + rw/2, ry + 322, "Універсальне накриття: SU(2) ≅ S³", size=12, color=MUTED))

    render(os.path.join(OUT, "so3-rp3-topology.svg"), W, H, *fr)


def fig_su2_double_cover():
    """Фігура 3: Подвійне покриття SU(2) -> SO(3) і трюк Дірака."""
    W, H = 820, 440
    fr = []

    fr.append(text(W / 2, 28, "Подвійне покриття 2-до-1: SU(2) ≅ S³  →  SO(3) ≅ ℝP³", size=17, bold=True))

    # Ліва колонка: SU(2) - сфера S3
    sx, sy, sr = 190, 220, 110
    fr.append(circle(sx, sy, sr, fill="#eaf0fd", stroke="#2457d6", sw=2))
    # Еліпси для сфери S3
    fr.append('<ellipse cx="%d" cy="%d" rx="%d" ry="32" fill="none" stroke="#93c5fd" stroke-width="1.4"/>' % (sx, sy, sr))
    fr.append(text(sx, sy - sr - 18, "Група SU(2) (сфера S³)", size=15, color=NEG, bold=True))
    fr.append(text(sx, sy - sr - 2, "Одиничні кватерніони |q| = 1", size=12, color=MUTED))

    # Дві антиподальні точки +q та -q
    q1x, q1y = sx, sy - 55
    q2x, q2y = sx, sy + 55
    fr.append(circle(q1x, q1y, 6, fill=POS, stroke=POS, sw=1.5))
    fr.append(circle(q2x, q2y, 6, fill=POS, stroke=POS, sw=1.5))
    fr.append(text(q1x + 14, q1y + 4, "+q  (+I у нулі)", size=13, color=POS, bold=True, anchor="start"))
    fr.append(text(q2x + 14, q2y + 4, "−q  (−I після 360°)", size=13, color=POS, bold=True, anchor="start"))

    # З'єднувальна пунктирна лінія між антиподами
    fr.append(line(q1x, q1y + 6, q2x, q2y - 6, color=POS, sw=1.5, dash="4 3"))

    # Права колонка: SO(3)
    rx, ry, rr = 610, 220, 100
    fr.append(circle(rx, ry, rr, fill="#fdf2e9", stroke="#c0392b", sw=2))
    fr.append('<ellipse cx="%d" cy="%d" rx="%d" ry="28" fill="none" stroke="#fca5a5" stroke-width="1.4"/>' % (rx, ry, rr))
    fr.append(text(rx, ry - rr - 18, "Група поворотів SO(3)", size=15, color=POS, bold=True))
    fr.append(text(rx, ry - rr - 2, "Многовид орієнтацій ℝP³", size=12, color=MUTED))

    # Одна точка R у SO(3)
    r_pt_x, r_pt_y = rx, ry
    fr.append(circle(r_pt_x, r_pt_y, 6, fill=INK, stroke=INK, sw=1.5))
    fr.append(text(r_pt_x, r_pt_y - 14, "R(q) ∈ SO(3)", size=14, bold=True))

    # Стрілки відображення 2-до-1: Phi(q) = Phi(-q) = R
    fr.append('<path d="M %d,%d C %d,%d %d,%d %d,%d" fill="none" stroke="%s" stroke-width="2.4" marker-end="url(#arrow)"/>' %
              (q1x + 40, q1y, 380, 150, 450, 180, r_pt_x - 12, r_pt_y - 6, POS))
    fr.append('<path d="M %d,%d C %d,%d %d,%d %d,%d" fill="none" stroke="%s" stroke-width="2.4" marker-end="url(#arrow)"/>' %
              (q2x + 40, q2y, 380, 290, 450, 260, r_pt_x - 12, r_pt_y + 6, POS))

    fr.append(text(400, 195, "Гомоморфізм Φ", size=14, bold=True))
    fr.append(text(400, 215, "2-до-1 покриття", size=12, color=MUTED))
    fr.append(text(400, 235, "ker(Φ) = {+I, −I}", size=12, color=POS, bold=True))

    # Нижня плашка: фізичний сенс і трюк Дірака
    bx, by, bw, bh = 60, 360, 700, 60
    fr.append(rect(bx, by, bw, bh, fill="#ffffff", stroke="#9ca3af", sw=1.5, rx=6))
    fr.append(text(bx + bw/2, by + 22, "Трюк Дірака з ременем: поворот на 360° міняє знак стану (q ↦ −q),", size=12, color=INK, bold=True))
    fr.append(text(bx + bw/2, by + 42, "а повний поворот на 720° повертає кватерніон і топологічний стан до початкового (+q).", size=12, color=INK))

    render(os.path.join(OUT, "su2-double-cover.svg"), W, H, *fr)


def fig_gimbal_lock_vs_slerp():
    """Фігура 4: Карданне заклинювання в кутах Ейлера проти інтерполяції SLERP на S³."""
    W, H = 820, 440
    fr = []

    fr.append(text(W / 2, 28, "Карданне заклинювання (Gimbal Lock) проти інтерполяції SLERP", size=17, bold=True))

    # Ліва панель: Карданне заклинювання (Euler angles)
    lx, ly, lw, lh = 40, 60, 350, 355
    fr.append(rect(lx, ly, lw, lh, fill="#fdf2e9", stroke=POS, sw=1.8, rx=8))
    fr.append(text(lx + lw/2, ly + 26, "Кути Ейлера: Карданне заклинювання", size=14, color=POS, bold=True))

    # Три кільця кардана
    kcx, kcy = lx + lw/2, ly + 140
    # Зовнішнє кільце (Yaw)
    fr.append('<ellipse cx="%d" cy="%d" rx="75" ry="75" fill="none" stroke="#2457d6" stroke-width="3"/>' % (kcx, kcy))
    fr.append(text(kcx, kcy - 82, "Зовнішнє кільце (Курс/Yaw)", size=11, color=NEG, bold=True))

    # Середнє кільце під 90 градусів (Pitch = 90)
    fr.append('<ellipse cx="%d" cy="%d" rx="55" ry="12" fill="none" stroke="#c0392b" stroke-width="3"/>' % (kcx, kcy))
    fr.append(text(kcx + 80, kcy + 4, "Тангаж = 90°", size=11, color=POS, bold=True, anchor="start"))

    # Внутрішнє кільце (Roll) - тепер співвісне із зовнішнім!
    fr.append('<ellipse cx="%d" cy="%d" rx="40" ry="40" fill="none" stroke="#27ae60" stroke-width="2.5" stroke-dasharray="5 3"/>' % (kcx, kcy))
    fr.append(text(kcx, kcy + 60, "Внутрішнє кільце (Крен/Roll)", size=11, color=FIELD, bold=True))

    # Вісь заклинювання
    fr.append(line(kcx, kcy - 95, kcx, kcy + 95, color=POS, sw=2, dash="4 3"))
    fr.append(text(kcx + 10, kcy - 45, "Осі збіглися!", size=12, color=POS, bold=True, anchor="start"))

    # Пояснення вади
    b_eul, _, _ = textbox(lx + lw/2, ly + 285, "Тангаж θ = ±90° вироджує матрицю:\nКрен і курс крутять навколо ОДНІЄЇ осі.\nВтрачено 1 ступінь свободи!\nШвидкості кутів прямують до ∞.", size=11, pad=6, fill="#ffffff", stroke=POS, min_w=310)
    fr.append(b_eul)

    # Права панель: SLERP у групі SU(2) / кватерніонах
    rx, ry, rw, rh = 430, 60, 350, 355
    fr.append(rect(rx, ry, rw, rh, fill="#eafaf1", stroke=FIELD, sw=1.8, rx=8))
    fr.append(text(rx + rw/2, ry + 26, "Кватерніони: Інтерполяція SLERP на S³", size=14, color=FIELD, bold=True))

    # Сфера S3 з геодезичною дугою
    scx, scy, srad = rx + rw/2, ry + 140, 75
    fr.append(circle(scx, scy, srad, fill="#ffffff", stroke="#9ca3af", sw=1.5))
    fr.append('<ellipse cx="%d" cy="%d" rx="%d" ry="22" fill="none" stroke="#d1d5db" stroke-width="1.2"/>' % (scx, scy, srad))

    # Точки q1 і q2
    q1_x, q1_y = scx - 48, scy + 25
    q2_x, q2_y = scx + 45, scy - 30
    fr.append(circle(q1_x, q1_y, 5, fill=POS, stroke=POS, sw=1.5))
    fr.append(circle(q2_x, q2_y, 5, fill=FIELD, stroke=FIELD, sw=1.5))
    fr.append(text(q1_x - 10, q1_y + 16, "q₁", size=13, color=POS, bold=True))
    fr.append(text(q2_x + 10, q2_y - 8, "q₂", size=13, color=FIELD, bold=True))

    # Геодезична дуга (найкоротший шлях на сфері)
    fr.append('<path d="M %d,%d A %d,%d 0 0 1 %d,%d" fill="none" stroke="#27ae60" stroke-width="3" marker-end="url(#arrow)"/>' %
              (q1_x, q1_y, srad, srad, q2_x, q2_y))
    fr.append(text(scx - 8, scy - 12, "q(t) = Slerp(q₁, q₂, t)", size=11, color=FIELD, bold=True))

    # Пояснення переваг
    b_slp, _, _ = textbox(rx + rw/2, ry + 285, "Геодезичний рух уздовж великого кола:\n✔ Стала кутова швидкість (ω = const)\n✔ Жодних сингулярностей чи заклинювань\n✔ Найкоротший шлях (вибір знаку q₁·q₂ ≥ 0)\nПлавний рух камер і маніпуляторів.", size=11, pad=6, fill="#ffffff", stroke=FIELD, min_w=310)
    fr.append(b_slp)

    render(os.path.join(OUT, "gimbal-lock-vs-slerp.svg"), W, H, *fr)


if __name__ == '__main__':
    fig_so3_lie_algebra()
    fig_so3_rp3_topology()
    fig_su2_double_cover()
    fig_gimbal_lock_vs_slerp()
    print("Всі фігури згенеровано успішно.")
