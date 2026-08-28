# -*- coding: utf-8 -*-
"""figs.py — генератор SVG-фігур для теми «Піддатливе керування: сила замість положення».
svgkit імпортуємо зі scripts/, вивід у ./img/."""
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

TOPIC_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(TOPIC_DIR, "img")
os.makedirs(IMG_DIR, exist_ok=True)


# ── Фігура 1: Жорсткий позиційний контакт проти піддатливого ──────────────────
def fig_rigid_vs_compliant():
    W, H = 960, 480
    parts = []

    # Заголовок секцій
    parts.append(text(240, 30, "Жорсткий позиційний контур (PID)", size=15, bold=True))
    parts.append(text(240, 50, "геометрична похибка спричиняє руйнівне контактне зусилля", size=11.5, color=MUTED))

    parts.append(text(720, 30, "Піддатливий контур (імпеданс / адмітанс)", size=15, bold=True))
    parts.append(text(720, 50, "похибка перетворюється на безпечну пружну деформацію", size=11.5, color=MUTED))

    # Вертикальний роздільник
    parts.append(line(480, 20, 480, 460, color="#e2e8f0", sw=1.5, dash="6,6"))

    # ── ЛІВА ПАНЕЛЬ: Жорсткий контакт ──
    lx = 170
    wall_y = 290

    # Поверхня перешкоди (тверда стінка)
    parts.append(rect(40, wall_y, 400, 24, fill="#cbd5e1", stroke=INK, sw=1.5))
    for sx in range(50, 440, 24):
        parts.append(line(sx, wall_y + 24, sx + 16, wall_y + 40, color="#94a3b8", sw=1.2))
    parts.append(text(240, wall_y + 58, "Тверде довкілля (K_env ≈ 10⁶ Н/м)", size=11.5, color=MUTED, bold=True))

    # Бажана позиція
    des_y = wall_y + 40
    parts.append(line(50, des_y, 300, des_y, color=NEG, sw=1.5, dash="4,4"))
    parts.append(text(305, des_y + 4, "x_d (бажана)", size=11, color=NEG, anchor="start", bold=True))

    # Шток робота
    tool_w = 40
    parts.append(rect(lx - 26, 75, 52, 20, fill="#e2e8f0", stroke=INK, sw=1.5, rx=3))
    parts.append(text(lx, 89, "Шпиндель", size=9.5, bold=True))
    parts.append(rect(lx - tool_w / 2, 95, tool_w, wall_y - 95, fill="#f8fafc", stroke=INK, sw=1.8, rx=4))

    # Вимірювальна лінія деформації Δx
    parts.append(line(75, wall_y, 75, des_y, color=POS, sw=2))
    parts.append(line(69, wall_y, 81, wall_y, color=POS, sw=2))
    parts.append(line(69, des_y, 81, des_y, color=POS, sw=2))
    parts.append(text(88, (wall_y + des_y) / 2 + 4, "Δx = 0.5 мм", size=11, color=POS, anchor="start", bold=True))

    # Стрілка колосальної сили реакції
    parts.append(arrow(lx, wall_y - 10, lx, 120, color=POS, sw=3.5))

    # Текстовий блок попередження праворуч від штока
    b1, _, _ = textbox(335, 185, "F_ext = K_env · Δx\nF > 2000 Н\nСтрумове відсікання\nЗріз зубів редуктора", size=11.5, pad=8, fill="#fee2e2", stroke=POS, bold=True)
    parts.append(b1)


    # ── ПРАВА ПАНЕЛЬ: Піддатливий контакт ──
    rx = 630

    # Поверхня перешкоди
    parts.append(rect(520, wall_y, 400, 24, fill="#cbd5e1", stroke=INK, sw=1.5))
    for sx in range(530, 920, 24):
        parts.append(line(sx, wall_y + 24, sx + 16, wall_y + 40, color="#94a3b8", sw=1.2))
    parts.append(text(720, wall_y + 58, "Тверде довкілля (K_env ≈ 10⁶ Н/м)", size=11.5, color=MUTED, bold=True))

    # Бажана траєкторія
    parts.append(line(530, des_y, 770, des_y, color=NEG, sw=1.5, dash="4,4"))
    parts.append(text(775, des_y + 4, "x_d (бажана)", size=11, color=NEG, anchor="start", bold=True))

    # Верхній тримач
    parts.append(rect(rx - 30, 75, 60, 22, fill="#f8fafc", stroke=INK, sw=1.8, rx=3))
    parts.append(text(rx, 90, "Шпиндель", size=9.5, bold=True))

    # Пружина ліворуч (зигзаг)
    spring_top = 97
    spring_bot = 195
    n_coils = 4
    coil_h = (spring_bot - spring_top) / n_coils
    pts = ["%.1f,%.1f" % (rx - 15, spring_top)]
    for i in range(n_coils):
        y1 = spring_top + (i + 0.25) * coil_h
        y2 = spring_top + (i + 0.75) * coil_h
        pts.append("%.1f,%.1f" % (rx - 25, y1))
        pts.append("%.1f,%.1f" % (rx - 5, y2))
    pts.append("%.1f,%.1f" % (rx - 15, spring_bot))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts), FIELD))
    parts.append(text(rx - 38, (spring_top + spring_bot) / 2 + 4, "K_d", size=11.5, color=FIELD, bold=True))

    # Демпфер праворуч
    dx = rx + 16
    parts.append(line(dx, spring_top, dx, spring_top + 25, color=INK, sw=1.8))
    parts.append(line(dx - 8, spring_top + 25, dx + 8, spring_top + 25, color=INK, sw=2.2))
    parts.append(line(dx - 11, spring_top + 15, dx - 11, spring_bot - 10, color=INK, sw=1.8))
    parts.append(line(dx + 11, spring_top + 15, dx + 11, spring_bot - 10, color=INK, sw=1.8))
    parts.append(line(dx - 11, spring_bot - 10, dx + 11, spring_bot - 10, color=INK, sw=1.8))
    parts.append(line(dx, spring_bot - 10, dx, spring_bot, color=INK, sw=1.8))
    parts.append(text(rx + 38, (spring_top + spring_bot) / 2 + 4, "B_d", size=11.5, color=MUTED, bold=True))

    # Нижня частина (кінцевик TCP)
    parts.append(rect(rx - tool_w / 2, spring_bot, tool_w, wall_y - spring_bot, fill="#dcfce7", stroke=FIELD, sw=1.8, rx=4))

    # Керована сила (стрілка)
    parts.append(arrow(rx, wall_y - 8, rx, 220, color=FIELD, sw=2.5))

    # Текстовий блок праворуч
    b2, _, _ = textbox(815, 185, "F_ext = K_d · (x_d − x) + B_d · ẋ\nF_ext = 25 Н (задане зусилля)\nМ'який контакт без ривка\nБезпечна взаємодія", size=11.5, pad=8, fill="#f0fdf4", stroke=FIELD, bold=True)
    parts.append(b2)

    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
           '<rect width="100%%" height="100%%" fill="%s"/>\n%s\n</svg>'
           % (W, H, W, H, BG, "\n".join(parts)))
    with open(os.path.join(IMG_DIR, "fig-rigid-vs-compliant-contact.svg"), "w", encoding="utf-8") as f:
        f.write(svg)


# ── Фігура 2: Імпедансне проти Адмітансного керування ─────────────────────────
def fig_impedance_vs_admittance():
    W, H = 960, 500
    parts = []

    # ── ВЕРХНЯ ЧАСТИНА: Імпедансне керування ──
    parts.append(text(480, 24, "Імпедансне керування: Похибка руху → Зусилля двигунів", size=15, bold=True))
    parts.append(text(480, 44, "робот формує імпеданс, підходить для двигунів прямого приводу та FOC з низьким тертям", size=11, color=MUTED))

    # Блоки верхнього контуру
    # 1. Траєкторія x_d
    b_traj, _, _ = textbox(90, 100, "Бажана траєкторія\nx_d(t), ẋ_d(t)", size=11, pad=7, fill="#eff6ff", stroke=NEG)
    parts.append(b_traj)
    parts.append(arrow(165, 100, 205, 100, color=INK, sw=1.5))

    # Суматор похибки
    parts.append(circle(215, 100, 10, fill=BG, stroke=INK, sw=1.5))
    parts.append(text(215, 104, "Σ", size=11, bold=True))
    parts.append(arrow(225, 100, 265, 100, color=INK, sw=1.5))
    parts.append(text(245, 88, "e, ė", size=10, color=MUTED))

    # 2. Віртуальний імпеданс
    b_imp, _, _ = textbox(345, 100, "Віртуальний імпеданс\nM_d·ë + B_d·ė + K_d·e", size=11, pad=8, fill="#f0fdf4", stroke=FIELD, bold=True)
    parts.append(b_imp)
    parts.append(arrow(425, 100, 475, 100, color=INK, sw=1.5))
    parts.append(text(450, 88, "F_cmd", size=10.5, color=FIELD, bold=True))

    # 3. Транспонований Якобіан J^T
    b_jac, _, _ = textbox(545, 100, "Матриця Якобі\nτ = Jᵀ(q)·F_cmd + g(q)", size=11, pad=8, fill="#faf5ff", stroke="#8b5cf6")
    parts.append(b_jac)
    parts.append(arrow(615, 100, 665, 100, color=INK, sw=1.5))
    parts.append(text(640, 88, "τ_cmd", size=10.5, color="#8b5cf6", bold=True))

    # 4. Мотори і механіка робота
    b_bot, _, _ = textbox(735, 100, "Механіка робота\nі приводи (FOC)", size=11, pad=8, fill="#f8fafc", stroke=INK)
    parts.append(b_bot)
    parts.append(arrow(805, 100, 875, 100, color=INK, sw=1.5))
    parts.append(text(840, 88, "x, ẋ", size=10, color=INK))

    # Зворотний зв'язок за положенням
    parts.append(line(875, 100, 875, 155, color=INK, sw=1.5))
    parts.append(line(875, 155, 215, 155, color=INK, sw=1.5))
    parts.append(arrow(215, 155, 215, 115, color=INK, sw=1.5))
    parts.append(text(540, 168, "Зворотний зв'язок енкодерів (пряма кінематика x = FK(q))", size=10.5, color=MUTED))


    # Горизонтальний роздільник
    parts.append(line(40, 220, 920, 220, color="#e2e8f0", sw=1.5, dash="6,6"))


    # ── НИЖНЯ ЧАСТИНА: Адмітансне керування ──
    parts.append(text(480, 248, "Адмітансне керування: Виміряна сила → Корекція траєкторії", size=15, bold=True))
    parts.append(text(480, 268, "робот формує адмітанс, підходить для промислових роботів із високоредукторними приводами", size=11, color=MUTED))

    # 1. Датчик сили-моменту F/T
    b_sens, _, _ = textbox(110, 340, "Датчик сили F/T\nвимірювання F_ext", size=11, pad=7, fill="#fee2e2", stroke=POS, bold=True)
    parts.append(b_sens)
    parts.append(arrow(185, 340, 225, 340, color=INK, sw=1.5))
    parts.append(text(205, 328, "F_ext", size=10.5, color=POS, bold=True))

    # 2. Фільтр адмітансу
    b_adm, _, _ = textbox(315, 340, "Адмітансний фільтр\nΔẍ = M_d⁻¹(F_ext − B_d·Δẋ − K_d·Δx)", size=11, pad=8, fill="#f0fdf4", stroke=FIELD, bold=True)
    parts.append(b_adm)
    parts.append(arrow(425, 340, 475, 340, color=INK, sw=1.5))
    parts.append(text(450, 326, "Δx_c", size=10.5, color=FIELD, bold=True))

    # Суматор похибки положення
    parts.append(circle(485, 340, 10, fill=BG, stroke=INK, sw=1.5))
    parts.append(text(485, 344, "Σ", size=11, bold=True))

    # Вхід бажаної траєкторії знизу
    b_traj2, _, _ = textbox(485, 428, "Бажана x_d(t)", size=11, pad=6, fill="#eff6ff", stroke=NEG)
    parts.append(b_traj2)
    parts.append(arrow(485, 403, 485, 355, color=INK, sw=1.5))

    parts.append(arrow(495, 340, 545, 340, color=INK, sw=1.5))
    parts.append(text(520, 328, "x_cmd", size=10.5, color=NEG, bold=True))

    # 3. Внутрішній контур положення
    b_pos, _, _ = textbox(645, 340, "Внутрішній позиційний\nконтур PID (жорсткий)", size=11, pad=8, fill="#f8fafc", stroke=INK)
    parts.append(b_pos)
    parts.append(arrow(745, 340, 790, 340, color=INK, sw=1.5))
    parts.append(text(768, 328, "q_cmd", size=10, color=INK))

    # 4. Приводи робота
    b_bot2, _, _ = textbox(850, 340, "Сервоприводи\nманіпулятора", size=11, pad=7, fill="#f8fafc", stroke=INK)
    parts.append(b_bot2)

    # Зв'язок із середовищем
    parts.append(line(850, 370, 850, 465, color=INK, sw=1.5))
    parts.append(line(850, 465, 110, 465, color=INK, sw=1.5))
    parts.append(arrow(110, 465, 110, 375, color=INK, sw=1.5))
    parts.append(text(480, 480, "Механічний контакт із середовищем породжує зовнішню силу F_ext", size=10.5, color=MUTED))

    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
           '<rect width="100%%" height="100%%" fill="%s"/>\n%s\n</svg>'
           % (W, H, W, H, BG, "\n".join(parts)))
    with open(os.path.join(IMG_DIR, "fig-impedance-vs-admittance.svg"), "w", encoding="utf-8") as f:
        f.write(svg)


# ── Фігура 3: Механізм дистанційного центру піддатливості (RCC) ───────────────
def fig_rcc_geometry():
    W, H = 960, 490
    parts = []

    # Заголовок
    parts.append(text(480, 28, "Пристрій дистанційного центру піддатливості (RCC — Remote Center Compliance)", size=15, bold=True))
    parts.append(text(480, 48, "похилі пружні балки проектують центр обертання на кінчик стрижня, усуваючи заклинювання", size=11.5, color=MUTED))

    # ── ЛІВОРУЧ: Звичайний жорсткий шток без RCC (заклинювання) ──
    lx = 240
    parts.append(text(lx, 82, "Без RCC: поворот навколо фланця", size=12.5, bold=True))

    # Фланець
    parts.append(rect(lx - 50, 100, 100, 16, fill="#64748b", stroke=INK, sw=1.5, rx=3))
    parts.append(circle(lx, 116, 4, fill=POS, stroke=INK))
    parts.append(text(lx + 55, 120, "Центр C₁", size=10.5, color=POS, anchor="start", bold=True))

    # Отвір
    hole_w = 42
    hole_top = 270
    parts.append(rect(lx - 80, hole_top, 80 - hole_w / 2, 140, fill="#cbd5e1", stroke=INK, sw=1.5))
    parts.append(rect(lx + hole_w / 2, hole_top, 80 - hole_w / 2, 140, fill="#cbd5e1", stroke=INK, sw=1.5))

    # Стрижень (нахилений під кутом)
    rad1 = math.radians(4.5)
    cos1, sin1 = math.cos(rad1), math.sin(rad1)
    peg_w, peg_len = 38, 165
    pts_peg1 = []
    for dx, dy in [(-peg_w/2, 0), (peg_w/2, 0), (peg_w/2, peg_len), (-peg_w/2, peg_len)]:
        rx = lx + dx * cos1 - dy * sin1
        ry = 116 + dx * sin1 + dy * cos1
        pts_peg1.append("%.1f,%.1f" % (rx, ry))
    parts.append('<polygon points="%s" fill="#f8fafc" stroke="%s" stroke-width="2"/>' % (" ".join(pts_peg1), INK))

    # Точки двоточкового заклинювання
    parts.append(circle(lx - hole_w / 2 + 1, hole_top + 12, 5, fill=POS, stroke=INK))
    parts.append(circle(lx + hole_w / 2 - 1, hole_top + 98, 5, fill=POS, stroke=INK))
    parts.append(text(lx - hole_w / 2 - 12, hole_top + 10, "F₁", size=11, color=POS, bold=True, anchor="end"))
    parts.append(text(lx + hole_w / 2 + 12, hole_top + 100, "F₂", size=11, color=POS, bold=True, anchor="start"))

    b_jam, _, _ = textbox(lx, 442, "Двоточкове заклинювання (Wedging)\nМомент сили F_lat збільшує перекіс", size=11, pad=6, fill="#fee2e2", stroke=POS, bold=True)
    parts.append(b_jam)


    # ── ПРАВОРУЧ: RCC з похилими пружними балками ──
    rx = 720
    parts.append(text(rx, 82, "З RCC: віртуальний центр на кінчику", size=12.5, bold=True))

    # Верхня пластина фланця
    parts.append(rect(rx - 70, 100, 140, 14, fill="#64748b", stroke=INK, sw=1.5, rx=3))

    # Похилі еластомерні/пружинні стрижні RCC
    parts.append(line(rx - 55, 114, rx - 35, 165, color=FIELD, sw=3))
    parts.append(line(rx - 25, 114, rx - 12, 165, color=FIELD, sw=3))
    parts.append(line(rx + 25, 114, rx + 12, 165, color=FIELD, sw=3))
    parts.append(line(rx + 55, 114, rx + 35, 165, color=FIELD, sw=3))

    # Пунктирні лінії фокуса
    tip_y = 345
    parts.append(line(rx - 55, 114, rx, tip_y, color=MUTED, sw=1.2, dash="3,3"))
    parts.append(line(rx + 55, 114, rx, tip_y, color=MUTED, sw=1.2, dash="3,3"))

    # Нижня плаваюча пластина RCC
    parts.append(rect(rx - 50, 165, 100, 14, fill="#94a3b8", stroke=INK, sw=1.5, rx=3))

    # Отвір
    parts.append(rect(rx - 80, hole_top, 80 - hole_w / 2, 140, fill="#cbd5e1", stroke=INK, sw=1.5))
    parts.append(rect(rx + hole_w / 2, hole_top, 80 - hole_w / 2, 140, fill="#cbd5e1", stroke=INK, sw=1.5))

    # Стрижень
    parts.append(rect(rx - peg_w / 2, 179, peg_w, 160, fill="#dcfce7", stroke=FIELD, sw=2, rx=2))

    # Віртуальний центр піддатливості на кінчику
    parts.append(circle(rx, tip_y, 5, fill=FIELD, stroke=INK, sw=1.5))
    parts.append(text(rx + 14, tip_y + 4, "Центр C_rcc", size=11, color=FIELD, bold=True, anchor="start"))

    # Бічна сила на фасці над отвором (y=255)
    parts.append(arrow(rx - hole_w / 2 - 35, 255, rx - peg_w / 2, 255, color=POS, sw=2.5))
    parts.append(text(rx - hole_w / 2 - 40, 245, "F_lat", size=11, color=POS, bold=True, anchor="end"))

    # Зсув плаваючої пластини
    b_shift, _, _ = textbox(rx + 85, 172, "паралельний зсув δx", size=10, pad=4, fill="#ecfdf5", stroke=FIELD)
    parts.append(b_shift)

    b_rcc, _, _ = textbox(rx, 442, "Бокова сила F_lat діє через центр C_rcc\nОбертальний момент відсутній → кутовий перекіс = 0\nБезперешкодний спуск в отвір", size=11, pad=6, fill="#f0fdf4", stroke=FIELD, bold=True)
    parts.append(b_rcc)

    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
           '<rect width="100%%" height="100%%" fill="%s"/>\n%s\n</svg>'
           % (W, H, W, H, BG, "\n".join(parts)))
    with open(os.path.join(IMG_DIR, "fig-rcc-geometry.svg"), "w", encoding="utf-8") as f:
        f.write(svg)


if __name__ == "__main__":
    fig_rigid_vs_compliant()
    fig_impedance_vs_admittance()
    fig_rcc_geometry()
    print("All figures generated successfully.")
