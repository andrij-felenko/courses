# -*- coding: utf-8 -*-
"""Фігури до статті «Вал приходить у заданий кут».
Запуск:  python figs.py   → генерує SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Архітектура триконтурного каскадного регулятора ────────────────────────
def fig_cascade_architecture():
    W, H = 1080, 530
    f = []

    f.append(text(W / 2, 28, "Триконтурний каскад керування сервоприводом із випередженням", size=16, bold=True))

    # Області контурів (фонові панелі)
    # Зовнішній контур положення
    f.append(rect(30, 60, 220, 370, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=8))
    f.append(text(140, 85, "Контур положення (500–1000 Гц)", size=12, bold=True, color="#475569"))

    # Середній контур швидкості
    f.append(rect(270, 60, 270, 370, fill="#f0fdf4", stroke="#86efac", sw=1.2, rx=8))
    f.append(text(405, 85, "Контур швидкості (2–5 кГц)", size=12, bold=True, color="#166534"))

    # Внутрішній контур струму
    f.append(rect(560, 60, 250, 370, fill="#eff6ff", stroke="#93c5fd", sw=1.2, rx=8))
    f.append(text(685, 85, "Контур струму (10–50 кГц)", size=12, bold=True, color="#1e40af"))

    # Об'єкт керування
    f.append(rect(830, 60, 220, 370, fill="#fdf2f8", stroke="#f472b6", sw=1.2, rx=8))
    f.append(text(940, 85, "Фізичний привід і вал", size=12, bold=True, color="#9d174d"))

    # 1. Вхід: завдання положення
    f.append(text(45, 155, "θ* (профіль)", size=12, bold=True, color=INK, anchor="start"))
    f.append(arrow(115, 150, 140, 150, color=INK, sw=1.8))

    # Суматор положення
    f.append(circle(150, 150, 10, fill=BG, stroke=INK, sw=1.5))
    f.append(text(150, 154, "+", size=12, bold=True))
    f.append(text(150, 168, "−", size=12, bold=True, color=NEG))

    f.append(arrow(160, 150, 185, 150, color=INK, sw=1.8))

    # Блок P-регулятора положення
    f.append(rect(185, 125, 55, 50, fill=FILL, stroke=LINE, sw=1.5, rx=4))
    f.append(text(212, 146, "P-поз", size=11, bold=True))
    f.append(text(212, 163, "Kp_pos", size=10, color=MUTED))

    f.append(arrow(240, 150, 285, 150, color=INK, sw=1.8))

    # Суматор випередження швидкості (V_ff)
    f.append(circle(295, 150, 10, fill=BG, stroke=INK, sw=1.5))
    f.append(text(295, 154, "+", size=12, bold=True))
    f.append(text(295, 136, "+", size=12, bold=True, color=FIELD))

    # Лінія випередження швидкості зверху
    f.append(line(70, 120, 295, 120, color=FIELD, sw=1.5))
    f.append(arrow(295, 120, 295, 140, color=FIELD, sw=1.5))
    f.append(text(160, 114, "Випередження швидкості: V_ff = ω*", size=10, bold=True, color=FIELD))

    f.append(arrow(305, 150, 335, 150, color=INK, sw=1.8))
    f.append(text(320, 142, "ω*", size=11, bold=True))

    # Суматор швидкості
    f.append(circle(345, 150, 10, fill=BG, stroke=INK, sw=1.5))
    f.append(text(345, 154, "+", size=12, bold=True))
    f.append(text(345, 168, "−", size=12, bold=True, color=NEG))

    f.append(arrow(355, 150, 380, 150, color=INK, sw=1.8))

    # Блок PI-регулятора швидкості
    f.append(rect(380, 125, 75, 50, fill=FILL, stroke=LINE, sw=1.5, rx=4))
    f.append(text(417, 145, "PI-швидкість", size=11, bold=True))
    f.append(text(417, 163, "+ Anti-windup", size=10, color=MUTED))

    f.append(arrow(455, 150, 490, 150, color=INK, sw=1.8))

    # Суматор компенсації навантаження і тертя (A_ff, Friction, Grav)
    f.append(circle(500, 150, 10, fill=BG, stroke=INK, sw=1.5))
    f.append(text(500, 154, "+", size=12, bold=True))
    f.append(text(500, 136, "+", size=12, bold=True, color=POS))

    # Лінії випередження моменту зверху
    f.append(line(70, 205, 500, 205, color=POS, sw=1.5))
    f.append(arrow(500, 205, 500, 160, color=POS, sw=1.5))
    f.append(text(285, 219, "Компенсація: J·α* (прискорення) + τ_fric (тертя) + τ_grav (гравітація)", size=10, bold=True, color=POS))

    f.append(arrow(510, 150, 580, 150, color=INK, sw=1.8))
    f.append(text(545, 142, "I* (струм)", size=11, bold=True))

    # Суматор струму
    f.append(circle(590, 150, 10, fill=BG, stroke=INK, sw=1.5))
    f.append(text(590, 154, "+", size=12, bold=True))
    f.append(text(590, 168, "−", size=12, bold=True, color=NEG))

    f.append(arrow(600, 150, 630, 150, color=INK, sw=1.8))

    # Блок PI-регулятора струму
    f.append(rect(630, 125, 75, 50, fill=FILL, stroke=LINE, sw=1.5, rx=4))
    f.append(text(667, 145, "PI-струм", size=11, bold=True))
    f.append(text(667, 163, "FOC / H-міст", size=10, color=MUTED))

    f.append(arrow(705, 150, 740, 150, color=INK, sw=1.8))

    # Блок силового інвертора / ШІМ
    f.append(rect(740, 125, 60, 50, fill=FILL, stroke=LINE, sw=1.5, rx=4))
    f.append(text(770, 145, "ШІМ/Драйвер", size=10, bold=True))
    f.append(text(770, 163, "U_pwm", size=10, color=MUTED))

    f.append(arrow(800, 150, 850, 150, color=INK, sw=1.8))

    # Блок мотора і редуктора
    f.append(rect(850, 115, 180, 70, fill="#fdf2f8", stroke=LINE, sw=1.5, rx=6))
    f.append(text(940, 142, "Мотор + Редуктор + Вал", size=12, bold=True))
    f.append(text(940, 163, "Інерція J, пружність, тертя", size=10, color=MUTED))

    # Вихідний рух вала
    f.append(arrow(1030, 150, 1060, 150, color=INK, sw=1.8))
    f.append(text(1065, 145, "θ, ω", size=12, bold=True, anchor="start"))

    # Блоки давачів та ліній зворотного зв'язку
    # 1. Давач струму (шунт)
    f.append(rect(860, 245, 160, 48, fill="#eff6ff", stroke="#3b82f6", sw=1.4, rx=4))
    f.append(text(940, 265, "Давач струму (шунт)", size=11, bold=True))
    f.append(text(940, 281, "I_meas (фазний струм)", size=10, color=MUTED))

    f.append(line(880, 185, 880, 245, color="#3b82f6", sw=1.5))
    f.append(line(860, 267, 590, 267, color="#3b82f6", sw=1.5))
    f.append(arrow(590, 267, 590, 160, color="#3b82f6", sw=1.5))
    f.append(text(680, 257, "Зворотний зв'язок по струму (I_meas)", size=10, color="#2563eb"))

    # 2. Енкодер (положення і швидкість)
    f.append(rect(860, 320, 160, 55, fill="#f0fdf4", stroke="#22c55e", sw=1.4, rx=4))
    f.append(text(940, 342, "Оптичний/Магнітний енкодер", size=10, bold=True))
    f.append(text(940, 360, "Квадратурний рахунок → θ, ω", size=10, color=MUTED))

    f.append(line(990, 185, 990, 320, color="#16a34a", sw=1.5))

    # Зворотний зв'язок швидкості
    f.append(line(860, 335, 345, 335, color="#16a34a", sw=1.5))
    f.append(arrow(345, 335, 345, 160, color="#16a34a", sw=1.5))
    f.append(text(460, 326, "Зворотний зв'язок швидкості (ω_meas)", size=10, color="#16a34a"))

    # Зворотний зв'язок положення
    f.append(line(860, 360, 150, 360, color="#0f766e", sw=1.5))
    f.append(arrow(150, 360, 150, 160, color="#0f766e", sw=1.5))
    f.append(text(270, 375, "Зворотний зв'язок положення (θ_meas)", size=10, color="#0f766e"))

    # Пояснювальний підвал на діаграмі
    f.append(text(W / 2, 480, "Швидкі внутрішні контури компенсують електричні нелінійності, а зовнішній — керує кінематикою", size=12, bold=True, color="#334155"))
    f.append(text(W / 2, 502, "Випередження (Feedforward) розвантажує петлі зі зворотним зв'язком і мінімізує похибку під час динамічного руху", size=11, color=MUTED))

    render(os.path.join(IMG, "cascade-control-architecture.svg"), W, H, *f)


# ── 2. Порівняння профілів руху: трапеція проти S-кривої ──────────────────────
def fig_motion_profiles():
    W, H = 1040, 520
    f = []

    f.append(text(W / 2, 28, "Порівняння профілів руху: трапецієподібний та 7-фазний S-кривий (з обмеженням ривка)", size=15, bold=True))

    # Ліва колонка: Трапецієподібний профіль швидкості
    f.append(rect(30, 60, 475, 435, fill="#fafaf9", stroke="#d6d3d1", sw=1.4, rx=8))
    f.append(text(267, 85, "Трапецієподібний профіль (Trap Profile)", size=13, bold=True, color="#44403c"))
    f.append(text(267, 103, "Стрибок прискорення → нескінченний ривок (Jerk = ∞) → вібрації", size=10, color=POS))

    # Графік положення s(t)
    f.append(rect(60, 120, 420, 80, fill=BG, stroke="#e7e5e4", sw=1, rx=4))
    f.append(text(70, 136, "θ(t) Положення", size=10, bold=True, color="#0284c7", anchor="start"))
    f.append(line(90, 190, 450, 190, color="#d6d3d1", sw=1)) # вісь t
    f.append(path_svg([(90, 190), (190, 170), (330, 140), (430, 130)], color="#0284c7", sw=2.2))

    # Графік швидкості v(t) - трапеція
    f.append(rect(60, 210, 420, 80, fill=BG, stroke="#e7e5e4", sw=1, rx=4))
    f.append(text(70, 226, "ω(t) Швидкість", size=10, bold=True, color=FIELD, anchor="start"))
    f.append(line(90, 280, 450, 280, color="#d6d3d1", sw=1))
    f.append(path_svg([(90, 280), (190, 225), (330, 225), (430, 280)], color=FIELD, sw=2.2))
    f.append(text(260, 220, "ω_max", size=10, bold=True, color=FIELD))

    # Графік прискорення a(t) - прямокутники (ступені)
    f.append(rect(60, 300, 420, 80, fill=BG, stroke="#e7e5e4", sw=1, rx=4))
    f.append(text(70, 316, "α(t) Прискорення", size=10, bold=True, color=POS, anchor="start"))
    f.append(line(90, 340, 450, 340, color="#d6d3d1", sw=1)) # 0 рівень
    # Прямокутна сходинка вгору, нуль, сходинка вниз
    f.append(path_svg([(90, 340), (90, 315), (190, 315), (190, 340), (330, 340), (330, 365), (430, 365), (430, 340)], color=POS, sw=2.2))
    f.append(text(140, 310, "+a_max", size=10, bold=True, color=POS))
    f.append(text(380, 379, "−a_max", size=10, bold=True, color=POS))

    # Графік ривка jerk - дельта-імпульси
    f.append(rect(60, 390, 420, 85, fill=BG, stroke="#e7e5e4", sw=1, rx=4))
    f.append(text(70, 406, "j(t) Ривок (Jerk = dα/dt)", size=10, bold=True, color="#9333ea", anchor="start"))
    f.append(line(90, 435, 450, 435, color="#d6d3d1", sw=1))
    # 4 дельта-імпульси зі стрілками
    f.append(arrow(90, 435, 90, 405, color=POS, sw=2))
    f.append(arrow(190, 435, 190, 465, color=POS, sw=2))
    f.append(arrow(330, 435, 330, 465, color=POS, sw=2))
    f.append(arrow(430, 435, 430, 405, color=POS, sw=2))
    f.append(text(95, 403, "+∞", size=10, bold=True, color=POS))
    f.append(text(195, 473, "−∞", size=10, bold=True, color=POS))
    f.append(text(335, 473, "−∞", size=10, bold=True, color=POS))
    f.append(text(435, 403, "+∞", size=10, bold=True, color=POS))


    # Права колонка: 7-фазний S-кривий профіль
    f.append(rect(535, 60, 475, 435, fill="#f0fdfa", stroke="#99f6e4", sw=1.4, rx=8))
    f.append(text(772, 85, "S-кривий профіль (7-Phase S-Curve)", size=13, bold=True, color="#115e59"))
    f.append(text(772, 103, "Обмежений ривок (Jerk ≤ J_max) → відсутність механічного резонансу", size=10, color="#0d9488"))

    # Графік положення s(t)
    f.append(rect(565, 120, 420, 80, fill=BG, stroke="#ccfbf1", sw=1, rx=4))
    f.append(text(575, 136, "θ(t) Положення", size=10, bold=True, color="#0284c7", anchor="start"))
    f.append(line(595, 190, 955, 190, color="#d6d3d1", sw=1))
    f.append(path_svg([(595, 190), (670, 180), (740, 155), (830, 135), (935, 130)], color="#0284c7", sw=2.2))

    # Графік швидкості v(t) - плавні закруглення S-форми
    f.append(rect(565, 210, 420, 80, fill=BG, stroke="#ccfbf1", sw=1, rx=4))
    f.append(text(575, 226, "ω(t) Швидкість", size=10, bold=True, color=FIELD, anchor="start"))
    f.append(line(595, 280, 955, 280, color="#d6d3d1", sw=1))
    f.append(path_svg([(595, 280), (630, 275), (665, 255), (700, 225), (790, 225), (825, 225), (860, 255), (895, 275), (935, 280)], color=FIELD, sw=2.2))
    f.append(text(745, 220, "ω_max", size=10, bold=True, color=FIELD))

    # Графік прискорення a(t) - трапеція (лінійне наростання)
    f.append(rect(565, 300, 420, 80, fill=BG, stroke="#ccfbf1", sw=1, rx=4))
    f.append(text(575, 316, "α(t) Прискорення", size=10, bold=True, color=POS, anchor="start"))
    f.append(line(595, 340, 955, 340, color="#d6d3d1", sw=1))
    # Трапецієподібне прискорення
    f.append(path_svg([(595, 340), (630, 315), (665, 315), (700, 340), (790, 340), (825, 365), (860, 365), (895, 340), (935, 340)], color=POS, sw=2.2))
    f.append(text(647, 310, "+a_max", size=10, bold=True, color=POS))
    f.append(text(842, 379, "−a_max", size=10, bold=True, color=POS))

    # Графік ривка jerk - прямокутні імпульси ±J_max
    f.append(rect(565, 390, 420, 85, fill=BG, stroke="#ccfbf1", sw=1, rx=4))
    f.append(text(575, 406, "j(t) Ривок (Jerk = const)", size=10, bold=True, color="#9333ea", anchor="start"))
    f.append(line(595, 435, 955, 435, color="#d6d3d1", sw=1))
    # 7 фаз ривка: +J, 0, -J, 0, -J, 0, +J
    f.append(path_svg([(595, 435), (595, 412), (630, 412), (630, 435), (665, 435), (665, 458), (700, 458), (700, 435), (790, 435), (790, 458), (825, 458), (825, 435), (860, 435), (860, 412), (895, 412), (895, 435), (935, 435)], color="#9333ea", sw=2))
    f.append(text(612, 406, "+J_max", size=9, bold=True, color="#9333ea"))
    f.append(text(682, 469, "−J_max", size=9, bold=True, color="#9333ea"))

    render(os.path.join(IMG, "motion-profiles-trapezoid-scurve.svg"), W, H, *f)


# ── 3. Зона нечутливості, автоколивання (hunting) та гістерезис ────────────────
def fig_deadband_hysteresis():
    W, H = 1040, 490
    f = []

    f.append(text(W / 2, 28, "Зона нечутливості з гістерезисом: усунення автоколивань вала (Hunting / Chatter)", size=15, bold=True))

    # Ліва частина: Проблема автоколивань біля цілі без мертвої зони
    f.append(rect(30, 60, 475, 405, fill="#fff1f2", stroke="#fecdd3", sw=1.4, rx=8))
    f.append(text(267, 85, "Автоколивання навколо цілі (Hunting)", size=13, bold=True, color="#9f1239"))
    f.append(text(267, 103, "Дискретність енкодера + інтегратор + сухе тертя", size=10, color=MUTED))

    # Осцилограма положення
    f.append(rect(55, 125, 425, 155, fill=BG, stroke="#fda4af", sw=1, rx=4))
    f.append(line(75, 202, 460, 202, color="#94a3b8", sw=1, dash="4,4")) # ціль 0
    f.append(text(85, 195, "Цільовий кут θ*", size=10, bold=True, color="#0284c7", anchor="start"))
    f.append(text(450, 195, "0°", size=10, bold=True, color="#0284c7"))

    # Межі дискретності енкодера ±1 tick
    f.append(line(75, 172, 460, 172, color="#cbd5e1", sw=1, dash="2,2"))
    f.append(line(75, 232, 460, 232, color="#cbd5e1", sw=1, dash="2,2"))
    f.append(text(85, 168, "+1 тік енкодера", size=9, color=MUTED, anchor="start"))
    f.append(text(85, 243, "−1 тік енкодера", size=9, color=MUTED, anchor="start"))

    # Хвиля автоколивань
    pts_hunting = []
    for step in range(350):
        t = step / 20.0
        # Коливання релейного типу
        val = 22 * math.sin(t * 1.5) + 3 * math.sin(t * 4.5)
        pts_hunting.append((90 + step, 202 + val))
    f.append(path_svg(pts_hunting, color=POS, sw=2))

    # Схема циклу зриву
    f.append(rect(55, 295, 425, 155, fill="#fff", stroke="#f43f5e", sw=1.2, rx=6))
    f.append(text(267, 315, "Механізм релейного зриву (Limit Cycle):", size=11, bold=True, color="#9f1239"))
    f.append(text(267, 340, "1. Вал зупинився з помилкою в 1 тік енкодера (e = +1)", size=10, color=INK))
    f.append(text(267, 362, "2. P-момент замалий, але I-складова невпинно росте", size=10, color=INK))
    f.append(text(267, 384, "3. Момент перевищує тертя спокою → вал різко зривається", size=10, color=POS, bold=True))
    f.append(text(267, 406, "4. Вал перелітає ціль на e = −1 → процес повторюється назад", size=10, color=INK))
    f.append(text(267, 428, "Наслідок: безперервне дрижання (chatter), нагрів мотора і шум", size=10, bold=True, color=POS))


    # Права частина: Гістерезисна зона нечутливості з заморожуванням інтегратора
    f.append(rect(535, 60, 475, 405, fill="#f0fdf4", stroke="#bbf7d0", sw=1.4, rx=8))
    f.append(text(772, 85, "Гістерезисна зона з I-Freeze (In-Position)", size=13, bold=True, color="#166534"))
    f.append(text(772, 103, "Чітка фіксація спокою без мікровитрат струму", size=10, color=FIELD))

    # Графік заходу в зону
    f.append(rect(560, 125, 425, 155, fill=BG, stroke="#86efac", sw=1, rx=4))
    f.append(line(580, 202, 965, 202, color="#94a3b8", sw=1, dash="4,4")) # ціль 0
    f.append(text(590, 195, "Цільовий кут θ*", size=10, bold=True, color="#0284c7", anchor="start"))

    # Пороги входу й виходу
    f.append(rect(580, 182, 385, 40, fill="#dcfce7", stroke="#4ade80", sw=1, rx=2))
    f.append(text(960, 177, "+ε_exit (вихід)", size=9, color="#166534", anchor="end"))
    f.append(text(960, 192, "+ε_enter (вхід)", size=9, color="#15803d", anchor="end"))
    f.append(text(960, 215, "−ε_enter", size=9, color="#15803d", anchor="end"))
    f.append(text(960, 230, "−ε_exit", size=9, color="#166534", anchor="end"))

    # Траєкторія заходу й заспокоєння
    pts_settled = []
    for step in range(350):
        t = step / 25.0
        if step < 180:
            val = 45 * math.exp(-t * 0.9) * math.cos(t * 2.2)
        else:
            val = 0.0 # ідеальний спокій
        pts_settled.append((595 + step, 202 + val))
    f.append(path_svg(pts_settled, color=FIELD, sw=2.2))

    f.append(circle(595 + 180, 202, 5, fill=FIELD, stroke=BG, sw=1.5))
    f.append(text(595 + 180, 160, "Захоплення в In-Position", size=10, bold=True, color=FIELD))
    f.append(arrow(595 + 180, 166, 595 + 180, 195, color=FIELD, sw=1.5))

    # Блок логіки алгоритму гістерезису
    f.append(rect(560, 295, 425, 155, fill="#fff", stroke="#22c55e", sw=1.2, rx=6))
    f.append(text(772, 315, "Алгоритм фіксації положення (Dual-Threshold):", size=11, bold=True, color="#166534"))
    f.append(text(772, 340, "• Вхід: |e| < ε_enter ТА швидкість |ω| < ω_still", size=10, color=INK))
    f.append(text(772, 362, "• Дія: I-складова заморожується (Freeze), вихід = 0", size=10, bold=True, color=FIELD))
    f.append(text(772, 384, "• Вихід із зони: ТІЛЬКИ коли похибка перевищить більший поріг (|e| > ε_exit)", size=10, color=INK))
    f.append(text(772, 406, "• Результат: вал надійно стоїть у точці, мотор холодний,", size=10, color=INK))
    f.append(text(772, 428, "  відсутнє дрижання шестерень і струмовий шум", size=10, bold=True, color=FIELD))

    render(os.path.join(IMG, "deadband-hunting-hysteresis.svg"), W, H, *f)


# ── 4. Модель тертя та пряма компенсація (Stiction / Friction Feedforward) ────
def fig_friction_feedforward():
    W, H = 1040, 480
    f = []

    f.append(text(W / 2, 28, "Модель тертя механічного приводу та функція прямої компенсації (Feedforward)", size=15, bold=True))

    # Ліва панель: Реальна нелінійна характеристика тертя (Stribeck curve)
    f.append(rect(30, 60, 475, 395, fill="#f8fafc", stroke="#cbd5e1", sw=1.4, rx=8))
    f.append(text(267, 85, "Фізична характеристика тертя вала", size=13, bold=True, color="#1e293b"))
    f.append(text(267, 103, "Тертя спокою (Stiction) + ефект Страйбека + в'язке тертя", size=10, color=MUTED))

    f.append(rect(55, 120, 425, 230, fill=BG, stroke="#e2e8f0", sw=1, rx=4))
    # Осі координат
    f.append(line(65, 235, 470, 235, color="#64748b", sw=1.5)) # вісь ω
    f.append(line(267, 130, 267, 340, color="#64748b", sw=1.5)) # вісь τ_fric
    f.append(text(465, 248, "ω (швидкість)", size=10, bold=True, color="#475569", anchor="end"))
    f.append(text(275, 140, "τ_fric (момент тертя)", size=10, bold=True, color="#475569", anchor="start"))

    # Крива тертя: справа від 0 (ω > 0)
    pts_fric_pos = [(267, 170), (280, 185), (310, 200), (370, 190), (450, 160)]
    f.append(path_svg(pts_fric_pos, color=POS, sw=2.5))
    # Крива тертя: зліва від 0 (ω < 0)
    pts_fric_neg = [(267, 300), (254, 285), (224, 270), (164, 280), (84, 310)]
    f.append(path_svg(pts_fric_neg, color=POS, sw=2.5))

    # Стрибок страгування (Stiction peak)
    f.append(circle(267, 170, 4, fill=POS, stroke=BG, sw=1.5))
    f.append(circle(267, 300, 4, fill=POS, stroke=BG, sw=1.5))
    f.append(text(285, 172, "+τ_stiction (зрив)", size=10, bold=True, color=POS, anchor="start"))
    f.append(text(250, 304, "−τ_stiction", size=10, bold=True, color=POS, anchor="end"))

    f.append(line(310, 200, 310, 235, color="#94a3b8", sw=1, dash="2,2"))
    f.append(text(315, 212, "Кулонівське тертя τ_c", size=9, color="#0284c7", anchor="start"))
    f.append(text(440, 150, "В'язке тертя: k_v · ω", size=10, bold=True, color=FIELD, anchor="end"))

    # Опис зон
    f.append(rect(55, 360, 425, 80, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=4))
    f.append(text(267, 380, "Головна пастка: при нульовій швидкості тертя найвище!", size=10, bold=True, color=POS))
    f.append(text(267, 400, "ПІД-регулятор запізнюється зі створенням моменту страгування,", size=10, color=INK))
    f.append(text(267, 420, "що породжує зону застопорення (Dead Zone) і затримку старту", size=10, color=INK))


    # Права панель: Алгоритмічна компенсація Feedforward у контролері
    f.append(rect(535, 60, 475, 395, fill="#f0fdf4", stroke="#86efac", sw=1.4, rx=8))
    f.append(text(772, 85, "Алгоритм Stiction & Dynamic Feedforward", size=13, bold=True, color="#166534"))
    f.append(text(772, 103, "Миттєве додавання розрахованого моменту до уставки струму", size=10, color=FIELD))

    # Схема алгоритму обчислення Feedforward
    f.append(rect(560, 120, 425, 230, fill=BG, stroke="#bbf7d0", sw=1, rx=4))

    # Графік компенсаційної функції
    f.append(line(570, 235, 975, 235, color="#64748b", sw=1.5))
    f.append(line(772, 130, 772, 340, color="#64748b", sw=1.5))
    f.append(text(970, 248, "ω* (задана)", size=10, bold=True, color="#475569", anchor="end"))
    f.append(text(780, 140, "τ_ff (добавка)", size=10, bold=True, color=FIELD, anchor="start"))

    # Лінеаризована функція компенсації: sign(w)*tau_c + k_v*w + stiction boost
    pts_ff_pos = [(772, 235), (776, 185), (850, 185), (960, 155)]
    f.append(path_svg(pts_ff_pos, color=FIELD, sw=2.5))
    pts_ff_neg = [(772, 235), (768, 285), (694, 285), (584, 315)]
    f.append(path_svg(pts_ff_neg, color=FIELD, sw=2.5))

    f.append(text(850, 175, "+τ_c + k_v·ω*", size=10, bold=True, color=FIELD))
    f.append(text(690, 300, "−τ_c − k_v·ω*", size=10, bold=True, color=FIELD))
    f.append(text(785, 205, "Stiction-імпульс", size=10, bold=True, color=POS))

    # Формула внизу
    f.append(rect(560, 360, 425, 80, fill="#ecfdf5", stroke="#6ee7b7", sw=1, rx=4))
    f.append(text(772, 380, "Формула повного моменту випередження:", size=10, bold=True, color="#065f46"))
    f.append(text(772, 402, "τ_cmd = τ_PID + J·α* + τ_coulomb·sgn(ω*) + k_v·ω* + τ_gravity(θ)", size=10, bold=True, color="#047857"))
    f.append(text(772, 424, "Похибка регулювання падає до 5–10 разів без зміни коефіцієнтів ПІД", size=10, color=INK))

    render(os.path.join(IMG, "friction-feedforward-curve.svg"), W, H, *f)


# ── Допоміжні функції ────────────────────────────────────────────────────────
def path_svg(points, color=LINE, sw=1.5):
    d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw:.1f}" stroke-linejoin="round"/>'


if __name__ == "__main__":
    fig_cascade_architecture()
    fig_motion_profiles()
    fig_deadband_hysteresis()
    fig_friction_feedforward()
    print("Всі фігури згенеровано успішно у ./img/")
