# -*- coding: utf-8 -*-
"""Фігури для теми «Рука на рухомій платформі: реакція, стійкість, зсув ЦМ».
Запуск: python figs.py -> ./img/*.svg
"""
import sys, os, math

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Динамічний зв'язок маніпулятора й шасі ────────────────────────
def fig_dynamic_coupling():
    W, H = 760, 420
    parts = []

    # Ґрунт / опорна поверхня
    parts.append(line(40, 360, 720, 360, color=LINE, sw=2))
    # Штрихування землі
    for gx in range(50, 710, 25):
        parts.append(line(gx, 360, gx - 12, 375, color=MUTED, sw=1.2))

    # Колеса платформи
    parts.append(circle(160, 325, 35, fill="#e2e8f0", stroke=LINE, sw=2))
    parts.append(circle(160, 325, 12, fill="#94a3b8", stroke=LINE, sw=1.5))
    parts.append(circle(360, 325, 35, fill="#e2e8f0", stroke=LINE, sw=2))
    parts.append(circle(360, 325, 12, fill="#94a3b8", stroke=LINE, sw=1.5))

    # Гусеничний контур / підвіска
    parts.append(line(160, 360, 360, 360, color=LINE, sw=3))
    parts.append(line(160, 290, 360, 290, color=LINE, sw=3))

    # Корпус платформи (шасі ровера)
    parts.append(rect(120, 220, 280, 70, fill="#f8fafc", stroke=LINE, sw=2, rx=6))
    parts.append(text(260, 255, "Рухоме шасі (маса M₀)", size=14, color=INK, bold=True))

    # Пружини підвіски (передня стиснута, задня розтиснута)
    # Задня підвіска (ліворуч)
    parts.append(line(160, 290, 160, 245, color=MUTED, sw=2, dash="3 3"))
    parts.append(text(160, 210, "Розвантаження", size=11, color=NEG, anchor="middle", bold=True))
    # Передня підвіска (праворуч)
    parts.append(line(360, 290, 360, 260, color=MUTED, sw=2, dash="3 3"))
    parts.append(text(360, 210, "Стиснення підвіски", size=11, color=POS, anchor="middle", bold=True))

    # Тумба/база маніпулятора
    parts.append(rect(310, 185, 60, 35, fill="#cbd5e1", stroke=LINE, sw=1.5, rx=3))
    parts.append(circle(340, 185, 8, fill="#475569", stroke=LINE, sw=1.5))

    # Ланка 1 (плече)
    parts.append(line(340, 185, 450, 110, color=LINE, sw=6))
    parts.append(circle(450, 110, 7, fill="#475569", stroke=LINE, sw=1.5))

    # Ланка 2 (передпліччя, витягнуте вперед)
    parts.append(line(450, 110, 600, 95, color=LINE, sw=5))
    parts.append(circle(600, 95, 6, fill="#475569", stroke=LINE, sw=1.5))

    # Захват із вантажем
    parts.append(rect(595, 85, 25, 20, fill="#64748b", stroke=LINE, sw=1.5, rx=2))
    parts.append(circle(640, 95, 18, fill="#fee2e2", stroke=POS, sw=2))
    parts.append(text(640, 99, "m_в", size=12, color=POS, bold=True))

    # Стрілка прискорення ланки й вантажу (рух уперед-вниз)
    parts.append(arrow(640, 60, 710, 60, color=FIELD, sw=2.5))
    parts.append(text(675, 48, "Прискорення руки a_руки", size=12, color=FIELD, bold=True))

    # Сила інерції Д'Аламбера на ланку
    parts.append(arrow(640, 95, 540, 95, color=POS, sw=2.2))
    parts.append(text(550, 125, "Сила інерції −m_в·a", size=12, color=POS, bold=True))

    # Реактивний перекидний момент на фланці шасі (дугова стрілка за годинниковою стрілкою)
    parts.append('<path d="M 320 160 A 35 35 0 0 1 370 160" fill="none" stroke="%s" stroke-width="2.5" marker-end="url(#arrow)"/>' % POS)
    parts.append(text(345, 145, "Реактивний момент τ_реакц", size=12, color=POS, bold=True))

    # Реакція нормальної сили під колесами (N_задня менша, N_передня більша)
    parts.append(arrow(160, 395, 160, 362, color=NEG, sw=2))
    parts.append(text(160, 412, "N_заднє (мала)", size=12, color=NEG, anchor="middle"))

    parts.append(arrow(360, 405, 360, 362, color=POS, sw=3.2))
    parts.append(text(360, 415, "N_переднє (зросла)", size=12, color=POS, anchor="middle"))

    render(os.path.join(IMG, "dynamic-coupling.svg"), W, H, *parts,
           title="Динамічний зв'язок: реактивні сили та моменти на платформі")


# ── Фігура 2: Багатокутник опори, статичний ЦМ і динамічний ZMP ─────────────
def fig_support_polygon_cog_zmp():
    W, H = 760, 400
    parts = []

    # Рамка багатокутника опори (вид згори)
    poly_pts = [(160, 100), (520, 100), (520, 300), (160, 300)]
    poly_d = "M %d %d L %d %d L %d %d L %d %d Z" % (
        poly_pts[0][0], poly_pts[0][1],
        poly_pts[1][0], poly_pts[1][1],
        poly_pts[2][0], poly_pts[2][1],
        poly_pts[3][0], poly_pts[3][1]
    )
    # Заливка безпечної зони
    parts.append('<path d="%s" fill="#f0fdf4" stroke="%s" stroke-width="2.5"/>' % (poly_d, FIELD))

    # 4 плями контакту коліс
    wheels = [
        (160, 100, "Колесо 1 (заднє ліве)"),
        (520, 100, "Колесо 2 (переднє ліве)"),
        (520, 300, "Колесо 3 (переднє праве)"),
        (160, 300, "Колесо 4 (заднє праве)")
    ]
    for wx, wy, wname in wheels:
        parts.append(rect(wx - 25, wy - 35, 50, 70, fill="#cbd5e1", stroke=LINE, sw=1.5, rx=4))
        parts.append(circle(wx, wy, 4, fill=LINE, stroke=LINE, sw=1))

    # Підписи коліс
    parts.append(text(125, 55, "Заднє ліве", size=11, color=MUTED, anchor="middle"))
    parts.append(text(555, 55, "Переднє ліве", size=11, color=MUTED, anchor="middle"))
    parts.append(text(555, 355, "Переднє праве", size=11, color=MUTED, anchor="middle"))
    parts.append(text(125, 355, "Заднє праве", size=11, color=MUTED, anchor="middle"))

    # Вісь перекидання (передня кромка x = 520)
    parts.append(line(520, 60, 520, 340, color=POS, sw=2.5, dash="6 4"))
    parts.append(text(535, 200, "Перекидна вісь", size=12, color=POS, bold=True, anchor="start"))

    # Статична проєкція центру мас (CoG)
    cog_x, cog_y = 310, 190
    parts.append(circle(cog_x, cog_y, 9, fill="#93c5fd", stroke=NEG, sw=2))
    parts.append(line(cog_x - 12, cog_y, cog_x + 12, cog_y, color=NEG, sw=1.5))
    parts.append(line(cog_x, cog_y - 12, cog_x, cog_y + 12, color=NEG, sw=1.5))
    parts.append(text(cog_x - 15, cog_y - 15, "Статичний CoM", size=12, color=NEG, bold=True, anchor="end"))

    # Вектор статичного запасу стійкості (SSM)
    parts.append(arrow(cog_x, cog_y, 520, cog_y, color=NEG, sw=1.5))
    parts.append(text(410, cog_y - 8, "Статичний запас SSM (210 мм)", size=11, color=NEG, bold=True))

    # Динамічна точка ZMP (зсунута вперед через різке гальмування / розгін руки)
    zmp_x, zmp_y = 480, 220
    parts.append(circle(zmp_x, zmp_y, 10, fill="#fca5a5", stroke=POS, sw=2.5))
    parts.append(line(zmp_x - 12, zmp_y, zmp_x + 12, zmp_y, color=POS, sw=2))
    parts.append(line(zmp_x, zmp_y - 12, zmp_x, zmp_y + 12, color=POS, sw=2))
    parts.append(text(zmp_x, zmp_y - 16, "Динамічний ZMP", size=12, color=POS, bold=True, anchor="middle"))

    # Стрілка зсуву від сил інерції
    parts.append(arrow(cog_x + 15, cog_y + 10, zmp_x - 15, zmp_y - 5, color=MUTED, sw=1.8))
    parts.append(text(390, 240, "Динамічний зсув Δr = (z·a_x)/g", size=11, color=MUTED, italic=True))

    # Динамічний запас стійкості (DSM)
    parts.append(arrow(zmp_x, zmp_y, 520, zmp_y, color=POS, sw=2))
    parts.append(text(zmp_x + 18, zmp_y + 20, "DSM (40 мм)", size=11, color=POS, bold=True))

    # Зона небезпеки біля краю
    parts.append(rect(500, 100, 20, 200, fill="#fee2e2", stroke="none"))
    parts.append(text(660, 150, "Багатокутник опори", size=13, color=FIELD, bold=True, anchor="middle"))
    parts.append(text(660, 172, "Зелене — безпечно", size=11, color=MUTED, anchor="middle"))
    parts.append(text(660, 192, "Червоне — загроза перекидання", size=11, color=POS, anchor="middle"))

    render(os.path.join(IMG, "support-polygon-cog-zmp.svg"), W, H, *parts,
           title="Багатокутник опори: статичний CoM проти динамічного ZMP")


# ── Фігура 3: Архітектура випереджальної компенсації та Whole-Body контролю ──
def fig_feedforward_compensation():
    W, H = 760, 360
    parts = []

    # Блок 1: Планувальник траєкторії маніпулятора
    b1_body, b1_w, b1_h = textbox(120, 100, "Планувальник траєкторії\nq_m(t), q̇_m(t), q̈_m(t)", size=12, pad=10, fill="#e0f2fe", stroke=NEG, bold=True)
    parts.append(b1_body)

    # Блок 2: Динамічна модель маніпулятора (Обернена динаміка)
    b2_body, b2_w, b2_h = textbox(360, 100, "Модель реакцій\nF_реакц, τ_реакц, ZMP", size=12, pad=10, fill="#fef3c7", stroke="#d97706", bold=True)
    parts.append(b2_body)

    # Стрілка з Блоку 1 в Блок 2
    parts.append(arrow(120 + b1_w/2, 100, 360 - b2_w/2, 100, color=LINE, sw=1.8))

    # Стрілка вниз до приводів руки
    b_arm_body, _, _ = textbox(120, 240, "Сервоприводи маніпулятора\nКонтур положення/швидкості", size=12, pad=8, fill="#f1f5f9", stroke=LINE)
    parts.append(b_arm_body)
    parts.append(arrow(120, 100 + b1_h/2, 120, 240 - 25, color=LINE, sw=1.8))

    # Блок 3: Контролер шасі (Feedforward + Whole-Body)
    b3_body, b3_w, b3_h = textbox(600, 100, "Випереджальне керування шасі\nτ_коліс_ff = −K_ff · τ_реакц", size=12, pad=10, fill="#dcfce7", stroke=FIELD, bold=True)
    parts.append(b3_body)

    # Стрілка з Блоку 2 в Блок 3 (сигнал компенсації)
    parts.append(arrow(360 + b2_w/2, 100, 600 - b3_w/2, 100, color=FIELD, sw=2))
    parts.append(text(475, 82, "Випереджальний сигнал", size=11, color=FIELD, bold=True))

    # Блок 4: Приводи шасі / підвіски
    b4_body, _, _ = textbox(600, 240, "Тягові мотори шасі\nАктивна протидія перекиданню", size=12, pad=8, fill="#f1f5f9", stroke=LINE)
    parts.append(b4_body)
    parts.append(arrow(600, 100 + b3_h/2, 600, 240 - 25, color=FIELD, sw=2))

    # Блок об'єкта керування
    parts.append(rect(240, 220, 240, 50, fill="#f8fafc", stroke=LINE, sw=1.8, rx=4))
    parts.append(text(360, 240, "Мобільний робот із рукою", size=13, color=INK, bold=True))
    parts.append(text(360, 258, "Зв'язана механічна система", size=11, color=MUTED))

    # Стрілки в об'єкт від обох приводів
    parts.append(arrow(120 + 80, 240, 240, 240, color=LINE, sw=1.5))
    parts.append(arrow(600 - 80, 240, 480, 240, color=FIELD, sw=1.8))

    # Зворотний зв'язок від IMU до планувальника/коректора
    parts.append(line(360, 270, 360, 315, color=NEG, sw=1.5))
    parts.append(line(360, 315, 360, 315, color=NEG, sw=1.5))
    parts.append(line(360, 315, 360 - 240, 315, color=NEG, sw=1.5))
    parts.append(arrow(120, 315, 120, 275, color=NEG, sw=1.5))
    parts.append(text(240, 335, "Зворотний зв'язок (IMU / крен і тангаж бази)", size=11, color=NEG, bold=True))

    render(os.path.join(IMG, "feedforward-compensation.svg"), W, H, *parts,
           title="Архітектура випереджального гасіння реактивних моментів")


if __name__ == "__main__":
    fig_dynamic_coupling()
    fig_support_polygon_cog_zmp()
    fig_feedforward_compensation()
    print("Всі фігури згенеровано успішно.")
