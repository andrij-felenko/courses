# -*- coding: utf-8 -*-
"""figs.py — генератор ілюстрацій для теми «Failsafe за динамікою».
Використовує svgkit зі scripts/ (4 рівні вгору від теки теми).
Вивід у ./img/
"""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), "img"), exist_ok=True)


# ── Фігура 1: Чотири фази динамічного відновлення ────────────────────────────
def fig_recovery_phases():
    W, H = 960, 480
    P = []

    # Заголовок
    P.append(text(W / 2, 32, "Чотири фази динамічного відновлення керованості апарата",
                  size=17, bold=True))

    # 4 колонки
    cols = [135, 365, 595, 825]
    card_w = 205
    card_h = 320
    top_y = 75

    phases = [
        {
            "num": "Фаза 1",
            "title": "Гасіння кутових\nшвидкостей та крену",
            "color": POS,
            "fill": "#fdf2f0",
            "goal": "Пріоритет: крен і обертання",
            "details": [
                "• Демпфування p, q, r",
                "• Виведення крену |φ| < 15°",
                "• Зняття авторотації",
                "• Запобігання затягуванню",
                "  у спіральне пікірування"
            ],
            "status": "Крен нейтралізовано"
        },
        {
            "num": "Фаза 2",
            "title": "Вивід з пікірування\nз обмеженням G",
            "color": "#c0560b",
            "fill": "#fdeede",
            "goal": "Пріоритет: вектор підйому",
            "details": [
                "• Вибірка тангажу θ ↑",
                "• Лімітер nz ≤ nz_max (2.5g)",
                "• Дросель у нуль при V > Vmax",
                "• Контроль втрати висоти",
                "• Захист від руйнування крила"
            ],
            "status": "Пікірування подолано"
        },
        {
            "num": "Фаза 3",
            "title": "Стабілізація швидкості\nй набір висоти",
            "color": "#b08900",
            "fill": "#fdf8ea",
            "goal": "Пріоритет: запас енергії",
            "details": [
                "• Відновлення тяги двигуна",
                "• Захист від звалювання",
                "• Контроль Vias > 1.3 Vstall",
                "• Пологий набір (γ = 5°..10°)",
                "• Вихід на безпечний ешелон"
            ],
            "status": "Енергію відновлено"
        },
        {
            "num": "Фаза 4",
            "title": "Передача керування\nв навігацію (RTL)",
            "color": FIELD,
            "fill": "#eaf7ee",
            "goal": "Пріоритет: маршрут повернення",
            "details": [
                "• Горизонтальний політ",
                "• Похибки |Δφ|, |Δθ| < 3°",
                "• Висота H ≥ Hsafe",
                "• Вмикання автопілота",
                "• Повернення на точку старту"
            ],
            "status": "Автономна місія"
        }
    ]

    for i, ph in enumerate(phases):
        cx = cols[i]

        # Фон картки
        P.append(rect(cx - card_w / 2, top_y, card_w, card_h, fill=ph["fill"], stroke=ph["color"], sw=1.8, rx=8))

        # Номер і назва фази
        P.append(text(cx, top_y + 24, ph["num"], size=13, bold=True, color=ph["color"]))
        P.append(mtext(cx, top_y + 48, ph["title"], size=13, bold=True, color=INK, lh=1.2))

        P.append(line(cx - card_w / 2 + 12, top_y + 88, cx + card_w / 2 - 12, top_y + 88, color=ph["color"], sw=1.0))

        # Ціль
        P.append(text(cx, top_y + 108, ph["goal"], size=11, bold=True, color=ph["color"]))

        # Список кроків
        for j, item in enumerate(ph["details"]):
            P.append(text(cx - card_w / 2 + 14, top_y + 134 + j * 22, item, size=11, color=INK, anchor="start"))

        # Статус на виході
        fr, _, _ = textbox(cx, top_y + card_h - 26, ph["status"], size=11, bold=True, color=ph["color"], fill="#ffffff", stroke=ph["color"], pad=6, min_w=175)
        P.append(fr)

        # Стрілка переходу між фазами
        if i < 3:
            arrow_x1 = cx + card_w / 2 + 3
            arrow_x2 = cols[i + 1] - card_w / 2 - 3
            arrow_y = top_y + card_h / 2
            P.append(arrow(arrow_x1, arrow_y, arrow_x2, arrow_y, color=MUTED, sw=2.0))

    # Нижній висновок
    P.append(rect(50, 420, W - 100, 42, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    P.append(text(W / 2, 445, "Ключовий принцип: спочатку вирівнювання крил (крен), потім вивід з пікірування (перевантаження), і лише наприкінці — навігація", size=12, bold=True, color=INK))

    render(os.path.join(os.path.dirname(__file__), "img", "recovery-phases.svg"), W, H, *P)


# ── Фігура 2: Діаграма V-n (Flight Envelope) та траєкторії ──────────────────
def fig_dynamic_envelope():
    W, H = 1000, 560
    P = []

    # Заголовок
    P.append(text(W / 2, 28, "Польотний конверт (V-n діаграма) та траєкторії виходу з аварійного стану", size=17, bold=True))

    # Координатна сітка
    ox = 150
    oy = 370
    w_ax = 780
    h_ax = 300

    # Осі
    P.append(arrow(ox, oy + 70, ox, oy - h_ax, color=INK, sw=1.8))
    P.append(arrow(ox, oy, ox + w_ax, oy, color=INK, sw=1.8))

    P.append(text(ox - 35, oy - h_ax + 10, "nz (G)", size=13, bold=True, color=INK))
    P.append(text(ox + w_ax - 10, oy + 36, "Повітряна швидкість V (м/с) →", size=12, bold=True, color=INK, anchor="end"))

    # Позначки осі Y (G)
    g_marks = [
        (-1.5, oy + 54, "-1.5g"),
        (0.0, oy, "0g"),
        (1.0, oy - 38, "1.0g (горизонт)"),
        (2.5, oy - 95, "2.5g (ліміт виводу)"),
        (3.8, oy - 144, "3.8g (руйнування)")
    ]
    for g_val, y_pos, label in g_marks:
        P.append(line(ox - 6, y_pos, ox, y_pos, color=INK, sw=1.2))
        P.append(line(ox, y_pos, ox + w_ax - 60, y_pos, color="#e5e7eb", sw=1.0, dash="3 3"))
        P.append(text(ox - 12, y_pos + 4, label, size=11, color=INK, anchor="end"))

    # Позначки осі X (Швидкість)
    v_marks = [
        (14, ox + 120, "14 (Vstall)"),
        (22, ox + 250, "22 (Vcruise)"),
        (36, ox + 430, "36 (Vdive)"),
        (50, ox + 620, "50 (Vne — ліміт)")
    ]
    for v_val, x_pos, label in v_marks:
        P.append(line(x_pos, oy - 5, x_pos, oy + 5, color=INK, sw=1.2))
        P.append(line(x_pos, oy - h_ax + 30, x_pos, oy + 54, color="#e5e7eb", sw=1.0, dash="3 3"))
        P.append(text(x_pos, oy + 24, label, size=11, color=INK))

    # Зона безпечного польотного конверта (заливка)
    # Межі: X від 14 до 50 м/с (x: ox+120 .. ox+620, w=500), Y від -1.5g до +3.8g (y: oy-144 .. oy+54, h=198)
    P.append(rect(ox + 120, oy - 144, 500, 198, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=0))
    P.append(text(ox + 350, oy - 120, "ДОПУСТИМИЙ ПОЛЬОТНИЙ КОНВЕРТ (SAFE ENVELOPE)", size=12, bold=True, color=FIELD))

    # Зона звалювання зліва
    P.append(rect(ox + 10, oy - 144, 110, 198, fill="#fef2f2", stroke="#fca5a5", sw=1.2, rx=0))
    P.append(text(ox + 65, oy - 50, "Звалювання\n(V < Vstall)", size=11, bold=True, color=POS))

    # Зона руйнування зверху
    P.append(rect(ox + 120, oy - h_ax + 15, 500, h_ax - 159, fill="#fff1f2", stroke="#fda4af", sw=1.2, rx=0))
    P.append(text(ox + 320, oy - 200, "НЕБЕЗПЕКА: Механічне руйнування крила (nz > 3.8g)", size=11, bold=True, color=POS))

    # Траєкторія 1: Статичний failsafe (руйнівна)
    # V=36, n=1.0 (ox+430, oy-38) -> різкий ривок керма висоти -> точка (ox+470, oy-180)
    p1 = f"M {ox + 430} {oy - 38} Q {ox + 455} {oy - 170} {ox + 470} {oy - 195}"
    P.append(f'<path d="{p1}" fill="none" stroke="{POS}" stroke-width="2.6" stroke-dasharray="6 4" marker-end="url(#arrow)"/>')

    # Виноска для статичного failsafe (розміщена праворуч у вільній зоні)
    fr_bad, _, _ = textbox(ox + 690, oy - 200, "Статичний failsafe:\nмиттєвий ривок керма →\nруйнування крила (nz > 4g)", size=10.5, bold=True, color=POS, fill="#ffffff", stroke=POS, pad=6)
    P.append(fr_bad)

    # Траєкторія 2: Динамічно-адаптивний failsafe (безпечна)
    # Початок: V=36, n=1.0 (ox+430, oy-38) -> зняття крену -> вивід 2.3g (ox+340, oy-88) -> вихід у Vcruise (ox+250, oy-38)
    p2 = f"M {ox + 430} {oy - 38} C {ox + 395} {oy - 88}, {ox + 330} {oy - 90}, {ox + 250} {oy - 38}"
    P.append(f'<path d="{p2}" fill="none" stroke="{FIELD}" stroke-width="3.0" marker-end="url(#arrow)"/>')

    # Точки етапів на траєкторії 2
    P.append(circle(ox + 430, oy - 38, 4.5, fill=POS, stroke=INK, sw=1.5))
    P.append(circle(ox + 340, oy - 88, 4.5, fill="#c0560b", stroke=INK, sw=1.5))
    P.append(circle(ox + 250, oy - 38, 4.5, fill=FIELD, stroke=INK, sw=1.5))

    # Пояснення до динамічної траєкторії (розміщене всередині зеленого конверта)
    fr_good, _, _ = textbox(ox + 335, oy - 25, "Динамічний failsafe:\n1. Зняття крену (|φ| < 15°)\n2. Вивід з лімітом nz ≤ 2.5g\n3. Повернення у Vcruise (1.0g)", size=10.5, bold=True, color=FIELD, fill="#ffffff", stroke=FIELD, pad=6)
    P.append(fr_good)

    # Примітки знизу
    P.append(rect(50, oy + 105, W - 100, 48, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    P.append(text(W / 2, oy + 126, "Адаптивний регулятор утримує рух апарата всередині польотного конверта, балансуючи між", size=11.5, bold=False, color=INK))
    P.append(text(W / 2, oy + 143, "мінімальною швидкістю звалювання Vstall та граничним перевантаженням конструкції nz_max.", size=11.5, bold=True, color=INK))

    render(os.path.join(os.path.dirname(__file__), "img", "dynamic-envelope.svg"), W, H, *P)


if __name__ == "__main__":
    fig_recovery_phases()
    fig_dynamic_envelope()
    print("Згенеровано recovery-phases.svg та dynamic-envelope.svg")
