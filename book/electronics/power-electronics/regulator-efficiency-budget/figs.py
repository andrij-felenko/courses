# -*- coding: utf-8 -*-
"""Генератор векторних фігур SVG для теми «ККД регулятора в енергетичному бюджеті».
Запуск із теки теми:  python figs.py   →  ./img/*.svg
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

# ── Кольорова палітра ────────────────────────────────────────────────────────
COLOR_LDO   = "#c0392b"   # червоний — LDO
COLOR_BUCK  = "#2457d6"   # синій — Buck з PFM/PWM
COLOR_PWM   = "#8e44ad"   # фіолетовий — Buck тільки PWM
COLOR_FIXED = "#7f8c8d"   # сірий — фіксовані / Iq
COLOR_COND  = "#d35400"   # помаранчевий — провідні I²R
COLOR_ACC   = "#27ae60"   # зелений — активний стан / оптимум

def polyline(pts, color, sw=2.6, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.2f,%.2f" % (x, y) for x, y in pts)
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (p, color, sw, d)

def logspace(a, b, n):
    la, lb = math.log10(a), math.log10(b)
    return [10 ** (la + (lb - la) * i / (n - 1)) for i in range(n)]

# ── Фігура 1: Порівняння кривих ККД LDO та Buck (лог шкала струму) ───────────
def fig_efficiency_curves():
    W, H = 820, 520
    x0, x1, y0, y1 = 90, 750, 70, 410
    Imin, Imax = 1e-6, 2.0     # 1 мкА .. 2 А
    emin, emax = 0.0, 100.0    # 0 .. 100 %

    Vin = 3.7
    Vout = 3.3

    # Модель LDO (Iq = 1 мкА)
    def eff_ldo(I):
        Iq = 1e-6
        Pin = Vin * (I + Iq)
        Pout = Vout * I
        return 100.0 * (Pout / Pin)

    # Модель Buck з PFM/PWM перемиканням (Iq_sleep = 2 мкА, k_sw змінюється, R_eq = 0.15 Ом)
    def eff_buck_pfm(I):
        Iq = 2e-6
        # PFM знижує f_sw при малому струмі, втрати комутації ~ k*I
        P_loss = Vin * Iq + 0.04 * I + 0.18 * (I ** 2)
        Pout = Vout * I
        return 100.0 * (Pout / (Pout + P_loss))

    # Модель класичного Buck без PFM (жорсткий PWM 1.5 МГц, фіксовані втрати 15 мВт)
    def eff_buck_pwm(I):
        P_loss = 0.015 + 0.05 * I + 0.20 * (I ** 2)
        Pout = Vout * I
        return 100.0 * (Pout / (Pout + P_loss))

    def X(I):
        return x0 + (math.log10(I) - math.log10(Imin)) / (math.log10(Imax) - math.log10(Imin)) * (x1 - x0)
    def Y(e):
        return y1 - (e - emin) / (emax - emin) * (y1 - y0)

    s = []

    # Горизонтальна сітка
    for e in range(0, 101, 20):
        s.append(line(x0, Y(e), x1, Y(e), color="#eef0f3", sw=1.2))
        s.append(text(x0 - 12, Y(e) + 4, "%d%%" % e, size=12, color=MUTED, anchor="end"))

    # Осі
    s.append(line(x0, y1, x1, y1, color=INK, sw=1.6))
    s.append(line(x0, y0, x0, y1, color=INK, sw=1.6))

    # Позначки по осі X
    ticks = [(1e-6, "1 мкА"), (1e-5, "10 мкА"), (1e-4, "100 мкА"),
             (1e-3, "1 мА"), (1e-2, "10 мА"), (1e-1, "100 мА"), (1.0, "1 А"), (2.0, "2 А")]
    for I, lab in ticks:
        xi = X(I)
        s.append(line(xi, y1, xi, y1 + 6, color=INK, sw=1.4))
        s.append(line(xi, y0, xi, y1, color="#f4f5f7", sw=1.0))
        s.append(text(xi, y1 + 22, lab, size=12, color=MUTED))

    s.append(text(x0 - 45, (y0 + y1) / 2, "ККД (η)", size=13, color=INK, anchor="middle"))
    s.append(text((x0 + x1) / 2, y1 + 45, "Струм навантаження I_out (логарифмічна шкала)", size=13, color=INK))

    # Зони на графіку
    s.append(line(X(5e-4), y0, X(5e-4), y1, color="#cbd5e1", sw=1.2, dash="4 4"))
    s.append(line(X(0.3), y0, X(0.3), y1, color="#cbd5e1", sw=1.2, dash="4 4"))

    s.append(text((x0 + X(5e-4)) / 2, y0 + 16, "Зона мікрострумів (I_q)", size=11, color=MUTED))
    s.append(text((X(5e-4) + X(0.3)) / 2, y0 + 16, "Зона пікового ККД", size=11, color=COLOR_ACC))
    s.append(text((X(0.3) + x1) / 2, y0 + 16, "Зона I²·R втрат", size=11, color=COLOR_COND))

    # Криві
    pts_buck_pfm = [(X(I), Y(eff_buck_pfm(I))) for I in logspace(Imin, Imax, 120)]
    pts_ldo = [(X(I), Y(eff_ldo(I))) for I in logspace(Imin, Imax, 120)]
    pts_buck_pwm = [(X(I), Y(eff_buck_pwm(I))) for I in logspace(1e-5, Imax, 100)]

    s.append(polyline(pts_buck_pwm, COLOR_PWM, sw=2.2, dash="5 4"))
    s.append(polyline(pts_ldo, COLOR_LDO, sw=2.8))
    s.append(polyline(pts_buck_pfm, COLOR_BUCK, sw=3.2))

    # Підписи до кривих
    s.append(text(X(2e-4), Y(eff_ldo(2e-4)) + 18, "LDO (стеля Vout/Vin ≈ 89%)", size=12, color=COLOR_LDO, bold=True))
    s.append(text(X(0.04), Y(eff_buck_pfm(0.04)) - 12, "Buck з PFM/PWM (пік 95%)", size=12, color=COLOR_BUCK, bold=True))
    s.append(text(X(0.002), Y(eff_buck_pwm(0.002)) - 14, "Buck тільки PWM (провал при I < 10 мА)", size=11, color=COLOR_PWM))

    # Легенда внизу
    ly = 485
    s.append(line(70, ly, 110, ly, color=COLOR_BUCK, sw=3.2))
    s.append(text(120, ly + 4, "Синхронний Buck (PFM/PWM)", size=12, color=INK, anchor="start"))

    s.append(line(340, ly, 380, ly, color=COLOR_LDO, sw=2.8))
    s.append(text(390, ly + 4, "Нанопотужний LDO", size=12, color=INK, anchor="start"))

    s.append(line(570, ly, 610, ly, color=COLOR_PWM, sw=2.2, dash="5 4"))
    s.append(text(620, ly + 4, "Стандартний PWM Buck", size=12, color=INK, anchor="start"))

    render(os.path.join(OUT, 'efficiency-curves-ldo-vs-buck.svg'), W, H, *s,
           title="Залежність ККД від струму навантаження для різних топологій стабілізатора")

# ── Фігура 2: Часовий профіль навантаження (Сон 99% vs Сплеск 1%) ────────────
def fig_duty_cycle_profile():
    W, H = 820, 480
    s = []

    # Верхній графік: Струм навантаження у часі
    gx0, gx1, gy0, gy1 = 80, 750, 65, 230
    s.append(line(gx0, gy1, gx1, gy1, color=INK, sw=1.6))
    s.append(line(gx0, gy0, gx0, gy1, color=INK, sw=1.6))
    s.append(text(gx0 - 45, (gy0 + gy1) / 2, "Струм", size=13, color=INK, anchor="middle"))

    # Візуалізація циклу: 0..100 мс (95 мс сон, 5 мс активність для наочності малюнка)
    # Зони сну та сплеску
    # Сон 1
    s.append(rect(gx0 + 20, gy1 - 15, 260, 15, fill="#e8f4f8", stroke="#bce0fd", sw=1, rx=0))
    s.append(line(gx0, gy1 - 15, gx0 + 280, gy1 - 15, color=COLOR_BUCK, sw=2.5))
    # Сплеск
    s.append(rect(gx0 + 280, gy0 + 20, 50, gy1 - gy0 - 20, fill="#fdecea", stroke="#f5c6cb", sw=1, rx=0))
    s.append(line(gx0 + 280, gy1 - 15, gx0 + 280, gy0 + 20, color=POS, sw=2.5))
    s.append(line(gx0 + 280, gy0 + 20, gx0 + 330, gy0 + 20, color=POS, sw=2.5))
    s.append(line(gx0 + 330, gy0 + 20, gx0 + 330, gy1 - 15, color=POS, sw=2.5))
    # Сон 2
    s.append(rect(gx0 + 330, gy1 - 15, 360, 15, fill="#e8f4f8", stroke="#bce0fd", sw=1, rx=0))
    s.append(line(gx0 + 330, gy1 - 15, gx1 - 20, gy1 - 15, color=COLOR_BUCK, sw=2.5))

    # Підписи струмів
    s.append(text(gx0 - 10, gy1 - 15, "15 мкА", size=11, color=COLOR_BUCK, anchor="end"))
    s.append(text(gx0 - 10, gy0 + 25, "120 мА", size=11, color=POS, anchor="end"))

    # Позначки інтервалів
    s.append(line(gx0 + 20, gy1 + 15, gx0 + 280, gy1 + 15, color=MUTED, sw=1.2))
    s.append(text(gx0 + 150, gy1 + 32, "Сон (Sleep): 99% часу (t_sleep = 9.9 с)", size=12, color=INK))

    s.append(line(gx0 + 280, gy0 + 8, gx0 + 330, gy0 + 8, color=POS, sw=1.2))
    s.append(text(gx0 + 305, gy0 - 4, "Активність: 1% (t_active = 0.1 с)", size=11, color=POS, bold=True))

    # Нижня панель: Порівняння розподілу спожитої енергії (Дві стовпчикові діаграми)
    bx0, by0 = 80, 290
    bw, bh = 670, 160
    s.append(rect(bx0, by0, bw, bh, fill="#fafbfc", stroke="#e1e4e8", sw=1.4, rx=6))

    s.append(text(bx0 + 20, by0 + 25, "Структура втрат енергії за період (LDO vs імпульсний Buck):", size=13, color=INK, bold=True, anchor="start"))

    # Смужка 1: Нанопотужний LDO
    s.append(text(bx0 + 20, by0 + 60, "LDO (Iq = 0.8 мкА):", size=12, color=INK, anchor="start"))
    # Корисна енергія (зелена), втрати сну (сірі), втрати активності (червоні)
    s.append(rect(bx0 + 180, by0 + 46, 260, 22, fill="#27ae60", stroke="#219653", sw=1, rx=3))
    s.append(rect(bx0 + 440, by0 + 46, 12, 22, fill="#7f8c8d", stroke="#555", sw=1, rx=3))
    s.append(rect(bx0 + 452, by0 + 46, 75, 22, fill="#e74c3c", stroke="#c0392b", sw=1, rx=3))
    s.append(text(bx0 + 540, by0 + 62, "E_total = 1.34 мДж (η_avg = 77%)", size=12, color=INK, anchor="start"))

    # Смужка 2: Buck з великим Iq
    s.append(text(bx0 + 20, by0 + 105, "Buck (Iq = 60 мкА):", size=12, color=INK, anchor="start"))
    s.append(rect(bx0 + 180, by0 + 91, 260, 22, fill="#27ae60", stroke="#219653", sw=1, rx=3))
    s.append(rect(bx0 + 440, by0 + 91, 165, 22, fill="#7f8c8d", stroke="#555", sw=1, rx=3))
    s.append(rect(bx0 + 605, by0 + 91, 20, 22, fill="#e74c3c", stroke="#c0392b", sw=1, rx=3))
    s.append(text(bx0 + 635, by0 + 107, "E_total = 1.82 мДж (η_avg = 57%)", size=12, color=POS, bold=True, anchor="start"))

    # Підписи блоків
    s.append(circle(bx0 + 190, by0 + 140, 5, fill="#27ae60", stroke="#219653"))
    s.append(text(bx0 + 202, by0 + 144, "Корисна робота E_out", size=11, color=MUTED, anchor="start"))
    s.append(circle(bx0 + 360, by0 + 140, 5, fill="#7f8c8d", stroke="#555"))
    s.append(text(bx0 + 372, by0 + 144, "Втрати спокою (Iq) у сні", size=11, color=MUTED, anchor="start"))
    s.append(circle(bx0 + 540, by0 + 140, 5, fill="#e74c3c", stroke="#c0392b"))
    s.append(text(bx0 + 552, by0 + 144, "Втрати регулятора в активності", size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'duty-cycle-profile.svg'), W, H, *s,
           title="Профіль навантаження IoT-вузла та баланс розсіювання енергії")

# ── Фігура 3: Тепловий ланцюжок регулятора (P_loss, R_thJA, T_junction) ──────
def fig_thermal_chain():
    W, H = 820, 440
    s = []

    # Заголовок та вхідний потік тепла
    cx = 410
    s.append(text(cx, 60, "Електричні втрати: P_loss = (V_in − V_out)·I_out + V_in·I_q", size=14, color=POS, bold=True))
    s.append(arrow(cx, 75, cx, 115, color=POS, sw=2.5))

    # Вузол 1: Кристал (Junction)
    b1, w1, h1 = textbox(cx, 140, "Кристал напівпровідника (Junction)\nТемпература T_j ≤ 125 °C", size=13, fill="#fdecea", stroke=POS, bold=True)
    s.append(b1)

    s.append(arrow(cx, 165, cx, 205, color=LINE, sw=2.0))
    s.append(text(cx + 80, 185, "θ_JC (кристал-корпус)", size=12, color=MUTED, anchor="start"))

    # Вузол 2: Корпус мікросхеми (Case / Exposed Pad)
    b2, w2, h2 = textbox(cx, 230, "Корпус мікросхеми / Тепловий майданчик\nТемпература T_case", size=13, fill=FILL, stroke=LINE)
    s.append(b2)

    s.append(arrow(cx, 255, cx, 295, color=LINE, sw=2.0))
    s.append(text(cx + 80, 275, "θ_CS (корпус-плата/радіатор)", size=12, color=MUTED, anchor="start"))

    # Вузол 3: Плата (PCB / Heat Sink)
    b3, w3, h3 = textbox(cx, 320, "Друкована плата (Мідні полігони, Vias)\nТемпература T_pcb", size=13, fill=FILL, stroke=LINE)
    s.append(b3)

    s.append(arrow(cx, 345, cx, 385, color=LINE, sw=2.0))
    s.append(text(cx + 80, 365, "θ_SA (плата-повітря)", size=12, color=MUTED, anchor="start"))

    # Вузол 4: Навколишнє середовище
    s.append(text(cx, 405, "Навколишнє повітря (Ambient): T_a = 25...60 °C", size=13, color=COLOR_BUCK, bold=True))

    # Сумарний шлях праворуч: R_thJA
    s.append(line(cx + 260, 140, cx + 290, 140, color=POS, sw=1.5))
    s.append(line(cx + 290, 140, cx + 290, 405, color=POS, sw=1.5))
    s.append(line(cx + 260, 405, cx + 290, 405, color=POS, sw=1.5))
    s.append(text(cx + 300, 275, "Сумарний θ_JA = θ_JC + θ_CS + θ_SA\nΔT = P_loss · θ_JA", size=12, color=POS, bold=True, anchor="start"))

    # Ліворуч: Формула безпеки
    s.append(rect(50, 180, 200, 120, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    s.append(text(150, 205, "Умова безпеки кристала:", size=12, color=INK, bold=True))
    s.append(text(150, 235, "T_j = T_a + P_loss · θ_JA", size=13, color=POS, bold=True))
    s.append(text(150, 265, "T_j < T_j_max − 25°C", size=12, color=COLOR_ACC))
    s.append(text(150, 285, "(інженерний запас)", size=11, color=MUTED))

    render(os.path.join(OUT, 'thermal-resistance-model.svg'), W, H, *s,
           title="Тепловий ланцюг розсіювання потужності регулятора")

# ── Фігура 4: Дерево вибору топології живлення ──────────────────────────────
def fig_architecture_selection():
    W, H = 840, 500
    s = []

    # Корінь: Вхідні умови
    b_root, _, _ = textbox(420, 50, "Визначення діапазону вхідної напруги: V_in_min...V_in_max проти V_out", size=13, fill="#eaf0fd", stroke=COLOR_BUCK, bold=True)
    s.append(b_root)

    # 3 Гілки: Vin > Vout, Vin перетинає Vout, Vin < Vout
    s.append(arrow(240, 70, 160, 120, color=LINE, sw=1.6))
    s.append(arrow(420, 70, 420, 120, color=LINE, sw=1.6))
    s.append(arrow(600, 70, 680, 120, color=LINE, sw=1.6))

    s.append(text(175, 88, "V_in > V_out", size=11, color=INK, bold=True))
    s.append(text(485, 95, "V_in ≈ V_out", size=11, color=INK, bold=True, anchor="start"))
    s.append(text(665, 88, "V_in < V_out", size=11, color=INK, bold=True))

    # Вузол 1: V_in > V_out (Вибір між LDO та Buck)
    b_vdown, _, _ = textbox(160, 145, "Пониження напруги\n(V_in − V_out) та профіль струму", size=11, fill=FILL, stroke=LINE)
    s.append(b_vdown)

    # Вузол 2: V_in перетинає V_out
    b_vcross, _, _ = textbox(420, 145, "Діапазон перекриття\n(наприклад Li-ion 3.0..4.2 В → 3.3 В)", size=11, fill=FILL, stroke=LINE)
    s.append(b_vcross)

    # Вузол 3: V_in < V_out
    b_vup, _, _ = textbox(680, 145, "Підвищення напруги\n(наприклад 1.5 В батарейка → 3.3 В)", size=11, fill=FILL, stroke=LINE)
    s.append(b_vup)

    # Розгалуження для V_in > V_out
    s.append(arrow(110, 172, 85, 235, color=LINE, sw=1.4))
    s.append(arrow(210, 172, 235, 235, color=LINE, sw=1.4))

    s.append(text(45, 202, "Малий ΔV / Сон 99%", size=10, color=COLOR_LDO, anchor="start"))
    s.append(text(215, 202, "Великий ΔV / Струм >50 мА", size=10, color=COLOR_BUCK, anchor="start"))

    # Фінальні картки рішень
    # 1. LDO
    f1 = fitbox(20, 240, 170, 115, "LDO (лінійний)\n• Наднизький Iq (0.5..2 мкА)\n• Чисте живлення без шуму\n• Простий і компактний\n• Втрати: (Vin−Vout)·I", size=11, fill="#fdecea", stroke=COLOR_LDO)
    s.append(f1)

    # 2. Buck
    f2 = fitbox(210, 240, 170, 115, "Buck (Step-Down)\n• Високий ККД (до 95%)\n• Обов'язковий PFM для сну\n• Потребує L + C фільтр\n• Пульсації комутації", size=11, fill="#e8f4f8", stroke=COLOR_BUCK)
    s.append(f2)

    # 3. Buck-Boost & SEPIC
    s.append(arrow(420, 172, 420, 235, color=LINE, sw=1.4))
    f3 = fitbox(400, 240, 190, 115, "4-Switch Buck-Boost\n• Стабільні 3.3 В весь розряд\n• 4 MOSFET-ключі\n• Складніше керування\n• Альтернатива: Buck + LDO", size=11, fill="#f3e5f5", stroke=COLOR_PWM)
    s.append(f3)

    # 4. Boost
    s.append(arrow(680, 172, 680, 235, color=LINE, sw=1.4))
    f4 = fitbox(610, 240, 210, 115, "Boost (Step-Up)\n• Працює до повного розряду\n• Піковий струм ключа Iout/(1−D)\n• Струм к.з. через індуктивність\n• True-Shutdown розмикання", size=11, fill="#e8f8f5", stroke=COLOR_ACC)
    s.append(f4)

    # Нижній блок: Гібридні та багаторівневі компроміси
    s.append(rect(20, 375, 800, 100, fill="#fafbfc", stroke="#cbd5e1", sw=1.4, rx=6))
    s.append(text(420, 400, "Критерії компромісу в системному бюджеті:", size=13, color=INK, bold=True))
    s.append(text(420, 424, "1. Співвідношення часу Сон / Активність (Duty Cycle)  —  2. Допустимий рівень пульсацій живлення АЦП/радіо", size=12, color=MUTED))
    s.append(text(420, 448, "3. Тепловий бюджет кристала (P_loss · θ_JA)  —  4. Габарити друкованої плати та вартість компонентів", size=12, color=MUTED))

    render(os.path.join(OUT, 'architecture-selection-flow.svg'), W, H, *s,
           title="Дерево рішень щодо вибору архітектури регулятора напруги")

if __name__ == "__main__":
    fig_efficiency_curves()
    fig_duty_cycle_profile()
    fig_thermal_chain()
    fig_architecture_selection()
    print("All figures generated successfully.")
