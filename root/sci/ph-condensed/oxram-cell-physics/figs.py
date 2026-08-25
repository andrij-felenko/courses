# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

DARK = INK

def polygon(points, fill=DARK, stroke="none", sw=1.0):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    st = ' stroke="%s" stroke-width="%.1f"' % (stroke, sw) if stroke != "none" else ''
    return '<polygon points="%s" fill="%s"%s/>' % (pts_str, fill, st)

def path(d_str, stroke="#c0392b", sw=2.5, fill="none", dash=None):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d_str, stroke, sw, fill, d_attr)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Структура осередку OxRAM (MIM) у станах HRS та LRS
# ════════════════════════════════════════════════════════════════════════════
def fig_oxram_cell_structure():
    W, H = 860, 440
    f = []

    # Розділювальна лінія між панелями
    f.append(line(430, 25, 430, 415, color=MUTED, sw=1.5, dash="4 4"))

    # ── Ліва панель: Високорезистивний стан (HRS / OFF) ──
    f.append(text(215, 38, "Високорезистивний стан (HRS / «0»)", size=14, bold=True, color=INK))
    f.append(text(215, 58, "Розірваний оксидний філамент (розрив x_gap)", size=11.5, color=MUTED))

    # Верхній електрод TE (TiN / Ti reservoir)
    f.append(rect(60, 85, 310, 35, fill="#d6eaf8", stroke="#2980b9", sw=2))
    f.append(text(215, 107, "Верхній електрод TE (TiN / Ti Scavenging)", size=11, bold=True, color="#1b4f72"))

    # Оксидний шар HfO₂-x (діелектричний перехідний шар)
    f.append(rect(60, 120, 310, 170, fill="#fef9e7", stroke="#f39c12", sw=2))
    f.append(text(125, 140, "Функціональний оксид HfO₂-x", size=10.5, color="#7e5109"))

    # Нижній електрод BE (Pt / TiN)
    f.append(rect(60, 290, 310, 45, fill="#eaeded", stroke="#7f8c8d", sw=2))
    f.append(text(215, 317, "Нижній електрод BE (Pt / TiN)", size=11, bold=True, color="#2c3e50"))

    # Нитка філамента у HRS (недобудована, є розрив біля TE)
    f.append(rect(195, 185, 40, 105, fill="#fadbd8", stroke="#e74c3c", sw=1.5))
    f.append(text(215, 235, "CF", size=11, bold=True, color="#c0392b"))

    # Дефектні вакансії кисню (червоні кола V_O)
    for vy in [195, 215, 235, 255, 275]:
        for vx in [203, 215, 227]:
            f.append(circle(vx, vy, 4, fill="#e74c3c", stroke="#922b21", sw=1))

    # Розрив зазору x_gap (діелектричний бар'єр тунелювання)
    f.append(rect(190, 122, 50, 60, fill="#fcf3cf", stroke="#f1c40f", sw=1.5))
    f.append(line(245, 125, 245, 180, color="#d4ac0d", sw=1.5))
    f.append(text(285, 155, "Зазор x_gap ≈ 1 нм", size=10.5, bold=True, color="#b7950b"))
    f.append(line(245, 152, 268, 152, color="#b7950b", sw=1.2))

    # Іони кисню O²⁻ накопичені у шарі поглинання Ti
    for ox in [90, 140, 280, 330]:
        f.append(circle(ox, 102, 6, fill="#3498db", stroke="#1b4f72", sw=1))
        f.append(text(ox, 105, "O²⁻", size=9, color="#ffffff"))

    # Опис струму у HRS
    f.append(text(215, 360, "Струм обмежений тунелюванням:", size=11, bold=True, color="#c0392b"))
    f.append(text(215, 380, "I_HRS ≈ 10⁻⁸–10⁻⁶ А (Пуль — Френкель / TAT)", size=10.5, color=DARK))
    f.append(text(215, 400, "Високий опір R_HRS ≈ 10⁶–10⁸ Ом", size=10.5, color=DARK))


    # ── Права панель: Низькорезистивний стан (LRS / ON) ──
    f.append(text(645, 38, "Низькорезистивний стан (LRS / «1»)", size=14, bold=True, color=INK))
    f.append(text(645, 58, "Неперервний провідний кисневий філамент", size=11.5, color=MUTED))

    # Верхній електрод TE (TiN / Ti)
    f.append(rect(490, 85, 310, 35, fill="#d6eaf8", stroke="#2980b9", sw=2))
    f.append(text(645, 107, "Верхній електрод TE (+V_SET)", size=11, bold=True, color="#1b4f72"))

    # Оксидний шар HfO₂-x
    f.append(rect(490, 120, 310, 170, fill="#fef9e7", stroke="#f39c12", sw=2))
    f.append(text(555, 140, "Оксидна матриця HfO₂", size=10.5, color="#7e5109"))

    # Нижній електрод BE (Pt / TiN)
    f.append(rect(490, 290, 310, 45, fill="#eaeded", stroke="#7f8c8d", sw=2))
    f.append(text(645, 317, "Нижній електрод BE (Земля / GND)", size=11, bold=True, color="#2c3e50"))

    # Повний неперервний провідний філамент CF (від BE до TE)
    f.append(rect(625, 120, 40, 170, fill="#fadbd8", stroke="#e74c3c", sw=2))

    # Густа сітка кисневих вакансій V_O
    for vy in range(125, 286, 16):
        for vx in [633, 645, 657]:
            f.append(circle(vx, vy, 4, fill="#e74c3c", stroke="#922b21", sw=1))

    # Потік електронів крізь філамент
    f.append(line(645, 285, 645, 125, color="#27ae60", sw=2.5))
    f.append(polygon([(645, 120), (640, 130), (650, 130)], fill="#27ae60"))
    f.append(text(685, 205, "Струм I_LRS", size=11, bold=True, color="#27ae60"))

    # Опис струму у LRS
    f.append(text(645, 360, "Металевий / омічний транспорт:", size=11, bold=True, color="#27ae60"))
    f.append(text(645, 380, "I_LRS ≈ 10⁻⁴–10⁻³ А (балістичний / квазіомічний)", size=10.5, color=DARK))
    f.append(text(645, 400, "Низький опір R_LRS ≈ 10³–10⁴ Ом", size=10.5, color=DARK))

    render(os.path.join(OUT, "oxram-cell-structure.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Вольт-амперна гістерезисна характеристика OxRAM (Forming, SET, RESET)
# ════════════════════════════════════════════════════════════════════════════
def fig_forming_set_reset_cycle():
    W, H = 860, 440
    f = []

    f.append(text(430, 30, "Вольт-амперна ВАХ комірки OxRAM (Двополярне перемикання)", size=14, bold=True, color=INK))

    # Вісі координат (Струм I у логарифмічному масштабі vs Напруга V)
    ox, oy = 430, 240
    f.append(line(60, oy, 800, oy, color=INK, sw=1.5)) # Вісь V
    f.append(line(ox, 50, ox, 390, color=INK, sw=1.5)) # Вісь I

    f.append(text(810, oy + 4, "V (В)", size=12, bold=True, color=INK))
    f.append(text(ox + 10, 45, "I (А, лог. масштаб)", size=12, bold=True, color=INK))

    # Позначки напруг
    f.append(line(ox + 120, oy - 5, ox + 120, oy + 5, color=INK, sw=1.2))
    f.append(text(ox + 120, oy + 20, "V_SET (~1.2 В)", size=10.5, bold=True, color="#27ae60"))

    f.append(line(ox + 260, oy - 5, ox + 260, oy + 5, color=INK, sw=1.2))
    f.append(text(ox + 260, oy + 20, "V_FORMING (~3.0 В)", size=10.5, bold=True, color="#8e44ad"))

    f.append(line(ox - 150, oy - 5, ox - 150, oy + 5, color=INK, sw=1.2))
    f.append(text(ox - 150, oy + 20, "V_RESET (~ -1.0 В)", size=10.5, bold=True, color="#c0392b"))

    # Рівень обмеження струму Compliance Current I_comp
    f.append(line(80, 100, 780, 100, color="#d35400", sw=1.5, dash="4 4"))
    f.append(text(160, 90, "Струм обмеження I_comp (1T1R)", size=10.5, bold=True, color="#d35400"))

    # 1. Крива Формоутворення (Forming) — фіолетова
    path_forming = f"M {ox} {oy} Q {ox + 150} {oy - 10} {ox + 260} {oy - 30} L {ox + 260} 100"
    f.append(path(path_forming, stroke="#8e44ad", sw=2.5, fill="none"))
    f.append(text(ox + 200, oy - 45, "① Формоутворення (Forming)", size=11, bold=True, color="#8e44ad"))

    # 2. Крива RESET (з LRS у HRS) — червона
    path_reset = f"M {ox} {oy - 140} L {ox - 150} {oy - 140} Q {ox - 160} {oy - 50} {ox - 120} {oy + 120} L {ox} {oy}"
    f.append(path(path_reset, stroke="#c0392b", sw=2.5, fill="none"))
    f.append(text(ox - 240, oy - 110, "② RESET (Розрив CF)", size=11, bold=True, color="#c0392b"))

    # 3. Крива HRS (зчитування у закритому стані) — сіра / помаранчева
    path_hrs = f"M {ox} {oy} Q {ox + 60} {oy + 80} {ox + 120} {oy + 110}"
    f.append(path(path_hrs, stroke="#f39c12", sw=2, fill="none"))
    f.append(text(ox + 60, oy + 130, "Стан HRS (R_HRS)", size=10.5, bold=True, color="#d35400"))

    # 4. Крива SET (з HRS у LRS) — зелена
    path_set = f"M {ox + 120} {oy + 110} L {ox + 120} 100 L {ox} 100"
    f.append(path(path_set, stroke="#27ae60", sw=2.5, fill="none"))
    f.append(text(ox + 140, 135, "③ SET (Відновлення CF)", size=11, bold=True, color="#27ae60"))

    # 5. Лінія LRS — провідний стан
    f.append(line(ox, 100, ox, oy - 140, color="#27ae60", sw=2.5))
    f.append(text(ox - 100, oy - 120, "Стан LRS (R_LRS)", size=10.5, bold=True, color="#27ae60"))

    # Легенда
    f.append(rect(60, 315, 330, 100, fill="#f8f9f9", stroke="#bdc3c7", sw=1.5))
    f.append(text(75, 335, "Легенда перемикання:", size=11, bold=True, color=INK, anchor="start"))
    f.append(text(75, 355, "• Forming: м'який пробій fresh-осередку", size=10, color="#8e44ad", anchor="start"))
    f.append(text(75, 375, "• SET (V > V_SET): міграція V_O, закриття x_gap", size=10, color="#27ae60", anchor="start"))
    f.append(text(75, 395, "• RESET (V < V_RESET): джоулів розрив CF", size=10, color="#c0392b", anchor="start"))

    render(os.path.join(OUT, "forming-set-reset-cycle.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Потенціальний рельєф мигтіння вакансій кисню під полем та без поля
# ════════════════════════════════════════════════════════════════════════════
def fig_vacancy_energy_landscape():
    W, H = 860, 400
    f = []

    # ── Верхня частина: Рівноважний стан без електричного поля (E = 0) ──
    f.append(text(215, 30, "а) Рівноважне термічне стрибання (E = 0)", size=13, bold=True, color=INK))

    # Симетричні потенціальні ями
    py0 = 140
    path_e0 = f"M 40 {py0} Q 65 {py0 - 60} 90 {py0} Q 115 {py0 - 60} 140 {py0} Q 165 {py0 - 60} 190 {py0} Q 215 {py0 - 60} 240 {py0} Q 265 {py0 - 60} 290 {py0} Q 315 {py0 - 60} 340 {py0}"
    f.append(path(path_e0, stroke="#2980b9", sw=2.5, fill="none"))

    # Базовий рівень та висота бар'єра E_a
    f.append(line(40, py0, 340, py0, color=MUTED, sw=1, dash="3 3"))
    f.append(line(90, py0 - 60, 140, py0 - 60, color="#c0392b", sw=1.2, dash="2 2"))
    f.append(line(115, py0, 115, py0 - 60, color="#c0392b", sw=1.5))
    f.append(text(125, py0 - 30, "E_a", size=11, bold=True, color="#c0392b"))

    # Відстань між ямами (період ґратки a)
    f.append(line(90, py0 + 15, 140, py0 + 15, color=DARK, sw=1.2))
    f.append(text(115, py0 + 32, "a", size=11, bold=True, color=DARK))

    # Іон кисню у ямі
    f.append(circle(90, py0 - 8, 7, fill="#3498db", stroke="#1b4f72", sw=1.5))
    f.append(text(90, py0 - 5, "O²⁻", size=9, color="#ffffff"))
    f.append(text(215, 185, "Стрибки однаково ймовірні в обидва боки", size=10.5, color=MUTED))


    # ── Нижня частина: Спрямований дрейф під сильним полем (E > 0) ──
    f.append(text(645, 30, "б) Спрямований дрейф у сильному полі (E >> 0)", size=13, bold=True, color=INK))

    # Нахилений потенціальний рельєф через потенціал -q·E·x
    py1 = 105
    path_e1 = f"M 470 {py1} Q 495 {py1 - 45} 520 {py1 + 25} Q 545 {py1 - 20} 570 {py1 + 50} Q 595 {py1 + 5} 620 {py1 + 75} Q 645 {py1 + 30} 670 {py1 + 100} Q 695 {py1 + 55} 720 {py1 + 125}"
    f.append(path(path_e1, stroke="#27ae60", sw=2.5, fill="none"))

    # Знижений бар'єр у напрямку поля ΔE = q·α·E / 2
    f.append(line(520, py1 + 25, 570, py1 - 20, color="#c0392b", sw=1.2, dash="2 2"))
    f.append(text(600, py1 + 15, "E_a - q·α·E / 2", size=10.5, bold=True, color="#c0392b"))

    # Напрямок електричного поля E та дрейфу іонів/вакансій
    f.append(line(470, 250, 720, 250, color="#8e44ad", sw=2.5))
    f.append(polygon([(725, 250), (715, 245), (715, 255)], fill="#8e44ad"))
    f.append(text(600, 268, "Електричне поле E", size=11, bold=True, color="#8e44ad"))

    # Іон кисню O²⁻ рухається проти поля, вакансії V_O — за полем
    f.append(circle(570, py1 + 40, 8, fill="#e74c3c", stroke="#922b21", sw=1.5))
    f.append(text(570, py1 + 43, "V_O", size=9, bold=True, color="#ffffff"))
    f.append(line(570, py1 + 40, 620, py1 + 65, color="#e74c3c", sw=2))
    f.append(polygon([(625, py1 + 67), (617, py1 + 58), (615, py1 + 66)], fill="#e74c3c"))

    # Формула Мотта — Ґерні
    f.append(rect(180, 310, 500, 65, fill="#f4f6f7", stroke="#bdc3c7", sw=1.5))
    f.append(text(430, 332, "Швидкість йонного мигтіння Мотта — Ґерні:", size=11, bold=True, color=INK))
    f.append(text(430, 355, "v = v₀ · exp(-E_a / (k_B·T)) · sinh(q·a·E / (2·k_B·T))", size=11, bold=True, color="#2980b9"))

    render(os.path.join(OUT, "vacancy-energy-landscape.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 4 — Температурний профіль джоулевого нагріву у звуженні філамента
# ════════════════════════════════════════════════════════════════════════════
def fig_thermal_joule_profile():
    W, H = 860, 400
    f = []

    f.append(text(430, 30, "Профіль температури T(z) та термоформування при RESET", size=14, bold=True, color=INK))

    # ── Ліва сторона: Схема звуження провідного каналу ──
    f.append(text(215, 65, "Звуження філамента (Constriction)", size=12, bold=True, color=INK))

    # Верхній та нижній електроди як тепловідводи (T0 = 300 K)
    f.append(rect(60, 85, 310, 25, fill="#d6eaf8", stroke="#2980b9", sw=1.5))
    f.append(text(215, 102, "Верхній електрод TE (T_0 = 300 K)", size=10.5, color="#1b4f72"))

    f.append(rect(60, 275, 310, 25, fill="#eaeded", stroke="#7f8c8d", sw=1.5))
    f.append(text(215, 292, "Нижній електрод BE (T_0 = 300 K)", size=10.5, color="#2c3e50"))

    # Філамент у формі пісочного годинника (конусне звуження)
    f.append(polygon([(195, 110), (235, 110), (220, 180), (225, 195), (235, 275), (195, 275), (205, 195), (210, 180)], fill="#fadbd8", stroke="#e74c3c", sw=1.5))

    # Гаряча область у найвужчому місці (Hotspot)
    f.append(circle(215, 187, 18, fill="#e74c3c", stroke="#922b21", sw=1.5))
    f.append(text(215, 191, "T_max", size=10, bold=True, color="#ffffff"))
    f.append(text(115, 190, "Гаряча точка z_0", size=10.5, bold=True, color="#c0392b"))
    f.append(line(150, 190, 195, 190, color="#c0392b", sw=1.2, dash="2 2"))


    # ── Права сторона: Графік розподілу температури T(z) ──
    ox, oy = 490, 280
    f.append(line(ox, oy, ox + 320, oy, color=INK, sw=1.5)) # Вісь z (координата вздовж філамента)
    f.append(line(ox, oy, ox, 80, color=INK, sw=1.5))       # Вісь T (температура)

    f.append(text(ox + 330, oy + 4, "z (вісь філамента)", size=11, bold=True, color=INK))
    f.append(text(ox - 10, 75, "T (K)", size=11, bold=True, color=INK))

    # Рівень кімнатної температури T_0 = 300 K
    f.append(line(ox, oy - 20, ox + 310, oy - 20, color=MUTED, sw=1, dash="3 3"))
    f.append(text(ox - 45, oy - 15, "T_0 (300 K)", size=10, color=MUTED))

    # Параболічна крива температури T(z) з піком T_max у центрі z_0
    path_temp = f"M {ox} {oy - 20} Q {ox + 155} {oy - 230} {ox + 310} {oy - 20}"
    f.append(path(path_temp, stroke="#e74c3c", sw=2.5, fill="none"))

    # Пікова температура T_max
    f.append(line(ox, oy - 180, ox + 155, oy - 180, color="#c0392b", sw=1.2, dash="2 2"))
    f.append(text(ox - 65, oy - 175, "T_max (~800 K)", size=10.5, bold=True, color="#c0392b"))
    f.append(circle(ox + 155, oy - 180, 4, fill="#c0392b"))

    # Співвідношення Кольрауша — Відемана — Франца
    f.append(rect(60, 325, 740, 55, fill="#f4f6f7", stroke="#bdc3c7", sw=1.5))
    f.append(text(430, 345, "Співвідношення Кольрауша для пікової температури джоулевого нагріву:", size=11, bold=True, color=INK))
    f.append(text(430, 366, "T_max = √( T_0² + V² / (4 · L_W) ),  де L_W = 2.44·10⁻⁸ Вт·Ом/К² (число Відемана — Франца)", size=11, bold=True, color="#2980b9"))

    render(os.path.join(OUT, "thermal-joule-profile.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    fig_oxram_cell_structure()
    fig_forming_set_reset_cycle()
    fig_vacancy_energy_landscape()
    fig_thermal_joule_profile()
    print("Всі фігури успішно згенеровано у теці ./img/")
