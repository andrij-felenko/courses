# -*- coding: utf-8 -*-
"""Фігури до теми «Трансформатор струму й котушка Роговського».
Запуск: python figs.py  → записує SVG у ./img/
"""
import sys, os, math

# Додаємо шлях до scripts/ у корені репо для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

COLOR_BLUE = "#2457d6"
COLOR_RED = "#c0392b"
COLOR_GREEN = "#27ae60"
COLOR_ORANGE = "#d35400"
COLOR_PURPLE = "#8e44ad"
COLOR_GRAY = "#7f8c8d"


# ── Фігура 1: Принцип дії трансформатора струму (CT) ────────────────────────
def fig_ct_principle():
    W, H = 840, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Принцип дії вимірювального трансформатора струму (CT) і навантажувальний резистор", size=15, bold=True))

    # Ліва частина: фізична геометрія тороїдального CT
    f.append(text(210, 56, "Фізична модель: тороїд і баланс МРС", size=13, bold=True, color=COLOR_BLUE))

    # Первинний провідник (шинний провідник крізь центр)
    f.append(rect(40, 190, 340, 24, fill='#f9ebea', stroke=COLOR_RED, sw=2, rx=4))
    f.append(arrow(60, 202, 110, 202, color=COLOR_RED, sw=2))
    f.append(arrow(290, 202, 350, 202, color=COLOR_RED, sw=2))
    f.append(text(180, 175, "Первинний струм I₁ (N₁ = 1)", size=11, bold=True, color=COLOR_RED))

    # Тороїдальне магнітне осердя (подвійне коло)
    f.append(circle(210, 202, 85, fill='none', stroke='#566573', sw=14))
    f.append(circle(210, 202, 85, fill='none', stroke='#abb2b9', sw=10))

    # Стрілка магнітного потоку в осерді
    f.append(arrow(210, 117, 230, 117, color=COLOR_PURPLE, sw=2))
    f.append(text(210, 102, "Магнітний потік Φ(t)", size=11, bold=True, color=COLOR_PURPLE))

    # Вторинна обмотка N2 (показано витки на нижньому секторі тороїда)
    for i in range(7):
        ang_x = 175 + i * 12
        f.append(line(ang_x, 265, ang_x + 6, 305, color=COLOR_BLUE, sw=2.5))

    # Виводи вторинної обмотки
    f.append(line(175, 305, 175, 350, color=COLOR_BLUE, sw=2))
    f.append(line(247, 305, 247, 350, color=COLOR_BLUE, sw=2))
    f.append(line(175, 350, 200, 350, color=COLOR_BLUE, sw=2))
    f.append(line(247, 350, 222, 350, color=COLOR_BLUE, sw=2))

    # Резистор навантаження Rb (Burden)
    f.append(rect(200, 342, 22, 16, fill='#eaf2f8', stroke=COLOR_BLUE, sw=1.8, rx=2))
    f.append(text(211, 375, "Rb (Burden)", size=11, bold=True, color=COLOR_BLUE))
    f.append(text(211, 325, "I₂ = I₁ · (N₁ / N₂)", size=11, bold=True, color=COLOR_BLUE))

    # Вертикальна розділова лінія
    f.append(line(420, 50, 420, 395, color="#d5dbdb", sw=1.4, dash="5,5"))

    # Права частина: Еквівалентна електрична схема
    f.append(text(630, 56, "Еквівалентна схема вторинного кола", size=13, bold=True, color=COLOR_GREEN))

    # Ідеальне джерело вторинного струму I2'
    f.append(circle(480, 140, 20, fill='#f4f6f7', stroke=LINE, sw=1.8))
    f.append(text(480, 140, "I₂'", size=12, bold=True, color=COLOR_BLUE))
    f.append(arrow(480, 154, 480, 126, color=COLOR_BLUE, sw=1.5))

    # Горизонтальні шини
    f.append(line(480, 90, 780, 90, color=LINE, sw=1.8))
    f.append(line(480, 190, 780, 190, color=LINE, sw=1.8))
    f.append(line(480, 90, 480, 120, color=LINE, sw=1.8))
    f.append(line(480, 160, 480, 190, color=LINE, sw=1.8))

    # Вітка намагнічування: Rfe (втрати в осерді) паралельно Lm (індуктивність)
    # Rfe
    f.append(line(550, 90, 550, 115, color=LINE, sw=1.5))
    f.append(rect(542, 115, 16, 30, fill='#fdfefe', stroke=INK, sw=1.5, rx=2))
    f.append(text(525, 133, "Rfe", size=10, color=MUTED))
    f.append(line(550, 145, 550, 190, color=LINE, sw=1.5))

    # Lm (індуктивність намагнічування)
    f.append(line(600, 90, 600, 115, color=LINE, sw=1.5))
    f.append(circle(600, 123, 7, fill='none', stroke=COLOR_PURPLE, sw=1.5))
    f.append(circle(600, 137, 7, fill='none', stroke=COLOR_PURPLE, sw=1.5))
    f.append(text(622, 133, "Lm", size=10, bold=True, color=COLOR_PURPLE))
    f.append(line(600, 145, 600, 190, color=LINE, sw=1.5))

    # Послідовний опір обмотки Rw та індуктивність розсіювання
    f.append(rect(650, 82, 28, 16, fill='#fdfefe', stroke=INK, sw=1.5, rx=2))
    f.append(text(664, 73, "Rw₂", size=10, color=MUTED))

    # Навантажувальний резистор Rb на виході
    f.append(line(740, 90, 740, 115, color=COLOR_BLUE, sw=1.8))
    f.append(rect(731, 115, 18, 36, fill='#eaf2f8', stroke=COLOR_BLUE, sw=2, rx=3))
    f.append(text(765, 133, "Rb", size=12, bold=True, color=COLOR_BLUE))
    f.append(line(740, 151, 740, 190, color=COLOR_BLUE, sw=1.8))

    # Вихідна напруга Vout
    f.append(circle(780, 90, 3.5, fill=COLOR_RED, stroke=LINE, sw=1))
    f.append(circle(780, 190, 3.5, fill=COLOR_BLUE, stroke=LINE, sw=1))
    f.append(arrow(780, 175, 780, 105, color=COLOR_GREEN, sw=1.5))
    f.append(text(805, 140, "Vout", size=12, bold=True, color=COLOR_GREEN))

    # Пояснювальний текстовий блок унизу праворуч
    b, w, h = textbox(630, 295,
                      "Закон ампер-витків:  I₁·N₁ − I₂·N₂ = I_m·N₁ ≈ 0\n"
                      "При малому навантаженні (Rb << ωLm) весь струм іде в Rb:\n"
                      "Vout(t) = I₁(t) · (N₁ / N₂) · Rb  [струмовий режим]",
                      size=11, pad=8, fill='#eafaf1', stroke='#a3e4d7', sw=1.2)
    f.append(b)

    # Пояснення знизу зліва
    b_left, w_l, h_l = textbox(210, 395, "Осердя з високим μ_r (10 000..80 000) мінімізує струм намагнічування I_m",
                               size=10, pad=5, fill='#fdfefe', stroke='#d5dbdb', sw=1)
    f.append(b_left)

    return render(os.path.join(IMG, "ct-working-principle.svg"), W, H, *f)


# ── Фігура 2: Небезпека розімкненого кола вторинної обмотки CT ──────────────
def fig_ct_open_circuit():
    W, H = 840, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Небезпека розімкненого вторинного кола трансформатора струму", size=15, bold=True))

    midx = 420
    f.append(line(midx, 48, midx, H - 15, color="#d5dbdb", sw=1.4, dash="5,5"))

    # Ліва частина: Осцилограми при розриві вторинного кола
    f.append(text(210, 52, "Осцилограми при I₂ = 0 (розрив Rb)", size=13, bold=True, color=COLOR_RED))

    # Вісь часу графіка 1 (Первинний струм I1)
    f.append(line(50, 100, 370, 100, color=MUTED, sw=1.2))
    f.append(text(380, 104, "t", size=11, color=MUTED))
    f.append(text(40, 75, "I₁(t)", size=11, bold=True, color=COLOR_BLUE))
    # Синусоїда струму I1
    f.append('<path d="M 50 100 Q 90 40 130 100 T 210 100 T 290 100 T 370 100" fill="none" stroke="%s" stroke-width="2"/>' % COLOR_BLUE)

    # Вісь часу графіка 2 (Магнітна індукція в осерді B(t))
    f.append(line(50, 185, 370, 185, color=MUTED, sw=1.2))
    f.append(text(380, 189, "t", size=11, color=MUTED))
    f.append(text(40, 160, "B(t)", size=11, bold=True, color=COLOR_PURPLE))
    f.append(line(50, 155, 370, 155, color="#e74c3c", sw=1, dash="3,3"))
    f.append(text(385, 157, "+Bsat", size=9, color=COLOR_RED))
    f.append(line(50, 215, 370, 215, color="#e74c3c", sw=1, dash="3,3"))
    f.append(text(385, 217, "-Bsat", size=9, color=COLOR_RED))
    # Трапецієподібна насичена крива B(t)
    f.append('<path d="M 50 185 L 60 155 L 120 155 L 140 215 L 200 215 L 220 155 L 280 155 L 300 215 L 360 215 L 370 185" fill="none" stroke="%s" stroke-width="2.2"/>' % COLOR_PURPLE)

    # Вісь часу графіка 3 (Вторинна напруга V_open(t) = -N2 * dB/dt)
    f.append(line(50, 310, 370, 310, color=MUTED, sw=1.2))
    f.append(text(380, 314, "t", size=11, color=MUTED))
    f.append(text(35, 260, "V₂(t)", size=11, bold=True, color=COLOR_RED))
    # Гострі високовольтні імпульси під час переходів B(t) через 0
    f.append('<path d="M 50 310 L 58 310 L 60 240 L 62 310 L 138 310 L 140 380 L 142 310 L 218 310 L 220 240 L 222 310 L 298 310 L 300 380 L 302 310 L 370 310" fill="none" stroke="%s" stroke-width="2.5"/>' % COLOR_RED)
    f.append(text(85, 235, "+1..5 кВ!", size=11, bold=True, color=COLOR_RED))
    f.append(text(165, 395, "−1..5 кВ!", size=11, bold=True, color=COLOR_RED))

    # Права частина: Захист від розриву кола
    f.append(text(630, 52, "Захист та регламент обслуговування", size=13, bold=True, color=COLOR_GREEN))

    # Схема захисту
    f.append(rect(460, 80, 340, 180, fill='#fdfefe', stroke='#bdc3c7', sw=1.5, rx=6))
    f.append(text(630, 102, "Схема захисту вторинної обмотки", size=12, bold=True, color=INK))

    # Обмотка CT
    f.append(line(490, 130, 490, 160, color=COLOR_BLUE, sw=2))
    f.append(circle(490, 168, 8, fill='none', stroke=COLOR_BLUE, sw=1.8))
    f.append(circle(490, 184, 8, fill='none', stroke=COLOR_BLUE, sw=1.8))
    f.append(circle(490, 200, 8, fill='none', stroke=COLOR_BLUE, sw=1.8))
    f.append(line(490, 208, 490, 235, color=COLOR_BLUE, sw=2))
    f.append(text(465, 185, "N₂", size=11, bold=True, color=COLOR_BLUE))

    # Шини до виходу
    f.append(line(490, 130, 770, 130, color=LINE, sw=1.8))
    f.append(line(490, 235, 770, 235, color=LINE, sw=1.8))

    # 1. Закорочувальний перемикач (Shorting block / switch)
    f.append(line(580, 130, 580, 160, color='#e67e22', sw=1.8))
    f.append(line(580, 175, 580, 235, color='#e67e22', sw=1.8))
    f.append(line(580, 160, 595, 172, color='#e67e22', sw=2.2)) # розімкнений ключ
    f.append(circle(580, 160, 3, fill='#e67e22', stroke=LINE, sw=1))
    f.append(circle(580, 175, 3, fill='#e67e22', stroke=LINE, sw=1))
    f.append(text(580, 118, "Закоротка", size=10, bold=True, color=COLOR_ORANGE))

    # 2. TVS-супресор двонапрямковий
    f.append(line(670, 130, 670, 165, color=COLOR_RED, sw=1.6))
    f.append(rect(661, 165, 18, 35, fill='#fadbd8', stroke=COLOR_RED, sw=1.5, rx=2))
    f.append(text(670, 186, "TVS", size=10, bold=True, color=COLOR_RED))
    f.append(line(670, 200, 670, 235, color=COLOR_RED, sw=1.6))

    # 3. Вихід на вимірювальний резистор Rb
    f.append(line(750, 130, 750, 165, color=COLOR_BLUE, sw=1.8))
    f.append(rect(741, 165, 18, 35, fill='#ebf5fb', stroke=COLOR_BLUE, sw=1.8, rx=2))
    f.append(text(750, 186, "Rb", size=11, bold=True, color=COLOR_BLUE))
    f.append(line(750, 200, 750, 235, color=COLOR_BLUE, sw=1.8))

    # Текстовий блок із правилами безпеки
    b_rules, w_r, h_r = textbox(630, 345,
                                "ПРАВИЛА БЕЗПЕКИ ПРИ РОБОТІ З CT:\n"
                                "1. ЗАБОРОНЕНО розривати коло вторинної обмотки під струмом!\n"
                                "2. Перед демонтажем амперметра/Rb — ЗАКОРОТИТИ вторинну обмотку.\n"
                                "3. На платах — обов'язковий захисний двонапрямковий TVS/варистор\n"
                                "   паралельно Rb для обмеження викидів на рівні < 15 В.",
                                size=11, pad=8, fill='#fef9e7', stroke='#f9e79f', sw=1.2)
    f.append(b_rules)

    return render(os.path.join(IMG, "ct-open-circuit-hazard.svg"), W, H, *f)


# ── Фігура 3: Конструкція котушки Роговського ────────────────────────────────
def fig_rogowski_construction():
    W, H = 840, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Конструкція котушки Роговського та компенсація зовнішніх полів", size=15, bold=True))

    midx = 420
    f.append(line(midx, 50, midx, H - 15, color="#d5dbdb", sw=1.4, dash="5,5"))

    # Ліва частина: Геометрія та центральний зворотний провідник
    f.append(text(210, 56, "Топологія намотки та зворотна петля", size=13, bold=True, color=COLOR_BLUE))

    # Силовий кабель зі струмом i(t) по центру
    f.append(circle(210, 200, 28, fill='#fadbd8', stroke=COLOR_RED, sw=2))
    f.append(circle(210, 200, 6, fill=COLOR_RED, stroke='none', sw=0))
    f.append(text(210, 200, "i(t)", size=12, bold=True, color=COLOR_RED))

    # Немагнітний каркас (повітряне осердя, mu_r = 1)
    f.append(circle(210, 200, 105, fill='none', stroke='#eaeded', sw=24))
    f.append(circle(210, 200, 105, fill='none', stroke='#bdc3c7', sw=1.5))

    # Центральний зворотний провідник (Return Conductor всередині каркаса)
    f.append(circle(210, 200, 105, fill='none', stroke=COLOR_ORANGE, sw=2.5))

    # Витки обмотки навколо немагнітного каркаса
    for ang_deg in range(15, 345, 12):
        rad = math.radians(ang_deg)
        cx = 210 + 105 * math.cos(rad)
        cy = 200 + 105 * math.sin(rad)
        dx = 14 * math.cos(rad)
        dy = 14 * math.sin(rad)
        f.append(line(cx - dx, cy - dy, cx + dx, cy + dy, color=COLOR_BLUE, sw=2.2))

    # Замок/стик котушки Роговського
    f.append(rect(195, 80, 30, 30, fill='#fcf3cf', stroke='#f39c12', sw=1.8, rx=4))
    f.append(text(210, 72, "Рознімний замок", size=10, bold=True, color='#b9770e'))

    # Виводи котушки
    f.append(line(210, 305, 210, 345, color=COLOR_BLUE, sw=2))
    f.append(line(210, 320, 230, 320, color=COLOR_ORANGE, sw=2))
    f.append(line(230, 320, 230, 345, color=COLOR_ORANGE, sw=2))
    f.append(text(220, 365, "v(t) = −M · (di/dt)", size=12, bold=True, color=COLOR_PURPLE))

    # Підписи деталей зліва
    f.append(text(210, 125, "Зворотний провідник у центрі", size=10, bold=True, color=COLOR_ORANGE))
    f.append(text(85, 200, "Повітряне осердя (μᵣ = 1)", size=10, color=MUTED))

    # Права частина: Переваги та математична модель
    f.append(text(630, 56, "Взаємна індуктивність та властивості", size=13, bold=True, color=COLOR_GREEN))

    # Текстовий блок із формулами
    b_math, w_m, h_m = textbox(630, 140,
                               "Теорема про циркуляцію (закон Ампера):\n"
                               "  ∮ H·dl = i(t)   [повний охоплений струм]\n\n"
                               "ЕРС індукції в контурі Фарадея:\n"
                               "  v(t) = −μ₀ · n · A · (di/dt) = −M · (di(t)/dt)\n"
                               "  де M = μ₀·n·A — взаємна індуктивність котушки.",
                               size=11, pad=8, fill='#f4f6f7', stroke='#d5dbdb', sw=1.2)
    f.append(b_math)

    # Порівняльна таблиця переваг
    b_feat, w_f, h_f = textbox(630, 295,
                               "КЛЮЧОВІ ПЕРЕВАГИ КОТУШКИ РОГОВСЬКОГО:\n"
                               "• Немає феромагнетика → АБСОЛЮТНА лінійність від 1 А до 100 кА.\n"
                               "• Нульове насичення осердя при будь-яких надструмах КЗ.\n"
                               "• Безпека: розрив кола дає лише мілівольти (немає кіловольт).\n"
                               "• Гнучкий розімкнений контур: монтаж без розриву товстих шин.\n"
                               "• Смуга частот: від одиниць герц до десятків мегагерц.",
                               size=10.5, pad=8, fill='#eafaf1', stroke='#a3e4d7', sw=1.2)
    f.append(b_feat)

    return render(os.path.join(IMG, "rogowski-coil-construction.svg"), W, H, *f)


# ── Фігура 4: Аналоговий та цифровий інтегратор для сигналу Роговського ─────
def fig_integrator_circuits():
    W, H = 840, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Схемотехніка аналогового та цифрового інтеграторів для котушки Роговського", size=15, bold=True))

    midx = 420
    f.append(line(midx, 50, midx, H - 15, color="#d5dbdb", sw=1.4, dash="5,5"))

    # Ліва частина: Аналоговий активний інтегратор на ОП
    f.append(text(210, 56, "1. Аналоговий інтегратор із витоком (Leaky)", size=13, bold=True, color=COLOR_BLUE))

    # Вхідний сигнал v_in = -M * di/dt
    f.append(line(40, 160, 90, 160, color=COLOR_BLUE, sw=1.8))
    f.append(text(65, 145, "Vin(t)", size=11, bold=True, color=COLOR_BLUE))
    f.append(circle(40, 160, 3.5, fill=COLOR_BLUE, stroke=LINE, sw=1))

    # Вхідний резистор R_in
    f.append(rect(90, 152, 35, 16, fill='#fdfefe', stroke=INK, sw=1.5, rx=2))
    f.append(text(107, 142, "R_in", size=10, color=INK))
    f.append(line(125, 160, 180, 160, color=LINE, sw=1.8))

    # Операційний підсилювач (трикутник)
    f.append('<polygon points="180,140 180,210 240,175" fill="#f4f6f7" stroke="%s" stroke-width="1.8"/>' % LINE)
    f.append(text(188, 163, "−", size=14, bold=True, color=COLOR_RED))
    f.append(text(188, 193, "+", size=14, bold=True, color=COLOR_GREEN))

    # Неінвертуючий вхід на віртуальну землю (Vref або GND)
    f.append(line(180, 190, 150, 190, color=LINE, sw=1.5))
    f.append(line(150, 190, 150, 210, color=LINE, sw=1.5))
    f.append(line(140, 210, 160, 210, color=MUTED, sw=1.5))
    f.append(text(150, 225, "Vref", size=10, color=MUTED))

    # Вузол інвертуючого входу для зворотного зв'язку
    f.append(circle(160, 160, 3, fill=INK, stroke='none', sw=0))
    f.append(line(160, 160, 160, 100, color=LINE, sw=1.5))
    f.append(line(160, 100, 270, 100, color=LINE, sw=1.5))

    # Паралельні C_int та R_f (Leaky resistor) у ланцюзі ЗЗ
    # Гілка C_int
    f.append(line(190, 100, 190, 80, color=LINE, sw=1.4))
    f.append(line(190, 80, 205, 80, color=LINE, sw=1.4))
    f.append(line(205, 70, 205, 90, color=COLOR_PURPLE, sw=2))
    f.append(line(212, 70, 212, 90, color=COLOR_PURPLE, sw=2))
    f.append(line(212, 80, 240, 80, color=LINE, sw=1.4))
    f.append(line(240, 80, 240, 100, color=LINE, sw=1.4))
    f.append(text(222, 62, "C_int", size=10, bold=True, color=COLOR_PURPLE))

    # Гілка R_f (розряджає DC-дрейф ОП)
    f.append(line(190, 100, 190, 120, color=LINE, sw=1.4))
    f.append(line(190, 120, 200, 120, color=LINE, sw=1.4))
    f.append(rect(200, 112, 30, 16, fill='#fdfefe', stroke=COLOR_RED, sw=1.5, rx=2))
    f.append(line(230, 120, 240, 120, color=LINE, sw=1.4))
    f.append(line(240, 120, 240, 100, color=LINE, sw=1.4))
    f.append(text(215, 138, "Rf (витік)", size=10, bold=True, color=COLOR_RED))

    # З'єднання ЗЗ з виходом ОП
    f.append(line(240, 175, 270, 175, color=LINE, sw=1.8))
    f.append(line(270, 100, 270, 175, color=LINE, sw=1.5))
    f.append(circle(270, 175, 3, fill=INK, stroke='none', sw=0))
    f.append(line(270, 175, 360, 175, color=COLOR_GREEN, sw=2))
    f.append(circle(360, 175, 3.5, fill=COLOR_GREEN, stroke=LINE, sw=1))
    f.append(text(330, 160, "Vout ∝ i(t)", size=12, bold=True, color=COLOR_GREEN))

    # Пояснення зрізу аналогового інтегратора
    b_ana, w_a, h_a = textbox(210, 320,
                              "Функція передачі аналогового інтегратора:\n"
                              "  H(s) = − (Rf / Rin) / (1 + s · Rf · Cint)\n\n"
                              "Частота зрізу ФНЧ:  fc = 1 / (2π · Rf · Cint) ≤ 0.5 Гц\n"
                              "При f >> fc:  Vout(t) = (M / (Rin·Cint)) · i(t)",
                              size=10.5, pad=8, fill='#eaf2f8', stroke='#aed6f1', sw=1.2)
    f.append(b_ana)

    # Права частина: Цифровий конвеєр DSP інтегрування в MCU
    f.append(text(630, 56, "2. Цифровий інтегратор (DSP конвеєр MCU)", size=13, bold=True, color=COLOR_GREEN))

    # Блоки конвеєра: АЦП -> DC-Blocker -> Leaky Integrator -> Scaling/RMS
    blocks = [
        ("Швидкий АЦП (ADC)\nдискретизація fs ≥ 10 кГц", 105),
        ("Цифровий IIR ФВЧ (DC-Blocker)\ny_dc[n] = x[n] − x[n-1] + α·y[n-1]", 175),
        ("Leaky інтегратор Трапецій (Tustin)\ny[n] = λ·y[n-1] + (Ts/2)·(x[n] + x[n-1])", 255),
        ("Калібрування та розрахунок\nI_rms = √(Σ i²[n] / N), P = Σ u·i / N", 345)
    ]

    for i, (txt, cy) in enumerate(blocks):
        b_dsp, w_d, h_d = textbox(630, cy, txt, size=10.5, pad=6, fill='#fdfefe', stroke=COLOR_GREEN if i==2 else LINE, sw=1.5, rx=5)
        f.append(b_dsp)
        if i < len(blocks) - 1:
            next_cy = blocks[i+1][1]
            f.append(arrow(630, cy + 22, 630, next_cy - 22, color=COLOR_BLUE, sw=1.6))

    return render(os.path.join(IMG, "integrator-analog-digital.svg"), W, H, *f)


if __name__ == '__main__':
    fig_ct_principle()
    fig_ct_open_circuit()
    fig_rogowski_construction()
    fig_integrator_circuits()
    print("Всі 4 фігури згенеровано успішно у ./img/")
