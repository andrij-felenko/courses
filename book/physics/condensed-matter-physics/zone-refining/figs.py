# -*- coding: utf-8 -*-
import sys, os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def svg_path(d_str, stroke=LINE, sw=2.0, fill="none", dash=None):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d_str, stroke, sw, fill, d_attr)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Схема бестигельного зонного очищення (Float Zone)
# ════════════════════════════════════════════════════════════════════════════
def fig_zone_refining_principle():
    W, H = 820, 500
    f = []

    f.append(text(410, 25, "Принцип бестигельного зонного очищення (Float Zone Process)", size=15, bold=True, color=INK))

    # Верхній полікристалічний зливок кремнію
    f.append(rect(360, 50, 100, 130, fill="#d6eaf8", stroke=LINE, sw=2.0, rx=4))
    f.append(text(410, 115, "Полікристалічний", size=12, bold=True, color="#1b4f72"))
    f.append(text(410, 133, "кремній (сировина)", size=11, color="#1b4f72"))

    # Рух зливка униз
    f.append(arrow(310, 80, 310, 150, color=POS, sw=2.5))
    f.append(text(250, 115, "Подача", size=12, bold=True, color=POS))
    f.append(text(250, 132, "униз", size=11, color=POS))

    # Рідка розплавлена зона
    f.append(svg_path("M 360 180 C 345 205, 345 225, 360 250 L 460 250 C 475 225, 475 205, 460 180 Z", stroke=POS, sw=2.5, fill="#fadbd8"))
    f.append(text(410, 210, "Розплавлена зона", size=12, bold=True, color=POS))
    f.append(text(410, 228, "(поверхневий натяг)", size=10, bold=True, color=POS))

    # ВЧ-Індуктор (нагрівальні котушки з боків)
    f.append(circle(325, 200, 14, fill="#f5b041", stroke=LINE, sw=2.0))
    f.append(circle(325, 230, 14, fill="#f5b041", stroke=LINE, sw=2.0))
    f.append(text(325, 204, "~", size=14, bold=True, color=INK))
    f.append(text(325, 234, "~", size=14, bold=True, color=INK))

    f.append(circle(495, 200, 14, fill="#f5b041", stroke=LINE, sw=2.0))
    f.append(circle(495, 230, 14, fill="#f5b041", stroke=LINE, sw=2.0))
    f.append(text(495, 204, "~", size=14, bold=True, color=INK))
    f.append(text(495, 234, "~", size=14, bold=True, color=INK))

    f.append(text(240, 215, "ВЧ-індуктор нагріву", size=12, bold=True, color="#b9770e"))

    # Фронт кристалізації
    f.append(line(360, 250, 460, 250, color=FIELD, sw=2.5, dash="4 2"))
    f.append(arrow(550, 250, 470, 250, color=FIELD, sw=2.0))
    f.append(text(640, 253, "Фронт кристалізації (фазовий перехід)", size=11, bold=True, color=FIELD))

    # Нижня вирощена монокристалічна частина
    f.append(rect(360, 250, 100, 160, fill="#e8f8f5", stroke=LINE, sw=2.0, rx=4))
    f.append(text(410, 320, "Чистий монокристал Si", size=12, bold=True, color="#117a65"))
    f.append(text(410, 340, "(висока чистота)", size=11, color="#117a65"))

    # Затравочний кристал у самому низу
    f.append(rect(385, 410, 50, 40, fill="#a3e4d7", stroke=LINE, sw=1.5, rx=2))
    f.append(text(410, 434, "Затравка [111]", size=10, bold=True, color=INK))

    # Напрямок переміщення зони відносно зливка
    f.append(arrow(560, 330, 560, 120, color=NEG, sw=2.5))
    f.append(text(660, 210, "Напрямок руху розплавленої зони", size=12, bold=True, color=NEG))
    f.append(text(660, 230, "Домішки вимиваються вгору! (k₀ < 1)", size=11, color=POS))

    render(os.path.join(OUT, "zone-refining-principle.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Фазова діаграма стану та коефіцієнт сегрегації
# ════════════════════════════════════════════════════════════════════════════
def fig_phase_diagram_segregation():
    W, H = 820, 480
    f = []

    f.append(text(410, 25, "Фазова діаграма двокомпонентного розчину та коефіцієнт сегрегації k₀", size=15, bold=True, color=INK))

    # Вісі
    f.append(line(100, 420, 750, 420, color=LINE, sw=1.5))
    f.append(line(100, 420, 100, 70, color=LINE, sw=1.5))
    f.append(text(425, 455, "Концентрація домішки C →", size=12, color=INK))
    f.append(text(40, 235, "Температура T →", size=12, color=INK))

    # Лінія плавлення чистого кремнію T_m
    f.append(line(90, 90, 110, 90, color=LINE, sw=1.5))
    f.append(text(65, 94, "T_m", size=12, bold=True, color=INK))

    # Ліквідус та Солідус для k0 < 1
    p_liq = "M 100 90 C 300 160, 500 280, 720 400"
    p_sol = "M 100 90 C 200 240, 320 360, 450 420"

    f.append(svg_path(p_liq, stroke=NEG, sw=2.5))
    f.append(svg_path(p_sol, stroke=POS, sw=2.5))

    f.append(text(560, 260, "Ліквідус (Рідина L)", size=12, bold=True, color=NEG))
    f.append(text(270, 240, "Солідус (Тверде тіло S)", size=12, bold=True, color=POS))

    # Горизонтальна ізотерма T_1
    T1_y = 220
    f.append(line(100, T1_y, 600, T1_y, color=MUTED, sw=1.2, dash="4 4"))
    f.append(text(70, T1_y + 4, "T₁", size=12, bold=True, color=INK))

    CS_x = 190
    CL_x = 410

    f.append(circle(CS_x, T1_y, 5, fill=POS, stroke=LINE, sw=1.5))
    f.append(circle(CL_x, T1_y, 5, fill=NEG, stroke=LINE, sw=1.5))

    f.append(line(CS_x, T1_y, CS_x, 420, color=POS, sw=1.2, dash="3 3"))
    f.append(line(CL_x, T1_y, CL_x, 420, color=NEG, sw=1.2, dash="3 3"))

    f.append(text(CS_x, 438, "C_S", size=12, bold=True, color=POS))
    f.append(text(CL_x, 438, "C_L", size=12, bold=True, color=NEG))

    f.append(arrow(CS_x + 10, T1_y - 30, CS_x, T1_y - 5, color=POS, sw=1.5))
    f.append(arrow(CL_x - 10, T1_y - 30, CL_x, T1_y - 5, color=NEG, sw=1.5))

    fb, fw, fh = textbox(520, 130, "Рівноважний коефіцієнт сегрегації:\nk₀ = C_S / C_L < 1\n(домішка відкидається в розплав)", size=12, pad=10, fill="#fcf3cf", stroke="#f39c12", sw=1.5)
    f.append(fb)

    render(os.path.join(OUT, "phase-diagram-segregation.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Профілі розподілу домішок після різної кількості проходів
# ════════════════════════════════════════════════════════════════════════════
def fig_concentration_profile_passes():
    W, H = 820, 500
    f = []

    f.append(text(410, 25, "Розподіл домішки C(x)/C₀ вздовж зливка при k₀ = 0.1 та l/L = 0.1", size=15, bold=True, color=INK))

    # Вісі
    f.append(line(100, 420, 750, 420, color=LINE, sw=1.5))
    f.append(line(100, 420, 100, 60, color=LINE, sw=1.5))

    f.append(text(425, 455, "Відносна довжина зливка x/L →", size=12, color=INK))
    f.append(text(40, 235, "C(x) / C₀ (лог. масштаб) →", size=12, color=INK))

    f.append(line(100, 200, 750, 200, color=MUTED, sw=1.5, dash="6 4"))
    f.append(text(70, 204, "C₀ (1.0)", size=11, bold=True, color=MUTED))

    # 1 прохід
    p_n1 = "M 100 340 L 200 330 L 400 310 L 600 260 L 680 190 C 700 150, 730 80, 750 70"
    f.append(svg_path(p_n1, stroke="#e74c3c", sw=2.0))
    f.append(text(610, 245, "n = 1", size=11, bold=True, color="#e74c3c"))

    # 3 проходи
    p_n3 = "M 100 370 L 200 365 L 400 345 L 600 290 L 670 210 C 690 140, 720 75, 750 70"
    f.append(svg_path(p_n3, stroke="#e67e22", sw=2.0))
    f.append(text(550, 310, "n = 3", size=11, bold=True, color="#e67e22"))

    # 10 проходів
    p_n10 = "M 100 400 L 200 395 L 400 385 L 580 340 L 660 230 C 680 130, 720 75, 750 70"
    f.append(svg_path(p_n10, stroke="#27ae60", sw=2.2))
    f.append(text(480, 370, "n = 10", size=11, bold=True, color="#27ae60"))

    # Граничний розподіл
    p_ultimate = "M 100 415 L 300 413 L 500 405 L 620 380 L 660 250 C 680 120, 720 75, 750 70"
    f.append(svg_path(p_ultimate, stroke="#2980b9", sw=2.5, dash="4 2"))
    f.append(text(340, 400, "Межа очищення (n → ∞)", size=11, bold=True, color="#2980b9"))

    f.append(rect(120, 80, 220, 45, fill="#e8f8f5", stroke="#27ae60", sw=1.2, rx=4))
    f.append(text(230, 100, "Очищена область монокристала", size=11, bold=True, color="#117a65"))
    f.append(text(230, 115, "(вміст домішок знижено у 10²–10⁴ разів)", size=9, color="#117a65"))

    f.append(rect(540, 80, 190, 45, fill="#fadbd8", stroke="#c0392b", sw=1.2, rx=4))
    f.append(text(635, 100, "Брудний «хвіст» (зрізається)", size=11, bold=True, color="#922b21"))
    f.append(text(635, 115, "накопичення домішок", size=9, color="#922b21"))

    render(os.path.join(OUT, "concentration-profile-passes.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 4 — Дифузійний приповерхневий шар (Модель BPS)
# ════════════════════════════════════════════════════════════════════════════
def fig_boundary_layer_bps():
    W, H = 820, 480
    f = []

    f.append(text(410, 25, "Дифузійний приповерхневий шар товщиною δ у моделі Бертона — Прімма — Сліхтера", size=15, bold=True, color=INK))

    f.append(rect(60, 60, 200, 360, fill="#e8f8f5", stroke="none"))
    f.append(text(160, 90, "Твердий кристал Si", size=13, bold=True, color="#117a65"))

    f.append(rect(260, 60, 180, 360, fill="#fcf3cf", stroke="none"))
    f.append(text(350, 90, "Дифузійний шар δ", size=12, bold=True, color="#b9770e"))

    f.append(rect(440, 60, 320, 360, fill="#ebf5fb", stroke="none"))
    f.append(text(600, 90, "Об'єм рідкої зони (конвекція)", size=13, bold=True, color="#1b4f72"))

    f.append(line(260, 60, 260, 420, color=LINE, sw=2.5))
    f.append(text(260, 440, "z = 0 (фронт)", size=11, bold=True, color=INK))

    f.append(line(440, 60, 440, 420, color=MUTED, sw=1.5, dash="4 4"))
    f.append(text(440, 440, "z = δ", size=11, bold=True, color=MUTED))

    f.append(line(60, 420, 760, 420, color=LINE, sw=1.5))
    f.append(text(730, 440, "Координата z →", size=11, color=INK))

    f.append(line(80, 340, 260, 340, color=POS, sw=2.5))
    f.append(text(160, 330, "C_S = k₀ · C_L(0)", size=11, bold=True, color=POS))

    f.append(line(260, 340, 260, 150, color=POS, sw=1.5, dash="2 2"))

    p_bps = "M 260 150 C 310 160, 380 250, 440 260 L 740 260"
    f.append(svg_path(p_bps, stroke=NEG, sw=2.5))

    f.append(circle(260, 150, 5, fill=POS, stroke=LINE, sw=1.5))
    f.append(text(230, 153, "C_L(0)", size=11, bold=True, color=POS))

    f.append(circle(440, 260, 5, fill=NEG, stroke=LINE, sw=1.5))
    f.append(text(465, 255, "C_L (в об'ємі)", size=11, bold=True, color=NEG))

    f.append(line(260, 380, 440, 380, color="#b9770e", sw=1.5))
    f.append(arrow(310, 380, 260, 380, color="#b9770e", sw=1.5))
    f.append(arrow(390, 380, 440, 380, color="#b9770e", sw=1.5))
    f.append(text(350, 375, "Товщина δ", size=11, bold=True, color="#b9770e"))

    fb, fw, fh = textbox(600, 340, "Формула BPS:\nk_eff = k₀ / [ k₀ + (1 − k₀) e^(−vδ/D) ]\n• v → 0 ⇒ k_eff → k₀ (макс. очищення)\n• v → ∞ ⇒ k_eff → 1 (без очищення)", size=11, pad=10, fill="#f4f6f8", stroke=LINE, sw=1.2)
    f.append(fb)

    render(os.path.join(OUT, "boundary-layer-bps.svg"), W, H, *f)

if __name__ == "__main__":
    fig_zone_refining_principle()
    fig_phase_diagram_segregation()
    fig_concentration_profile_passes()
    fig_boundary_layer_bps()
    print("Figures generated successfully.")
