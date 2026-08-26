# -*- coding: utf-8 -*-
"""Фігури до теми «Перехресна чутливість».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GREY = "#8a8a8a"
LIGHT_BLUE = "#eef4fd"
LIGHT_RED = "#fdf2f2"
LIGHT_GREEN = "#f0fdf4"


def _axes(f, ox, oy, top, right, ylab="вихід U", xlab="величина x"):
    """Осі координат зі стрілками: вертикаль угору від (ox,oy), горизонталь управо."""
    f.append(arrow(ox, oy, ox, top, color=INK, sw=1.6))
    f.append(arrow(ox, oy, right, oy, color=INK, sw=1.6))
    f.append(text(ox - 8, top + 8, ylab, size=12, anchor="end", bold=True))
    f.append(text(right - 6, oy + 18, xlab, size=12, bold=True))


# ── 1. Огляд перехресної чутливості: TCO та TCS дрейф ─────────────────────────
def fig_cross_overview():
    W, H = 760, 370
    f = []
    
    # Ліва частина: структурна схема збурень
    f.append(rect(20, 20, 310, 330, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    f.append(text(175, 45, "Фізичний перетворювач у середовищі", size=13, bold=True))
    
    # Цільовий вхід
    f.append(arrow(30, 95, 80, 95, color=FIELD, sw=2.5))
    f.append(text(55, 82, "Цільова величина X", size=11, color=FIELD, bold=True))
    f.append(text(55, 114, "(тиск, сила, струм)", size=9.5, color=FIELD, italic=True))
    
    # Чутливий елемент
    f.append(rect(85, 75, 180, 160, fill="#ffffff", stroke=LINE, sw=1.8, rx=4))
    f.append(text(175, 105, "Чутливий елемент", size=12, bold=True))
    f.append(text(175, 125, "(п'єзорезистор, Холл,", size=10, color=MUTED))
    f.append(text(175, 142, "електрохімічна комірка)", size=10, color=MUTED))
    f.append(line(95, 158, 255, 158, color=GREY, sw=1, dash="2,2"))
    f.append(text(175, 180, "U = f(X, T, RH, B_ext)", size=11, color=INK, bold=True))
    f.append(text(175, 205, "паразитна взаємодія", size=10, color=POS, italic=True))
    
    # Паразитні входи
    f.append(arrow(30, 160, 80, 160, color=POS, sw=2))
    f.append(text(55, 150, "Температура T", size=10.5, color=POS, bold=True))
    
    f.append(arrow(30, 205, 80, 205, color=NEG, sw=2))
    f.append(text(55, 195, "Вологість RH", size=10.5, color=NEG, bold=True))
    
    f.append(arrow(175, 290, 175, 240, color="#d97706", sw=2))
    f.append(text(175, 308, "Зовнішнє магнітне поле B_ext", size=10.5, color="#d97706", bold=True))
    f.append(text(175, 325, "(завади від силових шин і двигунів)", size=9.5, color=MUTED, italic=True))
    
    # Вихідний сигнал
    f.append(arrow(265, 155, 315, 155, color=INK, sw=2.5))
    f.append(text(290, 142, "Вихід U", size=11, bold=True))
    
    # Права частина: графік характеристики (TCO та TCS)
    ox, oy = 410, 300
    top, right = 45, 730
    _axes(f, ox, oy, top, right, ylab="Вихідний сигнал U", xlab="Цільова величина X")
    
    # Номінальна пряма (T_ном = 25 °C)
    f.append(line(ox, 250, 690, 130, color=FIELD, sw=2.8))
    f.append(text(700, 130, "T = 25 °C (номінал)", size=10.5, color=FIELD, anchor="start", bold=True))
    
    # Пряма зі зсувом нуля TCO (паралельний зсув угору при нагріванні)
    f.append(line(ox, 200, 690, 80, color=POS, sw=2, dash="4,3"))
    f.append(text(700, 80, "T = 80 °C (зсув нуля TCO)", size=10.5, color=POS, anchor="start", bold=True))
    
    # Позначення TCO стрілкою
    f.append(arrow(ox + 30, 244, ox + 30, 196, color=POS, sw=1.5))
    f.append(text(ox + 38, 222, "ΔU_offset (TCO)", size=10, color=POS, anchor="start", bold=True))
    
    # Пряма зі зміною чутливості TCS (зміна нахилу)
    f.append(line(ox, 250, 690, 60, color=NEG, sw=2, dash="6,3"))
    f.append(text(700, 58, "Дрейф чутливості (TCS)", size=10.5, color=NEG, anchor="start", bold=True))
    
    # Позначення кута / зміни нахилу
    f.append(arrow(650, 138, 650, 72, color=NEG, sw=1.5))
    f.append(text(640, 105, "ΔS(T)", size=10, color=NEG, anchor="end", bold=True))
    
    f.append(text(ox + 160, 335, "Перехресна чутливість спотворює нуль (TCO) і нахил (TCS)", size=11, italic=True))
    
    render(os.path.join(IMG, "cross-sensitivity-overview.svg"), W, H, *f,
           title="Вплив нецільових факторів на передавальну характеристику")


# ── 2. Апаратна компенсація: міст Вітстона з неробочим плечем ──────────────────
def fig_wheatstone_dummy():
    W, H = 740, 360
    f = []
    
    # Ліва частина: механічна деталь
    f.append(rect(20, 20, 330, 320, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    f.append(text(185, 45, "Механічний зразок із тензорезисторами", size=13, bold=True))
    
    # Балка під навантаженням
    f.append(rect(50, 80, 270, 75, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=2))
    f.append(text(185, 100, "Пружна балка (навантажена F)", size=11, bold=True))
    
    # Активний тензодатчик R1
    f.append(rect(100, 115, 170, 26, fill=LIGHT_RED, stroke=POS, sw=1.8, rx=3))
    f.append(text(185, 132, "R_act: деформація ε + температура T", size=10.5, color=POS, bold=True))
    
    # Ненавантажена пластина для Dummy Gauge
    f.append(rect(50, 195, 270, 75, fill="#f1f5f9", stroke=GREY, sw=1.5, rx=2))
    f.append(text(185, 215, "Ненавантажена компенсаційна пластина", size=10.5, color=MUTED, bold=True))
    f.append(text(185, 230, "(той самий метал, тепловий контакт, без сили)", size=9.5, color=MUTED, italic=True))
    
    # Компенсаційний тензодатчик R2 (Dummy)
    f.append(rect(100, 240, 170, 24, fill=LIGHT_BLUE, stroke=NEG, sw=1.8, rx=3))
    f.append(text(185, 256, "R_dummy: лише температура T", size=10.5, color=NEG, bold=True))
    
    # Права частина: електричний міст
    f.append(rect(370, 20, 350, 320, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    f.append(text(545, 45, "Синфазне віднімання в мості Вітстона", size=13, bold=True))
    
    # Вузли мосту
    top_x, top_y = 545, 80
    bot_x, bot_y = 545, 240
    left_x, left_y = 445, 160
    right_x, right_y = 645, 160
    
    # Лінії мосту
    f.append(line(top_x, top_y, left_x, left_y, color=LINE, sw=2))
    f.append(line(top_x, top_y, right_x, right_y, color=LINE, sw=2))
    f.append(line(left_x, left_y, bot_x, bot_y, color=LINE, sw=2))
    f.append(line(right_x, right_y, bot_x, bot_y, color=LINE, sw=2))
    
    # Живлення
    f.append(circle(top_x, top_y, 4, fill=POS, stroke=POS))
    f.append(text(top_x, top_y - 10, "+V_exc", size=11, color=POS, bold=True))
    f.append(circle(bot_x, bot_y, 4, fill=INK, stroke=INK))
    f.append(text(bot_x, bot_y + 16, "GND", size=11, bold=True))
    
    # Резистори мосту
    # Верхнє ліве плече: R_act
    f.append(rect(470, 105, 45, 24, fill=LIGHT_RED, stroke=POS, sw=1.6, rx=2))
    f.append(text(492, 121, "R_act", size=10, color=POS, bold=True))
    # Нижнє ліве плече: R_dummy
    f.append(rect(470, 190, 45, 24, fill=LIGHT_BLUE, stroke=NEG, sw=1.6, rx=2))
    f.append(text(492, 206, "R_dum", size=10, color=NEG, bold=True))
    # Праві плечі: опорні резистори R3, R4
    f.append(rect(580, 105, 40, 24, fill=FILL, stroke=LINE, sw=1.5, rx=2))
    f.append(text(600, 121, "R₀", size=10, bold=True))
    f.append(rect(580, 190, 40, 24, fill=FILL, stroke=LINE, sw=1.5, rx=2))
    f.append(text(600, 206, "R₀", size=10, bold=True))
    
    # Вихідна діагональ
    f.append(circle(left_x, left_y, 4, fill=FIELD, stroke=FIELD))
    f.append(circle(right_x, right_y, 4, fill=FIELD, stroke=FIELD))
    f.append(arrow(right_x, right_y, left_x + 10, left_y, color=FIELD, sw=2))
    f.append(text(545, 150, "Диференційний вихід ΔU", size=11, color=FIELD, bold=True))
    
    # Формула компенсації
    f.append(rect(390, 265, 310, 60, fill=LIGHT_GREEN, stroke=FIELD, sw=1.5, rx=4))
    f.append(text(545, 285, "ΔU ≈ (V_exc / 4) · (ΔR_ε + ΔR_T − ΔR_T) / R₀", size=10.5, color=INK, bold=True))
    f.append(text(545, 308, "= (V_exc / 4) · (ΔR_ε / R₀)   [температурний дрейф зник]", size=10, color=FIELD, bold=True))
    
    render(os.path.join(IMG, "wheatstone-dummy-compensation.svg"), W, H, *f,
           title="Апаратна компенсація температури за допомогою неробочого плеча мосту")


# ── 3. Диференційний сенсор Холла: придушення стороннього магнітного поля ──────
def fig_diff_hall():
    W, H = 760, 370
    f = []
    
    f.append(rect(20, 20, 720, 330, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    f.append(text(380, 42, "Придушення зовнішнього магнітного поля в диференційній парі Холла", size=13, bold=True))
    
    # Зовнішнє однорідне поле завади B_ext вгорі
    f.append(text(250, 62, "Зовнішнє однорідне поле завади +B_ext (від сусідніх шин)", size=10.5, color=POS, bold=True))
    for x_pos in [90, 140, 200, 260, 320, 380, 420]:
        f.append(arrow(x_pos, 92, x_pos, 72, color=POS, sw=1.5))
    
    # Сенсор Холла 1 (A)
    f.append(rect(145, 105, 60, 32, fill=LIGHT_GREEN, stroke=FIELD, sw=2, rx=4))
    f.append(text(175, 126, "Холл A", size=11, color=FIELD, bold=True))
    
    # Сенсор Холла 2 (B)
    f.append(rect(325, 105, 60, 32, fill=LIGHT_GREEN, stroke=FIELD, sw=2, rx=4))
    f.append(text(355, 126, "Холл B", size=11, color=FIELD, bold=True))
    
    # Струмопровідна шина U-подібної форми (нижче сенсорів)
    # Ліва гілка (струм I вгору)
    f.append(rect(140, 150, 70, 130, fill="#fed7aa", stroke="#ea580c", sw=2, rx=4))
    f.append(arrow(175, 260, 175, 165, color="#c2410c", sw=3))
    f.append(text(175, 215, "Струм +I", size=11.5, color="#9a3412", bold=True))
    
    # Права гілка (струм I вниз)
    f.append(rect(320, 150, 70, 130, fill="#fed7aa", stroke="#ea580c", sw=2, rx=4))
    f.append(arrow(355, 165, 355, 260, color="#c2410c", sw=3))
    f.append(text(355, 215, "Струм −I", size=11.5, color="#9a3412", bold=True))
    
    # Вектори корисного магнітного поля B_I біля сенсорів
    f.append(arrow(175, 148, 175, 138, color=FIELD, sw=2.5))
    f.append(text(218, 120, "+B_I", size=10, color=FIELD, bold=True))
    
    f.append(arrow(355, 138, 355, 148, color=FIELD, sw=2.5))
    f.append(text(312, 120, "−B_I", size=10, color=FIELD, bold=True))
    
    # Блок диференційного підсилювача праворуч
    f.append(rect(470, 85, 250, 200, fill="#ffffff", stroke=LINE, sw=1.8, rx=6))
    f.append(text(595, 110, "Диференційний віднімач", size=12, bold=True))
    
    # Сигнали на вході
    f.append(arrow(207, 120, 465, 135, color=FIELD, sw=1.8))
    f.append(text(460, 125, "V_A = S·(+B_I + B_ext)", size=9, color=INK, anchor="end"))
    
    f.append(arrow(387, 120, 465, 175, color=FIELD, sw=1.8))
    f.append(text(460, 168, "V_B = S·(−B_I + B_ext)", size=9, color=INK, anchor="end"))
    
    # Формула в блоці
    f.append(line(485, 145, 705, 145, color=GREY, sw=1))
    f.append(text(595, 168, "V_out = V_A − V_B", size=11, color=INK, bold=True))
    f.append(text(595, 192, "= S·[(+B_I + B_ext) − (−B_I + B_ext)]", size=9.5, color=MUTED))
    f.append(text(595, 222, "= 2 · S · B_I", size=13, color=FIELD, bold=True))
    f.append(text(595, 250, "(зовнішня завада B_ext знищена)", size=10, color=POS, italic=True))
    
    # Підпис знизу
    f.append(text(380, 325, "Градієнтне розташування елементів подвоює сигнал струму й відсікає синфазну магнітну заваду", size=11, italic=True))
    
    render(os.path.join(IMG, "differential-hall-cancellation.svg"), W, H, *f,
           title="Диференційне придушення сторонніх магнітних полів у сенсорах Холла")


# ── 4. Двовимірна калібрувальна матриця: білінійна інтерполяція ────────────────
def fig_bilinear_lut():
    W, H = 720, 360
    f = []
    
    # Осі площини: X (Raw ADC) та T (Температура)
    ox, oy = 90, 290
    top, right = 40, 680
    _axes(f, ox, oy, top, right, ylab="Температура T (°C)", xlab="Сирий код сенсора X_raw (ADC)")
    
    # Сітка вузлів
    xs = [140, 260, 460, 600]
    ts = [250, 180, 100]
    
    for x_val in xs:
        f.append(line(x_val, oy, x_val, top + 20, color="#e2e8f0", sw=1, dash="2,2"))
    for t_val in ts:
        f.append(line(ox, t_val, right - 20, t_val, color="#e2e8f0", sw=1, dash="2,2"))
        
    # Виділена комірка інтерполяції між xs[1]=260, xs[2]=460 та ts[1]=180, ts[2]=100
    x1, x2 = xs[1], xs[2]
    t1, t2 = ts[1], ts[2]
    
    f.append(rect(x1, t2, x2 - x1, t1 - t2, fill=LIGHT_BLUE, stroke=NEG, sw=1.5, rx=2))
    
    # 4 кутові вузли калібрування
    # Q11: (x1, t1)
    f.append(circle(x1, t1, 5, fill=NEG, stroke=INK, sw=1.5))
    f.append(text(x1 - 10, t1 + 18, "Q₁₁ (X₁, T₁)", size=10.5, color=NEG, anchor="end", bold=True))
    
    # Q21: (x2, t1)
    f.append(circle(x2, t1, 5, fill=NEG, stroke=INK, sw=1.5))
    f.append(text(x2 + 10, t1 + 18, "Q₂₁ (X₂, T₁)", size=10.5, color=NEG, anchor="start", bold=True))
    
    # Q12: (x1, t2)
    f.append(circle(x1, t2, 5, fill=NEG, stroke=INK, sw=1.5))
    f.append(text(x1 - 10, t2 - 8, "Q₁₂ (X₁, T₂)", size=10.5, color=NEG, anchor="end", bold=True))
    
    # Q22: (x2, t2)
    f.append(circle(x2, t2, 5, fill=NEG, stroke=INK, sw=1.5))
    f.append(text(x2 + 10, t2 - 8, "Q₂₂ (X₂, T₂)", size=10.5, color=NEG, anchor="start", bold=True))
    
    # Поточна точка вимірювання P(X, T)
    px = x1 + int((x2 - x1) * 0.6)  # u = 0.6
    py = t1 - int((t1 - t2) * 0.55) # v = 0.55
    
    # Проміжні точки горизонтальної інтерполяції
    f.append(line(x1, t1, x2, t1, color=NEG, sw=2.5))
    f.append(circle(px, t1, 4, fill=POS, stroke=INK, sw=1))
    f.append(text(px, t1 + 16, "R₁", size=10, color=POS, bold=True))
    
    f.append(line(x1, t2, x2, t2, color=NEG, sw=2.5))
    f.append(circle(px, t2, 4, fill=POS, stroke=INK, sw=1))
    f.append(text(px, t2 - 8, "R₂", size=10, color=POS, bold=True))
    
    # Вертикальна лінія між R1 та R2 через точку P
    f.append(line(px, t1, px, t2, color=POS, sw=2, dash="3,2"))
    f.append(circle(px, py, 6, fill=FIELD, stroke=INK, sw=2))
    f.append(text(px + 12, py + 4, "P(X, T)", size=12, color=FIELD, anchor="start", bold=True))
    
    # Нормалізовані відрізки u та v
    f.append(arrow(x1, t1 + 32, px, t1 + 32, color=INK, sw=1.2))
    f.append(text(x1 + int((px - x1) / 2), t1 + 45, "u = ΔX/ΔX_grid", size=9.5, color=INK, bold=True))
    
    f.append(arrow(x2 + 35, t1, x2 + 35, py, color=INK, sw=1.2))
    f.append(text(x2 + 42, t1 - int((t1 - py) / 2), "v = ΔT/ΔT_grid", size=9.5, color=INK, anchor="start", bold=True))
    
    # Формула білінійної інтерполяції в рамці
    f.append(rect(340, 30, 350, 60, fill=LIGHT_GREEN, stroke=FIELD, sw=1.5, rx=4))
    f.append(text(515, 50, "P(u,v) = (1−u)(1−v)Q₁₁ + u(1−v)Q₂₁", size=10, color=INK, bold=True))
    f.append(text(515, 72, "+ (1−u)v·Q₁₂ + u·v·Q₂₂", size=10, color=FIELD, bold=True))
    
    f.append(text(370, 345, "Білінійна інтерполяція в 2D LUT забезпечує швидку корекцію без складних функцій", size=11, italic=True))
    
    render(os.path.join(IMG, "bilinear-interpolation-grid.svg"), W, H, *f,
           title="Двовимірна калібрувальна матриця та білінійна інтерполяція")


# ── 5. Динамічне теплове відставання: On-die проти зовнішнього сенсора ─────────
def fig_thermal_lag():
    W, H = 720, 340
    f = []
    
    ox, oy = 80, 270
    top, right = 40, 680
    _axes(f, ox, oy, top, right, ylab="Температура T", xlab="Час t (с)")
    
    # Стрибок температури середовища T_env (ступінчаста функція)
    t_step = 140
    f.append(line(ox, 220, t_step, 220, color=MUTED, sw=2, dash="3,3"))
    f.append(line(t_step, 220, t_step, 80, color=MUTED, sw=2, dash="3,3"))
    f.append(line(t_step, 80, right - 20, 80, color=MUTED, sw=2, dash="3,3"))
    f.append(text(right - 15, 75, "Середовище T_env", size=10.5, color=MUTED, anchor="end", bold=True))
    
    # Відгук On-die сенсора (швидка експонента, tau_die мала)
    pts_die = []
    for x in range(ox, right - 20, 4):
        if x < t_step:
            y = 220
        else:
            dt = (x - t_step) / 18.0
            y = 80 + 140 * math.exp(-dt)
        pts_die.append(f"{x:.1f},{y:.1f}")
    f.append(f'<polyline points="{" ".join(pts_die)}" fill="none" stroke="{POS}" stroke-width="2.6" />')
    f.append(text(310, 95, "On-die сенсор (τ_die ≈ 40 мс)", size=10.5, color=POS, bold=True))
    
    # Відгук зовнішнього сенсора на платі (повільна експонента, tau_pcb велика)
    pts_pcb = []
    for x in range(ox, right - 20, 4):
        if x < t_step:
            y = 220
        else:
            dt = (x - t_step) / 120.0
            y = 80 + 140 * math.exp(-dt)
        pts_pcb.append(f"{x:.1f},{y:.1f}")
    f.append(f'<polyline points="{" ".join(pts_pcb)}" fill="none" stroke="{NEG}" stroke-width="2.6" stroke-dasharray="6,3" />')
    f.append(text(540, 160, "Зовнішній NTC на платі (τ_pcb ≈ 3.5 с)", size=10.5, color=NEG, bold=True))
    
    # Позначення динамічної помилки між кривими
    f.append(arrow(320, 185, 320, 105, color="#d97706", sw=1.6))
    f.append(text(330, 145, "Динамічна помилка ΔT_lag", size=10, color="#d97706", anchor="start", bold=True))
    f.append(text(330, 160, "(спричиняє хибний сплеск виходу)", size=9, color=MUTED, anchor="start", italic=True))
    
    # Рамка з моделлю компенсації
    f.append(rect(380, 210, 310, 55, fill=FILL, stroke=LINE, sw=1.5, rx=4))
    f.append(text(535, 230, "Динамічна модель: T_est = T_pcb + τ · (dT_pcb / dt)", size=10, color=INK, bold=True))
    f.append(text(535, 250, "або пряме розміщення сенсора на кристалі (on-die)", size=9.5, color=POS, italic=True))
    
    f.append(text(370, 315, "Теплове відставання зовнішнього давача спотворює компенсацію під час швидких змін температури", size=11, italic=True))
    
    render(os.path.join(IMG, "thermal-lag-compensation.svg"), W, H, *f,
           title="Теплове відставання та різниця динаміки on-die і зовнішнього термодавача")


def main():
    fig_cross_overview()
    fig_wheatstone_dummy()
    fig_diff_hall()
    fig_bilinear_lut()
    fig_thermal_lag()
    print("Усі фігури згенеровано успішно.")


if __name__ == '__main__':
    main()
