# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. two-layer-architecture: Реактивний і планувальний шари ─────────────────
def fig_two_layer_architecture():
    W, H = 840, 480
    p = []

    # Лівий блок: Детектори та Давачі
    p.append(fitbox(20, 60, 160, 380, "ФІЗИЧНИЙ СВІТ\nТА ДАВАЧІ\n\n• Давачі наближення\n• Енкодери й IMU\n• Струмові шунти\n• Кінцеві вимикачі\n• Лідар / Камера", size=12, fill="#f8fafc", stroke=MUTED))

    # Верхній контур: Швидкий реактивний шар (Fast Path)
    p.append(rect(220, 50, 400, 160, fill="#fef2f2", stroke=POS, sw=2, rx=8))
    p.append(text(420, 75, "РЕАКТИВНИЙ ШАР (FAST PATH / РЕФЛЕКСИ)", size=13, color=POS, bold=True))
    p.append(text(420, 95, "Період циклу: T < 1 мс (жорсткий детермінізм)", size=11, color=POS, italic=True))

    p.append(fitbox(240, 110, 170, 80, "Контур безпеки\n• Зупинка зіткнень\n• Струмові відсічки\n• Локальні сили", size=11, fill="#ffffff", stroke=POS))
    p.append(fitbox(430, 110, 170, 80, "Рефлекторний вихід\n• Аварійне гальмо\n• Обхід перешкоди\n• Прямий стоп PWM", size=11, fill="#ffffff", stroke=POS))
    p.append(arrow(410, 150, 430, 150, color=POS))

    # Нижній контур: Повільний планувальний шар (Slow Path)
    p.append(rect(220, 270, 400, 170, fill="#eff6ff", stroke=NEG, sw=2, rx=8))
    p.append(text(420, 295, "ПЛАНУВАЛЬНИЙ ШАР (SLOW PATH / ДОРАДЧИЙ)", size=13, color=NEG, bold=True))
    p.append(text(420, 315, "Період циклу: T = 100–1000 мс (обчислювально важкий)", size=11, color=NEG, italic=True))

    p.append(fitbox(240, 330, 170, 90, "Модель і пошук\n• Глобальна карта\n• Граф A* / RRT*\n• Профіль швидкості", size=11, fill="#ffffff", stroke=NEG))
    p.append(fitbox(430, 330, 170, 90, "Цільова траєкторія\n• Масив точок q(t)\n• План дій місії\n• Тепловий баланс", size=11, fill="#ffffff", stroke=NEG))
    p.append(arrow(410, 375, 430, 375, color=NEG))

    # Правий блок: Арбітр та Актуатори
    p.append(rect(660, 120, 160, 240, fill="#f0fdf4", stroke=FIELD, sw=2, rx=8))
    p.append(text(740, 145, "АРБІТР СИГНАЛІВ", size=12, color=FIELD, bold=True))
    p.append(text(740, 165, "Subsumption Mux", size=11, color=MUTED))
    p.append(fitbox(675, 180, 130, 70, "Пріоритет:\n1. Рефлекс\n2. План", size=11, fill="#ffffff", stroke=FIELD))
    p.append(fitbox(675, 260, 130, 85, "АКТУАТОРИ\n• Мотори (PWM)\n• Сервоприводи\n• Силові ключі", size=11, fill="#ffffff", stroke=FIELD))

    # Зв'язки (стрілки)
    # Від давачів до реактивного шару
    p.append(arrow(180, 150, 240, 150, color=POS, sw=2))
    # Від давачів до планувального шару
    p.append(arrow(180, 375, 240, 375, color=NEG, sw=2))

    # Від реактивного до арбітра
    p.append(arrow(600, 150, 660, 185, color=POS, sw=2))
    p.append(text(625, 140, "Перехоплення", size=10, color=POS, bold=True))

    # Від планувальника до арбітра
    p.append(arrow(600, 375, 660, 215, color=NEG, sw=2))
    p.append(text(630, 390, "Уставка q(t)", size=10, color=NEG, bold=True))

    # Зворотний зв'язок: ресинхронізація (Re-anchoring)
    p.append(line(740, 360, 740, 460, color=MUTED, sw=1.5, dash="4 3"))
    p.append(line(740, 460, 325, 460, color=MUTED, sw=1.5, dash="4 3"))
    p.append(arrow(325, 460, 325, 440, color=MUTED, sw=1.5))
    p.append(text(530, 452, "Зворотний зв'язок реального стану (Re-anchoring для репланування)", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "two-layer-architecture.svg"), W, H, *p,
           title="Дворівнева архітектура: швидкий рефлекторний і повільний дорадчий шари")


# ── 2. brooks-subsumption: Архітектура придушення Брукса ──────────────────────
def fig_brooks_subsumption():
    W, H = 820, 430
    p = []

    layers = [
        ("Рівень 3: Побудова карти й довгостроковий план", "#eff6ff", NEG, 70),
        ("Рівень 2: Рух до глобальної цілі (Target Seek)", "#f5f3ff", "#7c3aed", 150),
        ("Рівень 1: Блукання та дослідження (Wander)",     "#fffbeb", "#d97706", 230),
        ("Рівень 0: Уникнення перешкод і захист (Avoid)",  "#fef2f2", POS, 310)
    ]

    # Стовпчик Давачі зліва, Актуатори справа
    p.append(fitbox(20, 80, 110, 300, "ДАВАЧІ\n\n• Сонар\n• Лідар\n• Бампер\n• Одометрія\n• Струм", size=11, fill="#f8fafc", stroke=MUTED))
    p.append(fitbox(690, 80, 110, 300, "АКТУАТОРИ\n\n• Лівий мотор\n• Правий мотор\n• Кермо\n• Гальмо", size=11, fill="#f8fafc", stroke=MUTED))

    for name, fill, col, y in layers:
        p.append(rect(170, y, 380, 56, fill=fill, stroke=col, sw=1.8, rx=6))
        p.append(text(360, y + 33, name, size=11, color=col, bold=True))
        # Стрілка від сенсорів
        p.append(arrow(130, y + 28, 170, y + 28, color=MUTED, sw=1.2))

    # Виходи шарів та вузли Subsumption (S) та Inhibition (I)
    # Рівень 0 йде напряму до актуаторів
    p.append(arrow(550, 338, 690, 338, color=POS, sw=2))

    # Рівень 1 придушується Рівнем 0
    p.append(line(550, 258, 600, 258, color="#d97706", sw=1.5))
    p.append(circle(600, 258, 12, fill="#ffffff", stroke=POS, sw=2))
    p.append(text(600, 262, "S", size=11, color=POS, bold=True))
    p.append(arrow(600, 270, 600, 338, color=POS, sw=1.5))
    p.append(arrow(612, 258, 690, 258, color="#d97706", sw=1.5))

    # Рівень 2 придушується Рівнем 1 або 0
    p.append(line(550, 178, 630, 178, color="#7c3aed", sw=1.5))
    p.append(circle(630, 178, 12, fill="#ffffff", stroke=POS, sw=2))
    p.append(text(630, 182, "S", size=11, color=POS, bold=True))
    p.append(arrow(630, 190, 630, 258, color=POS, sw=1.5))
    p.append(arrow(642, 178, 690, 178, color="#7c3aed", sw=1.5))

    # Рівень 3 гальмує вхід Рівня 2 (Inhibition node I)
    p.append(line(360, 126, 360, 140, color=NEG, sw=1.5))
    p.append(circle(360, 150, 11, fill="#ffffff", stroke=NEG, sw=2))
    p.append(text(360, 154, "I", size=10, color=NEG, bold=True))
    p.append(text(380, 145, "Inhibit (блокування входу)", size=10, color=NEG, anchor="start", italic=True))

    # Пояснення S і I внизу
    p.append(rect(140, 385, 540, 36, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    p.append(text(410, 408, "S (Subsume) — перехоплення виходу сигналом вищого пріоритету  |  I (Inhibit) — блокування входу", size=10, color=INK))

    render(os.path.join(OUT, "brooks-subsumption.svg"), W, H, *p,
           title="Архітектура придушення Брукса: вертикальні шари поведінки без монолітної моделі")


# ── 3. trajectory-blending: Злиття траєкторій та безударне перемикання ─────────
def fig_trajectory_blending():
    W, H = 820, 380
    p = []

    # Координатна сітка
    x0, y0 = 80, 300
    w_axis, h_axis = 680, 240
    p.append(line(x0, y0, x0 + w_axis, y0, color=LINE, sw=1.5))
    p.append(line(x0, y0, x0, y0 - h_axis, color=LINE, sw=1.5))
    p.append(text(x0 + w_axis, y0 + 20, "Час (t)", size=11, color=INK, anchor="end"))
    p.append(text(x0 - 15, y0 - h_axis + 10, "Положення / Швидкість", size=11, color=INK, anchor="end"))

    # Фази часу
    t_det = x0 + 170
    t_clr = x0 + 380
    t_end = x0 + 600

    # Вертикальні лінії подій
    p.append(line(t_det, y0, t_det, y0 - 220, color=POS, sw=1.2, dash="4 3"))
    p.append(text(t_det, y0 - 228, "t_alert (Перешкода)", size=10, color=POS, bold=True))

    p.append(line(t_clr, y0, t_clr, y0 - 220, color=FIELD, sw=1.2, dash="4 3"))
    p.append(text(t_clr, y0 - 228, "t_clear (Загрозу знято)", size=10, color=FIELD, bold=True))

    # Траєкторії:
    # 1. Початковий план (пунктир синій до кінця)
    pts_plan = [(x0, y0 - 20), (t_det, y0 - 80), (t_clr, y0 - 150), (t_end, y0 - 220)]
    for i in range(len(pts_plan) - 1):
        p.append(line(pts_plan[i][0], pts_plan[i][1], pts_plan[i+1][0], pts_plan[i+1][1], color=NEG, sw=2, dash="5 4"))
    p.append(text(t_end + 10, y0 - 220, "Старий план (відірваний від реальності)", size=10, color=NEG, anchor="start"))

    # 2. Реактивне відхилення (червона лінія від t_det до t_clr)
    p.append(line(x0, y0 - 20, t_det, y0 - 80, color=NEG, sw=2.5)) # рух за планом
    # Від t_det різкий маневр / гальмування
    p.append(line(t_det, y0 - 80, t_det + 100, y0 - 70, color=POS, sw=2.5))
    p.append(line(t_det + 100, y0 - 70, t_clr, y0 - 65, color=POS, sw=2.5))
    p.append(circle(t_det, y0 - 80, 4, fill=POS, stroke=POS))
    p.append(text(t_det + 90, y0 - 45, "Реактивний маневр ухилення (Fast Path)", size=10, color=POS, bold=True))

    # 3. Безударний перехід (Bumpless Blending, зелена лінія від t_clr з C^1/C^2 згладжуванням)
    p.append(circle(t_clr, y0 - 65, 5, fill=FIELD, stroke=FIELD))
    # Сплайн злиття повернення на ціль
    pts_blend = [(t_clr, y0 - 65), (t_clr + 80, y0 - 95), (t_clr + 160, y0 - 150), (t_end, y0 - 200)]
    for i in range(len(pts_blend) - 1):
        p.append(line(pts_blend[i][0], pts_blend[i][1], pts_blend[i+1][0], pts_blend[i+1][1], color=FIELD, sw=2.5))
    p.append(circle(t_end, y0 - 200, 4, fill=FIELD, stroke=FIELD))
    p.append(text(t_clr + 110, y0 - 165, "Згладжена траєкторія повернення (C^1/C^2)", size=10, color=FIELD, bold=True))

    # Пояснення ривка при розриві
    p.append(line(t_clr, y0 - 65, t_clr, y0 - 150, color=POS, sw=1.5, dash="2 2"))
    p.append(text(t_clr + 8, y0 - 110, "Δq (Удар/ривок без Re-anchoring!)", size=9, color=POS, anchor="start"))

    render(os.path.join(OUT, "trajectory-blending.svg"), W, H, *p,
           title="Злиття траєкторій (Bumpless Transfer): захист від механічного ривка при зміні шару")


if __name__ == "__main__":
    fig_two_layer_architecture()
    fig_brooks_subsumption()
    fig_trajectory_blending()
    print("All figures generated successfully.")
