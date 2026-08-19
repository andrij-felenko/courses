# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

REDBG   = "#fbecec"
GRNBG   = "#eef6ef"
BLUEBG  = "#e9eefb"
AMBERBG = "#fff3e0"
GRAYBG  = "#f8f9fa"

def polygon(pts, fill="#ffffff", stroke=LINE, sw=1.5):
    pts_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polygon points="{pts_str}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"/>'


# ── 1. faraday-flux-rule: Механізм індукції та правило знака Ленца ────────────
def fig_faraday_flux_rule():
    W, H = 760, 360
    p = []

    # Ліва панель: зовнішній потік зростає (dPhi/dt > 0)
    p.append(rect(30, 45, 335, 295, fill=BLUEBG, stroke=NEG, sw=1.5, rx=8))
    p.append(text(197, 70, "Зовнішній потік ЗРОСТАЄ (dΦ/dt > 0)", size=12, color=NEG, bold=True))
    
    # Контур зі стрілками індукції
    p.append(circle(197, 165, 60, fill="#ffffff", stroke=LINE, sw=2))
    # Зовнішнє поле (зелені стрілки вгору)
    p.append(arrow(170, 205, 170, 125, color=FIELD, sw=2))
    p.append(arrow(197, 205, 197, 125, color=FIELD, sw=2.5))
    p.append(arrow(224, 205, 224, 125, color=FIELD, sw=2))
    p.append(text(245, 135, "B_зовн ↑", size=11, color=FIELD, bold=True, anchor="start"))
    
    # Індуковане поле (проти зростання - червона стрілка вниз)
    p.append(arrow(197, 140, 197, 190, color=POS, sw=2))
    p.append(text(197, 208, "B_інд ↓ (проти)", size=10, color=POS, bold=True))

    # Струм індукції за годинниковою стрілкою
    p.append(text(197, 95, "Індукований струм I_інд", size=11, color=POS, bold=True))
    p.append(arrow(137, 165, 137, 150, color=POS, sw=2.5))
    p.append(arrow(257, 165, 257, 180, color=POS, sw=2.5))

    p.append(fitbox(45, 235, 305, 90,
                    "Правило Ленца (знак мінус):\n"
                    "Індукований струм створює поле B_інд,\n"
                    "яке намагається зупинити приріст потоку.\n"
                    "E = −dΦ/dt < 0",
                    size=10, fill="#ffffff", stroke=NEG, sw=1))

    # Права панель: зовнішній потік падає (dPhi/dt < 0)
    p.append(rect(395, 45, 335, 295, fill=REDBG, stroke=POS, sw=1.5, rx=8))
    p.append(text(562, 70, "Зовнішній потік СПАДАЄ (dΦ/dt < 0)", size=12, color=POS, bold=True))

    # Контур
    p.append(circle(562, 165, 60, fill="#ffffff", stroke=LINE, sw=2))
    # Зовнішнє поле (слабшає)
    p.append(arrow(540, 190, 540, 140, color=MUTED, sw=1.5))
    p.append(arrow(584, 190, 584, 140, color=MUTED, sw=1.5))
    p.append(text(610, 145, "B_зовн ↓", size=11, color=MUTED, bold=True, anchor="start"))

    # Індуковане поле (підтримує - зелена стрілка вгору)
    p.append(arrow(562, 190, 562, 135, color=FIELD, sw=2.5))
    p.append(text(562, 125, "B_інд ↑ (підтримує)", size=10, color=FIELD, bold=True))

    # Струм індукції проти годинникової стрілки
    p.append(text(562, 95, "Індукований струм I_інд", size=11, color=FIELD, bold=True))
    p.append(arrow(502, 165, 502, 180, color=FIELD, sw=2.5))
    p.append(arrow(622, 165, 622, 150, color=FIELD, sw=2.5))

    p.append(fitbox(410, 235, 305, 90,
                    "Електрична інерція контуру:\n"
                    "Індукований струм підтримує згасаюче поле,\n"
                    "протидіючи його зникненню.\n"
                    "E = −dΦ/dt > 0",
                    size=10, fill="#ffffff", stroke=POS, sw=1))

    render(os.path.join(OUT, "faraday-flux-rule.svg"), W, H, *p,
           title="Закон індукції Фарадея та правило Ленца")


# ── 2. inductive-kickback-breakdown: Анатомія індуктивного викиду ──────────────
def fig_inductive_kickback_breakdown():
    W, H = 760, 360
    p = []

    # Ліва половина: Ключ замкнено (накопичення струму)
    p.append(rect(30, 45, 335, 295, fill=GRAYBG, stroke=LINE, sw=1.5, rx=8))
    p.append(text(197, 70, "1. Ключ замкнено (сталий стан)", size=12, color=INK, bold=True))

    # Схема ліворуч
    p.append(text(65, 110, "+12 В", size=11, color=POS, bold=True))
    p.append(line(95, 105, 140, 105, color=LINE, sw=2))
    p.append(line(140, 105, 140, 125, color=LINE, sw=2))

    # Котушка L
    p.append(rect(125, 125, 30, 60, fill="#ffffff", stroke=LINE, sw=2, rx=4))
    p.append(text(140, 155, "L", size=13, color=INK, bold=True))
    p.append(arrow(165, 130, 165, 175, color=FIELD, sw=2))
    p.append(text(180, 155, "I_L = 2 А", size=10, color=FIELD, bold=True, anchor="start"))

    # Ключ замкнений
    p.append(line(140, 185, 140, 205, color=LINE, sw=2))
    p.append(line(140, 205, 140, 245, color=FIELD, sw=2.5)) # замкнений контакт
    p.append(text(175, 225, "SW (ON)", size=10, color=FIELD, bold=True, anchor="start"))
    p.append(line(140, 245, 140, 265, color=LINE, sw=2))
    p.append(line(120, 265, 160, 265, color=LINE, sw=2)) # Земля
    p.append(text(140, 280, "GND (0 В)", size=9, color=MUTED))

    p.append(textbox(197, 310, "Енергія в полі: W = ½·L·I² · V_SW = 0 В", size=9, fill="#ffffff", stroke=MUTED)[0])

    # Права половина: Ключ розмикається (індуктивний удар)
    p.append(rect(395, 45, 335, 295, fill=REDBG, stroke=POS, sw=1.8, rx=8))
    p.append(text(562, 70, "2. Ключ розімкнено (di/dt → −∞)", size=12, color=POS, bold=True))

    # Схема праворуч
    p.append(text(430, 110, "+12 В", size=11, color=POS, bold=True))
    p.append(line(460, 105, 505, 105, color=LINE, sw=2))
    p.append(line(505, 105, 505, 125, color=LINE, sw=2))

    # Котушка з перевернутою полярністю проти-ЕРС
    p.append(rect(490, 125, 30, 60, fill="#ffffff", stroke=POS, sw=2, rx=4))
    p.append(text(505, 155, "L", size=13, color=POS, bold=True))
    p.append(text(475, 135, "−", size=12, color=NEG, bold=True))
    p.append(text(475, 180, "+", size=12, color=POS, bold=True))
    p.append(text(530, 155, "V_L = +388 В", size=10, color=POS, bold=True, anchor="start"))

    # Розімкнений ключ
    p.append(line(505, 185, 505, 205, color=LINE, sw=2))
    p.append(circle(505, 205, 3, fill=POS, stroke=POS))
    p.append(line(505, 205, 525, 225, color=POS, sw=2)) # розімкнено
    p.append(circle(505, 245, 3, fill=POS, stroke=POS))
    p.append(line(505, 245, 505, 265, color=LINE, sw=2))
    p.append(line(485, 265, 525, 265, color=LINE, sw=2)) # Земля

    # Напруга на ключі
    p.append(arrow(545, 240, 545, 210, color=POS, sw=2))
    p.append(text(555, 225, "V_SW = 400 В!", size=11, color=POS, bold=True, anchor="start"))

    p.append(fitbox(410, 275, 305, 55,
                    "V_SW = V_CC + L·|di/dt|\n"
                    "Пробій MOSFET / дуга реле!",
                    size=10, fill="#ffffff", stroke=POS, sw=1.2, bold=True, color=POS))

    render(os.path.join(OUT, "inductive-kickback-breakdown.svg"), W, H, *p,
           title="Генезис індуктивного викиду напруги при комутації")


# ── 3. snubber-clamping-comparison: Порівняння трьох методів захисту ──────────
def fig_snubber_clamping_comparison():
    W, H = 760, 360
    p = []

    # 1. Flyback діод (ліва колонка)
    p.append(rect(20, 45, 225, 295, fill=GRAYBG, stroke=LINE, sw=1.5, rx=8))
    p.append(text(132, 68, "Flyback-діод", size=12, color=INK, bold=True))
    p.append(text(132, 85, "Найпростіший захист DC", size=9, color=MUTED))

    # Схема діода
    p.append(rect(95, 105, 24, 45, fill="#ffffff", stroke=LINE, sw=1.5, rx=3))
    p.append(text(107, 128, "L", size=10, color=INK, bold=True))
    p.append(line(135, 105, 135, 150, color=LINE, sw=1.5))
    p.append(polygon([(128, 133), (142, 133), (135, 120)], fill=NEG, stroke=NEG)) # діод вгору
    p.append(line(128, 120, 142, 120, color=NEG, sw=1.5))
    p.append(line(95, 105, 135, 105, color=LINE, sw=1.5))
    p.append(line(95, 150, 135, 150, color=LINE, sw=1.5))

    p.append(textbox(132, 185, "V_max = V_CC + 0.7 В", size=10, color=FIELD, bold=True, fill="#ffffff")[0])
    p.append(fitbox(30, 215, 205, 115,
                    "• Плюси: надійний кламп,\n  дешевий 1N4007/Schottky.\n"
                    "• Мінус: струм згасає повільно\n  (τ = L/R ≈ 10..50 мс).\n"
                    "  Затягує відпускання реле!",
                    size=9, fill="#ffffff", stroke=LINE, sw=1))

    # 2. TVS / Zener супресор (середня колонка)
    p.append(rect(265, 45, 230, 295, fill=GRNBG, stroke=FIELD, sw=1.5, rx=8))
    p.append(text(380, 68, "Діод + TVS / Zener", size=12, color=FIELD, bold=True))
    p.append(text(380, 85, "Швидке розсіювання енергії", size=9, color=INK))

    # Схема TVS
    p.append(rect(340, 105, 24, 45, fill="#ffffff", stroke=LINE, sw=1.5, rx=3))
    p.append(text(352, 128, "L", size=10, color=INK, bold=True))
    p.append(line(385, 105, 385, 150, color=LINE, sw=1.5))
    p.append(polygon([(378, 124), (392, 124), (385, 114)], fill=FIELD, stroke=FIELD))
    p.append(polygon([(378, 132), (392, 132), (385, 142)], fill=FIELD, stroke=FIELD))
    p.append(line(340, 105, 385, 105, color=LINE, sw=1.5))
    p.append(line(340, 150, 385, 150, color=LINE, sw=1.5))

    p.append(textbox(380, 185, "V_max = V_CC + V_Z", size=10, color=POS, bold=True, fill="#ffffff")[0])
    p.append(fitbox(275, 215, 210, 115,
                    "• Плюси: швидкий спад струму\n  (t_off = L·I / V_Z ≈ 0.5 мс),\n  зберігає контакти реле.\n"
                    "• Мінус: ключ має витримувати\n  напругу V_CC + V_Z.",
                    size=9, fill="#ffffff", stroke=FIELD, sw=1))

    # 3. RC-снубер (права колонка)
    p.append(rect(515, 45, 225, 295, fill=BLUEBG, stroke=NEG, sw=1.5, rx=8))
    p.append(text(627, 68, "RC / RCD Снубер", size=12, color=NEG, bold=True))
    p.append(text(627, 85, "Для AC та імпульсних SMPS", size=9, color=INK))

    # Схема RC
    p.append(rect(590, 105, 24, 45, fill="#ffffff", stroke=LINE, sw=1.5, rx=3))
    p.append(text(602, 128, "L", size=10, color=INK, bold=True))
    p.append(line(635, 105, 635, 118, color=LINE, sw=1.5))
    p.append(rect(627, 118, 16, 12, fill="#ffffff", stroke=NEG, sw=1.5)) # R
    p.append(line(635, 130, 635, 136, color=LINE, sw=1.5))
    p.append(line(627, 136, 643, 136, color=NEG, sw=2)) # C верх
    p.append(line(627, 140, 643, 140, color=NEG, sw=2)) # C низ
    p.append(line(635, 140, 635, 150, color=LINE, sw=1.5))
    p.append(line(590, 105, 635, 105, color=LINE, sw=1.5))
    p.append(line(590, 150, 635, 150, color=LINE, sw=1.5))

    p.append(textbox(627, 185, "Гасить dV/dt та дзвін", size=10, color=NEG, bold=True, fill="#ffffff")[0])
    p.append(fitbox(525, 215, 205, 115,
                    "• Плюси: працює в AC колах,\n  пригнічує EMI та дзвін LC.\n"
                    "• Мінус: розсіює потужність\n  P = C·V²·f_sw на резисторі.",
                    size=9, fill="#ffffff", stroke=NEG, sw=1))

    render(os.path.join(OUT, "snubber-clamping-comparison.svg"), W, H, *p,
           title="Порівняння методів демпфування індуктивного викиду")


# ── 4. smps-volt-second: Вольт-секундний баланс і ненасичення осердя ───────────
def fig_smps_volt_second():
    W, H = 760, 360
    p = []

    # Графік напруги V_L(t)
    p.append(rect(30, 45, 430, 295, fill=GRAYBG, stroke=LINE, sw=1.5, rx=8))
    p.append(text(245, 68, "Вольт-секундний баланс на котушці: ∫ V_L dt = 0", size=11, color=INK, bold=True))

    # Вісь часу та напруги
    p.append(line(60, 190, 430, 190, color=LINE, sw=1.5)) # вісь t
    p.append(arrow(60, 290, 60, 85, color=LINE, sw=1.5))  # вісь V
    p.append(text(50, 95, "V_L", size=11, color=INK, bold=True))
    p.append(text(420, 205, "t", size=11, color=INK))

    # Імпульс ON (зелена площа)
    p.append(rect(80, 110, 140, 80, fill=GRNBG, stroke=FIELD, sw=1.8))
    p.append(text(150, 145, "+ (V_in − V_out)", size=10, color=FIELD, bold=True))
    p.append(text(150, 165, "Площа A_on = V_on · t_on", size=9, color=FIELD))

    # Імпульс OFF (червона площа)
    p.append(rect(220, 190, 160, 70, fill=REDBG, stroke=POS, sw=1.8))
    p.append(text(300, 220, "− V_out", size=10, color=POS, bold=True))
    p.append(text(300, 240, "Площа A_off = V_off · t_off", size=9, color=POS))

    p.append(line(80, 275, 220, 275, color=FIELD, sw=1.5))
    p.append(text(150, 290, "t_on (накопичення)", size=9, color=FIELD))
    p.append(line(220, 275, 380, 275, color=POS, sw=1.5))
    p.append(text(300, 290, "t_off (віддача)", size=9, color=POS))

    # Права панель: Магнітний потік і наслідки дисбалансу
    p.append(rect(480, 45, 250, 295, fill=BLUEBG, stroke=NEG, sw=1.5, rx=8))
    p.append(text(605, 68, "Магнітний потік Φ(t)", size=12, color=NEG, bold=True))

    p.append(fitbox(490, 95, 230, 115,
                    "ΔΦ = (1/N) · ∫ V_L dt\n\n"
                    "Якщо A_on = A_off:\n"
                    "Потік повертається у вихідну\n"
                    "точку кожного періоду.\n"
                    "Стабільна робота SMPS!",
                    size=10, fill="#ffffff", stroke=FIELD, sw=1.2))

    p.append(fitbox(490, 220, 230, 110,
                    "УВАГА: Якщо A_on > A_off:\n"
                    "Потік щоперіоду зростає (дрейф),\n"
                    "осердя входить у НАСИЧЕННЯ,\n"
                    "L падає до нуля → струм злітає,\n"
                    "силовий ключ вибухає!",
                    size=9.5, fill=REDBG, stroke=POS, sw=1.5, color=POS, bold=True))

    render(os.path.join(OUT, "smps-volt-second.svg"), W, H, *p,
           title="Принцип вольт-секундного балансу в імпульсних перетворювачах")


# ── 5. pcb-loop-crosstalk: Індуктивна наводка та мінімізація петель на PCB ─────
def fig_pcb_loop_crosstalk():
    W, H = 760, 360
    p = []

    # Ліва половина: Погане трасування (велика площа петлі)
    p.append(rect(30, 45, 335, 295, fill=REDBG, stroke=POS, sw=1.5, rx=8))
    p.append(text(197, 68, "ПОГАНО: Велика площа петлі", size=12, color=POS, bold=True))
    p.append(text(197, 85, "Розрив землі / широкий контур", size=9, color=INK))

    # Сигнальна доріжка та далека земля
    p.append(line(60, 115, 320, 115, color=POS, sw=2.5))
    p.append(arrow(180, 115, 210, 115, color=POS, sw=2.5))
    p.append(text(70, 105, "Сигнал (Top Layer)", size=9, color=POS, anchor="start", bold=True))

    # Земля далеко внизу
    p.append(line(60, 215, 320, 215, color=LINE, sw=2))
    p.append(arrow(210, 215, 180, 215, color=LINE, sw=2))
    p.append(text(70, 230, "Шлях повернення GND (далеко)", size=9, color=MUTED, anchor="start"))

    # Заштрихована велетенська площа петлі
    p.append(rect(90, 125, 200, 80, fill="#fdecea", stroke=POS, sw=1.2))
    p.append(text(190, 155, "Величезна площа петлі A_loop", size=10, color=POS, bold=True))
    p.append(text(190, 175, "Ловить весь потік: V_noise = −dΦ/dt", size=9, color=POS))

    # Вектори завади B
    p.append(circle(120, 150, 8, fill="#ffffff", stroke=POS))
    p.append(text(120, 154, "×", size=12, color=POS, bold=True))
    p.append(circle(260, 150, 8, fill="#ffffff", stroke=POS))
    p.append(text(260, 154, "×", size=12, color=POS, bold=True))

    p.append(textbox(197, 305, "Високий Crosstalk, збої логіки та EMI", size=9.5, color=POS, bold=True, fill="#ffffff", stroke=POS)[0])

    # Права половина: Добре трасування (суцільний полігон землі)
    p.append(rect(395, 45, 335, 295, fill=GRNBG, stroke=FIELD, sw=1.5, rx=8))
    p.append(text(562, 68, "ДОБРЕ: Суцільний Ground Plane", size=12, color=FIELD, bold=True))
    p.append(text(562, 85, "Дзеркальний зворотний струм", size=9, color=INK))

    # Сигнальна доріжка
    p.append(line(425, 135, 685, 135, color=FIELD, sw=2.5))
    p.append(arrow(545, 135, 575, 135, color=FIELD, sw=2.5))
    p.append(text(435, 125, "Сигнал (Top Layer)", size=9, color=FIELD, anchor="start", bold=True))

    # Земляний шар безпосередньо під сигналом (товстий полігон)
    p.append(rect(425, 150, 260, 16, fill="#c8e6c9", stroke=FIELD, sw=1.5))
    p.append(arrow(575, 158, 545, 158, color=LINE, sw=2))
    p.append(text(435, 182, "GND Plane (Layer 2) прямо під доріжкою", size=9, color=INK, anchor="start"))

    p.append(fitbox(410, 205, 305, 80,
                    "Зворотний струм тече прямо під доріжкою\n"
                    "(шлях мінімальної індуктивності).\n"
                    "Площа петлі A → 0, потік Φ → 0,\n"
                    "Індукована завада придушена на >40 дБ!",
                    size=9.5, fill="#ffffff", stroke=FIELD, sw=1))

    p.append(textbox(562, 305, "Чистий сигнал, мінімальний EMI та Crosstalk", size=9.5, color=FIELD, bold=True, fill="#ffffff", stroke=FIELD)[0])

    render(os.path.join(OUT, "pcb-loop-crosstalk.svg"), W, H, *p,
           title="Індуктивна перехресна наводка на друкованій платі та мінімізація петель")


# ── 6. faraday-ring: Історичний дослід Фарадея (залізне кільце 1831 р.) ────────
def fig_faraday_ring():
    W, H = 760, 360
    p = []

    # Залізне кільце (осердя)
    p.append(circle(380, 180, 105, fill="#e2e8f0", stroke="#475569", sw=3))
    p.append(circle(380, 180, 65, fill="#ffffff", stroke="#475569", sw=3))
    p.append(text(380, 175, "Залізне", size=11, color="#334155", bold=True))
    p.append(text(380, 192, "кільце", size=11, color="#334155", bold=True))

    # Первинна обмотка (ліворуч)
    p.append(rect(260, 135, 30, 90, fill=REDBG, stroke=POS, sw=2, rx=4))
    p.append(textbox(275, 95, "Первинна обмотка (A)", size=10, fill=REDBG, stroke=POS, color=POS, bold=True)[0])

    # Коло первинної обмотки (батарея + ключ)
    p.append(line(260, 150, 140, 150, color=POS, sw=2))
    p.append(line(260, 210, 140, 210, color=LINE, sw=2))
    
    # Батарея
    p.append(line(140, 195, 140, 225, color=LINE, sw=2))
    p.append(line(130, 202, 130, 218, color=LINE, sw=3))
    p.append(text(135, 240, "Батарея", size=10, color=INK, bold=True))

    # Ключ ліворуч
    p.append(circle(140, 150, 3, fill=POS, stroke=POS))
    p.append(line(140, 150, 165, 130, color=POS, sw=2.5)) # розімкнений ключ
    p.append(circle(175, 150, 3, fill=POS, stroke=POS))
    p.append(text(155, 115, "Ключ (SW)", size=10, color=POS, bold=True))

    # Вторинна обмотка (праворуч)
    p.append(rect(470, 135, 30, 90, fill=BLUEBG, stroke=NEG, sw=2, rx=4))
    p.append(textbox(485, 95, "Вторинна обмотка (B)", size=10, fill=BLUEBG, stroke=NEG, color=NEG, bold=True)[0])

    # Коло вторинної обмотки (гальванометр)
    p.append(line(500, 150, 620, 150, color=NEG, sw=2))
    p.append(line(500, 210, 620, 210, color=NEG, sw=2))
    p.append(line(620, 150, 620, 160, color=NEG, sw=2))
    p.append(line(620, 200, 620, 210, color=NEG, sw=2))

    # Гальванометр
    p.append(circle(620, 180, 22, fill="#ffffff", stroke=NEG, sw=2))
    p.append(text(620, 175, "G", size=13, color=NEG, bold=True))
    p.append(arrow(620, 192, 632, 168, color=POS, sw=2)) # стрілка відхиляється
    p.append(text(620, 225, "Гальванометр", size=10, color=NEG, bold=True))

    # Пояснювальні плашки внизу
    p.append(fitbox(50, 275, 310, 65,
                    "У мить замикання/розмикання ключа:\n"
                    "Магнітний потік в кільці ЗМІНЮЄТЬСЯ (dΦ/dt ≠ 0).\n"
                    "Стрілка гальванометра коротко відхиляється!",
                    size=9.5, fill=GRNBG, stroke=FIELD, sw=1.2))

    p.append(fitbox(400, 275, 310, 65,
                    "При замкненому ключі (сталий струм):\n"
                    "Магнітне поле велике, але СТАЛЕ (dΦ/dt = 0).\n"
                    "Струм у вторинному колі СТРОГО НУЛЬ.",
                    size=9.5, fill=GRAYBG, stroke=MUTED, sw=1.2))

    render(os.path.join(OUT, "faraday-ring.svg"), W, H, *p,
           title="Історичний дослід Майкла Фарадея: залізне кільце (29 серпня 1831 р.)")


def main():
    fig_faraday_flux_rule()
    fig_inductive_kickback_breakdown()
    fig_snubber_clamping_comparison()
    fig_smps_volt_second()
    fig_pcb_loop_crosstalk()
    fig_faraday_ring()
    print("All 6 figures rendered successfully.")

if __name__ == "__main__":
    main()

