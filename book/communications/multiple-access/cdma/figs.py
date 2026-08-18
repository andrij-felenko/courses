# -*- coding: utf-8 -*-
"""Генератор векторних SVG-фігур для теми CDMA: код як адреса.
Запуск: python figs.py
"""

import sys
import os

# Підключаємо svgkit з кореневої теки scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_dsss_spread_spectrum():
    """Фігура 1: Пряме розширення спектра DSSS у часовій та частотній областях."""
    w, h = 880, 410
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h)]
    svg.append('<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/></marker></defs>' % LINE)
    svg.append(rect(0, 0, w, h, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=0))

    # Заголовок панелей
    tb, _, _ = textbox(225, 26, "Часова область: перемноження біта на чипи", size=12, fill="#eef2f7", stroke="#94a3b8", bold=True)
    svg.append(tb)
    tb, _, _ = textbox(660, 26, "Частотна область: розмивання під шум", size=12, fill="#eef2f7", stroke="#94a3b8", bold=True)
    svg.append(tb)

    # ── Ліва частина: Часова область ──
    # 1. Інформаційний біт d(t) = +1
    svg.append(text(25, 75, "Інформаційний біт d(t)", size=11, anchor="start", bold=True, color="#1e293b"))
    svg.append(line(25, 110, 400, 110, color="#cbd5e1", sw=1))
    svg.append(line(50, 110, 50, 85, color="#2563eb", sw=2))
    svg.append(line(50, 85, 370, 85, color="#2563eb", sw=2.5))
    svg.append(line(370, 85, 370, 110, color="#2563eb", sw=2))
    svg.append(text(210, 102, "d = +1 (тривалість T_b)", size=10, color="#1d4ed8", bold=True))

    # Знак множення
    svg.append(circle(210, 135, 11, fill="#f1f5f9", stroke="#64748b", sw=1.5))
    svg.append(text(210, 140, "×", size=15, bold=True, color="#0f172a"))

    # 2. Чипова послідовність c(t) (8 чипів: +1, -1, +1, +1, -1, +1, -1, -1)
    chips = [1, -1, 1, 1, -1, 1, -1, -1]
    chip_w = 40
    start_x = 50
    base_y = 200
    amp = 20

    svg.append(text(25, 168, "Псевдовипадковий код чипів c(t)", size=11, anchor="start", bold=True, color="#1e293b"))
    svg.append(line(25, base_y, 400, base_y, color="#cbd5e1", sw=1))

    for i, c_val in enumerate(chips):
        cx = start_x + i * chip_w
        cy = base_y - c_val * amp
        svg.append(line(cx, cy, cx + chip_w, cy, color="#059669", sw=2))
        if i > 0 and chips[i] != chips[i-1]:
            svg.append(line(cx, base_y - chips[i-1]*amp, cx, cy, color="#059669", sw=1.5, dash="2,2"))
        svg.append(text(cx + chip_w/2, cy - 5 if c_val > 0 else cy + 13, "+1" if c_val > 0 else "-1", size=9, color="#047857"))

    # Стрілка вниз до результуючого сигналу s(t)
    svg.append(arrow(210, 230, 210, 255, color="#475569", sw=1.5))

    # 3. Розширений сигнал s(t) = d(t) * c(t)
    base_y_res = 315
    svg.append(text(25, 275, "Результуючий сигнал s(t) = d(t) · c(t)", size=11, anchor="start", bold=True, color="#1e293b"))
    svg.append(line(25, base_y_res, 400, base_y_res, color="#cbd5e1", sw=1))

    for i, c_val in enumerate(chips):
        cx = start_x + i * chip_w
        cy = base_y_res - c_val * amp
        svg.append(line(cx, cy, cx + chip_w, cy, color="#dc2626", sw=2.2))
        if i > 0 and chips[i] != chips[i-1]:
            svg.append(line(cx, base_y_res - chips[i-1]*amp, cx, cy, color="#dc2626", sw=1.5, dash="2,2"))

    # Позначення періоду чипа Tc та біта Tb
    svg.append(line(50, 350, 90, 350, color="#64748b", sw=1.2))
    svg.append(line(50, 345, 50, 355, color="#64748b", sw=1.2))
    svg.append(line(90, 345, 90, 355, color="#64748b", sw=1.2))
    svg.append(text(70, 368, "T_c", size=10, color="#334155", bold=True))

    svg.append(line(50, 380, 370, 380, color="#64748b", sw=1.2))
    svg.append(line(50, 375, 50, 385, color="#64748b", sw=1.2))
    svg.append(line(370, 375, 370, 385, color="#64748b", sw=1.2))
    svg.append(text(210, 396, "Тривалість біта T_b = L_c · T_c (тут L_c = 8)", size=10, color="#334155", bold=True))

    # Розділова вертикальна лінія
    svg.append(line(430, 15, 430, 395, color="#cbd5e1", sw=1.5, dash="4,4"))

    # ── Права частина: Частотна область ──
    orig_x = 470
    axis_y = 330

    svg.append(arrow(orig_x, axis_y, 850, axis_y, color="#334155", sw=1.5))
    svg.append(text(850, axis_y + 18, "Частота f", size=10, color="#334155", anchor="end", bold=True))

    svg.append(arrow(orig_x + 15, axis_y, orig_x + 15, 55, color="#334155", sw=1.5))
    svg.append(text(orig_x + 10, 48, "Спектральна густина потужності (PSD)", size=10, color="#334155", anchor="start", bold=True))

    # Лінія теплового шуму N0
    noise_y = 215
    svg.append(line(orig_x + 15, noise_y, 845, noise_y, color="#64748b", sw=1.2, dash="5,4"))
    svg.append(text(840, noise_y - 8, "Шум N_0", size=10, color="#475569", anchor="end", bold=True))

    # 1. Вузькосмуговий сигнал до розширення (синій високий пік)
    fc_x = 600
    bw_b = 25
    peak_y = 80
    svg.append('<path d="M %d %d Q %d %d %d %d Q %d %d %d %d Z" fill="#93c5fd" fill-opacity="0.6" stroke="#2563eb" stroke-width="2"/>' %
               (fc_x - bw_b, axis_y, fc_x - bw_b/2, peak_y, fc_x, peak_y, fc_x + bw_b/2, peak_y, fc_x + bw_b, axis_y))
    svg.append(text(fc_x, peak_y - 8, "Вузькосмуговий сигнал B_b", size=10, color="#1d4ed8", bold=True))

    # Пояснення DSSS праворуч у вільному просторі (x = 730, y = 135)
    tb, _, _ = textbox(730, 135, "Розширений DSSS сигнал\n(Смуга B_rf розмита під шум)", size=10, pad=5, fill="#fff5f5", stroke="#fca5a5", color="#b91c1c", bold=True)
    svg.append(tb)
    svg.append(arrow(730, 160, 730, 245, color="#dc2626", sw=1.5))

    # 2. Широкосмуговий DSSS сигнал після розширення (червоний плаский купол нижче шуму)
    bw_rf = 150
    spread_peak_y = 255
    svg.append('<path d="M %d %d Q %d %d %d %d Q %d %d %d %d Z" fill="#fca5a5" fill-opacity="0.4" stroke="#dc2626" stroke-width="1.8"/>' %
               (fc_x - bw_rf, axis_y, fc_x - bw_rf/2, spread_peak_y, fc_x, spread_peak_y, fc_x + bw_rf/2, spread_peak_y, fc_x + bw_rf, axis_y))

    # Позначення смуги B_rf
    svg.append(line(fc_x - bw_rf, axis_y + 25, fc_x + bw_rf, axis_y + 25, color="#b91c1c", sw=1.2))
    svg.append(line(fc_x - bw_rf, axis_y + 20, fc_x - bw_rf, axis_y + 30, color="#b91c1c", sw=1.2))
    svg.append(line(fc_x + bw_rf, axis_y + 20, fc_x + bw_rf, axis_y + 30, color="#b91c1c", sw=1.2))
    svg.append(text(fc_x, axis_y + 38, "Широка смуга B_rf = 1 / T_c", size=10, color="#b91c1c", bold=True))

    svg.append('</svg>')
    with open(os.path.join(OUT_DIR, "dsss-spread-spectrum.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg))


def fig_correlation_despreading():
    """Фігура 2: Кореляційний прийом і виграш обробки (Despreading та стиснення спектра)."""
    w, h = 860, 360
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h)]
    svg.append('<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/></marker></defs>' % LINE)
    svg.append(rect(0, 0, w, h, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=0))

    # Заголовок
    tb, _, _ = textbox(430, 24, "Кореляційний демодулятор (деспрединг): видобування сигналу з-під шуму", size=12, fill="#eef2f7", stroke="#94a3b8", bold=True)
    svg.append(tb)

    # 1. Вхідний сигнал: r(t) = s_1(t) + ∑ s_k(t) + n(t)
    tb, _, _ = textbox(115, 110, "Вхідна суміш r(t)\nКорисний сигнал s₁(t)\n+ Інші абоненти ∑s_k(t)\n+ Тепловий шум n(t)", size=10, pad=7, fill="#fff1f2", stroke="#fda4af")
    svg.append(tb)

    # Стрілка до змішувача
    svg.append(arrow(200, 110, 270, 110, color="#475569", sw=1.8))

    # Змішувач (множник)
    svg.append(circle(290, 110, 15, fill="#f8fafc", stroke="#334155", sw=2))
    svg.append(text(290, 115, "×", size=18, bold=True, color="#0f172a"))

    # Локальний генератор коду c1(t)
    tb, _, _ = textbox(290, 205, "Синхронний код c₁(t)\n(Точна копія коду\nцільового абонента)", size=10, pad=7, fill="#ecfdf5", stroke="#6ee7b7", color="#065f46")
    svg.append(tb)
    svg.append(arrow(290, 170, 290, 130, color="#059669", sw=1.8))

    # Стрілка від змішувача до інтегратора
    svg.append(arrow(310, 110, 390, 110, color="#475569", sw=1.8))
    svg.append(text(350, 98, "c₁(t) · r(t)", size=10, color="#334155", bold=True))

    # Інтегратор (інтегрування за період біта Tb)
    tb, _, _ = textbox(460, 110, "Інтегратор зі скиданням\n∫₀^{T_b} (...) dt\nНакопичення енергії біта", size=10, pad=7, fill="#eff6ff", stroke="#93c5fd", color="#1e40af")
    svg.append(tb)

    # Стрілка до порогового детектора
    svg.append(arrow(535, 110, 615, 110, color="#475569", sw=1.8))
    svg.append(text(575, 98, "Y(T_b)", size=10, color="#334155", bold=True))

    # Пороговий вирішувач (sign)
    tb, _, _ = textbox(680, 110, "Пороговий вирішувач\nЯкщо Y > 0 → d̂ = +1\nЯкщо Y < 0 → d̂ = -1", size=10, pad=7, fill="#fefce8", stroke="#fde047", color="#854d0e")
    svg.append(tb)

    # Вихідний біт
    svg.append(arrow(755, 110, 820, 110, color="#16a34a", sw=2))
    svg.append(text(830, 115, "d̂₁", size=14, bold=True, color="#15803d", anchor="start"))

    # ── Нижня панель: математичний результат перетворення ──
    svg.append(rect(30, 255, 800, 90, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    svg.append(text(45, 275, "Математичний баланс енергії після деспредингу:", size=11, anchor="start", bold=True, color="#0f172a"))

    svg.append(text(45, 297, "• Корисний сигнал s₁(t) · c₁(t) = d₁ · c₁²(t) = d₁ · (+1) → інтегрується когерентно з повним підсиленням L_c", size=10, anchor="start", color="#1e3a8a"))
    svg.append(text(45, 316, "• Чужі сигнали s_k(t) · c₁(t) = d_k · [c_k(t) · c₁(t)] → взаємна кореляція близька до 0 (подавляються у G_p разів)", size=10, anchor="start", color="#78350f"))
    svg.append(text(45, 335, "• Тепловий шум n(t) · c₁(t) → залишається некорельованим білим шумом і не накопичується когерентно", size=10, anchor="start", color="#334155"))

    svg.append('</svg>')
    with open(os.path.join(OUT_DIR, "correlation-despreading.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg))


def fig_near_far_problem():
    """Фігура 3: Проблема близького/далекого абонента та швидке керування потужністю."""
    w, h = 900, 420
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h)]
    svg.append('<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/></marker></defs>' % LINE)
    svg.append(rect(0, 0, w, h, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=0))

    # Дві колонки: Ліворуч - Без керування (катастрофа), Праворуч - Зі швидким керуванням (баланс)
    # Заголовки
    tb, _, _ = textbox(225, 26, "Без керування потужністю: блокування далекого", size=12, fill="#fee2e2", stroke="#fca5a5", color="#991b1b", bold=True)
    svg.append(tb)
    tb, _, _ = textbox(675, 26, "Зі швидким замкненим керуванням (800–1500 Гц)", size=12, fill="#dcfce7", stroke="#86efac", color="#166534", bold=True)
    svg.append(tb)

    # ── Ліва колонка (Near-Far Problem) ──
    # Базова станція ліворуч
    bs_x1 = 70
    bs_y = 190
    svg.append(line(bs_x1, bs_y + 50, bs_x1, bs_y - 40, color="#1e293b", sw=3))
    svg.append(line(bs_x1 - 18, bs_y + 50, bs_x1 + 18, bs_y + 50, color="#1e293b", sw=3))
    svg.append(circle(bs_x1, bs_y - 40, 7, fill="#ef4444", stroke="#991b1b", sw=1.5))
    tb, _, _ = textbox(bs_x1, bs_y + 70, "Базова станція\n(приймач)", size=10, pad=4, fill="#f1f5f9", stroke="#cbd5e1", bold=True)
    svg.append(tb)

    # Близький абонент (100 м)
    u1_x = 240
    u1_y = 75
    tb, _, _ = textbox(u1_x, u1_y, "Близький абонент A\nВідстань d = 100 м, P_tx = 200 мВт", size=10, pad=5, fill="#fee2e2", stroke="#ef4444")
    svg.append(tb)

    # Потужний сигнал стрілкою (йде прямо зверху)
    svg.append(arrow(140, 75, bs_x1 + 15, bs_y - 40, color="#dc2626", sw=3))
    tb, _, _ = textbox(240, 120, "P_rx = -40 дБм (ДУЖЕ СИЛЬНИЙ)", size=9, pad=3, fill="#ffffff", stroke="#fca5a5", color="#b91c1c", bold=True)
    svg.append(tb)

    # Далекий абонент (3 км)
    u2_x = 330
    u2_y = 180
    tb, _, _ = textbox(u2_x, u2_y, "Далекий абонент B\nВідстань d = 3 км, P_tx = 200 мВт", size=10, pad=5, fill="#f1f5f9", stroke="#94a3b8")
    svg.append(tb)

    # Слабкий сигнал стрілкою
    svg.append(arrow(215, 180, bs_x1 + 20, bs_y - 15, color="#94a3b8", sw=1.2))
    tb, _, _ = textbox(330, 225, "P_rx = -110 дБм (ЗГАС НА 70 дБ)", size=9, pad=3, fill="#ffffff", stroke="#cbd5e1", color="#64748b", bold=True)
    svg.append(tb)

    # Висновок зліва
    tb, _, _ = textbox(225, 345, "Різниця потужностей 70 дБ (в 10 000 000 разів!)\nВиграш обробки G_p = 21 дБ не рятує:\nСигнал абонента B повністю потонув у заваді від A", size=10, pad=6, fill="#fef2f2", stroke="#f87171", color="#991b1b")
    svg.append(tb)

    # Розділова лінія
    svg.append(line(450, 15, 450, 400, color="#cbd5e1", sw=1.5, dash="4,4"))

    # ── Права колонка (Fast Power Control) ──
    bs_x2 = 520
    svg.append(line(bs_x2, bs_y + 50, bs_x2, bs_y - 40, color="#1e293b", sw=3))
    svg.append(line(bs_x2 - 18, bs_y + 50, bs_x2 + 18, bs_y + 50, color="#1e293b", sw=3))
    svg.append(circle(bs_x2, bs_y - 40, 7, fill="#22c55e", stroke="#15803d", sw=1.5))
    tb, _, _ = textbox(bs_x2, bs_y + 70, "Базова станція\n(керує 1500 Гц)", size=10, pad=4, fill="#f1f5f9", stroke="#cbd5e1", bold=True)
    svg.append(tb)

    # Близький абонент A (потужність зменшено)
    u1_x2 = 690
    tb, _, _ = textbox(u1_x2, u1_y, "Абонент A (100 м)\nP_tx = 0.02 мВт (-17 дБм)\n[Знижено командуванням]", size=10, pad=5, fill="#dcfce7", stroke="#22c55e", color="#166534")
    svg.append(tb)

    # Збалансований сигнал
    svg.append(arrow(590, 75, bs_x2 + 15, bs_y - 40, color="#16a34a", sw=2))
    tb, _, _ = textbox(690, 125, "P_rx = -95 дБм (Команда: «-1 дБ»)", size=9, pad=3, fill="#ffffff", stroke="#86efac", color="#15803d", bold=True)
    svg.append(tb)

    # Далекий абонент B (потужність збільшено)
    u2_x2 = 780
    tb, _, _ = textbox(u2_x2, u2_y, "Абонент B (3 км)\nP_tx = 200 мВт (+23 дБм)\n[Підвищено до максимуму]", size=10, pad=5, fill="#dcfce7", stroke="#22c55e", color="#166534")
    svg.append(tb)

    # Збалансований сигнал
    svg.append(arrow(665, 180, bs_x2 + 20, bs_y - 15, color="#16a34a", sw=2))
    tb, _, _ = textbox(780, 230, "P_rx = -95 дБм (Команда: «+1 дБ»)", size=9, pad=3, fill="#ffffff", stroke="#86efac", color="#15803d", bold=True)
    svg.append(tb)

    # Висновок справа
    tb, _, _ = textbox(675, 345, "Ідеальний баланс потужностей на антені вишки:\nP_rx(A) = P_rx(B) = -95 дБм (з точністю ±0.5 дБ)\nОртогональність відновлено, ємність мережі максимальна", size=10, pad=6, fill="#f0fdf4", stroke="#86efac", color="#166534")
    svg.append(tb)

    svg.append('</svg>')
    with open(os.path.join(OUT_DIR, "near-far-problem.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg))


def fig_rake_receiver():
    """Фігура 4: Rake-приймач (приймач-граблі) для збирання багатопроменевих відбитків."""
    w, h = 860, 420
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h)]
    svg.append('<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/></marker></defs>' % LINE)
    svg.append(rect(0, 0, w, h, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=0))

    # Заголовок
    tb, _, _ = textbox(430, 24, "Архітектура Rake-приймача: когерентне об'єднання відбитків (Maximal Ratio Combining)", size=12, fill="#eef2f7", stroke="#94a3b8", bold=True)
    svg.append(tb)

    # 1. Вхідна антена та багатопроменевий сигнал
    ant_x = 45
    ant_y = 180
    svg.append(line(ant_x, ant_y - 25, ant_x, ant_y + 35, color="#1e293b", sw=2))
    svg.append(line(ant_x - 15, ant_y - 25, ant_x, ant_y - 5, color="#1e293b", sw=2))
    svg.append(line(ant_x + 15, ant_y - 25, ant_x, ant_y - 5, color="#1e293b", sw=2))
    svg.append(text(ant_x, ant_y + 55, "Антена", size=10, bold=True, color="#334155"))

    # Багатопроменевий радіосигнал (3 промені з затримками)
    tb, _, _ = textbox(140, ant_y, "Сума променів:\n• Промінь 1 (прямий, τ₁)\n• Промінь 2 (відбиток 1, τ₂)\n• Промінь 3 (відбиток 2, τ₃)", size=10, pad=6, fill="#f8fafc", stroke="#cbd5e1")
    svg.append(tb)

    svg.append(arrow(ant_x, ant_y, 75, ant_y, color="#334155", sw=1.8))
    svg.append(line(210, ant_y, 240, ant_y, color="#334155", sw=1.8))

    # Розгалуження на 3 пальці (Fingers)
    y_f1 = 90
    y_f2 = 180
    y_f3 = 270

    svg.append(line(240, y_f1, 240, y_f3, color="#334155", sw=1.8))
    svg.append(arrow(240, y_f1, 275, y_f1, color="#334155", sw=1.5))
    svg.append(arrow(240, y_f2, 275, y_f2, color="#334155", sw=1.5))
    svg.append(arrow(240, y_f3, 275, y_f3, color="#334155", sw=1.5))

    # Блок пошуку затримок (Searcher Receiver)
    tb, _, _ = textbox(140, 340, "Пошуковий приймач (Searcher)\nСканує затримки кореляційного піка\nі призначає пальці на найсильніші промені", size=10, pad=6, fill="#fefce8", stroke="#ca8a04", color="#854d0e")
    svg.append(tb)
    svg.append(arrow(240, ant_y, 240, 310, color="#ca8a04", sw=1.5))
    svg.append(arrow(240, 340, 330, 340, color="#ca8a04", sw=1.5))

    # ── Три пальці Rake ──
    # Палець 1
    tb, _, _ = textbox(360, y_f1, "Палець 1 (Finger 1)\nКорелятор з кодом c(t - τ₁)\nОцінка каналу: a₁ · e^{-jθ₁}", size=10, pad=6, fill="#eff6ff", stroke="#93c5fd", color="#1e40af")
    svg.append(tb)

    # Палець 2
    tb, _, _ = textbox(360, y_f2, "Палець 2 (Finger 2)\nКорелятор з кодом c(t - τ₂)\nОцінка каналу: a₂ · e^{-jθ₂}", size=10, pad=6, fill="#eff6ff", stroke="#93c5fd", color="#1e40af")
    svg.append(tb)

    # Палець 3
    tb, _, _ = textbox(360, y_f3, "Палець 3 (Finger 3)\nКорелятор з кодом c(t - τ₃)\nОцінка каналу: a₃ · e^{-jθ₃}", size=10, pad=6, fill="#eff6ff", stroke="#93c5fd", color="#1e40af")
    svg.append(tb)

    # Блоки вагового масштабування (MRC Weights w_k = a_k*)
    w_x = 520
    tb, _, _ = textbox(w_x, y_f1, "Вага w₁ = a₁*\n(Компенсація фази\nі підсилення ~ a₁)", size=10, pad=6, fill="#f0fdf4", stroke="#86efac", color="#166534")
    svg.append(tb)
    svg.append(arrow(450, y_f1, w_x - 55, y_f1, color="#334155", sw=1.5))

    tb, _, _ = textbox(w_x, y_f2, "Вага w₂ = a₂*\n(Компенсація фази\nі підсилення ~ a₂)", size=10, pad=6, fill="#f0fdf4", stroke="#86efac", color="#166534")
    svg.append(tb)
    svg.append(arrow(450, y_f2, w_x - 55, y_f2, color="#334155", sw=1.5))

    tb, _, _ = textbox(w_x, y_f3, "Вага w₃ = a₃*\n(Компенсація фази\nі підсилення ~ a₃)", size=10, pad=6, fill="#f0fdf4", stroke="#86efac", color="#166534")
    svg.append(tb)
    svg.append(arrow(450, y_f3, w_x - 55, y_f3, color="#334155", sw=1.5))

    # Суматор MRC
    sum_x = 660
    svg.append(circle(sum_x, ant_y, 22, fill="#f8fafc", stroke="#1e293b", sw=2))
    svg.append(text(sum_x, ant_y + 6, "∑", size=22, bold=True, color="#0f172a"))

    svg.append(arrow(w_x + 55, y_f1, sum_x - 15, ant_y - 15, color="#16a34a", sw=1.8))
    svg.append(arrow(w_x + 55, y_f2, sum_x - 22, ant_y, color="#16a34a", sw=1.8))
    svg.append(arrow(w_x + 55, y_f3, sum_x - 15, ant_y + 15, color="#16a34a", sw=1.8))

    # Вихід суматора до детектора
    svg.append(arrow(sum_x + 22, ant_y, 740, ant_y, color="#1e293b", sw=2))

    # Детектор бітів
    tb, _, _ = textbox(790, ant_y, "Детектор\nбітів\n(Decision)", size=10, pad=7, fill="#fefce8", stroke="#fde047", color="#854d0e")
    svg.append(tb)

    # Пояснення знизу
    svg.append(text(430, 395, "Багатопроменеве різноманіття: енергія відбитих променів додається конструктивно замість руйнівного завмирання", size=10, bold=True, color="#0f172a"))

    svg.append('</svg>')
    with open(os.path.join(OUT_DIR, "rake-receiver.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg))


def main():
    print("Генерація SVG-фігур для теми CDMA...")
    fig_dsss_spread_spectrum()
    fig_correlation_despreading()
    fig_near_far_problem()
    fig_rake_receiver()
    print("Усі фігури успішно згенеровано в img/")


if __name__ == "__main__":
    main()
