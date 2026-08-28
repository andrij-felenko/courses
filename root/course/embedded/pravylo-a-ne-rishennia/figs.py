# -*- coding: utf-8 -*-
"""Фігури для статті pravylo-a-ne-rishennia («Правило, а не рішення»).
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. rule-vs-optimizer: Детерміноване правило проти автономного оптимізатора ─
def fig_rule_vs_optimizer():
    W, H = 840, 410
    p = []

    # Лівий блок: Автоматизація
    p.append(rect(20, 20, 385, 370, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    p.append(rect(20, 20, 385, 44, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=6))
    p.append(text(212, 48, "АВТОМАТИЗАЦІЯ (ПРАВИЛО)", size=14, color=INK, bold=True))

    p.append(rect(40, 85, 140, 48, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(110, 114, "Вхідний вектор X", size=12, color=INK, bold=True))

    p.append(arrow(180, 109, 230, 109, color=LINE, sw=1.5))

    p.append(rect(230, 85, 155, 48, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(307, 106, "f(x) -> y", size=13, color=FIELD, bold=True))
    p.append(text(307, 124, "(FSM / Таблиця)", size=11, color=FIELD))

    p.append(arrow(307, 133, 307, 175, color=LINE, sw=1.5))

    p.append(rect(40, 175, 345, 195, fill="#ffffff", stroke=MUTED, sw=1.0, rx=4))
    p.append(text(212, 210, "• 100% статична верифікація", size=12, color=INK, anchor="middle"))
    p.append(text(212, 245, "• Фіксований час WCET <= T_max", size=12, color=INK, anchor="middle"))
    p.append(text(212, 280, "• Рішення ухвалене інженером наперед", size=12, color=INK, anchor="middle"))
    p.append(text(212, 315, "• Відсутність прихованого стану", size=12, color=INK, anchor="middle"))
    p.append(text(212, 350, "• Детермінований граф переходів", size=12, color=INK, anchor="middle"))

    # Правий блок: Автономія
    p.append(rect(435, 20, 385, 370, fill="#fdfbf7", stroke=LINE, sw=1.5, rx=6))
    p.append(rect(435, 20, 385, 44, fill="#fef3c7", stroke=LINE, sw=1.5, rx=6))
    p.append(text(627, 48, "АВТОНОМІЯ (ОПТИМІЗАЦІЯ)", size=14, color=INK, bold=True))

    p.append(rect(455, 85, 140, 48, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(525, 114, "Неповні дані X", size=12, color=INK, bold=True))

    p.append(arrow(595, 109, 645, 109, color=LINE, sw=1.5))

    p.append(rect(645, 85, 155, 48, fill="#fdf2f2", stroke=POS, sw=1.5, rx=4))
    p.append(text(722, 106, "min J(u)", size=13, color=POS, bold=True))
    p.append(text(722, 124, "(Пошук плану)", size=11, color=POS))

    p.append(arrow(722, 133, 722, 175, color=LINE, sw=1.5))

    p.append(rect(455, 175, 345, 195, fill="#ffffff", stroke=MUTED, sw=1.0, rx=4))
    p.append(text(627, 210, "• Генерація власних субцілей", size=12, color=INK, anchor="middle"))
    p.append(text(627, 245, "• Варіативний час пошуку (евристика)", size=12, color=INK, anchor="middle"))
    p.append(text(627, 280, "• Ризик локальних мінімумів", size=12, color=INK, anchor="middle"))
    p.append(text(627, 315, "• Чутливість до шуму середовища", size=12, color=INK, anchor="middle"))
    p.append(text(627, 350, "• Стохастичний простір станів", size=12, color=INK, anchor="middle"))

    render(os.path.join(OUT, "rule-vs-optimizer.svg"), W, H, *p)


# ── 2. safety-cage: Архітектурний бар'єр безпеки (Safety Cage) ─────────────────
def fig_safety_cage():
    W, H = 820, 360
    p = []

    # Рівень автономії
    p.append(rect(30, 40, 230, 280, fill="#fef9f2", stroke="#e67e22", sw=1.5, rx=6))
    p.append(text(145, 70, "АВТОНОМНИЙ РІВЕНЬ", size=13, color="#d35400", bold=True))
    p.append(text(145, 92, "(High-level Planner / AI)", size=11, color=MUTED, italic=True))

    p.append(rect(45, 125, 200, 50, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
    p.append(text(145, 155, "Генерація траєкторії", size=12, color=INK))

    p.append(rect(45, 195, 200, 50, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
    p.append(text(145, 225, "Оптимізація цілей", size=12, color=INK))

    p.append(arrow(260, 180, 320, 180, color="#d35400", sw=2.0))
    p.append(text(290, 168, "u_req", size=12, color="#d35400", bold=True))

    # Safety Cage
    p.append(rect(320, 40, 240, 280, fill="#f4faf6", stroke=FIELD, sw=2.0, rx=6))
    p.append(text(440, 70, "SAFETY CAGE", size=14, color=FIELD, bold=True))
    p.append(text(440, 92, "(Детермінований рушій)", size=11, color=MUTED, italic=True))

    p.append(rect(335, 115, 210, 42, fill="#ffffff", stroke=FIELD, sw=1.0, rx=4))
    p.append(text(440, 140, "Перевірка меж (Envelope)", size=11, color=INK))

    p.append(rect(335, 168, 210, 42, fill="#ffffff", stroke=FIELD, sw=1.0, rx=4))
    p.append(text(440, 193, "Блокування (Interlocks)", size=11, color=INK))

    p.append(rect(335, 220, 210, 42, fill="#ffffff", stroke=FIELD, sw=1.0, rx=4))
    p.append(text(440, 245, "Failsafe & Watchdog", size=11, color=INK))

    p.append(arrow(560, 180, 620, 180, color=FIELD, sw=2.0))
    p.append(text(590, 168, "u_safe", size=12, color=FIELD, bold=True))

    # Актуатори
    p.append(rect(620, 40, 170, 280, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    p.append(text(705, 70, "АКТУАТОРИ", size=13, color=INK, bold=True))
    p.append(text(705, 92, "(Hard Real-Time)", size=11, color=MUTED, italic=True))

    p.append(rect(635, 125, 140, 50, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
    p.append(text(705, 155, "Мотори / Ключі", size=12, color=INK))

    p.append(rect(635, 195, 140, 50, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
    p.append(text(705, 225, "Клапани / Реле", size=12, color=INK))

    render(os.path.join(OUT, "safety-cage.svg"), W, H, *p)


# ── 3. autonomy-spectrum: Спектр рівнів від ручного до повної автономії ────────
def fig_autonomy_spectrum():
    W, H = 860, 410
    p = []

    # Головна вісь шкали
    p.append(arrow(40, 75, 820, 75, color=LINE, sw=2.0))
    p.append(text(820, 55, "Рівень автономії", size=12, color=INK, italic=True, anchor="end"))

    levels = [
        ("L0", "Ручне", 80, "#64748b", "Прямий міст", "Людина діє прямо"),
        ("L1", "Асистент", 215, "#0284c7", "Окремий контур", "PID стабілізація"),
        ("L2", "Часткова", 350, "#16a34a", "Таблиця правил", "FSM утримання"),
        ("L3", "Умовна", 500, "#d97706", "Межі ODD", "Оператор напоготові"),
        ("L4", "Висока", 640, "#ea580c", "Автономія ODD", "Safe State при збої"),
        ("L5", "Повна", 775, "#dc2626", "Без обмежень", "Повна самостійність")
    ]

    # Вертикальний вододіл: між L2 та L3
    p.append(line(425, 25, 425, 385, color=POS, sw=1.8, dash="6 4"))
    p.append(text(415, 40, "МЕЖА: Жорсткі правила", size=11, color=FIELD, bold=True, anchor="end"))
    p.append(text(435, 40, "Оптимізація й ODD", size=11, color=POS, bold=True, anchor="start"))

    for code, name, x, col, d1, d2 in levels:
        p.append(circle(x, 75, 7, fill=col, stroke=LINE, sw=1.5))
        p.append(text(x, 105, code, size=14, color=col, bold=True))
        p.append(text(x, 125, name, size=11, color=INK, bold=True))

        p.append(rect(x - 58, 145, 116, 220, fill="#f8fafc", stroke=MUTED, sw=1.0, rx=4))
        p.append(text(x, 185, d1, size=10, color=INK, bold=True))
        p.append(text(x, 220, d2, size=10, color=MUTED))

    render(os.path.join(OUT, "autonomy-spectrum.svg"), W, H, *p)


if __name__ == "__main__":
    fig_rule_vs_optimizer()
    fig_safety_cage()
    fig_autonomy_spectrum()
    print("All figures generated successfully.")
