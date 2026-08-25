# -*- coding: utf-8 -*-
# Фігури до статті «Затримка давача» (book/communications/synchronization/sensor-latency-compensation).
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: Анатомія затримки давача ────────────────────────────────────────
def fig_sensor_latency_breakdown():
    W, H = 760, 420
    parts = []

    parts.append(rect(15, 15, W - 30, H - 30, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))

    # Заголовок зверху
    parts.append(text(W / 2, 42, "Анатомія сумарної затримки сигналу давача (\u03c4_total)", size=15, color=INK, bold=True))
    parts.append(text(W / 2, 60, "Від механічного збурення чутливого елемента до обробки алгоритмом керування в RTOS", size=11, color=MUTED))

    # 4 етапи накопичення затримки
    stages = [
        ("1. Механічний відгук", ["Чутлива маса MEMS,", "підвіс, перехідні процеси", "динаміки 2-го порядку"], "\u03c4_phys \u2248 50\u2013200 \u043c\u043a\u0441", "#eff6ff", "#3b82f6"),
        ("2. Цифрова ЦОС", ["Апаратний АЦП, децимація,", "фільтри НЧ (DLPF/IIR/FIR)", "для гасіння вібрацій"], "\u03c4_filter \u2248 2\u201315 \u043c\u0441", "#fef3c7", "#d97706"),
        ("3. Інтерфейсна шина", ["Серіалізація пакетів", "SPI (10 МГц) vs I2C (400 кГц),", "опитування vs переривання"], "\u03c4_bus \u2248 0.02\u20132 \u043c\u0441", "#f0fdf4", "#16a34a"),
        ("4. RTOS та оцінювач", ["Черги uORB/AP_HAL,", "перемикання контексту,", "дискретизація ZOH (T/2)"], "\u03c4_rtos \u2248 1\u20135 \u043c\u0441", "#faf5ff", "#9333ea")
    ]

    card_w = 160
    card_h = 175
    start_x = 35
    gap = 20
    top_y = 85

    for i, (title, lines_list, delay, fill_c, stroke_c) in enumerate(stages):
        cx = start_x + i * (card_w + gap) + card_w / 2
        bx = start_x + i * (card_w + gap)
        
        parts.append(rect(bx, top_y, card_w, card_h, fill=fill_c, stroke=stroke_c, sw=1.5, rx=6))
        parts.append(text(cx, top_y + 24, title, size=12, color=INK, bold=True))
        
        # Лінія-роздільник
        parts.append(line(bx + 10, top_y + 35, bx + card_w - 10, top_y + 35, color=stroke_c, sw=1, dash="2 2"))
        
        # Опис
        for dl_idx, dl in enumerate(lines_list):
            parts.append(text(cx, top_y + 55 + dl_idx * 16, dl, size=10, color=INK))
            
        # Затримка внизу картки
        parts.append(rect(bx + 10, top_y + card_h - 42, card_w - 20, 30, fill="#ffffff", stroke=stroke_c, sw=1.2, rx=4))
        parts.append(text(cx, top_y + card_h - 23, delay, size=11, color=stroke_c, bold=True))

        # Стрілка переходу до наступного блоку
        if i < 3:
            ax1 = bx + card_w + 3
            ax2 = bx + card_w + gap - 3
            ay = top_y + card_h / 2
            parts.append(arrow(ax1, ay, ax2, ay, color=MUTED, sw=1.8))

    # Підсумкова шкала суми затримки
    bar_y = 285
    parts.append(rect(35, bar_y, W - 70, 70, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=6))
    
    parts.append(text(50, bar_y + 24, "Сумарний бюджет затримки: \u03c4_total = \u03c4_phys + \u03c4_filter + \u03c4_bus + \u03c4_rtos", size=12, color=INK, anchor="start", bold=True))
    parts.append(text(50, bar_y + 44, "\u2022 Швидкі давачі (IMU \u2014 гіроскоп, акселерометр): \u03c4_total \u2248 3\u201320 мс (критично для контуру кутової стабілізації)", size=11, color=MUTED, anchor="start"))
    parts.append(text(50, bar_y + 60, "\u2022 Повільні давачі (GNSS, барометр, оптичний потік): \u03c4_total \u2248 30\u2013250 мс (потребує відкладеного злиття в EKF)", size=11, color=MUTED, anchor="start"))

    # Підпис внизу
    cap = "Анатомія затримки давача: кожен каскад вимірювального тракту додає фазове запізнення \u0394\u03c6 = -\u03c9\u00b7\u03c4."
    parts.append(fitbox(35, H - 40, W - 70, 24, cap, size=11, fill="#f4f6f8", stroke=MUTED))

    return render(os.path.join(OUT, 'sensor-latency-breakdown.svg'), W, H,
                  *parts, title='Анатомія затримки давача')


# ── Фігура 2: Вплив чистого запізнення на запас стійкості (Bode plot) ─────────
def fig_phase_margin_bode_delay():
    W, H = 760, 450
    parts = []

    parts.append(rect(15, 15, W - 30, H - 30, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))

    parts.append(text(W / 2, 38, "Вплив чистого часового запізнення e^{-s\u00b7\u03c4} на запас стійкості за фазою", size=14, color=INK, bold=True))

    # Ліва частина: Графік ЛАЧХ (Амплітуда)
    ax_x, ax_y, ax_w, ax_h = 75, 75, 270, 130
    parts.append(rect(ax_x, ax_y, ax_w, ax_h, fill="#fafbfc", stroke="#cbd5e1", sw=1, rx=4))
    parts.append(text(ax_x + 10, ax_y + 18, "ЛАЧХ |L(j\u03c9)| (дБ)", size=11, color=INK, anchor="start", bold=True))
    
    # Сітка та 0 дБ
    zero_db_y = ax_y + 70
    parts.append(line(ax_x, zero_db_y, ax_x + ax_w, zero_db_y, color="#94a3b8", sw=1, dash="3 3"))
    parts.append(text(ax_x - 6, zero_db_y + 4, "0 дБ", size=10, color=MUTED, anchor="end"))
    
    # Крива ЛАЧХ (падає з частотою)
    mag_pts = []
    for k in range(50):
        t = k / 49.0
        x = ax_x + 20 + t * (ax_w - 40)
        y = ax_y + 20 + t * 90
        mag_pts.append((x, y))
    for k in range(len(mag_pts) - 1):
        parts.append(line(mag_pts[k][0], mag_pts[k][1], mag_pts[k+1][0], mag_pts[k+1][1], color=NEG, sw=2))

    # Частота зрізу wc (перетин 0 дБ)
    wc_x = ax_x + 20 + (50.0 / 90.0) * (ax_w - 40)
    parts.append(line(wc_x, ax_y + 10, wc_x, ax_y + ax_h, color=POS, sw=1.2, dash="2 2"))
    parts.append(circle(wc_x, zero_db_y, 4, fill=POS, stroke="#ffffff", sw=1.5))
    parts.append(text(wc_x, ax_y + ax_h - 8, "\u03c9_c (частота зрізу)", size=10, color=POS, bold=True))
    parts.append(text(ax_x + ax_w - 15, ax_y + 35, "|e^{-j\u03c9\u03c4}| = 1 (0 дБ)", size=10, color=NEG, anchor="end"))
    parts.append(text(ax_x + ax_w - 15, ax_y + 49, "Амплітуда незмінна", size=10, color=MUTED, anchor="end"))

    # Нижня частина ліворуч: Графік ЛФЧХ (Фаза)
    ph_x, ph_y, ph_w, ph_h = 75, 235, 270, 150
    parts.append(rect(ph_x, ph_y, ph_w, ph_h, fill="#fafbfc", stroke="#cbd5e1", sw=1, rx=4))
    parts.append(text(ph_x + 10, ph_y + 18, "ЛФЧХ \u2220L(j\u03c9) (градуси)", size=11, color=INK, anchor="start", bold=True))

    minus180_y = ph_y + 95
    parts.append(line(ph_x, minus180_y, ph_x + ph_w, minus180_y, color=POS, sw=1, dash="3 3"))
    parts.append(text(ph_x - 6, minus180_y + 4, "-180\u00b0", size=10, color=POS, anchor="end", bold=True))

    # Базова фаза без затримки (синя)
    base_ph_pts = []
    for k in range(50):
        t = k / 49.0
        x = ph_x + 20 + t * (ph_w - 40)
        y = ph_y + 30 + t * 45
        base_ph_pts.append((x, y))
    for k in range(len(base_ph_pts) - 1):
        parts.append(line(base_ph_pts[k][0], base_ph_pts[k][1], base_ph_pts[k+1][0], base_ph_pts[k+1][1], color=NEG, sw=2))

    # Фаза із затримкою (червона, падає як -w*tau)
    delay_ph_pts = []
    for k in range(50):
        t = k / 49.0
        x = ph_x + 20 + t * (ph_w - 40)
        y = ph_y + 30 + t * 45 + (t ** 1.3) * 60
        delay_ph_pts.append((x, y))
    for k in range(len(delay_ph_pts) - 1):
        parts.append(line(delay_ph_pts[k][0], delay_ph_pts[k][1], delay_ph_pts[k+1][0], delay_ph_pts[k+1][1], color=POS, sw=2))

    # Вертикаль wc вниз
    parts.append(line(wc_x, ph_y, wc_x, ph_y + ph_h, color=POS, sw=1.2, dash="2 2"))

    # Позначення запасів фази на wc
    base_wc_y = ph_y + 30 + (50.0 / 90.0) * 45
    delay_wc_y = ph_y + 30 + (50.0 / 90.0) * 45 + ((50.0 / 90.0) ** 1.3) * 60

    # Стрілка початкового PM (позитивний)
    parts.append(arrow(wc_x - 15, minus180_y, wc_x - 15, base_wc_y, color=FIELD, sw=1.5))
    parts.append(text(wc_x - 22, (minus180_y + base_wc_y) / 2 + 4, "PM\u2080 > 0", size=9, color=FIELD, anchor="end", bold=True))

    # Стрілка від'ємного PM (нестійкість)
    parts.append(arrow(wc_x + 15, minus180_y, wc_x + 15, delay_wc_y, color=POS, sw=1.5))
    parts.append(text(wc_x + 22, (minus180_y + delay_wc_y) / 2 + 4, "PM < 0 (зрив)", size=9, color=POS, anchor="start", bold=True))

    # Права частина: пояснювальні картки
    rx_x = 380
    parts.append(rect(rx_x, 75, 340, 150, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    parts.append(text(rx_x + 15, 98, "Математичний механізм втрати фази", size=12, color=INK, anchor="start", bold=True))
    parts.append(text(rx_x + 15, 122, "\u2022 Передатна функція затримки: W(s) = e^{-s\u00b7\u03c4}", size=11, color=INK, anchor="start"))
    parts.append(text(rx_x + 15, 142, "\u2022 Зсув фази: \u0394\u03c6(\u03c9) = -\u03c9\u00b7\u03c4 (рад) = -57.3\u00b0\u00b7\u03c9\u00b7\u03c4", size=11, color=POS, anchor="start", bold=True))
    parts.append(text(rx_x + 15, 164, "\u2022 Запас за фазою: PM = PM\u2080 - \u03c9_c\u00b7\u03c4", size=11, color=INK, anchor="start"))
    parts.append(text(rx_x + 15, 186, "\u2022 Критична затримка зриву стійкості: \u03c4_crit = PM\u2080 / \u03c9_c", size=11, color=POS, anchor="start", bold=True))
    parts.append(text(rx_x + 15, 208, "  (при PM\u2080=45\u00b0 та \u03c9_c=25 рад/с \u2192 \u03c4_crit = 31.4 мс)", size=10, color=MUTED, anchor="start"))

    parts.append(rect(rx_x, 235, 340, 150, fill="#fff5f5", stroke="#feb2b2", sw=1.2, rx=6))
    parts.append(text(rx_x + 15, 258, "Наслідки для замкненого контуру (Feedback)", size=12, color=POS, anchor="start", bold=True))
    parts.append(text(rx_x + 15, 282, "\u2022 Негативний зворотний зв'язок стає позитивним", size=11, color=INK, anchor="start"))
    parts.append(text(rx_x + 15, 302, "\u2022 Виникнення стійких автоколивань (граничні цикли)", size=11, color=INK, anchor="start"))
    parts.append(text(rx_x + 15, 322, "\u2022 Розхитування сервоприводів та перегрів моторів", size=11, color=INK, anchor="start"))
    parts.append(text(rx_x + 15, 342, "\u2022 Пілотажне розгойдування (Pilot-Induced Oscillation)", size=11, color=INK, anchor="start"))
    parts.append(text(rx_x + 15, 364, "\u2022 Зниження коефіцієнтів PID як паліатив погіршує динаміку", size=10, color=MUTED, anchor="start"))

    cap = "Вплив чистого запізнення: амплітуда не змінюється (0 дБ), але фаза падає лінійно з частотою \u03c9, руйнуючи запас стійкості PM."
    parts.append(fitbox(35, H - 40, W - 70, 24, cap, size=11, fill="#f4f6f8", stroke=MUTED))

    return render(os.path.join(OUT, 'phase-margin-bode-delay.svg'), W, H,
                  *parts, title='Вплив запізнення на запас стійкості за фазою')


# ── Фігура 3: Буфер затримок станів (Delayed Fusion в EKF) ────────────────────
def fig_delayed_fusion_ring_buffer():
    W, H = 760, 450
    parts = []

    parts.append(rect(15, 15, W - 30, H - 30, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))

    parts.append(text(W / 2, 38, "Принцип відкладеного злиття (Delayed Fusion) через кільцевий буфер в EKF", size=14, color=INK, bold=True))

    # Часова шкала зверху
    tl_y = 80
    parts.append(line(45, tl_y, W - 45, tl_y, color="#475569", sw=2))
    parts.append(arrow(W - 80, tl_y, W - 45, tl_y, color="#475569", sw=2))
    parts.append(text(W - 35, tl_y + 15, "Час t", size=11, color="#475569", bold=True))

    # Комірки кільцевого буфера станів
    buf_y = 120
    num_slots = 9
    slot_w = 68
    slot_h = 75
    start_bx = 55
    
    parts.append(text(45, buf_y - 12, "Кільцевий буфер збережених станів та коваріацій (State History Buffer, \u0394t = 10 мс):", size=11, color=INK, anchor="start", bold=True))

    for k in range(num_slots):
        bx = start_bx + k * (slot_w + 8)
        cx = bx + slot_w / 2
        
        # Виділення комірки затримки
        if k == 2:
            fill_c = "#fef3c7"
            strk_c = "#d97706"
            lines_slot = ["t_meas", "(t - \u03c4)"]
        elif k == num_slots - 1:
            fill_c = "#eff6ff"
            strk_c = "#3b82f6"
            lines_slot = ["t_now", "(поточний)"]
        else:
            fill_c = "#f8fafc"
            strk_c = "#cbd5e1"
            lines_slot = ["t - %d\u0394t" % (num_slots - 1 - k)]
            
        parts.append(rect(bx, buf_y, slot_w, slot_h, fill=fill_c, stroke=strk_c, sw=1.5, rx=4))
        
        for li, ln in enumerate(lines_slot):
            parts.append(text(cx, buf_y + 22 + li * 14, ln, size=10, color=INK, bold=(k==2 or k==num_slots-1)))
        
        parts.append(text(cx, buf_y + 58, "x̂, P, u", size=9, color=MUTED))

    # Стрілка затримки tau
    t_meas_x = start_bx + 2 * (slot_w + 8) + slot_w / 2
    t_now_x = start_bx + (num_slots - 1) * (slot_w + 8) + slot_w / 2
    
    parts.append(arrow(t_now_x, tl_y - 10, t_meas_x, tl_y - 10, color=POS, sw=1.8))
    parts.append(text((t_meas_x + t_now_x) / 2, tl_y - 18, "Затримка давача \u03c4 = 60 мс (6 кроків буфера)", size=11, color=POS, bold=True))

    # Нижні блоки операцій:
    op_y = 230
    
    # 1. Прихід вимірювання
    parts.append(rect(45, op_y, 205, 130, fill="#fffbeb", stroke="#f59e0b", sw=1.2, rx=6))
    parts.append(text(147, op_y + 22, "1. Прихід спостереження", size=11, color=INK, bold=True))
    parts.append(text(147, op_y + 44, "Пакет GNSS / Vision", size=10, color=MUTED))
    parts.append(text(147, op_y + 58, "надходить у момент t_now,", size=10, color=MUTED))
    parts.append(text(147, op_y + 72, "але несе мітку t_meas", size=10, color=MUTED))
    parts.append(rect(60, op_y + 90, 175, 26, fill="#ffffff", stroke="#f59e0b", sw=1, rx=4))
    parts.append(text(147, op_y + 107, "z_meas(t - \u03c4)", size=11, color="#b45309", bold=True))

    # Стрілка 1 -> 2
    parts.append(arrow(254, op_y + 65, 274, op_y + 65, color=MUTED, sw=1.5))

    # 2. Обчислення інновації на історичному стані
    parts.append(rect(278, op_y, 215, 130, fill="#eff6ff", stroke="#3b82f6", sw=1.2, rx=6))
    parts.append(text(385, op_y + 22, "2. Історична інновація", size=11, color=INK, bold=True))
    parts.append(text(385, op_y + 44, "Витяг стану x̂(t_meas)", size=10, color=MUTED))
    parts.append(text(385, op_y + 58, "Розрахунок нев'язки:", size=10, color=MUTED))
    parts.append(text(385, op_y + 72, "y = z_meas - h(x̂(t_meas))", size=10, color=MUTED))
    parts.append(rect(293, op_y + 90, 185, 26, fill="#ffffff", stroke="#3b82f6", sw=1, rx=4))
    parts.append(text(385, op_y + 107, "y = z - h(x̂_hist)", size=11, color=NEG, bold=True))

    # Стрілка 2 -> 3
    parts.append(arrow(497, op_y + 65, 517, op_y + 65, color=MUTED, sw=1.5))

    # 3. Корекція та прокочування вперед
    parts.append(rect(521, op_y, 194, 130, fill="#f0fdf4", stroke="#16a34a", sw=1.2, rx=6))
    parts.append(text(618, op_y + 22, "3. Оновлення стану", size=11, color=INK, bold=True))
    parts.append(text(618, op_y + 44, "Корекція \u0394x = K\u00b7y,", size=10, color=MUTED))
    parts.append(text(618, op_y + 58, "прокочування поправок", size=10, color=MUTED))
    parts.append(text(618, op_y + 72, "до актуального x̂(t_now)", size=10, color=MUTED))
    parts.append(rect(536, op_y + 90, 164, 26, fill="#ffffff", stroke="#16a34a", sw=1, rx=4))
    parts.append(text(618, op_y + 107, "x̂(t_now) скориговано", size=11, color=FIELD, bold=True))

    cap = "Відкладене злиття в EKF: обчислення нев'язки на точній часовій точці минулого x̂(t - \u03c4) запобігає розходженню оцінювача."
    parts.append(fitbox(35, H - 40, W - 70, 24, cap, size=11, fill="#f4f6f8", stroke=MUTED))

    return render(os.path.join(OUT, 'delayed-fusion-ring-buffer.svg'), W, H,
                  *parts, title='Буфер затримок станів у розширеному фільтрі Калмана')


if __name__ == '__main__':
    fig_sensor_latency_breakdown()
    fig_phase_margin_bode_delay()
    fig_delayed_fusion_ring_buffer()
    print("All figures generated successfully.")
