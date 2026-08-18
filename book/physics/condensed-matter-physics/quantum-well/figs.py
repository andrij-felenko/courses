# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

DARK = INK

def svg_path(d_str, stroke="#c0392b", sw=2.5, fill="none", dash=None):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d_str, stroke, sw, fill, d_attr)

def polygon(points, fill=DARK, stroke="none", sw=1.0):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    st = ' stroke="%s" stroke-width="%.1f"' % (stroke, sw) if stroke != "none" else ''
    return '<polygon points="%s" fill="%s"%s/>' % (pts_str, fill, st)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Енергетична зонна діаграма прямокутної квантової ями GaAs/AlGaAs
# ════════════════════════════════════════════════════════════════════════════
def fig_confinement():
    W, H = 820, 440
    f = []

    # Тло під зонними бар'єрами
    f.append(rect(60, 60, 200, 320, fill="#f8f9fa", stroke="none"))
    f.append(rect(560, 60, 200, 320, fill="#f8f9fa", stroke="none"))
    f.append(rect(260, 60, 300, 320, fill="#edf2f7", stroke="none"))

    # Текст матеріалів
    f.append(text(160, 85, "Al_x Ga_1-x As (бар'єр)", size=12, color=MUTED, bold=True))
    f.append(text(410, 85, "GaAs (активна яма, L_z ~ 10 нм)", size=13, color=INK, bold=True))
    f.append(text(660, 85, "Al_x Ga_1-x As (бар'єр)", size=12, color=MUTED, bold=True))

    # Лінія дна зони провідності Ec
    f.append(svg_path("M 60 120 L 260 120 L 260 240 L 560 240 L 560 120 L 760 120", stroke=POS, sw=2.5))
    f.append(text(110, 112, "E_c (AlGaAs)", size=11, color=POS, bold=True))
    f.append(text(410, 255, "E_c (GaAs)", size=11, color=POS, bold=True))

    # Офсет зони провідності Delta Ec
    f.append(line(230, 120, 230, 240, color=POS, sw=1.5, dash="3 3"))
    f.append(line(225, 120, 235, 120, color=POS, sw=1.5))
    f.append(line(225, 240, 235, 240, color=POS, sw=1.5))
    f.append(text(195, 185, "ΔE_c", size=12, color=POS, bold=True))

    # Квантовані рівні в зоні провідності (E1 та E2)
    f.append(line(260, 210, 560, 210, color="#8e44ad", sw=1.8, dash="4 4"))
    f.append(text(285, 203, "E_n1", size=12, color="#8e44ad", bold=True))

    # Хвильова функція psi_1(z)
    f.append(svg_path("M 160 210 Q 240 210 260 210 Q 410 160 560 210 Q 580 210 660 210", stroke="#9b59b6", sw=2.0))
    f.append(text(410, 172, "ψ_1(z)", size=12, color="#8e44ad", bold=True))

    # E2 = 160
    f.append(line(260, 160, 560, 160, color="#d35400", sw=1.8, dash="4 4"))
    f.append(text(285, 153, "E_n2", size=12, color="#d35400", bold=True))

    # Хвильова функція psi_2(z)
    f.append(svg_path("M 180 160 Q 240 160 260 160 Q 335 125 410 160 Q 485 195 560 160 Q 580 160 640 160", stroke="#e67e22", sw=2.0))
    f.append(text(485, 212, "ψ_2(z)", size=12, color="#d35400", bold=True))

    # Стеля валентної зони Ev
    f.append(svg_path("M 60 380 L 260 380 L 260 310 L 560 310 L 560 380 L 760 380", stroke=NEG, sw=2.5))
    f.append(text(110, 395, "E_v (AlGaAs)", size=11, color=NEG, bold=True))
    f.append(text(410, 298, "E_v (GaAs)", size=11, color=NEG, bold=True))

    # Квантований рівень дірок E_hh1
    f.append(line(260, 330, 560, 330, color="#16a085", sw=1.8, dash="4 4"))
    f.append(text(285, 342, "E_hh1", size=12, color="#16a085", bold=True))

    # Позначення ширини ями L_z
    f.append(line(260, 415, 560, 415, color=DARK, sw=1.5))
    f.append(line(260, 410, 260, 420, color=DARK, sw=1.5))
    f.append(line(560, 410, 560, 420, color=DARK, sw=1.5))
    f.append(text(410, 432, "Ширина ями L_z ≈ 10 нм ~ λ_dB", size=12, bold=True, color=DARK))

    render(os.path.join(OUT, "quantum-well-confinement.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Густина станів: 3D параболічна проти 2D східчастої
# ════════════════════════════════════════════════════════════════════════════
def fig_density_of_states():
    W, H = 780, 400
    f = []

    # Осі координат
    f.append(line(80, 340, 720, 340, color=DARK, sw=1.8))
    f.append(line(80, 340, 80, 40, color=DARK, sw=1.8))
    f.append(text(735, 344, "Енергія E", size=12, bold=True, color=DARK, anchor="start"))
    f.append(text(80, 25, "Густина станів g(E)", size=12, bold=True, color=DARK, anchor="middle"))

    # 3D параболічна густина станів g_3D(E)
    f.append(svg_path("M 120 340 Q 250 250 400 180 Q 550 120 700 80", stroke=MUTED, sw=2.0, dash="5 4"))
    f.append(text(620, 75, "g_3D(E) ∝ √(E)", size=12, color=MUTED, bold=True, anchor="start"))

    # 2D східчаста густина станів g_2D(E)
    f.append(line(80, 340, 180, 340, color=POS, sw=2.5))
    f.append(line(180, 340, 180, 260, color=POS, sw=2.5))
    f.append(line(180, 260, 360, 260, color=POS, sw=2.5))
    f.append(line(360, 260, 360, 180, color=POS, sw=2.5))
    f.append(line(360, 180, 540, 180, color=POS, sw=2.5))
    f.append(line(540, 180, 540, 100, color=POS, sw=2.5))
    f.append(line(540, 100, 710, 100, color=POS, sw=2.5))

    # Пунктири рівнів
    f.append(line(180, 340, 180, 350, color=DARK, sw=1.5))
    f.append(text(180, 368, "E_1", size=12, bold=True, color=POS))

    f.append(line(360, 340, 360, 350, color=DARK, sw=1.5))
    f.append(text(360, 368, "E_2", size=12, bold=True, color=POS))

    f.append(line(540, 340, 540, 350, color=DARK, sw=1.5))
    f.append(text(540, 368, "E_3", size=12, bold=True, color=POS))

    # Квант висоти сходинки Delta g_2D
    f.append(line(70, 260, 80, 260, color=POS, sw=1.5))
    f.append(line(70, 180, 80, 180, color=POS, sw=1.5))
    f.append(text(65, 225, "Δg_2D = m* / (π ℏ²)", size=11, color=POS, bold=True, anchor="end"))

    # Пояснення
    f.append(text(270, 245, "Підзона n = 1", size=11, color=POS, bold=True))
    f.append(text(450, 165, "Підзона n = 2", size=11, color=POS, bold=True))
    f.append(text(625, 85, "Підзона n = 3", size=11, color=POS, bold=True))

    render(os.path.join(OUT, "density-of-states-2d-vs-3d.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Міжзонні та міжпідзонні (ISBT) оптичні переходи
# ════════════════════════════════════════════════════════════════════════════
def fig_optical_transitions():
    W, H = 840, 420
    f = []

    f.append(line(420, 30, 420, 390, color=MUTED, sw=1.5, dash="4 4"))

    # ── Ліва панель: Міжзонні ──
    f.append(text(210, 48, "Міжзонні переходи (Interband)", size=14, bold=True, color=INK))
    f.append(text(210, 68, "Перехід між валентною зоною та зоною провідності", size=11, color=MUTED))

    f.append(line(80, 140, 340, 140, color=POS, sw=2.2))
    f.append(line(80, 320, 340, 320, color=NEG, sw=2.2))
    f.append(text(345, 144, "E_c1 (електрон)", size=11, color=POS, bold=True, anchor="start"))
    f.append(text(345, 324, "E_v1 (дірка)", size=11, color=NEG, bold=True, anchor="start"))

    f.append(line(170, 310, 170, 155, color="#8e44ad", sw=2.5))
    f.append(polygon([(165, 155), (170, 145), (175, 155)], fill="#8e44ad"))
    f.append(circle(170, 320, 5, fill=NEG, stroke="#1f618d", sw=1.5))
    f.append(circle(170, 140, 5, fill=POS, stroke="#7b241c", sw=1.5))

    f.append(svg_path("M 100 230 Q 115 220 130 230 Q 145 240 160 230", stroke="#8e44ad", sw=2.0))
    f.append(polygon([(155, 226), (165, 230), (155, 234)], fill="#8e44ad"))
    f.append(text(125, 215, "hν_inter = E_g + E_n1 + E_hh1", size=11, color="#8e44ad", bold=True))

    f.append(text(210, 370, "Поляризація світла: довільна (TE або TM)", size=11, color=DARK, bold=True))
    f.append(text(210, 390, "Застосування: світлодіоди, лазерні діоди", size=11, color=MUTED))

    # ── Права панель: ISBT ──
    f.append(text(630, 48, "Міжпідзонні переходи (ISBT)", size=14, bold=True, color=INK))
    f.append(text(630, 68, "Перехід між підзонами в межах однієї зони (E_c)", size=11, color=MUTED))

    f.append(line(500, 270, 760, 270, color=POS, sw=2.2))
    f.append(line(500, 150, 760, 150, color=POS, sw=2.2))
    f.append(text(765, 274, "E_n1", size=11, color=POS, bold=True, anchor="start"))
    f.append(text(765, 154, "E_n2", size=11, color=POS, bold=True, anchor="start"))

    f.append(line(590, 260, 590, 165, color="#d35400", sw=2.5))
    f.append(polygon([(585, 165), (590, 155), (595, 165)], fill="#d35400"))
    f.append(circle(590, 270, 5, fill=POS, stroke="#7b241c", sw=1.5))
    f.append(circle(590, 150, 5, fill="#e67e22", stroke="#d35400", sw=1.5))

    f.append(svg_path("M 510 210 Q 530 200 550 210 Q 570 220 585 210", stroke="#d35400", sw=2.0))
    f.append(polygon([(580, 206), (588, 210), (580, 214)], fill="#d35400"))
    f.append(text(545, 195, "hν_ISBT = E_n2 - E_n1", size=11, color="#d35400", bold=True))

    f.append(text(630, 370, "Правило відбору: вектор E ∥ z (TM-поляризація)", size=11, color="#c0392b", bold=True))
    f.append(text(630, 390, "Застосування: QCL-лазери, QWIP-детектори", size=11, color=MUTED))

    render(os.path.join(OUT, "optical-transitions-intersubband.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 4 — Квантово-розмірний ефект Штарка (QCSE)
# ════════════════════════════════════════════════════════════════════════════
def fig_qcse_stark():
    W, H = 820, 420
    f = []

    f.append(line(410, 25, 410, 395, color=MUTED, sw=1.5, dash="4 4"))

    # ── Ліва панель: F = 0 ──
    f.append(text(205, 45, "Без електричного поля (F = 0)", size=14, bold=True, color=INK))

    f.append(svg_path("M 50 110 L 130 110 L 130 210 L 280 210 L 280 110 L 360 110", stroke=POS, sw=2.2))
    f.append(svg_path("M 50 350 L 130 350 L 130 270 L 280 270 L 280 350 L 360 350", stroke=NEG, sw=2.2))

    f.append(line(130, 185, 280, 185, color="#8e44ad", sw=1.6, dash="3 3"))
    f.append(line(130, 290, 280, 290, color="#16a085", sw=1.6, dash="3 3"))

    f.append(svg_path("M 130 185 Q 205 145 280 185", stroke="#8e44ad", sw=2.0))
    f.append(svg_path("M 130 290 Q 205 330 280 290", stroke="#16a085", sw=2.0))
    f.append(circle(205, 165, 4, fill=POS, stroke="#7b241c", sw=1.2))
    f.append(circle(205, 310, 4, fill=NEG, stroke="#1f618d", sw=1.2))

    f.append(text(205, 235, "Енергія перехода: E_0", size=11, bold=True, color=INK))
    f.append(text(205, 385, "Максимальне перекриття хвильових функцій", size=11, color=MUTED))

    # ── Права панель: F > 0 ──
    f.append(text(615, 45, "Під дією поля F (QCSE-ефект)", size=14, bold=True, color=INK))

    f.append(svg_path("M 460 90 L 540 120 L 540 250 L 690 200 L 690 90 L 770 120", stroke=POS, sw=2.2))
    f.append(svg_path("M 460 330 L 540 360 L 540 310 L 690 260 L 690 330 L 770 360", stroke=NEG, sw=2.2))

    f.append(line(540, 215, 690, 185, color="#8e44ad", sw=1.6, dash="3 3"))
    f.append(line(540, 298, 690, 268, color="#16a085", sw=1.6, dash="3 3"))

    f.append(svg_path("M 540 215 Q 580 180 690 185", stroke="#8e44ad", sw=2.0))
    f.append(svg_path("M 540 298 Q 650 315 690 268", stroke="#16a085", sw=2.0))
    f.append(circle(570, 200, 4, fill=POS, stroke="#7b241c", sw=1.2))
    f.append(circle(660, 290, 4, fill=NEG, stroke="#1f618d", sw=1.2))

    f.append(line(520, 65, 710, 65, color="#d35400", sw=2.0))
    f.append(polygon([(710, 61), (720, 65), (710, 69)], fill="#d35400"))
    f.append(text(615, 55, "Зовнішнє поле F ⊥ ямі", size=11, color="#d35400", bold=True))

    f.append(text(615, 235, "Червоне зміщення: E_F < E_0", size=11, bold=True, color=POS))
    f.append(text(615, 385, "Просторове розділення e-h та спад поглинання", size=11, color=MUTED))

    render(os.path.join(OUT, "qcse-stark-effect.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 5 — Структура SCH-лазера
# ════════════════════════════════════════════════════════════════════════════
def fig_sch_laser():
    W, H = 840, 400
    f = []

    f.append(rect(50, 70, 170, 240, fill="#eaeded", stroke=LINE))
    f.append(rect(220, 70, 150, 240, fill="#d5dbdb", stroke=LINE))
    f.append(rect(370, 70, 100, 240, fill="#fadbd8", stroke=POS, sw=2.0))
    f.append(rect(470, 70, 150, 240, fill="#d5dbdb", stroke=LINE))
    f.append(rect(620, 70, 170, 240, fill="#eaeded", stroke=LINE))

    f.append(text(135, 95, "p-Al_0.6 Ga_0.4 As", size=11, color=MUTED, bold=True))
    f.append(text(135, 115, "Емітер (n_clad = 3.2)", size=10, color=MUTED))

    f.append(text(295, 95, "Al_0.3 Ga_0.7 As", size=11, color=INK, bold=True))
    f.append(text(295, 115, "Хвилевід (n_wg = 3.4)", size=10, color=INK))

    f.append(text(420, 95, "GaAs яма", size=12, color=POS, bold=True))
    f.append(text(420, 115, "L_z = 8 нм", size=10, color=POS, bold=True))

    f.append(text(545, 95, "Al_0.3 Ga_0.7 As", size=11, color=INK, bold=True))
    f.append(text(545, 115, "Хвилевід (n_wg = 3.4)", size=10, color=INK))

    f.append(text(705, 95, "n-Al_0.6 Ga_0.4 As", size=11, color=MUTED, bold=True))
    f.append(text(705, 115, "Емітер (n_clad = 3.2)", size=10, color=MUTED))

    f.append(svg_path("M 50 260 L 220 260 L 220 200 L 370 200 L 370 170 L 470 170 L 470 200 L 620 200 L 620 260 L 790 260", stroke=NEG, sw=2.0))
    f.append(text(135, 275, "Профіль показника заломлення n(z)", size=11, color=NEG, bold=True))

    f.append(svg_path("M 60 290 Q 220 290 295 240 Q 420 130 545 240 Q 620 290 780 290", stroke="#d35400", sw=2.5, dash="6 3"))
    f.append(text(420, 150, "Оптична мода E_opt(z)", size=11, color="#d35400", bold=True))

    f.append(line(370, 330, 470, 330, color=POS, sw=1.5))
    f.append(line(370, 325, 370, 335, color=POS, sw=1.5))
    f.append(line(470, 325, 470, 335, color=POS, sw=1.5))
    f.append(text(420, 350, "Коефіцієнт обмеження Γ ≈ 2-3%", size=11, bold=True, color=POS))
    f.append(text(420, 375, "Роздільне утримання: носії в ямі L_z, фотони у хвилеводі L_wg", size=11, color=MUTED))

    render(os.path.join(OUT, "sch-laser-structure.svg"), W, H, *f)


if __name__ == "__main__":
    fig_confinement()
    fig_density_of_states()
    fig_optical_transitions()
    fig_qcse_stark()
    fig_sch_laser()
    print("Всі 5 фігур успішно згенеровано.")
