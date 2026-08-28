# -*- coding: utf-8 -*-
import sys
import os
import math

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. shift-types.svg: Три типи зсуву розподілу даних ───────────────────────────
def fig_shift_types():
    W, H = 960, 480
    frags = []

    # Тло
    frags.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # Заголовок
    frags.append(text(W / 2, 28, "Класифікація зсувів розподілу у просторі ймовірностей P(X, Y)", size=16, bold=True, color=INK))

    # Спільна формула декомпозиції вхідного простору
    frags.append(text(W / 2, 54, "Спільний розподіл: P(X, Y) = P(X) · P(Y | X) = P(Y) · P(X | Y)", size=13, bold=False, color=MUTED))

    # Параметри 3 карток
    cw, ch = 285, 380
    card_y = 75
    xs = [25, 337, 650]

    # Картка 1: Covariate Shift
    c1_x = xs[0]
    frags.append(rect(c1_x, card_y, cw, ch, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(rect(c1_x, card_y, cw, 42, fill="#e2e8f0", stroke="#cbd5e1", sw=1.0, rx=8))
    frags.append(text(c1_x + cw / 2, card_y + 26, "1. Зсув коваріат (Covariate Shift)", size=13, bold=True, color=INK))

    frags.append(rect(c1_x + 15, card_y + 55, cw - 30, 68, fill="#ffffff", stroke="#94a3b8", sw=1.0, rx=6))
    frags.append(text(c1_x + cw / 2, card_y + 75, "P(X) змінюється", size=13, bold=True, color=POS))
    frags.append(text(c1_x + cw / 2, card_y + 95, "P(Y | X) залишається сталим", size=13, bold=True, color=FIELD))
    frags.append(text(c1_x + cw / 2, card_y + 112, "P_test(X) ≠ P_train(X)", size=11, color=MUTED))

    # Внутрішня схема-ілюстрація для Covariate Shift
    gx, gy, gw, gh = c1_x + 20, card_y + 135, cw - 40, 110
    frags.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=4))
    # Вісь X
    frags.append(line(gx + 15, gy + gh - 20, gx + gw - 15, gy + gh - 20, color=LINE, sw=1.2))
    # Розподіл Train (синій)
    frags.append('<path d="M %d %d Q %d %d %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="2.2"/>' %
                 (gx + 25, gy + gh - 20, gx + 60, gy + 15, gx + 95, gy + gh - 20, gx + 130, gy + gh - 20, gx + 160, gy + gh - 20, NEG))
    frags.append(text(gx + 60, gy + 32, "P_train(X)", size=11, bold=True, color=NEG))
    # Розподіл Test (червоний)
    frags.append('<path d="M %d %d Q %d %d %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="4,3"/>' %
                 (gx + 80, gy + gh - 20, gx + 115, gy + gh - 20, gx + 150, gy + gh - 20, gx + 185, gy + 15, gx + 220, gy + gh - 20, POS))
    frags.append(text(gx + 185, gy + 32, "P_test(X)", size=11, bold=True, color=POS))
    # Розділова межа (стала)
    frags.append(line(gx + 125, gy + 15, gx + 125, gy + gh - 10, color=FIELD, sw=1.8, dash="3,2"))
    frags.append(text(gx + 125, gy + gh - 6, "Межа Y|X", size=10, bold=True, color=FIELD))

    # Текстовий опис прикладів
    frags.append(text(c1_x + cw / 2, card_y + 265, "Фізичні причини в бортових системах:", size=11, bold=True, color=INK))
    frags.append(text(c1_x + 20, card_y + 288, "• Зміна сенсора, освітлення, оптики", size=11, color=INK, anchor="start"))
    frags.append(text(c1_x + 20, card_y + 308, "• Туман, дощ, засліплення сонцем", size=11, color=INK, anchor="start"))
    frags.append(text(c1_x + 20, card_y + 328, "• Перехід із шосе на бездоріжжя", size=11, color=INK, anchor="start"))
    frags.append(text(c1_x + 20, card_y + 352, "Наслідок: висока впевненість на OOD", size=11, bold=True, color=POS, anchor="start"))

    # Картка 2: Concept Shift
    c2_x = xs[1]
    frags.append(rect(c2_x, card_y, cw, ch, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(rect(c2_x, card_y, cw, 42, fill="#e2e8f0", stroke="#cbd5e1", sw=1.0, rx=8))
    frags.append(text(c2_x + cw / 2, card_y + 26, "2. Зсув концепту (Concept Shift)", size=13, bold=True, color=INK))

    frags.append(rect(c2_x + 15, card_y + 55, cw - 30, 68, fill="#ffffff", stroke="#94a3b8", sw=1.0, rx=6))
    frags.append(text(c2_x + cw / 2, card_y + 75, "P(Y | X) змінюється", size=13, bold=True, color=POS))
    frags.append(text(c2_x + cw / 2, card_y + 95, "P(X) може бути незмінним", size=13, bold=True, color=FIELD))
    frags.append(text(c2_x + cw / 2, card_y + 112, "P_test(Y|X) ≠ P_train(Y|X)", size=11, color=MUTED))

    # Внутрішня схема-ілюстрація для Concept Shift
    gx, gy, gw, gh = c2_x + 20, card_y + 135, cw - 40, 110
    frags.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=4))
    # Вісь X
    frags.append(line(gx + 15, gy + gh - 20, gx + gw - 15, gy + gh - 20, color=LINE, sw=1.2))
    # Розподіл X спільний
    frags.append('<path d="M %d %d Q %d %d %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="2.0"/>' %
                 (gx + 30, gy + gh - 20, gx + 120, gy + 15, gx + 215, gy + gh - 20, gx + 230, gy + gh - 20, gx + 235, gy + gh - 20, MUTED))
    frags.append(text(gx + 120, gy + 26, "P(X) незмінний", size=11, color=MUTED))
    # Початкова межа Train
    frags.append(line(gx + 90, gy + 20, gx + 90, gy + gh - 10, color=NEG, sw=2.0))
    frags.append(text(gx + 90, gy + gh - 6, "Межа Train", size=10, bold=True, color=NEG))
    # Зсунута межа Test
    frags.append(line(gx + 160, gy + 20, gx + 160, gy + gh - 10, color=POS, sw=2.0, dash="4,3"))
    frags.append(text(gx + 160, gy + gh - 6, "Межа Test", size=10, bold=True, color=POS))
    frags.append(arrow(gx + 95, gy + 45, gx + 155, gy + 45, color=POS, sw=1.8))

    # Текстовий опис прикладів
    frags.append(text(c2_x + cw / 2, card_y + 265, "Фізичні причини в бортових системах:", size=11, bold=True, color=INK))
    frags.append(text(c2_x + 20, card_y + 288, "• Поява ожеледиці: гальмівний шлях", size=11, color=INK, anchor="start"))
    frags.append(text(c2_x + 20, card_y + 308, "• Зміна правил руху чи розмітки", size=11, color=INK, anchor="start"))
    frags.append(text(c2_x + 20, card_y + 328, "• Камуфляж, мімікрія, знос шасі", size=11, color=INK, anchor="start"))
    frags.append(text(c2_x + 20, card_y + 352, "Наслідок: хибні прогнози безпеки", size=11, bold=True, color=POS, anchor="start"))

    # Картка 3: Label / Prior Shift
    c3_x = xs[2]
    frags.append(rect(c3_x, card_y, cw, ch, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(rect(c3_x, card_y, cw, 42, fill="#e2e8f0", stroke="#cbd5e1", sw=1.0, rx=8))
    frags.append(text(c3_x + cw / 2, card_y + 26, "3. Зсув апріорних значень (Label Shift)", size=13, bold=True, color=INK))

    frags.append(rect(c3_x + 15, card_y + 55, cw - 30, 68, fill="#ffffff", stroke="#94a3b8", sw=1.0, rx=6))
    frags.append(text(c3_x + cw / 2, card_y + 75, "P(Y) змінюється", size=13, bold=True, color=POS))
    frags.append(text(c3_x + cw / 2, card_y + 95, "P(X | Y) залишається сталим", size=13, bold=True, color=FIELD))
    frags.append(text(c3_x + cw / 2, card_y + 112, "P_test(Y) ≠ P_train(Y)", size=11, color=MUTED))

    # Внутрішня схема-ілюстрація для Label Shift
    gx, gy, gw, gh = c3_x + 20, card_y + 135, cw - 40, 110
    frags.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=4))
    # Стовпчики класів Y=0 та Y=1 для Train
    frags.append(text(gx + 60, gy + 18, "Навчання (Train)", size=10, bold=True, color=MUTED))
    frags.append(rect(gx + 30, gy + 30, 25, 60, fill=NEG, stroke=LINE, sw=1.0, rx=2))
    frags.append(rect(gx + 65, gy + 70, 25, 20, fill=POS, stroke=LINE, sw=1.0, rx=2))
    frags.append(text(gx + 42, gy + gh - 6, "90%", size=10, bold=True, color=INK))
    frags.append(text(gx + 77, gy + gh - 6, "10%", size=10, bold=True, color=INK))

    # Стовпчики класів Y=0 та Y=1 для Test (інверсія пропорцій)
    frags.append(text(gx + 175, gy + 18, "Експлуатація (Test)", size=10, bold=True, color=MUTED))
    frags.append(rect(gx + 145, gy + 65, 25, 25, fill=NEG, stroke=LINE, sw=1.0, rx=2))
    frags.append(rect(gx + 180, gy + 25, 25, 65, fill=POS, stroke=LINE, sw=1.0, rx=2))
    frags.append(text(gx + 157, gy + gh - 6, "20%", size=10, bold=True, color=INK))
    frags.append(text(gx + 192, gy + gh - 6, "80%", size=10, bold=True, color=INK))

    # Текстовий опис прикладів
    frags.append(text(c3_x + cw / 2, card_y + 265, "Фізичні причини в бортових системах:", size=11, bold=True, color=INK))
    frags.append(text(c3_x + 20, card_y + 288, "• Спалах дефектів на лінії виробництва", size=11, color=INK, anchor="start"))
    frags.append(text(c3_x + 20, card_y + 308, "• Вхід дрона в зону високої загрози", size=11, color=INK, anchor="start"))
    frags.append(text(c3_x + 20, card_y + 328, "• Зміна балансу норма/аномалія", size=11, color=INK, anchor="start"))
    frags.append(text(c3_x + 20, card_y + 352, "Наслідок: зсув байєсового порогу", size=11, bold=True, color=POS, anchor="start"))

    render(os.path.join(OUT, "shift-types.svg"), W, H, *frags)


# ── 2. shift-degradation.svg: Деградація моделі при зсуві та зона небезпеки ─────
def fig_shift_degradation():
    W, H = 860, 440
    frags = []

    frags.append(rect(0, 0, W, H, fill=BG, stroke="none"))
    frags.append(text(W / 2, 28, "Деградація метрик якості та впевненості при зростанні розбіжності розподілу", size=15, bold=True, color=INK))

    # Область графіків
    gx, gy = 90, 70
    gw, gh = 680, 290

    # Тло графіку
    frags.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=4))

    # Зонування безпеки (3 кольорові смуги)
    z1_w = gw * 0.32
    z2_w = gw * 0.33
    z3_w = gw * 0.35

    frags.append(rect(gx, gy, z1_w, gh, fill="#f0fdf4", stroke="none"))
    frags.append(rect(gx + z1_w, gy, z2_w, gh, fill="#fefce8", stroke="none"))
    frags.append(rect(gx + z1_w + z2_w, gy, z3_w, gh, fill="#fef2f2", stroke="none"))

    # Межі зон
    frags.append(line(gx + z1_w, gy, gx + z1_w, gy + gh, color="#22c55e", sw=1.5, dash="4,3"))
    frags.append(line(gx + z1_w + z2_w, gy, gx + z1_w + z2_w, gy + gh, color="#ef4444", sw=2.0, dash="5,3"))

    # Написи зон
    frags.append(text(gx + z1_w / 2, gy + 22, "1. Номінальна зона", size=12, bold=True, color="#15803d"))
    frags.append(text(gx + z1_w / 2, gy + 38, "ODD дотримано (W₁ < 0.15)", size=10, color=MUTED))

    frags.append(text(gx + z1_w + z2_w / 2, gy + 22, "2. Зона застереження", size=12, bold=True, color="#a16207"))
    frags.append(text(gx + z1_w + z2_w / 2, gy + 38, "Ріст ECE, легкий зсув", size=10, color=MUTED))

    frags.append(text(gx + z1_w + z2_w + z3_w / 2, gy + 22, "3. Критична деградація", size=12, bold=True, color="#b91c1c"))
    frags.append(text(gx + z1_w + z2_w + z3_w / 2, gy + 38, "Аварійне перемикання", size=10, color=MUTED))

    # Горизонтальні лінії сітки
    for frac in [0.25, 0.50, 0.75]:
        ly = gy + gh * (1.0 - frac)
        frags.append(line(gx, ly, gx + gw, ly, color="#e2e8f0", sw=1.0))
        frags.append(text(gx - 10, ly + 4, "%d%%" % int(frac * 100), size=11, color=MUTED, anchor="end"))

    frags.append(text(gx - 10, gy + gh + 4, "0%", size=11, color=MUTED, anchor="end"))
    frags.append(text(gx - 10, gy + 4, "100%", size=11, color=MUTED, anchor="end"))

    # Крива 1: Реальна точність (Accuracy) — стрімко падає вниз
    p_acc = [
        (gx, gy + gh * 0.04),
        (gx + z1_w * 0.5, gy + gh * 0.06),
        (gx + z1_w, gy + gh * 0.09),
        (gx + z1_w + z2_w * 0.5, gy + gh * 0.22),
        (gx + z1_w + z2_w, gy + gh * 0.38),
        (gx + z1_w + z2_w + z3_w * 0.5, gy + gh * 0.58),
        (gx + gw, gy + gh * 0.72)
    ]
    path_acc = "M " + " L ".join("%.1f %.1f" % pt for pt in p_acc)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.0"/>' % (path_acc, POS))

    # Крива 2: Сира вихідна впевненість Softmax — залишається оманливо високою
    p_conf = [
        (gx, gy + gh * 0.02),
        (gx + z1_w, gy + gh * 0.04),
        (gx + z1_w + z2_w, gy + gh * 0.09),
        (gx + gw, gy + gh * 0.18)
    ]
    path_conf = "M " + " L ".join("%.1f %.1f" % pt for pt in p_conf)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="6,4"/>' % (path_conf, NEG))

    # Крива 3: Відстань розбіжності Вассерштейна W1 (зростає)
    p_w1 = [
        (gx, gy + gh * 0.95),
        (gx + z1_w, gy + gh * 0.80),
        (gx + z1_w + z2_w, gy + gh * 0.50),
        (gx + gw, gy + gh * 0.12)
    ]
    path_w1 = "M " + " L ".join("%.1f %.1f" % pt for pt in p_w1)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_w1, FIELD))

    # Розрив надмірної впевненості (Overconfidence Gap)
    gap_x = gx + z1_w + z2_w + z3_w * 0.4
    gap_y1 = gy + gh * 0.15
    gap_y2 = gy + gh * 0.54
    frags.append(line(gap_x, gap_y1, gap_x, gap_y2, color=POS, sw=1.5, dash="2,2"))
    frags.append(arrow(gap_x, gap_y1 + 20, gap_x, gap_y1, color=POS, sw=1.5))
    frags.append(arrow(gap_x, gap_y2 - 20, gap_x, gap_y2, color=POS, sw=1.5))
    frags.append(text(gap_x + 10, (gap_y1 + gap_y2) / 2, "Прихована помилка", size=11, bold=True, color=POS, anchor="start"))
    frags.append(text(gap_x + 10, (gap_y1 + gap_y2) / 2 + 14, "(Overconfidence gap)", size=10, color=POS, anchor="start"))

    # Позначення по осі X
    frags.append(text(gx, gy + gh + 22, "0.0 (Збіг)", size=11, color=INK, anchor="middle"))
    frags.append(text(gx + z1_w, gy + gh + 22, "Поріг W₁ = 0.15", size=11, bold=True, color="#15803d", anchor="middle"))
    frags.append(text(gx + z1_w + z2_w, gy + gh + 22, "Критичний W₁ = 0.40", size=11, bold=True, color="#b91c1c", anchor="middle"))
    frags.append(text(gx + gw, gy + gh + 22, "1.0 (OOD)", size=11, color=INK, anchor="middle"))
    frags.append(text(gx + gw / 2, gy + gh + 42, "Ступінь розбіжності розподілу даних: W₁(P_train, P_stream) або MMD", size=12, bold=True, color=INK))

    # Легенда внизу
    leg_y = H - 20
    # Елемент 1
    frags.append(line(gx + 30, leg_y, gx + 65, leg_y, color=POS, sw=3.0))
    frags.append(text(gx + 75, leg_y + 4, "Реальна точність (Accuracy)", size=11, bold=True, color=INK, anchor="start"))
    # Елемент 2
    frags.append(line(gx + 260, leg_y, gx + 295, leg_y, color=NEG, sw=2.5, dash="6,4"))
    frags.append(text(gx + 305, leg_y + 4, "Оцінка Softmax (Conf)", size=11, bold=True, color=INK, anchor="start"))
    # Елемент 3
    frags.append(line(gx + 480, leg_y, gx + 515, leg_y, color=FIELD, sw=2.5))
    frags.append(text(gx + 525, leg_y + 4, "Метрика зсуву (W₁ / MMD)", size=11, bold=True, color=INK, anchor="start"))

    render(os.path.join(OUT, "shift-degradation.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_shift_types()
    fig_shift_degradation()
    print("Figures generated successfully in %s" % OUT)
