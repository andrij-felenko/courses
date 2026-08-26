# -*- coding: utf-8 -*-
"""Фігури теми «Два давачі, які не згодні». Запуск: python figs.py → ./img/*.svg
Імпортуємо svgkit зі scripts/ (не переписуємо)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Порівняння архітектур надлишковості (1oo1, 1oo2, 2oo3) ─────────
def fig_redundancy_architectures():
    W, H = 840, 480
    parts = []

    # Заголовок та три колонки архітектур
    col_w = 250
    gap = 20
    x0 = 35

    # ── Блок 1: 1oo1 (Одиночний канал)
    c1_x = x0 + col_w / 2
    b_card1 = rect(x0, 20, col_w, 440, fill="#ffffff", stroke=LINE, sw=1.2, rx=8)
    parts.append(b_card1)
    parts.append(text(c1_x, 46, "1oo1 (Одиночний канал)", size=14, color=INK, bold=True))
    parts.append(text(c1_x, 66, "Немає захисту від збоїв", size=11, color=MUTED, italic=True))

    # Схема 1oo1
    tb_s1, _, _ = textbox(c1_x, 120, ["Давач A", "12.4 bar"], size=12, pad=8, fill="#f8fafc", stroke=LINE, min_w=140)
    parts.append(tb_s1)
    parts.append(arrow(c1_x, 145, c1_x, 195, color=LINE, sw=1.5))
    
    tb_proc1, _, _ = textbox(c1_x, 225, ["Контролер", "прямий вимір"], size=12, pad=8, fill="#f8fafc", stroke=LINE, min_w=140)
    parts.append(tb_proc1)
    parts.append(arrow(c1_x, 255, c1_x, 305, color=LINE, sw=1.5))

    tb_out1, _, _ = textbox(c1_x, 335, ["Керування клапаном", "сліпа довіра"], size=12, pad=8, fill="#fff1f2", stroke=POS, min_w=150)
    parts.append(tb_out1)

    parts.append(line(x0 + 15, 380, x0 + col_w - 15, 380, color=MUTED, sw=1, dash="3 3"))
    parts.append(text(c1_x, 404, "Відмова давача непомітна:", size=11, color=POS, bold=True))
    parts.append(text(c1_x, 424, "тихий дрейф веде до аварії", size=11, color=INK))
    parts.append(text(c1_x, 444, "Безпека: 0 / Доступність: 1", size=10, color=MUTED))

    # ── Блок 2: 1oo2 / 2oo2 (Дублювання — два давачі)
    x1 = x0 + col_w + gap
    c2_x = x1 + col_w / 2
    b_card2 = rect(x1, 20, col_w, 440, fill="#ffffff", stroke=LINE, sw=1.2, rx=8)
    parts.append(b_card2)
    parts.append(text(c2_x, 46, "1oo2 (Дублювання каналів)", size=14, color=INK, bold=True))
    parts.append(text(c2_x, 66, "Виявлення розбіжності без вибору", size=11, color=MUTED, italic=True))

    # Два давачі
    tb_s2a, _, _ = textbox(c2_x - 55, 115, ["Давач A", "12.4 bar"], size=11, pad=6, fill="#f8fafc", stroke=LINE, min_w=95)
    tb_s2b, _, _ = textbox(c2_x + 55, 115, ["Давач B", "14.8 bar"], size=11, pad=6, fill="#fff1f2", stroke=POS, min_w=95)
    parts.append(tb_s2a)
    parts.append(tb_s2b)

    parts.append(arrow(c2_x - 55, 140, c2_x - 20, 195, color=LINE, sw=1.5))
    parts.append(arrow(c2_x + 55, 140, c2_x + 20, 195, color=POS, sw=1.5))

    tb_comp, _, _ = textbox(c2_x, 225, ["Компаратор |A - B|", "Δ = 2.4 bar > 0.5 bar!", "Хто бреше? (Паритет)"], size=11, pad=8, fill="#fef3c7", stroke="#d97706", min_w=170)
    parts.append(tb_comp)

    parts.append(arrow(c2_x, 262, c2_x, 305, color=POS, sw=1.5))

    tb_out2, _, _ = textbox(c2_x, 335, ["Failsafe / Зупинка", "або песимістичний вибір"], size=11, pad=8, fill="#fee2e2", stroke=POS, min_w=165)
    parts.append(tb_out2)

    parts.append(line(x1 + 15, 380, x1 + col_w - 15, 380, color=MUTED, sw=1, dash="3 3"))
    parts.append(text(c2_x, 404, "Розбіжність виявлено миттєво,", size=11, color=LINE, bold=True))
    parts.append(text(c2_x, 424, "але робота переривається", size=11, color=INK))
    parts.append(text(c2_x, 444, "Безпека: ВИСОКА / Доступність: НИЗЬКА", size=10, color=MUTED))

    # ── Блок 3: 2oo3 / TMR (Потрійне мажоритарне голосування)
    x2 = x1 + col_w + gap
    c3_x = x2 + col_w / 2
    b_card3 = rect(x2, 20, col_w, 440, fill="#ffffff", stroke=LINE, sw=1.2, rx=8)
    parts.append(b_card3)
    parts.append(text(c3_x, 46, "2oo3 / TMR (Потрійне голосування)", size=14, color=INK, bold=True))
    parts.append(text(c3_x, 66, "Ізоляція несправного каналу", size=11, color=MUTED, italic=True))

    # Три давачі
    tb_s3a, _, _ = textbox(c3_x - 75, 115, ["Давач A", "12.4 bar"], size=10, pad=5, fill="#f8fafc", stroke=LINE, min_w=70)
    tb_s3b, _, _ = textbox(c3_x, 115, ["Давач B", "12.5 bar"], size=10, pad=5, fill="#f8fafc", stroke=LINE, min_w=70)
    tb_s3c, _, _ = textbox(c3_x + 75, 115, ["Давач C", "14.8 bar (збій)"], size=10, pad=5, fill="#fff1f2", stroke=POS, min_w=70)
    parts.append(tb_s3a)
    parts.append(tb_s3b)
    parts.append(tb_s3c)

    parts.append(arrow(c3_x - 75, 138, c3_x - 30, 195, color=FIELD, sw=1.5))
    parts.append(arrow(c3_x, 138, c3_x, 195, color=FIELD, sw=1.5))
    parts.append(arrow(c3_x + 75, 138, c3_x + 30, 195, color=POS, sw=1.5))

    tb_vote, _, _ = textbox(c3_x, 225, ["Мажоритарний воутер", "Кворум {A, B} узгоджено", "C відкинуто як викид"], size=11, pad=8, fill="#f0fdf4", stroke=FIELD, min_w=170)
    parts.append(tb_vote)

    parts.append(arrow(c3_x, 262, c3_x, 305, color=FIELD, sw=1.5))

    tb_out3, _, _ = textbox(c3_x, 335, ["Безперервна робота", "Консенсус = 12.45 bar"], size=11, pad=8, fill="#ecfdf5", stroke=FIELD, min_w=165)
    parts.append(tb_out3)

    parts.append(line(x2 + 15, 380, x2 + col_w - 15, 380, color=MUTED, sw=1, dash="3 3"))
    parts.append(text(c3_x, 404, "Відмову C локалізовано,", size=11, color=FIELD, bold=True))
    parts.append(text(c3_x, 424, "система продовжує штатний рух", size=11, color=INK))
    parts.append(text(c3_x, 444, "Безпека: ВИСОКА / Доступність: ВИСОКА", size=10, color=MUTED))

    render(os.path.join(IMG, "dual-sensor-dilemma.svg"), W, H, *parts,
           title="Порівняння конфігурацій надлишковості: 1oo1, 1oo2 та 2oo3 (TMR)")


# ── Фігура 2: Аналітична (віртуальна) надлишковість сервоприводу ──────────────
def fig_analytical_redundancy():
    W, H = 820, 420
    parts = []

    # Зовнішня рамка системи
    parts.append(rect(20, 20, 780, 380, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    parts.append(text(410, 48, "Розв'язання паритету через фізичну модель (Аналітична надлишковість)", size=14, color=INK, bold=True))

    # Ліва колонка: фізичні давачі
    tb_pot, _, _ = textbox(150, 110, ["Давач 1: Потенціометр", "Кут на валу: θ₁ = 45.0°"], size=11, pad=8, fill="#f8fafc", stroke=LINE, min_w=200)
    tb_enc, _, _ = textbox(150, 200, ["Давач 2: Оптичний енкодер", "Кут на валу: θ₂ = 68.5° (збій)"], size=11, pad=8, fill="#fff1f2", stroke=POS, min_w=200)
    parts.append(tb_pot)
    parts.append(tb_enc)

    # Центральний компаратор розбіжності
    tb_disc, _, _ = textbox(410, 155, ["Детектор розбіжності", "|θ₁ - θ₂| = 23.5° > 3.0°", "СТАН: РОЗСИНХРОНІЗАЦІЯ"], size=11, pad=8, fill="#fef3c7", stroke="#d97706", min_w=190)
    parts.append(tb_disc)

    parts.append(arrow(260, 110, 310, 140, color=LINE, sw=1.5))
    parts.append(arrow(260, 200, 310, 170, color=POS, sw=1.5))

    # Нижня гілка: Модель електродвигуна (Аналітичний спостерігач)
    tb_inputs, _, _ = textbox(150, 320, ["Фізичні входи двигуна:", "• Напруга ШІМ U(t)", "• Інтеграл струму I(t)"], size=11, pad=8, fill="#eff6ff", stroke=NEG, min_w=200)
    parts.append(tb_inputs)

    tb_model, _, _ = textbox(410, 320, ["Динамічна модель сервоприводу", "dω/dt = (k_m · I - T_load) / J", "θ_model = ∫ ω dt = 46.2°"], size=11, pad=8, fill="#eff6ff", stroke=NEG, min_w=220)
    parts.append(tb_model)

    parts.append(arrow(260, 320, 295, 320, color=NEG, sw=1.5))

    # Права колонка: Арбітр та вихідний селектор
    tb_arb, _, _ = textbox(670, 235, [
        "Модельний арбітр (Валідатор):",
        "|θ₁ - θ_model| = 1.2°  → [ПРАВДОПОДІБНО]",
        "|θ₂ - θ_model| = 22.3° → [ВІДХИЛЕНО]",
        "Ізольовано енкодер; обрано θ₁ = 45.0°"
    ], size=10.5, pad=10, fill="#f0fdf4", stroke=FIELD, min_w=225)
    parts.append(tb_arb)

    parts.append(arrow(510, 155, 550, 210, color="#d97706", sw=1.5))
    parts.append(arrow(525, 320, 550, 260, color=NEG, sw=1.5))

    render(os.path.join(IMG, "analytical-redundancy.svg"), W, H, *parts,
           title="Крос-валідація двох розбіжних давачів за допомогою динамічної моделі двигуна")


# ── Фігура 3: Характеристики APPS і Fail-Safe Biasing ────────────────────────
def fig_failsafe_biasing():
    W, H = 820, 420
    parts = []

    # Зовнішня рамка
    parts.append(rect(20, 20, 780, 380, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    parts.append(text(410, 48, "Безпечне зміщення (Fail-Safe Biasing) та перехресні характеристики", size=14, color=INK, bold=True))

    # Ліва половина: Графік передавальних характеристик подвійного педального датчика APPS
    g_l, g_r = 70, 360
    g_t, g_b = 90, 320
    
    parts.append(line(g_l, g_b, g_r, g_b, color=LINE, sw=1.5))
    parts.append(line(g_l, g_t, g_l, g_b, color=LINE, sw=1.5))
    parts.append(text((g_l + g_r) / 2, g_b + 28, "Положення педалі (0% → 100%)", size=11, color=INK))
    parts.append(text(g_l - 10, g_t - 5, "Напруга АЦП (В)", size=11, color=INK, anchor="end"))

    # Поділки напруг
    parts.append(text(g_l - 8, g_b - 5, "0V", size=9, color=MUTED, anchor="end"))
    parts.append(text(g_l - 8, g_b - 50, "1.0V", size=9, color=MUTED, anchor="end"))
    parts.append(text(g_l - 8, g_b - 120, "2.5V", size=9, color=MUTED, anchor="end"))
    parts.append(text(g_l - 8, g_b - 210, "4.5V", size=9, color=MUTED, anchor="end"))

    # Канал 1: Пряма лінійна (0.5V -> 4.5V)
    parts.append(line(g_l + 20, g_b - 25, g_r - 20, g_b - 210, color=NEG, sw=2.5))
    parts.append(text(g_r - 15, g_b - 215, "Канал 1: 0.5V → 4.5V", size=10, color=NEG, anchor="end", bold=True))

    # Канал 2: Інверсна або половинна характеристика (4.5V -> 0.5V)
    parts.append(line(g_l + 20, g_b - 210, g_r - 20, g_b - 25, color=POS, sw=2.5, dash="6 3"))
    parts.append(text(g_r - 15, g_b - 35, "Канал 2: 4.5V → 0.5V (інверсний)", size=10, color=POS, anchor="end", bold=True))

    # Підпис захисту від КЗ
    parts.append(text((g_l + g_r) / 2, g_b - 110, "V₁ + V₂ = 5.0V (Константа)", size=10, color=FIELD, bold=True))
    parts.append(text((g_l + g_r) / 2, g_b - 90, "КЗ на VCC чи GND миттєво руйнує суму", size=9, color=MUTED, italic=True))

    # Права половина: Матриця вибору безпечного стану (Fail-Safe Biasing Rules)
    r_x = 420
    r_w = 360

    parts.append(rect(r_x, 80, r_w, 290, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    parts.append(text(r_x + r_w / 2, 105, "Політика асиметричного ризику (1oo2 Bias)", size=12, color=INK, bold=True))

    # Правило 1: Педаль газу / Тяга
    tb_p1, _, _ = textbox(r_x + r_w / 2, 150, [
        "1. Педаль газу / Дросель (APPS):",
        "Розбіжність > 10% → Педаль = 0% (Холостий хід)",
        "Ризик: Самовільний розгін смертельний"
    ], size=10, pad=6, fill="#fee2e2", stroke=POS, min_w=330)
    parts.append(tb_p1)

    # Правило 2: Температура батареї / BMS
    tb_p2, _, _ = textbox(r_x + r_w / 2, 225, [
        "2. Температура акумулятора (BMS):",
        "T₁ = 42°C, T₂ = 68°C → Обираємо MAX(T₁, T₂) = 68°C",
        "Ризик: Недооцінка нагріву веде до пожежі"
    ], size=10, pad=6, fill="#fef3c7", stroke="#d97706", min_w=330)
    parts.append(tb_p2)

    # Правило 3: Висотомір посадки
    tb_p3, _, _ = textbox(r_x + r_w / 2, 300, [
        "3. Висота приземлення дрона:",
        "h₁ = 4.2 м, h₂ = 1.8 м → Обираємо MIN(h₁, h₂) = 1.8 м",
        "Ризик: Завищення висоти веде до удару об землю"
    ], size=10, pad=6, fill="#eff6ff", stroke=NEG, min_w=330)
    parts.append(tb_p3)

    # Підсумок унизу
    parts.append(text(410, 388, "Коли розбіжність неможливо арбітрувати — обирається стан найменшого фізичного ризику", size=11, color=INK, italic=True))

    render(os.path.join(IMG, "failsafe-biasing.svg"), W, H, *parts,
           title="Принцип захисного зміщення при виборі між двома незгідними давачами")


if __name__ == "__main__":
    fig_redundancy_architectures()
    fig_analytical_redundancy()
    fig_failsafe_biasing()
    print("Figures generated successfully.")
