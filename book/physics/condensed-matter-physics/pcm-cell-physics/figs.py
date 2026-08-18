# -*- coding: utf-8 -*-
import sys, os
# Four levels up to reach scripts directory from book/physics/condensed-matter-physics/pcm-cell-physics
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

DARK = INK

def svg_path(d_str, stroke="#c0392b", sw=2.5, fill="none", dash=None):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d_str, stroke, sw, fill, d_attr)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Структура Mushroom Cell PCM
# ════════════════════════════════════════════════════════════════════════════
def fig_pcm_cell_structure():
    W, H = 820, 440
    f = []

    f.append(text(W/2, 30, "Конструкція грибоподібної комірки PCM (Mushroom Cell)", size=16, bold=True, color=INK))
    f.append(text(W/2, 52, "Розподіл фаз, нагрівальний електрод (BEC) та зона аморфізації", size=12, color=MUTED))

    # Верхній електрод (TEC - Top Electrode Contact)
    f.append(rect(180, 85, 460, 40, fill="#d5dbdb", stroke="#7f8c8d", sw=2, rx=4))
    f.append(text(W/2, 110, "Верхній електрод (TEC: TiN / Al)", size=12, bold=True, color="#2c3e50"))

    # Масив халькогеніду GST (Кристалічна фаза c-GST)
    f.append(rect(180, 125, 460, 130, fill="#d6eaf8", stroke="#2980b9", sw=2, rx=0))
    f.append(text(280, 160, "Кристалічна фаза GST (c-GST)", size=12, bold=True, color="#1b4f72"))
    f.append(text(280, 180, "Низький опір (Стан SET, R_ON)", size=11, color="#2980b9"))

    # Аморфна зона (RESET - Amorphous Dome / Hot Spot)
    f.append(svg_path("M 350 255 A 60 60 0 0 1 470 255 Z", stroke="#e74c3c", sw=2, fill="#fadbd8"))
    f.append(text(W/2, 220, "Аморфний купол (a-GST)", size=12, bold=True, color="#922b21"))
    f.append(text(W/2, 240, "Високий опір (RESET, R_OFF)", size=10.5, color="#c0392b"))

    # Теплоізолюючий діелектрик навколо нагрівача (SiO2 / SiNx)
    f.append(rect(180, 255, 190, 110, fill="#f4f6f7", stroke="#bdc3c7", sw=1.5, rx=0))
    f.append(rect(440, 255, 200, 110, fill="#f4f6f7", stroke="#bdc3c7", sw=1.5, rx=0))
    f.append(text(275, 305, "Термоізолюючий діелектрик", size=11, color="#7f8c8d"))
    f.append(text(275, 323, "(SiO₂ / SiN_x)", size=10, color="#95a5a6"))
    f.append(text(540, 305, "Термоізолюючий діелектрик", size=11, color="#7f8c8d"))
    f.append(text(540, 323, "(SiO₂ / SiN_x)", size=10, color="#95a5a6"))

    # Нагрівальний електрод (BEC - Bottom Electrode Contact / Heater)
    f.append(rect(370, 255, 70, 110, fill="#fdebd0", stroke="#d35400", sw=2, rx=2))
    f.append(text(W/2, 300, "Нагрівач", size=11, bold=True, color="#a04000"))
    f.append(text(W/2, 318, "(TiN Heater)", size=10, color="#d35400"))
    f.append(text(W/2, 336, "d ≈ 20 нм", size=9.5, bold=True, color="#ba4a00"))

    # Нижній електрод підкладки (Bottom Contact)
    f.append(rect(180, 365, 460, 35, fill="#d5dbdb", stroke="#7f8c8d", sw=2, rx=4))
    f.append(text(W/2, 387, "Нижній шинний контакт (Bottom Electrode)", size=12, bold=True, color="#2c3e50"))

    # Стрілки теплового випромінювання / градієнта від гарячої точки
    f.append(arrow(410, 245, 440, 210, color="#e67e22", sw=1.5))
    f.append(arrow(410, 245, 380, 210, color="#e67e22", sw=1.5))
    f.append(text(495, 195, "Гаряча точка (Hot Spot)", size=10.5, italic=True, color="#d35400"))

    render(os.path.join(OUT, "fig1-pcm-cell-structure.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Профілі імпульсів Reset / Set та часова температура
# ════════════════════════════════════════════════════════════════════════════
def fig_reset_set_pulses():
    W, H = 840, 420
    f = []

    f.append(text(W/2, 28, "Електричні імпульси Reset / Set та часовий температурний відгук", size=16, bold=True, color=INK))

    # Ліва панель: Електричні імпульси струму/напруги
    f.append(text(210, 60, "Електричні імпульси струму", size=13, bold=True, color=INK))
    
    # Осі для імпульсів
    f.append(arrow(50, 340, 390, 340, color=LINE, sw=1.5)) # Вісь t
    f.append(arrow(60, 350, 60, 80, color=LINE, sw=1.5))   # Вісь V/I
    f.append(text(395, 345, "t (ns)", size=11, color=MUTED))
    f.append(text(55, 75, "V / I", size=11, color=MUTED))

    # RESET імпульс
    f.append(svg_path("M 80 340 L 80 110 L 160 110 L 165 340", stroke="#c0392b", sw=2.5, fill="rgba(231,76,60,0.15)"))
    f.append(text(120, 100, "RESET", size=12, bold=True, color="#c0392b"))
    f.append(text(120, 130, "Швидкий спад", size=10, color="#922b21"))
    f.append(text(120, 145, "(t_f < 2 ns)", size=9.5, italic=True, color="#922b21"))

    # SET імпульс
    f.append(svg_path("M 200 340 L 200 210 L 280 210 L 360 340", stroke="#2980b9", sw=2.5, fill="rgba(52,152,219,0.15)"))
    f.append(text(250, 200, "SET імпульс", size=12, bold=True, color="#1b4f72"))
    f.append(text(290, 260, "Тривалий відпал", size=10, color="#2471a3"))
    f.append(text(290, 275, "(50 - 100 ns)", size=9.5, italic=True, color="#2471a3"))

    # Права панель: Температура комірки T(t) відносно T_m та T_g
    f.append(text(630, 60, "Температурний профіль T(t)", size=13, bold=True, color=INK))

    f.append(arrow(470, 340, 810, 340, color=LINE, sw=1.5)) # Вісь t
    f.append(arrow(480, 350, 480, 80, color=LINE, sw=1.5))   # Вісь T
    f.append(text(815, 345, "t (ns)", size=11, color=MUTED))
    f.append(text(475, 75, "T (°C)", size=11, color=MUTED))

    # Рівні температур T_m (600°C) та T_g (200°C)
    f.append(line(480, 130, 800, 130, color="#c0392b", sw=1.5, dash="4 4"))
    f.append(text(450, 134, "T_m (600°C)", size=10.5, bold=True, color="#c0392b"))

    f.append(line(480, 240, 800, 240, color="#27ae60", sw=1.5, dash="4 4"))
    f.append(text(450, 244, "T_g (200°C)", size=10.5, bold=True, color="#27ae60"))

    # Температура RESET
    f.append(svg_path("M 500 340 Q 520 100 540 100 L 550 100 Q 555 340 560 340", stroke="#e74c3c", sw=2.5, fill="none"))
    f.append(text(540, 90, "Плавлення T > T_m", size=10.5, bold=True, color="#c0392b"))
    f.append(text(575, 200, "Загартування (Quenching)", size=10, bold=True, color="#922b21"))
    f.append(text(575, 215, "dT/dt > 10⁹ K/s", size=9.5, italic=True, color="#922b21"))

    # Температура SET
    f.append(svg_path("M 610 340 Q 630 180 650 180 L 730 180 Q 770 340 790 340", stroke="#2980b9", sw=2.5, fill="none"))
    f.append(text(690, 170, "Вікно кристалізації (T_g < T < T_m)", size=10.5, bold=True, color="#1b4f72"))

    render(os.path.join(OUT, "fig2-reset-set-pulses.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Порогове перемикання Овшинського (I-V curve)
# ════════════════════════════════════════════════════════════════════════════
def fig_ovshinsky_iv_curve():
    W, H = 820, 430
    f = []

    f.append(text(W/2, 28, "Вольт-амперна характеристика (I-V) та порогове перемикання Овшинського", size=16, bold=True, color=INK))

    # Осі I-V
    f.append(arrow(80, 360, 760, 360, color=LINE, sw=1.5)) # Напруга V
    f.append(arrow(100, 380, 100, 60, color=LINE, sw=1.5))  # Струм I
    f.append(text(765, 365, "Напруга V (В)", size=11, bold=True, color=INK))
    f.append(text(95, 52, "Струм I (мА)", size=11, bold=True, color=INK))

    # Стан SET (Кристалічний)
    f.append(line(100, 360, 420, 90, color="#2980b9", sw=2.5))
    f.append(text(280, 180, "Стан SET (Кристалічний, R_ON)", size=12, bold=True, color="#1b4f72"))

    # Стан RESET (Аморфний підпороговий стан OFF)
    f.append(svg_path("M 100 360 Q 350 355 550 330", stroke="#c0392b", sw=2.5, fill="none"))
    f.append(text(330, 345, "Стан RESET (Аморфний OFF, R_OFF)", size=12, bold=True, color="#922b21"))

    # Порогова точка V_th, I_th
    f.append(circle(550, 330, 5, fill="#e74c3c", stroke="#922b21", sw=1.5))
    f.append(line(550, 330, 550, 360, color="#c0392b", sw=1.5, dash="3 3"))
    f.append(text(550, 375, "V_th", size=11, bold=True, color="#c0392b"))
    f.append(text(585, 325, "Порогова точка (V_th, I_th)", size=11, bold=True, color="#c0392b"))

    # Снапбек / Негативний диференціальний опір
    f.append(svg_path("M 550 330 Q 380 300 320 175", stroke="#e67e22", sw=2.5, dash="5 4", fill="none"))
    f.append(text(460, 270, "Лавинний перехід (Snapback)", size=11, bold=True, color="#d35400"))
    f.append(text(460, 288, "Негативний опір (NDR)", size=10, italic=True, color="#e67e22"))

    # Динамічний стан ON
    f.append(svg_path("M 320 175 Q 350 120 400 90", stroke="#27ae60", sw=2.5, fill="none"))
    f.append(text(410, 115, "Динамічний ON-стан", size=11, bold=True, color="#1e8449"))

    # Напруга утримання V_hold
    f.append(line(320, 175, 320, 360, color="#7f8c8d", sw=1.5, dash="3 3"))
    f.append(text(320, 375, "V_hold", size=11, bold=True, color="#7f8c8d"))

    render(os.path.join(OUT, "fig3-ovshinsky-iv-curve.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 4 — Дрейф опору (Resistance Drift) та MLC рівні
# ════════════════════════════════════════════════════════════════════════════
def fig_resistance_drift():
    W, H = 840, 430
    f = []

    f.append(text(W/2, 28, "Дрейф опору R(t) аморфного стану та зсув порогових вікон MLC", size=16, bold=True, color=INK))

    # Осі Log(R) vs Log(t)
    f.append(arrow(80, 360, 770, 360, color=LINE, sw=1.5)) # log t
    f.append(arrow(100, 380, 100, 60, color=LINE, sw=1.5))  # log R
    f.append(text(775, 365, "Час log₁₀(t)", size=11, bold=True, color=INK))
    f.append(text(95, 52, "Опір log₁₀(R)", size=11, bold=True, color=INK))

    # Стан SET (Кристалічний)
    f.append(line(100, 310, 740, 310, color="#2980b9", sw=2.5))
    f.append(text(420, 300, "Стан SET (Кристалічний, v ≈ 0.001)", size=11.5, bold=True, color="#1b4f72"))

    # Стан RESET - Повний аморфний стан
    f.append(line(100, 140, 740, 80, color="#c0392b", sw=2.5))
    f.append(text(460, 95, "Стан RESET (Аморфний, R(t) = R_0 · (t/t_0)^v, v ≈ 0.10)", size=11.5, bold=True, color="#922b21"))

    # Проміжні стани MLC (2-bit per cell: 10, 01)
    f.append(line(100, 200, 740, 155, color="#e67e22", sw=2, dash="6 4"))
    f.append(text(460, 165, "Проміжний стан MLC '01' (Частковий RESET, v ≈ 0.06)", size=10.5, color="#d35400"))

    f.append(line(100, 255, 740, 230, color="#d4ac0d", sw=2, dash="6 4"))
    f.append(text(460, 235, "Проміжний стан MLC '10' (Частковий SET, v ≈ 0.03)", size=10.5, color="#b7950b"))

    # Початкова точка вимірювання t_0 = 1 с
    f.append(line(180, 80, 180, 360, color="#7f8c8d", sw=1.5, dash="3 3"))
    f.append(text(180, 375, "t_0 (1 с)", size=10.5, bold=True, color="#7f8c8d"))

    # Точка тривалої експлуатації t = 10^8 с
    f.append(line(680, 80, 680, 360, color="#c0392b", sw=1.5, dash="3 3"))
    f.append(text(680, 375, "t (10⁸ с)", size=10.5, bold=True, color="#c0392b"))

    # Стрілки порогового вікна та звуження марджіну
    f.append(line(680, 90, 680, 150, color="#e74c3c", sw=2))
    f.append(text(725, 120, "Звуження вікна", size=10, bold=True, color="#c0392b"))
    f.append(text(725, 134, "помилок MLC", size=9.5, color="#922b21"))

    render(os.path.join(OUT, "fig4-resistance-drift.svg"), W, H, *f)


if __name__ == "__main__":
    fig_pcm_cell_structure()
    fig_reset_set_pulses()
    fig_ovshinsky_iv_curve()
    fig_resistance_drift()
    print("Всі 4 фігури успішно згенеровано у img/")
