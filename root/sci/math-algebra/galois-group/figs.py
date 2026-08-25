# -*- coding: utf-8 -*-
"""Фігури до теми «Група Ґалуа»."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def arc_arrow(cx, cy, r, a0, a1, color=INK, sw=2.4):
    """Дуга-стрілка від кута a0 до a1 (градуси, екранні коорд. y вниз)."""
    ra0, ra1 = math.radians(a0), math.radians(a1)
    sx, sy = cx + r * math.cos(ra0), cy + r * math.sin(ra0)
    ex, ey = cx + r * math.cos(ra1), cy + r * math.sin(ra1)
    large = 1 if abs(a1 - a0) > 180 else 0
    sweep = 1 if a1 > a0 else 0
    return ('<path d="M %.1f %.1f A %.1f %.1f 0 %d %d %.1f %.1f" fill="none" '
            'stroke="%s" stroke-width="%.1f" marker-end="url(#arrow)"/>'
            % (sx, sy, r, r, large, sweep, ex, ey, color, sw))


def fig_galois_lattice():
    """Фігура 1: Відповідність Ґалуа між ґраткою полів та ґраткою підгруп."""
    W, H = 1000, 490
    frags = []

    # Заголовок колонок
    frags.append(textbox(240, 30, "Ґратка проміжних полів розкладу\nf(x) = x³ − 2 над Q", size=14, bold=True, fill="#f8fafc")[0])
    frags.append(textbox(760, 30, "Ґратка підгруп групи Ґалуа\nGal(K/Q) ≅ S₃", size=14, bold=True, fill="#f8fafc")[0])

    # Вузли лівої ґратки (Поля)
    # Рівень 3 (верх): Повне поле K
    tb_k, _, _ = textbox(240, 95, "K = Q(³√2, ω)  [розмірність 6]", size=13, bold=True, fill="#eef2ff", stroke="#4f46e5", sw=2)
    frags.append(tb_k)

    # Рівень 2 (середина): Проміжні поля
    tb_qw, _, _ = textbox(65, 230, "Q(ω)\n[степ. 2, норм.]", size=11, bold=True, fill="#ecfdf5", stroke=FIELD, sw=2)
    tb_q1, _, _ = textbox(175, 230, "Q(³√2)\n[степ. 3]", size=11, fill=FILL, stroke=LINE)
    tb_q2, _, _ = textbox(275, 230, "Q(³√2·ω)\n[степ. 3]", size=11, fill=FILL, stroke=LINE)
    tb_q3, _, _ = textbox(375, 230, "Q(³√2·ω²)\n[степ. 3]", size=11, fill=FILL, stroke=LINE)
    frags.extend([tb_qw, tb_q1, tb_q2, tb_q3])

    # Рівень 1 (низ): Базове поле Q
    tb_q, _, _ = textbox(240, 385, "Базове поле Q  [розмірність 1]", size=13, bold=True, fill="#f1f5f9", stroke=LINE)
    frags.append(tb_q)

    # Лінії включення полів (зліва)
    frags.append(line(240, 115, 65, 205, color=FIELD, sw=2))
    frags.append(line(240, 115, 175, 205, color=LINE, sw=1.5))
    frags.append(line(240, 115, 275, 205, color=LINE, sw=1.5))
    frags.append(line(240, 115, 375, 205, color=LINE, sw=1.5))

    frags.append(line(65, 255, 240, 365, color=FIELD, sw=2))
    frags.append(line(175, 255, 240, 365, color=LINE, sw=1.5))
    frags.append(line(275, 255, 240, 365, color=LINE, sw=1.5))
    frags.append(line(375, 255, 240, 365, color=LINE, sw=1.5))

    # Центральний блок — дзеркальна стрілка двоїстості
    frags.append(arrow(450, 180, 550, 180, color=POS, sw=2))
    frags.append(arrow(550, 280, 450, 280, color=NEG, sw=2))
    frags.append(textbox(500, 230, "Антиізоморфізм\n(інверсія порядку)\nE ↦ Gal(K/E)\nH ↦ Kᴴ", size=11, bold=True, fill="#fffbeb", stroke="#d97706", sw=1.8)[0])

    # Вузли правої ґратки (Підгрупи)
    # Рівень 3 (верх): Повна група S₃
    tb_s3, _, _ = textbox(760, 95, "Вся група Gal(K/Q) ≅ S₃  [порядок 6]", size=13, bold=True, fill="#f1f5f9", stroke=LINE)
    frags.append(tb_s3)

    # Рівень 2 (середина): Підгрупи
    tb_a3, _, _ = textbox(625, 230, "A₃ = {e, σ, σ²}\n[пор. 3, норм.]", size=11, bold=True, fill="#ecfdf5", stroke=FIELD, sw=2)
    tb_h1, _, _ = textbox(725, 230, "{e, τ}\n[пор. 2]", size=11, fill=FILL, stroke=LINE)
    tb_h2, _, _ = textbox(815, 230, "{e, στ}\n[пор. 2]", size=11, fill=FILL, stroke=LINE)
    tb_h3, _, _ = textbox(905, 230, "{e, σ²τ}\n[пор. 2]", size=11, fill=FILL, stroke=LINE)
    frags.extend([tb_a3, tb_h1, tb_h2, tb_h3])

    # Рівень 1 (низ): Тривіальна підгрупа {e}
    tb_e, _, _ = textbox(760, 385, "{e}  [тривіальна підгрупа, порядок 1]", size=13, bold=True, fill="#eef2ff", stroke="#4f46e5", sw=2)
    frags.append(tb_e)

    # Лінії включення підгруп (справа)
    frags.append(line(760, 115, 625, 205, color=FIELD, sw=2))
    frags.append(line(760, 115, 725, 205, color=LINE, sw=1.5))
    frags.append(line(760, 115, 815, 205, color=LINE, sw=1.5))
    frags.append(line(760, 115, 905, 205, color=LINE, sw=1.5))

    frags.append(line(625, 255, 760, 365, color=FIELD, sw=2))
    frags.append(line(725, 255, 760, 365, color=LINE, sw=1.5))
    frags.append(line(815, 255, 760, 365, color=LINE, sw=1.5))
    frags.append(line(905, 255, 760, 365, color=LINE, sw=1.5))

    # Нижній пояснювальний коментар
    frags.append(textbox(500, 450, "Зеленим виділено відповідність між нормальним розширенням Q(ω)/Q та нормальною підгрупою A₃ ⊲ S₃.\nНайбільше поле K відповідає найменшій підгрупі {e}; базове поле Q відповідає всій групі S₃.", size=11, fill="#f8fafc", stroke="#94a3b8")[0])

    render(os.path.join(OUT, "galois-connection-lattice.svg"), W, H, *frags)


def fig_root_symmetries():
    """Фігура 2: Корені x³ − 2 на комплексній площині та генератори групи Ґалуа."""
    W, H = 760, 440
    frags = []

    cx, cy = 360, 220
    R = 140

    # Координатні осі
    frags.append(arrow(cx - 220, cy, cx + 220, cy, color="#94a3b8", sw=1.5))
    frags.append(arrow(cx, cy + 180, cx, cy - 180, color="#94a3b8", sw=1.5))
    frags.append(text(cx + 215, cy - 12, "Re", size=13, color=MUTED, bold=True))
    frags.append(text(cx + 12, cy - 170, "Im", size=13, color=MUTED, bold=True))

    # Коло радіуса ³√2
    frags.append(circle(cx, cy, R, fill="none", stroke="#cbd5e1", sw=1.5))
    frags.append(text(cx + R * 0.7, cy - R * 0.75, "|z| = ³√2", size=11, color=MUTED, italic=True))

    # Координати 3-х коренів:
    p1 = (cx + R, cy)
    p2 = (cx - R * 0.5, cy - R * 0.866)
    p3 = (cx - R * 0.5, cy + R * 0.866)

    # Трикутник коренів
    pts = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (p1[0], p1[1], p2[0], p2[1], p3[0], p3[1])
    frags.append('<polygon points="%s" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.8" stroke-dasharray="4 4"/>' % pts)

    # Точки коренів
    for pt, col in [(p1, POS), (p2, NEG), (p3, FIELD)]:
        frags.append(circle(pt[0], pt[1], 7, fill=col, stroke="#ffffff", sw=2))

    # Підписи коренів
    frags.append(textbox(p1[0] + 55, p1[1] + 18, "α₁ = ³√2\n(дійсний корінь)", size=11, bold=True, fill="#fff1f2", stroke=POS)[0])
    frags.append(textbox(p2[0] - 65, p2[1] - 18, "α₂ = ³√2·e^{i2π/3}\n(комплексний)", size=11, bold=True, fill="#eff6ff", stroke=NEG)[0])
    frags.append(textbox(p3[0] - 65, p3[1] + 18, "α₃ = ³√2·e^{-i2π/3}\n(комплексний)", size=11, bold=True, fill="#ecfdf5", stroke=FIELD)[0])

    # Дія повороту σ (циклічний зсув на 120°)
    frags.append(arc_arrow(cx, cy, R + 25, -5, -115, color=POS, sw=2.2))
    frags.append(arc_arrow(cx, cy, R + 25, -125, -235, color=POS, sw=2.2))
    frags.append(arc_arrow(cx, cy, R + 25, -245, -355, color=POS, sw=2.2))
    frags.append(textbox(cx + 80, cy - R - 35, "Автоморфізм σ (поворот фази на 120°):\nα₁ ↦ α₂ ↦ α₃ ↦ α₁  (порядок 3)", size=11, bold=True, fill="#fdf2f8", stroke=POS)[0])

    # Дія комплексної спряженості τ (відбиття від осі Re)
    frags.append(line(cx - 200, cy, cx + 200, cy, color="#ef4444", sw=2, dash="5 4"))
    frags.append(arrow(p2[0], p2[1] + 12, p3[0], p3[1] - 12, color="#ef4444", sw=2))
    frags.append(arrow(p3[0], p3[1] - 12, p2[0], p2[1] + 12, color="#ef4444", sw=2))
    frags.append(textbox(cx - 190, cy, "Автоморфізм τ (спряження):\nфіксує α₁, міняє α₂ ↔ α₃\n(порядок 2)", size=11, bold=True, fill="#fef2f2", stroke="#ef4444")[0])

    render(os.path.join(OUT, "root-symmetries-cubic.svg"), W, H, *frags)


def fig_solvability_towers():
    """Фігура 3: Вежі підгруп: розв'язна група S₄ проти нерозв'язного глухого кута S₅."""
    W, H = 820, 460
    frags = []

    # Колонка 1: Рівняння 4-го степеня (S₄)
    frags.append(textbox(210, 30, "Рівняння 4-го степеня: Gal(f) ⊆ S₄\n(Розв'язується у радикалах за Феррарі)", size=13, bold=True, fill="#ecfdf5", stroke=FIELD)[0])

    tb_s4 = textbox(210, 85, "S₄  [порядок 24, усі перестановки 4 коренів]", size=12, bold=True, fill="#f8fafc", stroke=LINE)[0]
    tb_a4 = textbox(210, 155, "A₄  [порядок 12, парні перестановки]", size=12, bold=True, fill="#f8fafc", stroke=LINE)[0]
    tb_v4 = textbox(210, 225, "V₄ ≅ Z₂ × Z₂  [порядок 4, четвірна група Клейна]", size=12, bold=True, fill="#f8fafc", stroke=LINE)[0]
    tb_z2 = textbox(210, 295, "Z₂  [порядок 2, одна транспозиція]", size=12, bold=True, fill="#f8fafc", stroke=LINE)[0]
    tb_e4 = textbox(210, 365, "{e}  [порядок 1, тривіальна група]", size=12, bold=True, fill="#eef2ff", stroke="#4f46e5")[0]
    frags.extend([tb_s4, tb_a4, tb_v4, tb_z2, tb_e4])

    frags.append(arrow(210, 105, 210, 135, color=FIELD, sw=2))
    frags.append(text(285, 120, "S₄/A₄ ≅ Z₂ (абелева)", size=11, color=FIELD, bold=True))

    frags.append(arrow(210, 175, 210, 205, color=FIELD, sw=2))
    frags.append(text(285, 190, "A₄/V₄ ≅ Z₃ (абелева)", size=11, color=FIELD, bold=True))

    frags.append(arrow(210, 245, 210, 275, color=FIELD, sw=2))
    frags.append(text(285, 260, "V₄/Z₂ ≅ Z₂ (абелева)", size=11, color=FIELD, bold=True))

    frags.append(arrow(210, 315, 210, 345, color=FIELD, sw=2))
    frags.append(text(285, 330, "Z₂/{e} ≅ Z₂ (абелева)", size=11, color=FIELD, bold=True))

    frags.append(textbox(210, 420, "Усі фактори Z₂, Z₃, Z₂ циклічні й абелеві.\nКожен крок відповідає приєднанню кореня: √ чи ³√.", size=11, fill="#f0fdf4", stroke=FIELD)[0])

    # Колонка 2: Загальне рівняння 5-го степеня (S₅)
    frags.append(textbox(610, 30, "Загальне рівняння 5-го степеня: Gal(f) = S₅\n(Не розв'язується у радикалах: теорема Абеля — Ґалуа)", size=13, bold=True, fill="#fff1f2", stroke=POS)[0])

    tb_s5 = textbox(610, 85, "S₅  [порядок 120, перестановки 5 коренів]", size=12, bold=True, fill="#f8fafc", stroke=LINE)[0]
    tb_a5 = textbox(610, 175, "A₅  [порядок 60, парні перестановки]", size=12, bold=True, fill="#fee2e2", stroke=POS, sw=2)[0]
    frags.extend([tb_s5, tb_a5])

    frags.append(arrow(610, 105, 610, 155, color=POS, sw=2))
    frags.append(text(685, 130, "S₅/A₅ ≅ Z₂", size=11, color=POS, bold=True))

    frags.append(rect(450, 220, 320, 110, fill="#fef2f2", stroke=POS, sw=2, rx=8))
    frags.append(textbox(610, 250, "БАР'ЄР: ПРОСТА ГРУПА A₅", size=13, bold=True, fill="#fee2e2", stroke=POS)[0])
    frags.append(mtext(610, 280, "A₅ — найменша неабелева проста група (пор. 60).\nВона НЕ має жодної нормальної підгрупи, крім {e} та A₅.\nНеможливо розбити на простіші абелеві фактори!", size=11, color=POS, bold=True))

    frags.append(arrow(610, 195, 610, 218, color=POS, sw=2.5))
    frags.append(line(570, 335, 650, 335, color=POS, sw=2.5))
    frags.append(line(570, 335, 650, 355, color=POS, sw=2))
    frags.append(line(570, 355, 650, 335, color=POS, sw=2))
    frags.append(text(610, 370, "Шлях у радикалах перекрито", size=12, color=POS, bold=True))

    frags.append(textbox(610, 420, "Оскільки A₅ не містить нормальних підгруп, вежа обривається.\nФормули в радикалах для n ≥ 5 у загальному вигляді не існує.", size=11, fill="#fff1f2", stroke=POS)[0])

    render(os.path.join(OUT, "solvable-vs-unsolvable-towers.svg"), W, H, *frags)


if __name__ == '__main__':
    fig_galois_lattice()
    fig_root_symmetries()
    fig_solvability_towers()
    print("All figures generated successfully.")
