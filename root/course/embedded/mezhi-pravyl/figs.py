# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. combinatorial-explosion: експоненційний вибух станів проти покриття ────
def fig_combinatorial_explosion():
    W, H = 880, 440
    p = []

    # Тло блоку графіка
    p.append(rect(40, 60, 420, 340, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(250, 88, "Зростання комбінацій станів (k^N)", size=13, color=INK, bold=True))

    # Осі
    x0, y0 = 90, 350
    xw, yh = 340, 230
    p.append(line(x0, y0, x0 + xw, y0, color=LINE, sw=1.8))
    p.append(line(x0, y0, x0, y0 - yh, color=LINE, sw=1.8))
    p.append(text(x0 + xw - 10, y0 + 24, "Кількість змінних N →", size=10, color=MUTED, anchor="end"))
    p.append(text(x0 - 10, y0 - yh + 10, "Стани", size=10, color=MUTED, anchor="end"))

    # Сітка та мітки
    for i, n_val in enumerate(["2", "4", "6", "8"]):
        gx = x0 + 60 + i * 75
        p.append(line(gx, y0, gx, y0 - yh, color="#e2e8f0", sw=1, dash="3,3"))
        p.append(text(gx, y0 + 18, n_val, size=10, color=MUTED))

    # Криві
    p.append(f'<path d="M {x0} {y0} Q {x0+150} {y0-20} {x0+285} {y0-105}" fill="none" stroke="{NEG}" stroke-width="2.2"/>')
    p.append(f'<path d="M {x0} {y0} Q {x0+180} {y0-60} {x0+285} {y0-225}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    p.append(text(x0 + 295, y0 - 105, "2^N (бінарні)", size=10, color=NEG, anchor="start", bold=True))
    p.append(text(x0 + 295, y0 - 225, "4^N (квантовані)", size=10, color=POS, anchor="start", bold=True))

    # Лінія можливості ручного покриття (стеля людини/команди)
    p.append(line(x0, y0 - 65, x0 + xw, y0 - 65, color="#d97706", sw=1.8, dash="5,4"))
    p.append(text(x0 + 120, y0 - 72, "Стеля ручних правил (~200 правил)", size=10, color="#d97706", bold=True))

    # Правий блок: матриця простору та «темні кути»
    bx, by, bw, bh = 485, 60, 360, 340
    p.append(rect(bx, by, bw, bh, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(bx + bw/2, by + 26, "Покриття простору станів", size=13, color=INK, bold=True))

    # Квадрат усього простору станів
    sx, sy, sw_box, sh_box = bx + 30, by + 50, 300, 180
    p.append(rect(sx, sy, sw_box, sh_box, fill="#fee2e2", stroke=POS, sw=1.5, rx=4))
    p.append(text(sx + sw_box/2, sy + sh_box/2 + 20, "Непокритий простір (>99% станів)", size=11, color=POS, bold=True))
    p.append(text(sx + sw_box/2, sy + sh_box/2 + 38, "Непередбачені комбінації, збої, else-гілки", size=9, color=MUTED))

    # Маленький сектор ручного покриття
    p.append(rect(sx, sy, 70, 50, fill="#dcfce7", stroke=FIELD, sw=1.8, rx=4))
    p.append(text(sx + 35, sy + 22, "Ручні IF", size=10, color=FIELD, bold=True))
    p.append(text(sx + 35, sy + 36, "< 1%", size=9, color=FIELD))

    # Пояснювальні картки знизу
    p.append(rect(bx + 15, by + 245, 155, 75, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=6))
    p.append(text(bx + 92, by + 265, "6 змінних по 5 рівнів", size=10, color=INK, bold=True))
    p.append(text(bx + 92, by + 283, "5^6 = 15 625 станів", size=11, color=POS, bold=True))
    p.append(text(bx + 92, by + 302, "Тест-матриця неможлива", size=9, color=MUTED))

    p.append(rect(bx + 190, by + 245, 155, 75, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=6))
    p.append(text(bx + 267, by + 265, "8 змінних по 5 рівнів", size=10, color=INK, bold=True))
    p.append(text(bx + 267, by + 283, "5^8 = 390 625 станів", size=11, color=POS, bold=True))
    p.append(text(bx + 267, by + 302, "Повна сліпота логіки", size=9, color=MUTED))

    render(os.path.join(OUT, "combinatorial-explosion.svg"), W, H, *p,
           title="Комбінаторний вибух: зростання станів k^N унеможливлює повне ручне покриття")


# ── 2. rule-brittleness-traps: крихкість евристик і накладання збурень ────────
def fig_rule_brittleness_traps():
    W, H = 880, 420
    p = []

    # Лівий блок: 1D номінальне правило
    lx, ly, lw, lh = 40, 60, 380, 320
    p.append(rect(lx, ly, lw, lh, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(lx + lw/2, ly + 28, "Номінальний 1D-сценарій (на стенді)", size=13, color=FIELD, bold=True))

    # Схема руху на стенді
    p.append(line(lx + 40, ly + 120, lx + 340, ly + 120, color="#cbd5e1", sw=2, dash="4,4"))
    # Перешкода
    p.append(rect(lx + 240, ly + 80, 30, 80, fill="#fecaca", stroke=POS, sw=1.5, rx=4))
    p.append(text(lx + 255, ly + 125, "Стіна", size=9, color=POS, bold=True))
    # Траєкторія обходу
    p.append(f'<path d="M {lx+60} {ly+120} L {lx+180} {ly+120} Q {lx+220} {ly+60} {lx+290} {ly+60} L {lx+340} {ly+60}" fill="none" stroke="{FIELD}" stroke-width="2.5"/>')
    p.append(circle(lx + 60, ly + 120, 6, fill=FIELD, stroke="#ffffff", sw=2))
    p.append(text(lx + 60, ly + 142, "Старт", size=9, color=MUTED))

    p.append(rect(lx + 30, ly + 180, 320, 110, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=6))
    p.append(text(lx + 45, ly + 205, "Одне правило діє ізольовано:", size=10, color=INK, anchor="start", bold=True))
    p.append(text(lx + 45, ly + 225, "• Батарея 100% (немає обмеження тяги)", size=9, color=MUTED, anchor="start"))
    p.append(text(lx + 45, ly + 245, "• Вітер 0 м/с (немає бокового зносу)", size=9, color=MUTED, anchor="start"))
    p.append(text(lx + 45, ly + 265, "• Результат: маневр обходу успішний", size=10, color=FIELD, anchor="start", bold=True))

    # Правий блок: 3D катастрофа поєднання факторів
    rx_b, ry_b, rw, rh = 460, 60, 380, 320
    p.append(rect(rx_b, ry_b, rw, rh, fill="#fff1f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(rx_b + rw/2, ry_b + 28, "Реальне поле: накладання збурень", size=13, color=POS, bold=True))

    # Схема катастрофи
    p.append(line(rx_b + 40, ry_b + 120, rx_b + 340, ry_b + 120, color="#cbd5e1", sw=2, dash="4,4"))
    # Перешкода
    p.append(rect(rx_b + 240, ry_b + 80, 30, 80, fill="#fecaca", stroke=POS, sw=1.5, rx=4))
    p.append(text(rx_b + 255, ry_b + 125, "Стіна", size=9, color=POS, bold=True))

    # Вектори впливу
    p.append(arrow(rx_b + 180, ry_b + 55, rx_b + 180, ry_b + 95, color=NEG, sw=2))
    p.append(text(rx_b + 180, ry_b + 48, "Боковий вітер 12 м/с", size=9, color=NEG, bold=True))

    # Зрив траєкторії в перешкоду
    p.append(f'<path d="M {rx_b+60} {ly+120} L {rx_b+170} {ly+120} Q {rx_b+200} {ly+100} {rx_b+240} {ly+110}" fill="none" stroke="{POS}" stroke-width="2.5"/>')
    p.append(circle(rx_b + 240, ly + 110, 7, fill=POS, stroke="#ffffff", sw=2))
    p.append(text(rx_b + 240, ly + 135, "ЗІТКНЕННЯ", size=10, color=POS, bold=True))

    p.append(rect(rx_b + 30, ry_b + 180, 320, 110, fill="#ffffff", stroke="#fecaca", sw=1, rx=6))
    p.append(text(rx_b + 45, ry_b + 205, "Конфлікт 3 дискретних правил:", size=10, color=POS, anchor="start", bold=True))
    p.append(text(rx_b + 45, ry_b + 225, "1. Rule_Обхід: повернути вліво", size=9, color=INK, anchor="start"))
    p.append(text(rx_b + 45, ry_b + 245, "2. Rule_Економія: обмежити струм до 40%", size=9, color=INK, anchor="start"))
    p.append(text(rx_b + 45, ry_b + 265, "3. Вітер зносить апарат швидше за поворот", size=9, color=POS, anchor="start", bold=True))

    render(os.path.join(OUT, "rule-brittleness-traps.svg"), W, H, *p,
           title="Крихкість правил: ізольовані евристики катастрофічно ламаються при накладанні факторів")


# ── 3. local-minima-oscillation: пастка локального мінімуму та брязкіт ────────
def fig_local_minima_oscillation():
    W, H = 880, 420
    p = []

    # Ліва частина: U-подібна перешкода та застрягання (локальний мінімум)
    lx, ly, lw, lh = 40, 60, 380, 320
    p.append(rect(lx, ly, lw, lh, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(lx + lw/2, ly + 26, "Пастка локального мінімуму (U-кишеня)", size=12, color=INK, bold=True))

    # U-подібна перешкода
    p.append(rect(lx + 130, ly + 80, 20, 140, fill="#cbd5e1", stroke=LINE, sw=1.5, rx=3))
    p.append(rect(lx + 130, ly + 200, 140, 20, fill="#cbd5e1", stroke=LINE, sw=1.5, rx=3))
    p.append(rect(lx + 250, ly + 80, 20, 140, fill="#cbd5e1", stroke=LINE, sw=1.5, rx=3))
    p.append(text(lx + 200, ly + 235, "Увігнута перешкода", size=9, color=MUTED))

    # Ціль
    p.append(circle(lx + 200, ly + 60, 10, fill="#dcfce7", stroke=FIELD, sw=2))
    p.append(text(lx + 200, ly + 64, "★", size=10, color=FIELD))
    p.append(text(lx + 200, ly + 42, "Ціль", size=10, color=FIELD, bold=True))

    # Рух всередину кишені
    p.append(f'<path d="M {lx+200} {ly+290} L {lx+200} {ly+160}" fill="none" stroke="{POS}" stroke-width="2.2" stroke-dasharray="4,3"/>')
    p.append(circle(lx + 200, ly + 160, 8, fill=POS, stroke="#ffffff", sw=2))
    p.append(text(lx + 200, ly + 180, "Тупик: Fatt + Frep = 0", size=10, color=POS, bold=True))

    p.append(rect(lx + 20, ly + 250, 340, 55, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=6))
    p.append(text(lx + 30, ly + 270, "Реактивна евристика (Potential Field):", size=9, color=INK, anchor="start", bold=True))
    p.append(text(lx + 30, ly + 290, "Притягання до цілі врівноважується відштовхуванням стін", size=9, color=MUTED, anchor="start"))

    # Права частина: Брязкіт (Chattering / Limit Cycle)
    rx_b, ry_b, rw, rh = 460, 60, 380, 320
    p.append(rect(rx_b, ry_b, rw, rh, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(rx_b + rw/2, ry_b + 26, "Брязкіт (Chattering) між двома правилами", size=12, color=INK, bold=True))

    # Коридор
    p.append(rect(rx_b + 40, ry_b + 70, 300, 20, fill="#cbd5e1", stroke=LINE, sw=1, rx=2))
    p.append(rect(rx_b + 40, ry_b + 210, 300, 20, fill="#cbd5e1", stroke=LINE, sw=1, rx=2))
    p.append(text(rx_b + 190, ry_b + 60, "Ліва межа / геозона", size=9, color=MUTED))
    p.append(text(rx_b + 190, ry_b + 245, "Права перешкода", size=9, color=MUTED))

    # Зигзаг автоколивань
    p.append(f'<path d="M {rx_b+60} {ry_b+150} L {rx_b+110} {ry_b+100} L {rx_b+160} {ry_b+195} L {rx_b+210} {ry_b+100} L {rx_b+260} {ry_b+195} L {rx_b+310} {ry_b+150}" fill="none" stroke="{POS}" stroke-width="2.2"/>')

    p.append(text(rx_b + 110, ry_b + 90, "Rule: Вправо!", size=9, color=POS, bold=True))
    p.append(text(rx_b + 160, ry_b + 212, "Rule: Вліво!", size=9, color=POS, bold=True))

    p.append(rect(rx_b + 20, ry_b + 250, 340, 55, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=6))
    p.append(text(rx_b + 30, ry_b + 270, "Граничний цикл перемикання (20–50 Гц):", size=9, color=INK, anchor="start", bold=True))
    p.append(text(rx_b + 30, ry_b + 290, "Перегрів сервоприводів, струмовий удар, втрата курсу", size=9, color=POS, anchor="start"))

    render(os.path.join(OUT, "local-minima-oscillation.svg"), W, H, *p,
           title="Сліпота локальних евристик: пастка локального мінімуму та брязкіт перемикань")


# ── 4. hybrid-architecture: глобальний оптимізатор + бар'єр безпеки ───────────
def fig_hybrid_architecture():
    W, H = 900, 450
    p = []

    # Рівень 1: Місія / Глобальна ціль
    p.append(rect(60, 60, 200, 70, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=6))
    p.append(text(160, 88, "Глобальна місія", size=12, color=INK, bold=True))
    p.append(text(160, 108, "Вейпойнти, геозони (1–2 Гц)", size=9, color=MUTED))

    p.append(arrow(260, 95, 330, 95, color=LINE, sw=1.8))

    # Рівень 2: Оптимізаційний планувальник (Search / Trajectory Optimizer)
    p.append(rect(330, 50, 230, 90, fill="#e0f2fe", stroke=NEG, sw=2, rx=8))
    p.append(text(445, 78, "Оптимізаційний планувальник", size=12, color=NEG, bold=True))
    p.append(text(445, 98, "A* / DWA / Spline / MPC", size=10, color=INK))
    p.append(text(445, 118, "Мінімізує J(u, x) (10–50 Гц)", size=9, color=MUTED))

    # Кандидат уставки (стрілки до і після бейджа, щоб не було перетину з лінією)
    p.append(arrow(445, 140, 445, 155, color=NEG, sw=1.8))
    p.append(rect(370, 158, 150, 26, fill="#ffffff", stroke=NEG, sw=1, rx=4))
    p.append(text(445, 175, "Кандидат u_cand", size=10, color=NEG, bold=True))
    p.append(arrow(445, 185, 445, 200, color=NEG, sw=1.8))

    # Рівень 3: Детермінований фільтр безпеки / Бар'єр правил
    p.append(rect(270, 200, 350, 130, fill="#fef2f2", stroke=POS, sw=2.2, rx=8))
    p.append(text(445, 226, "ДЕТЕРМІНОВАНИЙ БАР'ЄР БЕЗПЕКИ", size=12, color=POS, bold=True))
    p.append(text(445, 245, "Жорсткі правила допуску / Interlocks (100–500 Гц)", size=10, color=INK))

    p.append(rect(290, 260, 145, 55, fill="#ffffff", stroke="#fca5a5", sw=1, rx=4))
    p.append(text(362, 280, "Кінематичні ліміти", size=9, color=INK, bold=True))
    p.append(text(362, 298, "a_max, v_stop(d_obs)", size=9, color=POS))

    p.append(rect(455, 260, 145, 55, fill="#ffffff", stroke="#fca5a5", sw=1, rx=4))
    p.append(text(527, 280, "Апаратні захисти", size=9, color=INK, bold=True))
    p.append(text(527, 298, "I_max, V_min, E-Stop", size=9, color=POS))

    # Валідована або обмежена команда (стрілки до і після бейджа)
    p.append(arrow(445, 330, 445, 342, color=FIELD, sw=1.8))
    p.append(rect(370, 345, 150, 26, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
    p.append(text(445, 362, "Безпечна уставка u_safe", size=10, color=FIELD, bold=True))
    p.append(arrow(445, 372, 445, 380, color=FIELD, sw=1.8))

    # Рівень 4: Виконавчий контур
    p.append(rect(330, 380, 230, 50, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(445, 402, "Контур стабілізації (ПІД)", size=11, color=FIELD, bold=True))
    p.append(text(445, 418, "Мотори / Сервоприводи (400–1000 Гц)", size=9, color=MUTED))

    # Бічна панель: швидкий Failsafe канал (якщо планувальник завис чи збій)
    p.append(rect(670, 150, 190, 180, fill="#fffbeb", stroke="#d97706", sw=1.5, rx=6))
    p.append(text(765, 175, "Прямий аварійний канал", size=11, color="#d97706", bold=True))
    p.append(text(765, 195, "Failsafe Override", size=10, color=INK, bold=True))
    p.append(mtext(765, 225, "Якщо планувальник\nзавис або тайм-аут →\nпряма зупинка/гальмо\nв обхід оптимізатора", size=9, color=MUTED, lh=1.3))

    p.append(f'<path d="M 670 240 L 620 240" fill="none" stroke="#d97706" stroke-width="1.8" marker-end="url(#arrow)"/>')

    render(os.path.join(OUT, "hybrid-architecture.svg"), W, H, *p,
           title="Гібридна архітектура: оптимізаційний планувальник під наглядом бар'єра правил безпеки")


if __name__ == "__main__":
    fig_combinatorial_explosion()
    fig_rule_brittleness_traps()
    fig_local_minima_oscillation()
    fig_hybrid_architecture()
    print("All 4 figures generated successfully in img/")
